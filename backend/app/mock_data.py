from typing import List, Dict, Any, Optional
import datetime

# Initial static configurations
INITIAL_GATES = [
    {
        "id": "gate_a",
        "name": "Gate A (North-West)",
        "status": "Open",
        "current_flow_rate": 120,          # people/min
        "ticket_scanner_speed": 4.5,       # seconds per ticket scan
        "current_queue_length": 620,       # people in queue
        "estimated_wait_time": 15,         # minutes
        "coordinates": {"x": 20, "y": 10}
    },
    {
        "id": "gate_b",
        "name": "Gate B (North-East)",
        "status": "Open",
        "current_flow_rate": 60,
        "ticket_scanner_speed": 3.0,
        "current_queue_length": 150,
        "estimated_wait_time": 4,
        "coordinates": {"x": 80, "y": 10}
    },
    {
        "id": "gate_c",
        "name": "Gate C (South-East)",
        "status": "Open",
        "current_flow_rate": 80,
        "ticket_scanner_speed": 3.5,
        "current_queue_length": 280,
        "estimated_wait_time": 7,
        "coordinates": {"x": 80, "y": 90}
    },
    {
        "id": "gate_d",
        "name": "Gate D (South-West)",
        "status": "Open",
        "current_flow_rate": 90,
        "ticket_scanner_speed": 3.8,
        "current_queue_length": 340,
        "estimated_wait_time": 9,
        "coordinates": {"x": 20, "y": 90}
    }
]

INITIAL_VOLUNTEERS = [
    {
        "id": "vol_1",
        "name": "Juan Perez",
        "specialty": "Information",
        "coordinates": {"x": 25, "y": 20},
        "workload": 0,
        "status": "Idle",
        "phone": "+1 (555) 019-2831"
    },
    {
        "id": "vol_2",
        "name": "John Doe",
        "specialty": "Medical",
        "coordinates": {"x": 42, "y": 35},
        "workload": 1,
        "status": "Busy",
        "phone": "+1 (555) 014-9988"
    },
    {
        "id": "vol_3",
        "name": "Marie Curie",
        "specialty": "Medical",
        "coordinates": {"x": 50, "y": 65},
        "workload": 0,
        "status": "Idle",
        "phone": "+1 (555) 017-3321"
    },
    {
        "id": "vol_4",
        "name": "Aisha Amin",
        "specialty": "Security",
        "coordinates": {"x": 78, "y": 15},
        "workload": 0,
        "status": "Idle",
        "phone": "+1 (555) 018-8877"
    },
    {
        "id": "vol_5",
        "name": "Yuki Tanaka",
        "specialty": "Accessibility",
        "coordinates": {"x": 15, "y": 80},
        "workload": 0,
        "status": "Idle",
        "phone": "+1 (555) 012-4455"
    },
    {
        "id": "vol_6",
        "name": "Liam Carter",
        "specialty": "Crowd Control",
        "coordinates": {"x": 85, "y": 85},
        "workload": 2,
        "status": "Busy",
        "phone": "+1 (555) 011-0099"
    },
    {
        "id": "vol_7",
        "name": "Carlos Ruiz",
        "specialty": "Crowd Control",
        "coordinates": {"x": 25, "y": 88},
        "workload": 0,
        "status": "Idle",
        "phone": "+1 (555) 013-7744"
    },
    {
        "id": "vol_8",
        "name": "Fatima Al-Sayed",
        "specialty": "Security",
        "coordinates": {"x": 55, "y": 12},
        "workload": 0,
        "status": "Idle",
        "phone": "+1 (555) 016-1122"
    }
]

INITIAL_INCIDENTS = [
    {
        "id": "inc_1",
        "type": "Medical",
        "title": "Heat Exhaustion",
        "description": "Elderly spectator feeling dizzy and dehydrated near Concourse A.",
        "location_name": "Section 112 (Row K)",
        "coordinates": {"x": 45, "y": 30},
        "severity": "Critical",
        "status": "Assigned",
        "assigned_volunteer_id": "vol_2",
        "timestamp": "2026-07-08T22:45:00Z"
    },
    {
        "id": "inc_2",
        "type": "Spill",
        "title": "Slippery Surface",
        "description": "Large soda spill causing a safety hazard on the stairs.",
        "location_name": "South Concourse (near Food Court B)",
        "coordinates": {"x": 72, "y": 55},
        "severity": "Low",
        "status": "Unassigned",
        "assigned_volunteer_id": None,
        "timestamp": "2026-07-08T23:01:00Z"
    },
    {
        "id": "inc_3",
        "type": "Ticket Scanner Malfunction",
        "title": "Scanner Offline",
        "description": "Turnstile 4 scanner is not reading barcodes, creating entry delays.",
        "location_name": "Gate A (Turnstile 4)",
        "coordinates": {"x": 22, "y": 12},
        "severity": "Medium",
        "status": "Unassigned",
        "assigned_volunteer_id": None,
        "timestamp": "2026-07-08T23:03:00Z"
    }
]

INITIAL_CONCESSIONS = [
    {
        "id": "food_a",
        "name": "Burgers & Beers (West)",
        "type": "Concession",
        "coordinates": {"x": 30, "y": 50},
        "current_wait_time": 18,
        "special_offer": "Buy 1 Get 1 on Soft Drinks after 65th minute"
    },
    {
        "id": "food_b",
        "name": "Tacos & Churros (East)",
        "type": "Concession",
        "coordinates": {"x": 70, "y": 50},
        "current_wait_time": 4,
        "special_offer": "Fast Queue for Disabled Badge Holders"
    },
    {
        "id": "restroom_a",
        "name": "Restroom Hub 1",
        "type": "Restroom",
        "coordinates": {"x": 50, "y": 15},
        "current_wait_time": 6,
        "accessibility_friendly": True
    },
    {
        "id": "restroom_b",
        "name": "Restroom Hub 2",
        "type": "Restroom",
        "coordinates": {"x": 50, "y": 85},
        "current_wait_time": 2,
        "accessibility_friendly": True
    }
]

# Database Simulation
class StadiumDatabase:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.gates = [dict(g) for g in INITIAL_GATES]
        self.volunteers = [dict(v) for v in INITIAL_VOLUNTEERS]
        self.incidents = [dict(i) for i in INITIAL_INCIDENTS]
        self.concessions = [dict(c) for c in INITIAL_CONCESSIONS]
        self.timeline_offset = 0 # Minutes from live: 0, 10, 20, 30
        
        # System action logs
        self.logs = [
            {"time": "22:50", "type": "system", "message": "StadiumOS Online. All systems monitoring live."},
            {"time": "22:52", "type": "cctv", "message": "Crowd flow at Gate C is optimal (80 persons/min)."},
            {"time": "22:58", "type": "volunteer", "message": "John Doe assigned to medical incident in Section 112."},
            {"time": "23:01", "type": "incident", "message": "New Incident: Spill reported in South Concourse."},
            {"time": "23:03", "type": "incident", "message": "New Incident: Ticket scanner offline at Gate A."}
        ]
        
    def get_status_summary(self) -> Dict[str, Any]:
        # Aggregate stats
        total_volunteers = len(self.volunteers)
        active_volunteers = sum(1 for v in self.volunteers if v["status"] == "Busy")
        idle_volunteers = sum(1 for v in self.volunteers if v["status"] == "Idle")
        
        total_incidents = len(self.incidents)
        critical_incidents = sum(1 for i in self.incidents if i["severity"] == "Critical" and i["status"] != "Resolved")
        active_incidents = sum(1 for i in self.incidents if i["status"] != "Resolved")
        
        # Total occupancy simulation (approx 85% capacity of 80,000)
        occupancy = 68450
        
        # Calculate crowd stress factor (based on queue lengths at Gates)
        max_wait = max(g["estimated_wait_time"] for g in self.gates)
        crowd_status = "Green"
        if max_wait > 12:
            crowd_status = "Red" if max_wait > 20 else "Yellow"
            
        return {
            "occupancy": occupancy,
            "occupancy_rate": round((occupancy / 80000) * 100, 1),
            "total_volunteers": total_volunteers,
            "active_volunteers": active_volunteers,
            "idle_volunteers": idle_volunteers,
            "total_incidents": total_incidents,
            "active_incidents": active_incidents,
            "critical_incidents": critical_incidents,
            "crowd_status": crowd_status,
            "max_gate_wait_time": max_wait
        }

    def add_log(self, message_type: str, message: str):
        now_str = datetime.datetime.now().strftime("%H:%M")
        self.logs.insert(0, {"time": now_str, "type": message_type, "message": message})
        if len(self.logs) > 50:
            self.logs.pop()

db = StadiumDatabase()
