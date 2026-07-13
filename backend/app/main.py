from fastapi import FastAPI, HTTPException, Query, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, constr
from typing import List, Dict, Any, Optional

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import secure

from app.config import settings
from app.database import db
from app.agents.coordinator import coordinator_agent
from app.agents.crowd import crowd_agent
from app.agents.volunteer import volunteer_agent
from app.agents.fan import fan_agent

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="StadiumOS API Services - AI Operations Platform for FIFA World Cup 2026",
    version="1.0.0"
)

# Setup SlowAPI Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Setup Secure Headers
secure_headers = secure.Secure()

@app.middleware("http")
async def set_secure_headers(request, call_next):
    response = await call_next(request)
    secure_headers.framework.fastapi(response)
    return response

# Standardized Exception Handler (Mod 9)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log exception here (structured logging) in production
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "An internal server error occurred.", "details": str(exc)}
    )

# Enable CORS for frontend integration
import os
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

# Add wildcards for cloud run environments or support credentials dynamically
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="https://.*\\.run\\.app",
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# --- Pydantic Models for Schema Validation (Mod 2) ---

class RerouteRequest(BaseModel):
    source_gate_id: str = Field(..., min_length=1, max_length=50, description="ID of gate experiencing bottleneck")
    dest_gate_id: str = Field(..., min_length=1, max_length=50, description="ID of gate to receive redirected flow")

class AssignRequest(BaseModel):
    incident_id: str = Field(..., min_length=1, max_length=50, description="ID of the active incident")
    volunteer_id: str = Field(..., min_length=1, max_length=50, description="ID of the volunteer being assigned")

class IncidentStatusUpdateRequest(BaseModel):
    incident_id: str = Field(..., min_length=1, max_length=50, description="ID of the active incident")
    status: str = Field(..., min_length=1, max_length=50, pattern="^(Assigned|In Progress|Resolved)$", description="Target status")

class CopilotQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Natural language question/prompt from organizer")

class FanQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Question from fan mobile app")
    language: str = Field("en", min_length=2, max_length=10, description="Language code")

class SelectStadiumRequest(BaseModel):
    stadium_id: str = Field(..., min_length=1, max_length=50, description="ID of target World Cup stadium")

class VisionInspectRequest(BaseModel):
    camera_id: str = Field(..., min_length=1, max_length=50, description="CCTV Camera ID to inspect")

class EgressRequest(BaseModel):
    transit_id: str = Field(..., min_length=1, max_length=50, description="ID of congested public transit line")

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "endpoints": {
            "status": "/api/status",
            "gates": "/api/gates",
            "volunteers": "/api/volunteers",
            "incidents": "/api/incidents"
        }
    }

@app.get("/api/status")
def get_status_summary():
    """Retrieve overall live telemetry status of the stadium."""
    try:
        summary = db.get_status_summary()
        summary["logs"] = db.logs[:15] # Top 15 logs
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch status: {str(e)}"
        )

@app.get("/api/gates")
def get_gates_telemetry(timeline: int = Query(0, description="Offset in minutes from live time (0, 10, 20, 30)")):
    """Retrieve gates status, wait times, queues, and predictions."""
    try:
        # Save timeline offset in database
        db.timeline_offset = timeline
        prediction = crowd_agent.get_predictions(timeline)
        return prediction
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch crowd predictions: {str(e)}"
        )

@app.post("/api/gates/reroute")
def post_reroute_flow(req: RerouteRequest):
    """Execute crowd rerouting recommendation to load-balance turnstiles."""
    try:
        res = crowd_agent.execute_rerouting(req.source_gate_id, req.dest_gate_id)
        if not res["success"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res["message"])
        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/api/volunteers")
def get_volunteers():
    """Retrieve volunteer registry, current positions, workloads, and workloads."""
    try:
        return db.volunteers
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/api/incidents")
def get_incidents():
    """Retrieve active and historical operational incidents."""
    try:
        return db.incidents
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/api/incidents/{incident_id}/recommend")
def get_volunteer_recommendations(incident_id: str):
    """Compute nearest and most suitable volunteers for a specific incident."""
    try:
        res = volunteer_agent.recommend_volunteer(incident_id)
        if not res["success"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=res["message"])
        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/api/incidents/assign")
def post_assign_volunteer(req: AssignRequest):
    """Dispatch a volunteer to an active incident."""
    try:
        res = volunteer_agent.assign_volunteer(req.incident_id, req.volunteer_id)
        if not res["success"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res["message"])
        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/api/incidents/status")
def post_update_incident_status(req: IncidentStatusUpdateRequest):
    """Update status of a dispatch ticket (Assigned, In Progress, Resolved)."""
    try:
        res = volunteer_agent.update_incident_status(req.incident_id, req.status)
        if not res["success"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res["message"])
        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/api/copilot/query")
@limiter.limit("5/minute")
def post_copilot_query(request: Request, req: CopilotQueryRequest):
    """Send natural language query to the Operations Copilot Agent."""
    try:
        res = coordinator_agent.process_organizer_query(req.query)
        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/api/fan/query")
@limiter.limit("10/minute")
def post_fan_query(request: Request, req: FanQueryRequest):
    """Send natural language query from fan app to Fan Experience Agent."""
    try:
        res = fan_agent.handle_query(req.query, req.language)
        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/api/reset")
def post_reset_simulation():
    """Resets the mock databases to their initial configuration."""
    try:
        db.reset()
        return {"success": True, "message": "Simulation databases reset."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/api/stadiums")
def get_stadiums_list():
    """List available stadiums and active scores."""
    try:
        from app.database import STADIUM_REGISTRY
        return [
            {
                "id": s_id,
                "name": s_info["name"],
                "location": s_info["location"],
                "capacity": s_info["capacity"],
                "match_teams": db.stadium_states[s_id]["match_teams"],
                "match_score": db.stadium_states[s_id]["match_score"],
                "match_minute": db.stadium_states[s_id]["match_minute"]
            }
            for s_id, s_info in STADIUM_REGISTRY.items()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stadiums/select")
def select_active_stadium(req: SelectStadiumRequest):
    """Switch active stadium context."""
    try:
        from app.database import STADIUM_REGISTRY
        if req.stadium_id not in STADIUM_REGISTRY:
            raise HTTPException(status_code=404, detail="Stadium not registered.")
        db.active_id = req.stadium_id
        db.add_log("system", f"Switched context to {STADIUM_REGISTRY[req.stadium_id]['name']}.")
        return {"success": True, "active_stadium_id": db.active_id, "summary": db.get_status_summary()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/transit")
def get_local_transit():
    """Retrieve local subway/bus status for active venue."""
    try:
        return db.transit
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transit/balance")
def balance_transit_flow(req: EgressRequest):
    """Egress Action: deploy shuttle transit and balance flow."""
    try:
        target_transit = next((t for t in db.transit if t["id"] == req.transit_id), None)
        if not target_transit:
            raise HTTPException(status_code=404, detail="Transit line not found.")
        
        old_wait = target_transit["wait_time"]
        target_transit["wait_time"] = max(5, target_transit["wait_time"] - 10)
        target_transit["status"] = "Normal"
        
        db.add_log("system", f"Egress dispatch: Deployed auxiliary shuttles for {target_transit['name']}. Wait time reduced to {target_transit['wait_time']}m.")
        return {"success": True, "transit": db.transit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vision/inspect")
def inspect_cctv_frame(req: VisionInspectRequest):
    """Inspect CCTV camera frame for safety obstructions."""
    try:
        camera_id = req.camera_id
        stadium_id = db.active_id
        
        presets = {
            "metlife": {
                "cam_104": {
                    "hazard_detected": True,
                    "severity": "Critical",
                    "hazard_type": "Crowd Bottleneck",
                    "description": "Severe crowd bottleneck detected at Gate A concourse. Flow rate is under 35 persons/min due to turnstile scanner delays.",
                    "action": "Execute Gate A to Gate B traffic diversion. Dispatch turnstile technician.",
                    "confidence": 96
                },
                "cam_202": {
                    "hazard_detected": True,
                    "severity": "Critical",
                    "hazard_type": "Obstruction",
                    "description": "Safety hazard detected in Section 228: Dual industrial trash bins are blocking the emergency exit stairwell.",
                    "action": "Dispatch nearby volunteer to clear obstruction immediately.",
                    "confidence": 98
                }
            },
            "azteca": {
                "cam_104": {
                    "hazard_detected": False,
                    "severity": "Low",
                    "hazard_type": "None",
                    "description": "Azteca Concourse entry flow is optimal. No bottleneck threat detected.",
                    "action": "Continue automated scanning.",
                    "confidence": 94
                },
                "cam_202": {
                    "hazard_detected": True,
                    "severity": "Medium",
                    "hazard_type": "Slippery Surface",
                    "description": "Liquid spill detected near East Concourse restrooms. Moderate slip hazard for descending fans.",
                    "action": "Dispatch cleanup volunteer to secure area.",
                    "confidence": 91
                }
            },
            "bc_place": {
                "cam_104": {
                    "hazard_detected": False,
                    "severity": "Low",
                    "hazard_type": "None",
                    "description": "BC Place entry Gate A flow rate is normal.",
                    "action": "Continue automated scanning.",
                    "confidence": 95
                },
                "cam_202": {
                    "hazard_detected": True,
                    "severity": "Medium",
                    "hazard_type": "Accessibility Blockage",
                    "description": "Section 104 ADA elevator corridor is blocked by broadcast equipment cables.",
                    "action": "Notify Facilities to relocate cables. Deploy volunteer to guide wheelchair users.",
                    "confidence": 93
                }
            }
        }
        
        report = presets.get(stadium_id, {}).get(camera_id, {
            "hazard_detected": False,
            "severity": "Low",
            "hazard_type": "None",
            "description": f"Camera {camera_id} area scanned. Crowd levels normal. No hazards found.",
            "action": "Maintain routine CCTV polling.",
            "confidence": 90
        })
        
        if coordinator_agent.use_api:
            try:
                import google.generativeai as genai
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"Rewrite this CCTV alert message to sound like a brief, highly professional military-grade or FIFA security dispatcher alert (1 sentence max): '{report['description']}'"
                response = model.generate_content(prompt)
                if response.text:
                    report["description"] = response.text.strip()
            except Exception:
                pass
                
        if report["hazard_detected"]:
            db.add_log("cctv", f"AI Vision Alert: {report['hazard_type']} detected on {camera_id.upper()}. Severity: {report['severity']}.")
            
        return {"success": True, "camera_id": camera_id, "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/match/tick")
def match_tick():
    """Increment match timeline by 1 minute."""
    try:
        db.increment_match_minute()
        return {
            "match_minute": db.match_minute,
            "match_score": db.match_score,
            "status": db.get_status_summary()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
