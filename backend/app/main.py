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

# Removed RerouteRequest

class HelpRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Requester's name")
    contact_number: str = Field(..., min_length=5, max_length=20, description="Requester's contact number")
    assistance_type: str = Field(..., min_length=2, max_length=100, description="Type of assistance required (e.g., Medical, Directions)")
    location: str = Field(..., min_length=2, max_length=200, description="Location or nearby landmark")

class FanQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Question from fan mobile app")
    language: str = Field("en", min_length=2, max_length=10, description="Language code")

class SelectStadiumRequest(BaseModel):
    stadium_id: str = Field(..., min_length=1, max_length=50, description="ID of target World Cup stadium")

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
            "volunteers": "/api/volunteers"
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

@app.get("/api/volunteers")
def get_volunteers():
    """Retrieve volunteer registry, current positions, workloads, and workloads."""
    try:
        return db.volunteers
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

@app.post("/api/help/request")
@limiter.limit("5/minute")
def post_help_request(request: Request, req: HelpRequest):
    """Process a fan's help request and assign a volunteer."""
    import random
    try:
        # Find an idle volunteer or use a fallback
        volunteers = db.volunteers
        idle_vols = [v for v in volunteers if v.get("status") == "Idle"]
        assigned = idle_vols[0] if idle_vols else {"name": "Staff Team Alpha", "phone": "N/A", "specialty": "General Support"}
        
        # Calculate a mock ETA in minutes
        eta_minutes = random.randint(2, 8)
        
        # In a real app we would save this to the DB, but here we just return the assignment.
        return {
            "success": True,
            "message": "Help request received.",
            "assigned_volunteer": {
                "name": assigned.get("name", "Support Staff"),
                "phone": assigned.get("phone", "N/A"),
                "specialty": assigned.get("specialty", "General")
            },
            "eta_minutes": eta_minutes
        }
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
        from app.database import STADIUM_REGISTRY, db_client
        stadiums = []
        for s_id, s_info in STADIUM_REGISTRY.items():
            match_teams = "Team A vs Team B"
            match_score = "0 - 0"
            match_minute = 0
            
            if db_client:
                doc = db_client.collection("stadiums").document(s_id).get()
                if doc.exists:
                    data = doc.to_dict()
                    match_teams = data.get("match_teams", match_teams)
                    match_score = data.get("match_score", match_score)
                    match_minute = data.get("match_minute", match_minute)
                    
            stadiums.append({
                "id": s_id,
                "name": s_info["name"],
                "location": s_info["location"],
                "capacity": s_info["capacity"],
                "match_teams": match_teams,
                "match_score": match_score,
                "match_minute": match_minute
            })
        return stadiums
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
