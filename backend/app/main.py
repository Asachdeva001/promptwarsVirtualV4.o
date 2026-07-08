from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from app.config import settings
from app.mock_data import db
from app.agents.coordinator import coordinator_agent
from app.agents.crowd import crowd_agent
from app.agents.volunteer import volunteer_agent
from app.agents.fan import fan_agent

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="StadiumOS API Services - AI Operations Platform for FIFA World Cup 2026",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for Schema Validation ---

class RerouteRequest(BaseModel):
    source_gate_id: str = Field(..., description="ID of gate experiencing bottleneck")
    dest_gate_id: str = Field(..., description="ID of gate to receive redirected flow")

class AssignRequest(BaseModel):
    incident_id: str = Field(..., description="ID of the active incident")
    volunteer_id: str = Field(..., description="ID of the volunteer being assigned")

class IncidentStatusUpdateRequest(BaseModel):
    incident_id: str = Field(..., description="ID of the active incident")
    status: str = Field(..., description="Target status (e.g. Assigned, In Progress, Resolved)")

class CopilotQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language question/prompt from organizer")

class FanQueryRequest(BaseModel):
    query: str = Field(..., description="Question from fan mobile app")
    language: str = Field("en", description="Language code (en, es, fr, de, ar)")

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
def post_copilot_query(req: CopilotQueryRequest):
    """Send natural language query to the Operations Copilot Agent."""
    try:
        res = coordinator_agent.process_organizer_query(req.query)
        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/api/fan/query")
def post_fan_query(req: FanQueryRequest):
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
