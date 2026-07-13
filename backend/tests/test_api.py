from fastapi.testclient import TestClient
from app.main import app
from app.database import db

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_get_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    assert "occupancy" in response.json()
    assert "active_volunteers" in response.json()
    assert "logs" in response.json()

def test_get_gates_telemetry():
    response = client.get("/api/gates?timeline=20")
    assert response.status_code == 200
    data = response.json()
    assert "gates" in data
    assert "alerts" in data
    assert data["timeline_offset"] == 20

def test_copilot_query():
    response = client.post("/api/copilot/query", json={"query": "What are the biggest operational risks?"})
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "confidence_score" in data
    assert "recommended_actions" in data

def test_fan_query():
    response = client.post("/api/fan/query", json={"query": "where are the restrooms?", "language": "en"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["category"] == "Restroom"

def test_get_stadiums():
    response = client.get("/api/stadiums")
    assert response.status_code == 200
    assert len(response.json()) == 3
    assert response.json()[0]["id"] == "metlife"

def test_select_stadium():
    response = client.post("/api/stadiums/select", json={"stadium_id": "azteca"})
    assert response.status_code == 200
    assert response.json()["active_stadium_id"] == "azteca"
    assert db.active_id == "azteca"

def test_get_transit():
    client.post("/api/stadiums/select", json={"stadium_id": "metlife"})
    response = client.get("/api/transit")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["id"] == "train"

def test_balance_transit():
    # In MetLife, train wait time starts at 15
    response = client.post("/api/transit/balance", json={"transit_id": "train"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    # Decreases by 10 to 5
    assert response.json()["transit"][0]["wait_time"] == 5

def test_vision_inspect():
    response = client.post("/api/vision/inspect", json={"camera_id": "cam_202"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "report" in data
    assert data["report"]["hazard_detected"] is True

def test_match_tick():
    db.reset()
    start_min = db.match_minute
    response = client.post("/api/match/tick")
    assert response.status_code == 200
    assert response.json()["match_minute"] == start_min + 1
def test_rate_limiting():
    # Attempt to hit the copilot endpoint 6 times (limit is 5/min)
    for _ in range(5):
        client.post("/api/copilot/query", json={"query": "Test query"})
    response = client.post("/api/copilot/query", json={"query": "Test query"})
    assert response.status_code == 429

def test_security_headers():
    response = client.get("/")
    assert response.status_code == 200
    assert "strict-transport-security" in response.headers
    assert "x-content-type-options" in response.headers

def test_form_validation():
    # Sending missing fields (schema violation)
    response = client.post("/api/stadiums/select", json={})
    assert response.status_code == 422
    
    # Sending empty string (min_length=1 violation)
    response = client.post("/api/stadiums/select", json={"stadium_id": ""})
    assert response.status_code == 422
