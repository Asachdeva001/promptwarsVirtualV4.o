import math
from typing import Dict, List, Any, Optional
from app.mock_data import db

class VolunteerCoordinatorAgent:
    def __init__(self):
        pass

    def calculate_distance(self, p1: Dict[str, int], p2: Dict[str, int]) -> float:
        """Calculate Euclidean distance between two points on the stadium grid."""
        return math.sqrt((p1["x"] - p2["x"])**2 + (p1["y"] - p2["y"])**2)

    def recommend_volunteer(self, incident_id: str) -> Dict[str, Any]:
        """
        Finds the nearest suitable volunteer based on location, workload, and specialty.
        Formula: Score = (Distance * 0.6) + (Workload * 15.0)
        If the specialty matches the incident type exactly, we give a preference offset.
        We sort in ascending order of score (lowest score is best).
        """
        incident = next((i for i in db.incidents if i["id"] == incident_id), None)
        if not incident:
            return {"success": False, "message": "Incident not found"}

        # Define specialty mapping
        # Incident type -> Needed volunteer specialty
        specialty_map = {
            "Medical": "Medical",
            "Security": "Security",
            "Ticket Scanner Malfunction": "Crowd Control",
            "Spill": "Crowd Control", # or general support
            "Lost Child": "Information"
        }
        
        target_specialty = specialty_map.get(incident["type"], None)
        
        candidates = []
        for volunteer in db.volunteers:
            if volunteer["status"] == "On Break":
                continue
                
            dist = self.calculate_distance(volunteer["coordinates"], incident["coordinates"])
            
            # Specialty match score adjustment
            # Volunteers matching the specialty get a bonus (multiplier reduction to score)
            specialty_match = (volunteer["specialty"] == target_specialty)
            
            # Calculate composite score
            # Lower is better. Workload is scaled to map to meters (e.g. 1 active task = 15m penalty)
            workload_penalty = volunteer["workload"] * 15.0
            
            # If specialty is required and matches, no penalty. If doesn't match, add a penalty
            specialty_penalty = 0.0 if (not target_specialty or specialty_match) else 30.0
            
            score = dist + workload_penalty + specialty_penalty
            
            candidates.append({
                "volunteer": volunteer,
                "distance": round(dist, 1),
                "workload": volunteer["workload"],
                "specialty_match": specialty_match,
                "score": round(score, 2)
            })
            
        # Sort candidates by score
        candidates.sort(key=lambda x: x["score"])
        
        return {
            "success": True,
            "incident": incident,
            "recommended_candidates": candidates[:3]  # Return top 3 choices
        }

    def assign_volunteer(self, incident_id: str, volunteer_id: str) -> Dict[str, Any]:
        """Assign volunteer to incident, update workloads and statuses."""
        incident = next((i for i in db.incidents if i["id"] == incident_id), None)
        volunteer = next((v for v in db.volunteers if v["id"] == volunteer_id), None)
        
        if not incident or not volunteer:
            return {"success": False, "message": "Incident or Volunteer not found"}
            
        # If volunteer already assigned to this incident, return
        if incident["assigned_volunteer_id"] == volunteer_id:
            return {"success": True, "message": "Volunteer already assigned", "incident": incident}

        # Clear previous volunteer workload if any
        if incident["assigned_volunteer_id"]:
            prev_vol = next((v for v in db.volunteers if v["id"] == incident["assigned_volunteer_id"]), None)
            if prev_vol:
                prev_vol["workload"] = max(0, prev_vol["workload"] - 1)
                if prev_vol["workload"] == 0:
                    prev_vol["status"] = "Idle"
                    
        # Assign new volunteer
        incident["assigned_volunteer_id"] = volunteer_id
        incident["status"] = "Assigned"
        
        volunteer["workload"] += 1
        volunteer["status"] = "Busy"
        
        db.add_log("volunteer", f"Dispatched {volunteer['name']} to {incident['title']} at {incident['location_name']}.")
        
        return {
            "success": True,
            "message": f"Successfully assigned {volunteer['name']} to {incident['title']}.",
            "incident": incident,
            "volunteer": volunteer,
            "volunteers": db.volunteers
        }

    def update_incident_status(self, incident_id: str, status: str) -> Dict[str, Any]:
        """Update status of an incident (e.g. Assigned -> In Progress -> Resolved)."""
        incident = next((i for i in db.incidents if i["id"] == incident_id), None)
        if not incident:
            return {"success": False, "message": "Incident not found"}
            
        old_status = incident["status"]
        incident["status"] = status
        
        # If resolved, reduce volunteer workload
        if status == "Resolved" and old_status != "Resolved":
            vol = next((v for v in db.volunteers if v["id"] == incident["assigned_volunteer_id"]), None)
            if vol:
                vol["workload"] = max(0, vol["workload"] - 1)
                if vol["workload"] == 0:
                    vol["status"] = "Idle"
            db.add_log("incident", f"Incident '{incident['title']}' at {incident['location_name']} marked as RESOLVED.")
        else:
            db.add_log("incident", f"Incident '{incident['title']}' status updated to {status}.")
            
        return {
            "success": True,
            "incident": incident,
            "volunteers": db.volunteers
        }

volunteer_agent = VolunteerCoordinatorAgent()
