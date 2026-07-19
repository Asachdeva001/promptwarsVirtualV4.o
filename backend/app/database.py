import os
import datetime
import logging
import json
from typing import List, Dict, Any, Optional
from firebase_admin import credentials, firestore
import firebase_admin
from dotenv import load_dotenv

load_dotenv()

# Structured Logging Config (Mod 14)
logger = logging.getLogger("stadiumOS")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}')
ch.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(ch)

# Initialize Firebase Admin SDK
firebase_cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
if firebase_cred_path and os.path.exists(firebase_cred_path):
    cred = credentials.Certificate(firebase_cred_path)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db_client = firestore.client()
    logger.info("Firebase Firestore initialized successfully with local credentials.")
else:
    # Try using Application Default Credentials (Cloud Run)
    try:
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        db_client = firestore.client()
        logger.info("Firebase Firestore initialized successfully using Application Default Credentials.")
    except Exception as e:
        logger.warning(f"Failed to initialize Firestore: {e}")
        db_client = None

STADIUM_REGISTRY = {
    "metlife": {
        "id": "metlife",
        "name": "MetLife Stadium",
        "location": "New York/New Jersey",
        "capacity": 82500,
    },
    "azteca": {
        "id": "azteca",
        "name": "Estadio Azteca",
        "location": "Mexico City",
        "capacity": 87500,
    },
    "bc_place": {
        "id": "bc_place",
        "name": "BC Place",
        "location": "Vancouver",
        "capacity": 54500,
    }
}

class MockDatabase:
    """
    In-memory Mock Database for StadiumOS telemetry simulation.
    
    This class maintains the state of the stadium simulation, including
    ticket gates, volunteer locations, active incidents, match progress,
    and system logs. It provides methods to reset and modify state safely.
    """
    def __init__(self):
        """Initializes the mock database with the default stadium context."""
        self._active_id = "metlife"
        self.timeline_offset = 0

    @property
    def active_id(self):
        return self._active_id

    @active_id.setter
    def active_id(self, val):
        self._active_id = val

    def _get_stadium_doc_ref(self):
        if not db_client: return None
        return db_client.collection("stadiums").document(self._active_id)

    def _get_collection_data(self, collection_name: str, fields: List[str] = None) -> List[Dict]:
        if not db_client: return []
        # Firestore Select Projections (Mod 13)
        query = self._get_stadium_doc_ref().collection(collection_name)
        if fields:
            query = query.select(fields)
        docs = query.stream()
        return [doc.to_dict() for doc in docs]

    def _set_collection_data(self, collection_name: str, data: List[Dict]):
        if not db_client: return
        col_ref = self._get_stadium_doc_ref().collection(collection_name)
        # simplistic replace logic for setter
        for doc in col_ref.limit(100).stream():
            doc.reference.delete()
        for item in data:
            doc_id = item.get("id")
            if doc_id:
                col_ref.document(doc_id).set(item)
            else:
                col_ref.add(item)

    @property
    def gates(self) -> List[Dict]:
        return self._get_collection_data("gates")

    @gates.setter
    def gates(self, val: List[Dict]):
        self._set_collection_data("gates", val)

    @property
    def volunteers(self) -> List[Dict]:
        return self._get_collection_data("volunteers")

    @volunteers.setter
    def volunteers(self, val: List[Dict]):
        self._set_collection_data("volunteers", val)

    @property
    def incidents(self) -> List[Dict]:
        return self._get_collection_data("incidents")

    @incidents.setter
    def incidents(self, val: List[Dict]):
        self._set_collection_data("incidents", val)

    @property
    def concessions(self) -> List[Dict]:
        return self._get_collection_data("concessions")

    @concessions.setter
    def concessions(self, val: List[Dict]):
        self._set_collection_data("concessions", val)

    @property
    def transit(self) -> List[Dict]:
        return self._get_collection_data("transit")

    @transit.setter
    def transit(self, val: List[Dict]):
        self._set_collection_data("transit", val)

    @property
    def logs(self) -> List[Dict]:
        if not db_client: return []
        docs = self._get_stadium_doc_ref().collection("logs").order_by("time", direction=firestore.Query.DESCENDING).limit(15).stream()
        return [doc.to_dict() for doc in docs]

    @property
    def match_minute(self) -> int:
        if not db_client: return 0
        doc = self._get_stadium_doc_ref().get()
        return doc.to_dict().get("match_minute", 0) if doc.exists else 0

    @match_minute.setter
    def match_minute(self, val: int):
        if not db_client: return
        self._get_stadium_doc_ref().set({"match_minute": val}, merge=True)

    @property
    def match_score(self) -> str:
        if not db_client: return "0 - 0"
        doc = self._get_stadium_doc_ref().get()
        return doc.to_dict().get("match_score", "0 - 0") if doc.exists else "0 - 0"

    @property
    def match_teams(self) -> str:
        if not db_client: return "Team A vs Team B"
        doc = self._get_stadium_doc_ref().get()
        return doc.to_dict().get("match_teams", "Team A vs Team B") if doc.exists else "Team A vs Team B"

    def get_status_summary(self) -> Dict[str, Any]:
        volunteers_list = self.volunteers
        incidents_list = self.incidents
        gates_list = self.gates

        total_volunteers = len(volunteers_list)
        active_volunteers = sum(1 for v in volunteers_list if v.get("status") == "Busy")
        idle_volunteers = sum(1 for v in volunteers_list if v.get("status") == "Idle")
        
        total_incidents = len(incidents_list)
        critical_incidents = sum(1 for i in incidents_list if i.get("severity") == "Critical" and i.get("status") != "Resolved")
        active_incidents = sum(1 for i in incidents_list if i.get("status") != "Resolved")
        
        capacity = STADIUM_REGISTRY[self.active_id]["capacity"]
        occupancy = int(capacity * 0.85)
        
        max_wait = 0
        if gates_list:
            max_wait = max((g.get("estimated_wait_time", 0) for g in gates_list), default=0)
            
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
        curr_min = self.match_minute
        new_min = curr_min + 1
        if new_min > 90:
            new_min = 0
        self.match_minute = new_min
            
        if new_min >= 75:
            transit_list = self.transit
            for t in transit_list:
                t["wait_time"] = min(45, t.get("wait_time", 0) + 1)
                t["status"] = "Congested" if t["wait_time"] > 18 else "Busy"
            self.transit = transit_list
            
            gates_list = self.gates
            for g in gates_list:
                g["current_queue_length"] = min(1200, g.get("current_queue_length", 0) + 25)
                g["estimated_wait_time"] = int(g["current_queue_length"] * g.get("ticket_scanner_speed", 3.0) / 60 / 3.0)
            self.gates = gates_list
                
            if new_min == 75:
                self.add_log("system", "Warning: Egress phase initiated at minute 75'. Transit queues rising.")

    def add_log(self, message_type: str, message: str):
        # Structured log to stdout
        logger.info(json.dumps({"type": message_type, "event": message}))
        
        if not db_client: return
        now_str = datetime.datetime.now().strftime("%H:%M")
        col_ref = self._get_stadium_doc_ref().collection("logs")
        col_ref.add({
            "time": now_str,
            "type": message_type,
            "message": message,
            "timestamp": firestore.SERVER_TIMESTAMP
        })

    def reset(self):
        pass # Firebase data usually isn't reset trivially this way in production

db = MockDatabase()
