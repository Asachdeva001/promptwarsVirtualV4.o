import os
import sys
from dotenv import load_dotenv

# Load env vars before importing database
load_dotenv()

# Ensure we have the credentials set
if not os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY"):
    print("ERROR: FIREBASE_SERVICE_ACCOUNT_KEY environment variable is not set.")
    print("Please set it in your backend/.env file before running this script.")
    sys.exit(1)

# Add backend to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.database import db_client, STADIUM_REGISTRY
except ImportError as e:
    print(f"Error importing app modules: {e}")
    sys.exit(1)

if not db_client:
    print("ERROR: Could not initialize Firebase client. Check your credentials.")
    sys.exit(1)

def seed_stadium(stadium_id: str):
    print(f"Seeding dummy data for stadium: {stadium_id}...")
    
    stadium_ref = db_client.collection("stadiums").document(stadium_id)
    
    # Base stadium doc
    stadium_ref.set({
        "match_minute": 0,
        "match_score": "0 - 0",
        "match_teams": "Home vs Away"
    }, merge=True)
    
    # 1. Gates
    gates_data = [
        {"id": "gate_a", "current_queue_length": 45, "estimated_wait_time": 5, "ticket_scanner_speed": 3.0, "status": "Normal", "coordinates": {"x": 20, "y": 10}},
        {"id": "gate_b", "current_queue_length": 150, "estimated_wait_time": 18, "ticket_scanner_speed": 2.5, "status": "Busy", "coordinates": {"x": 80, "y": 10}},
        {"id": "gate_c", "current_queue_length": 250, "estimated_wait_time": 28, "ticket_scanner_speed": 3.0, "status": "Congested", "coordinates": {"x": 80, "y": 90}},
        {"id": "gate_d", "current_queue_length": 30, "estimated_wait_time": 3, "ticket_scanner_speed": 3.5, "status": "Normal", "coordinates": {"x": 20, "y": 90}}
    ]
    for gate in gates_data:
        stadium_ref.collection("gates").document(gate["id"]).set(gate)
        
    # 2. Volunteers
    volunteers_data = [
        {"id": "vol_001", "name": "Sarah Jenkins", "role": "Medical", "status": "Idle", "location": "Section 104", "battery": 82, "assigned_incident": None},
        {"id": "vol_002", "name": "Marcus Chen", "role": "Security", "status": "Busy", "location": "Gate B", "battery": 45, "assigned_incident": "inc_992"},
        {"id": "vol_003", "name": "Elena Rodriguez", "role": "Guest Services", "status": "Idle", "location": "Concourse East", "battery": 95, "assigned_incident": None},
        {"id": "vol_004", "name": "James Wilson", "role": "Crowd Control", "status": "Busy", "location": "Gate C", "battery": 28, "assigned_incident": "inc_991"}
    ]
    for vol in volunteers_data:
        stadium_ref.collection("volunteers").document(vol["id"]).set(vol)
        
    # 3. Incidents
    incidents_data = [
        {"id": "inc_991", "type": "Crowd Bottleneck", "severity": "High", "location": "Gate C", "status": "In Progress", "assigned_to": ["vol_004"], "reported_at": "18:42"},
        {"id": "inc_992", "type": "Medical Emergency", "severity": "Critical", "location": "Section 215", "status": "Assigned", "assigned_to": ["vol_002"], "reported_at": "18:55"},
        {"id": "inc_993", "type": "Spill Cleanup", "severity": "Low", "location": "Concourse West", "status": "Open", "assigned_to": [], "reported_at": "19:01"}
    ]
    for inc in incidents_data:
        stadium_ref.collection("incidents").document(inc["id"]).set(inc)
        
    # 4. Transit
    transit_data = [
        {"id": "train", "name": "Blue Line Express", "wait_time": 15, "status": "Normal"},
        {"id": "bus", "name": "City Bus Route 42", "wait_time": 5, "status": "Normal"},
        {"id": "rideshare", "name": "Rideshare Zone A", "wait_time": 25, "status": "Busy"}
    ]
    for tr in transit_data:
        stadium_ref.collection("transit").document(tr["id"]).set(tr)
        
    # 5. Concessions
    concessions_data = [
        {"id": "conc_0", "type": "Food", "name": "Burger Stand A", "current_wait_time": 18, "special_offer": "Free fries with combo"},
        {"id": "conc_1", "type": "Food", "name": "Tacos & Churros East", "current_wait_time": 4, "special_offer": "2 for 1 Tacos"},
        {"id": "conc_2", "type": "Restroom", "name": "Restroom Hub 1", "current_wait_time": 12, "accessibility_friendly": True},
        {"id": "conc_3", "type": "Restroom", "name": "Restroom Hub 2", "current_wait_time": 2, "accessibility_friendly": True}
    ]
    for conc in concessions_data:
        stadium_ref.collection("concessions").document(conc["id"]).set(conc)
        
    print(f"Successfully seeded {stadium_id}!")

def main():
    print("Starting Firebase database seeding process...")
    for stadium_id in STADIUM_REGISTRY.keys():
        seed_stadium(stadium_id)
    print("Database seeding complete!")

if __name__ == "__main__":
    main()
