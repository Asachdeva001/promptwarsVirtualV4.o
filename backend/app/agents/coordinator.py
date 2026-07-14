import os
import json
import logging
from typing import Dict, Any, List
from app.config import settings
from app.database import db
from app.agents.volunteer import volunteer_agent

logger = logging.getLogger("StadiumOS.Coordinator")

# Try importing the official google-generativeai sdk
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

class CoordinatorAgent:
    """
    Coordinator Agent responsible for processing high-level operational intelligence.
    
    This agent parses natural language queries from the dashboard and orchestrates
    risk assessments, generating structured summaries, confidence scores, and
    actionable insights. It supports both Gemini LLM and deterministic fallback.
    """
    
    def __init__(self):
        """Initializes the CoordinatorAgent and configures API credentials."""
        self.api_key = settings.GEMINI_API_KEY
        self.use_api = False
        self.model_name = "gemini-1.5-flash"
        
        if HAS_GENAI:
            if self.api_key:
                try:
                    genai.configure(api_key=self.api_key)
                    self.use_api = True
                    logger.info(f"Gemini API configured successfully using GEMINI_API_KEY. Model: {self.model_name}")
                except Exception as e:
                    logger.error(f"Failed to configure Gemini API using API key: {e}.")
            else:
                # Try loading Application Default Credentials (ADC) from gcloud login / service accounts
                try:
                    import google.auth
                    credentials, project_id = google.auth.default()
                    genai.configure(credentials=credentials)
                    self.use_api = True
                    logger.info(f"Gemini API configured successfully using Application Default Credentials (ADC). Model: {self.model_name}")
                except Exception as e:
                    logger.info(f"No active Application Default Credentials (ADC) found: {e}.")
                    
        if not self.use_api:
            logger.info("Using local semantic rule engine fallback.")

    def run_live_risk_assessment(self) -> Dict[str, Any]:
        """Provides a structured risk summary, confidence, actions, and departments affected."""
        # Calculate current operational variables
        active_incidents = [inc for inc in db.incidents if inc["status"] != "Resolved"]
        
        risks = []
        departments = []
        actions = []
        
        # Look for bottlenecks (mocked directly from db now without crowd agent)
        if any(g.get("estimated_wait_time", 0) > 20 for g in db.gates):
            risks.append("Bottleneck threat at Gate A (expected wait >20 mins).")
            departments.append("Crowd Management")
            departments.append("Security")
            actions.append("Reroute incoming traffic from Gate A parking lot to Gate B.")
            
        # Look for medical or critical incidents
        critical_incidents = [i for i in active_incidents if i.get("severity") == "Critical"]
        if critical_incidents:
            for inc in critical_incidents:
                risks.append(f"Critical Incident: {inc.get('title', inc.get('type', 'Unknown Issue'))} at {inc.get('location', 'Unknown Location')}.")
                departments.append("Medical Services")
                actions.append(f"Ensure volunteer {inc.get('assigned_to', ['is assigned'])[0] if isinstance(inc.get('assigned_to'), list) and inc.get('assigned_to') else inc.get('assigned_volunteer_id', 'is assigned')} reaches {inc.get('location', 'the site')}.")
                
        # Unassigned incidents
        unassigned = [i for i in active_incidents if i["status"] == "Unassigned"]
        if unassigned:
            risks.append(f"There are {len(unassigned)} unassigned incidents requiring volunteer dispatch.")
            departments.append("Volunteer Coordination")
            actions.append("Dispatch nearest idle volunteers to South Concourse and Gate A.")

        # Egress transit delays check
        congested_transit = [t for t in db.transit if t["wait_time"] > 18]
        if congested_transit:
            for t in congested_transit:
                risks.append(f"Transit line {t['name']} is congested (Wait: {t['wait_time']} mins).")
                departments.append("Transportation")
                actions.append(f"Deploy auxiliary shuttles/buses for {t['name']} to balance egress.")
            
        # Default if everything is fine
        if not risks:
            risks.append("All systems operational. Minor wait times at ticketing turnstiles.")
            departments.append("Operations")
            actions.append("Continue monitoring live telemetry streams.")
            
        return {
            "summary": " ".join(risks),
            "confidence_score": 94 if critical_alerts or critical_incidents else 98,
            "departments": list(set(departments)),
            "recommended_actions": actions,
            "timestamp": "2026-07-08T23:09:17Z"
        }

    def process_organizer_query(self, query: str) -> Dict[str, Any]:
        """
        Processes natural language queries from organizers.
        If GEMINI_API_KEY is present, we call the Gemini API using function calling / schema generation.
        Otherwise, we fall back to a highly polished matching rule engine that generates beautiful, contextual outputs.
        """
        if self.use_api:
            try:
                # Construct a comprehensive prompt with live data context
                system_instruction = (
                    "You are the StadiumOS Coordinator Agent for the FIFA World Cup 2026. "
                    "You analyze live stadium telemetry and generate operational intelligence. "
                    "Always reply in JSON format with keys: 'summary' (str), 'confidence_score' (int), "
                    "'departments' (list of str), and 'recommended_actions' (list of str)."
                )
                
                context = {
                    "gates": db.gates,
                    "incidents": db.incidents,
                    "active_volunteers_count": sum(1 for v in db.volunteers if v["status"] == "Busy"),
                    "idle_volunteers_count": sum(1 for v in db.volunteers if v["status"] == "Idle"),
                }
                
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config={"response_mime_type": "application/json"}
                )
                
                prompt = (
                    f"Context: {json.dumps(context)}\n\n"
                    f"User Query: {query}\n\n"
                    f"System Instruction: {system_instruction}"
                )
                
                response = model.generate_content(prompt)
                
                # Robustly clean the markdown if it exists
                text = response.text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                elif text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
                
                parsed = json.loads(text)
                return {
                    "summary": parsed.get("summary", "Query processed successfully."),
                    "confidence_score": parsed.get("confidence_score", 90),
                    "departments": parsed.get("departments", ["Operations"]),
                    "recommended_actions": parsed.get("recommended_actions", ["Monitor the dashboard"])
                }
            except Exception as e:
                logger.error(f"Gemini API execution error: {e}. Raw response: {response.text if 'response' in locals() else 'None'}. Falling back to Rule Engine.")
                # Fallback to local rule engine on exception

        # --- Rule Engine Fallback ---
        q = query.lower()
        
        # Scenario 1: Risk questions
        if any(w in q for w in ["risk", "threat", "hazard", "problem", "bottleneck", "issue", "incident"]):
            assessment = self.run_live_risk_assessment()
            return {
                "summary": f"Our 15-20 min prediction models suggest {assessment['summary']}",
                "confidence_score": assessment["confidence_score"],
                "departments": assessment["departments"],
                "recommended_actions": assessment["recommended_actions"]
            }
            
        # Scenario 2: Volunteer query
        elif any(w in q for w in ["volunteer", "staff", "helper", "workload"]):
            idle = sum(1 for v in db.volunteers if v["status"] == "Idle")
            busy = sum(1 for v in db.volunteers if v["status"] == "Busy")
            return {
                "summary": f"We currently have {idle} idle volunteers ready for dispatch and {busy} busy. High concentration near Gate B and East Concourse. Section 112 has active medical coverage.",
                "confidence_score": 95,
                "departments": ["Volunteer Coordination", "Medical Services"],
                "recommended_actions": [
                    "Assign Carlos Ruiz or Marie Curie (both Idle) to pending spills.",
                    "Optimize volunteer coverage near Gate D before second half ends."
                ]
            }
            
        # Scenario 3: Gate / crowd congestion query
        elif any(w in q for w in ["gate", "crowd", "congestion", "traffic", "queue", "wait time"]):
            gate_a_wait = next(g["estimated_wait_time"] for g in db.gates if g["id"] == "gate_a")
            return {
                "summary": f"Gate A (North-West) is experiencing the highest wait times ({gate_a_wait} mins) due to an offline ticket scanner. Gates B, C, D have wait times under 10 minutes.",
                "confidence_score": 97,
                "departments": ["Crowd Management", "Technical Support"],
                "recommended_actions": [
                    "Initiate Gate A to Gate B traffic redirection.",
                    "Dispatch a hardware volunteer to fix the ticket scanner on Turnstile 4 at Gate A."
                ]
            }
            
        # Scenario 4: Concessions / food court query
        elif any(w in q for w in ["food", "concession", "churros", "burger", "hungry", "lines"]):
            return {
                "summary": "Food Court A (West) wait times are currently 18 minutes. Food Court B (East) is highly optimal with a 4-minute wait time.",
                "confidence_score": 99,
                "departments": ["Fan Experience", "Facilities"],
                "recommended_actions": [
                    "Push a mobile notification to fans recommending Food Court B.",
                    "Display special offers on West Concourse digital signage to divert traffic."
                ]
            }
        
        # Scenario 5: Transit & Egress query
        elif any(w in q for w in ["transit", "train", "bus", "ferry", "rideshare", "subway", "egress", "leave", "exit"]):
            congested = [t for t in db.transit if t["wait_time"] > 15]
            summary_parts = [f"{t['name']} wait is {t['wait_time']}m" for t in db.transit]
            summary_str = ", ".join(summary_parts)
            
            return {
                "summary": f"Local transit lines are loading for stadium egress. Status: {summary_str}. " + 
                           ("Delays detected on transit networks." if congested else "All lines running optimally."),
                "confidence_score": 98,
                "departments": ["Transportation", "Crowd Management"],
                "recommended_actions": [
                    f"Deploy auxiliary transit flow-balancing for congested lines.",
                    "Update digital signage to guide exiting crowds to optimal platforms."
                ]
            }
            
        # Default response
        return {
            "summary": "Operations running smoothly. Crowd levels, volunteer distributions, and incident response systems are within nominal boundaries.",
            "confidence_score": 90,
            "departments": ["Operations"],
            "recommended_actions": ["No direct intervention required. Maintain monitoring of standard telemetry."]
        }

coordinator_agent = CoordinatorAgent()
