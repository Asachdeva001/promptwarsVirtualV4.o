import pytest
from app.agents.volunteer import volunteer_agent
from app.agents.crowd import crowd_agent
from app.agents.fan import fan_agent
from app.mock_data import db

def test_distance_calculation():
    # Coords check (3, 4) to (0, 0) should be 5.0
    p1 = {"x": 3, "y": 4}
    p2 = {"x": 0, "y": 0}
    assert volunteer_agent.calculate_distance(p1, p2) == 5.0

def test_volunteer_recommendation():
    db.reset()
    # Find candidates for inc_2 (Spill in South Concourse)
    res = volunteer_agent.recommend_volunteer("inc_2")
    assert res["success"] is True
    assert len(res["recommended_candidates"]) > 0
    
    # First candidate should have the lowest score
    cands = res["recommended_candidates"]
    for i in range(len(cands) - 1):
        assert cands[i]["score"] <= cands[i+1]["score"]

def test_crowd_predictions():
    db.reset()
    # At timeline 0, no alerts
    res_live = crowd_agent.get_predictions(0)
    assert len(res_live["alerts"]) == 0
    
    # At timeline 20, we expect critical alert at Gate A
    res_20 = crowd_agent.get_predictions(20)
    assert len(res_20["alerts"]) > 0
    alert_gates = [a["target_gate"] for a in res_20["alerts"]]
    assert "gate_a" in alert_gates

def test_fan_multilingual_assistance():
    # Check English food recommendation
    res_en = fan_agent.handle_query("Where can I eat tacos?", "en")
    assert res_en["category"] == "Food"
    assert "Tacos & Churros" in res_en["response"]
    
    # Check Spanish food recommendation
    res_es = fan_agent.handle_query("Tengo hambre, ¿dónde comer?", "es")
    assert res_es["category"] == "Food"
    assert "Tacos & Churros" in res_es["response"]
    assert "recomiendo" in res_es["response"]
