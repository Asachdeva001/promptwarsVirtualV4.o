from typing import List, Dict, Any, Optional
import datetime

# Active World Cup Stadiums registries
STADIUM_REGISTRY = {
    "metlife": {
        "id": "metlife",
        "name": "MetLife Stadium",
        "location": "New York/New Jersey",
        "capacity": 82500,
        "match_teams": "USA vs England",
        "match_score": "2 - 1",
        "match_minute": 68,
        "transit": [
            {"id": "train", "name": "NJ Transit Train (Secaucus)", "type": "Train", "wait_time": 15, "status": "Delayed"},
            {"id": "bus", "name": "Coach USA Bus (Route 351)", "type": "Bus", "wait_time": 8, "status": "Normal"},
            {"id": "rideshare", "name": "Uber/Lyft Lot G", "type": "Rideshare", "wait_time": 20, "status": "Congested"}
        ]
    },
    "azteca": {
        "id": "azteca",
        "name": "Estadio Azteca",
        "location": "Mexico City",
        "capacity": 87500,
        "match_teams": "Mexico vs Argentina",
        "match_score": "0 - 0",
        "match_minute": 14,
        "transit": [
            {"id": "train", "name": "Tren Ligero Light Rail", "type": "Train", "wait_time": 6, "status": "Normal"},
            {"id": "bus", "name": "Colectivo Shuttle Depot", "type": "Bus", "wait_time": 12, "status": "Busy"},
            {"id": "rideshare", "name": "Taxi Stand North Gate", "type": "Rideshare", "wait_time": 18, "status": "Congested"}
        ]
    },
    "bc_place": {
        "id": "bc_place",
        "name": "BC Place",
        "location": "Vancouver",
        "capacity": 54500,
        "match_teams": "Canada vs France",
        "match_score": "1 - 1",
        "match_minute": 41,
        "transit": [
            {"id": "train", "name": "SkyTrain (Expo Line)", "type": "Train", "wait_time": 5, "status": "Normal"},
            {"id": "bus", "name": "TransLink Bus Hub", "type": "Bus", "wait_time": 12, "status": "Busy"},
            {"id": "rideshare", "name": "False Creek Ferry Dock", "type": "Rideshare", "wait_time": 10, "status": "Normal"}
        ]
    }
}

# Initial static configurations
INITIAL_GATES = [
    {
        "id": "gate_a",
        "name": "Gate A (North-West)",
        "status": "Open",
        "current_flow_rate": 120,
        "ticket_scanner_speed": 4.5,
        "current_queue_length": 620,
        "estimated_wait_time": 15,
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
        "description": "Spectator dehydrated near Concourse A.",
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
        "description": "Soda spill causing a hazard on the stairs.",
        "location_name": "South Concourse (near Food B)",
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
        "description": "Turnstile 4 scanner is offline creating delays.",
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
        self.active_id = "metlife"
        self.timeline_offset = 0
        self.stadium_states = {}
        
        for s_id, s_info in STADIUM_REGISTRY.items():
            self.stadium_states[s_id] = {
                "gates": [dict(g) for g in INITIAL_GATES],
                "volunteers": [dict(v) for v in INITIAL_VOLUNTEERS],
                "incidents": [dict(i) for i in INITIAL_INCIDENTS],
                "concessions": [dict(c) for c in INITIAL_CONCESSIONS],
                "transit": [dict(t) for t in s_info["transit"]],
                "match_minute": s_info["match_minute"],
                "match_score": s_info["match_score"],
                "match_teams": s_info["match_teams"],
                "logs": [
                    {"time": "22:50", "type": "system", "message": f"StadiumOS Online at {s_info['name']}. Monitoring live."},
                    {"time": "22:52", "type": "cctv", "message": "Crowd entry flow is nominal."},
                    {"time": "22:58", "type": "volunteer", "message": "Active volunteers synchronized with venue coordinates."}
                ]
            }

    @property
    def active_stadium(self):
        return self.stadium_states[self.active_id]

    @property
    def gates(self): return self.active_stadium["gates"]
    @gates.setter
    def gates(self, val): self.active_stadium["gates"] = val

    @property
    def volunteers(self): return self.active_stadium["volunteers"]
    @volunteers.setter
    def volunteers(self, val): self.active_stadium["volunteers"] = val

    @property
    def incidents(self): return self.active_stadium["incidents"]
    @incidents.setter
    def incidents(self, val): self.active_stadium["incidents"] = val

    @property
    def concessions(self): return self.active_stadium["concessions"]
    @concessions.setter
    def concessions(self, val): self.active_stadium["concessions"] = val

    @property
    def transit(self): return self.active_stadium["transit"]
    @transit.setter
    def transit(self, val): self.active_stadium["transit"] = val

    @property
    def logs(self): return self.active_stadium["logs"]
    @logs.setter
    def logs(self, val): self.active_stadium["logs"] = val

    @property
    def match_minute(self): return self.active_stadium["match_minute"]
    @match_minute.setter
    def match_minute(self, val): self.active_stadium["match_minute"] = val

    @property
    def match_score(self): return self.active_stadium["match_score"]
    @match_score.setter
    def match_score(self, val): self.active_stadium["match_score"] = val

    @property
    def match_teams(self): return self.active_stadium["match_teams"]
    @match_teams.setter
    def match_teams(self, val): self.active_stadium["match_teams"] = val

    def get_status_summary(self) -> Dict[str, Any]:
        total_volunteers = len(self.volunteers)
        active_volunteers = sum(1 for v in self.volunteers if v["status"] == "Busy")
        idle_volunteers = sum(1 for v in self.volunteers if v["status"] == "Idle")
        
        total_incidents = len(self.incidents)
        critical_incidents = sum(1 for i in self.incidents if i["severity"] == "Critical" and i["status"] != "Resolved")
        active_incidents = sum(1 for i in self.incidents if i["status"] != "Resolved")
        
        # Scale occupancy mock rates based on stadium capacity
        capacity = STADIUM_REGISTRY[self.active_id]["capacity"]
        occupancy = int(capacity * 0.85)
        
        max_wait = max(g["estimated_wait_time"] for g in self.gates)
        crowd_status = "Green"
        if max_wait > 12:
            crowd_status = "Red" if max_wait > 20 else "Yellow"
            
        return {
            "active_stadium_id": self.active_id,
            "stadium_name": STADIUM_REGISTRY[self.active_id]["name"],
            "stadium_location": STADIUM_REGISTRY[self.active_id]["location"],
            "match_teams": self.match_teams,
            "match_score": self.match_score,
            "match_minute": self.match_minute,
            "occupancy": occupancy,
            "occupancy_rate": 85.5,
            "total_volunteers": total_volunteers,
            "active_volunteers": active_volunteers,
            "idle_volunteers": idle_volunteers,
            "total_incidents": total_incidents,
            "active_incidents": active_incidents,
            "critical_incidents": critical_incidents,
            "crowd_status": crowd_status,
            "max_gate_wait_time": max_wait
        }

    def increment_match_minute(self):
        self.match_minute += 1
        if self.match_minute > 90:
            self.match_minute = 0
            
        # Simulate traffic changes in the egress phase (75m - 90m)
        if self.match_minute >= 75:
            # Increase transit wait times
            for t in self.transit:
                t["wait_time"] = min(45, t["wait_time"] + 1)
                t["status"] = "Congested" if t["wait_time"] > 18 else "Busy"
            
            # Increase gate queues as fans exit
            for g in self.gates:
                g["current_queue_length"] = min(1200, g["current_queue_length"] + 25)
                g["estimated_wait_time"] = int(g["current_queue_length"] * g["ticket_scanner_speed"] / 60 / 3.0)
                
            if self.match_minute == 75:
                self.add_log("system", "Warning: Egress phase initiated at minute 75'. Transit queues rising.")

    def add_log(self, message_type: str, message: str):
        now_str = datetime.datetime.now().strftime("%H:%M")
        self.logs.insert(0, {"time": now_str, "type": message_type, "message": message})
        if len(self.logs) > 50:
            self.logs.pop()

db = StadiumDatabase()
