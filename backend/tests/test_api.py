from fastapi.testclient import TestClient
from app.main import app
from app.mock_data import db

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
