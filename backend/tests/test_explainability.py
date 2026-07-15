import uuid
import pytest
from app.services.explainability import DefaultExplainabilityEngine

def test_explainability_engine_normal_generation() -> None:
    """
    Verifies that a standard explainability trace generates all core elements.
    """
    pred_id = uuid.uuid4()
    agent_traces = {
        "warnings": [],
        "timeline": [
            {"event": "Start Ingestion", "duration_ms": 1.0, "status": "success"},
            {"event": "Evaluated Fraud", "duration_ms": 12.0, "status": "success"}
        ],
        "feature_importance": {
            "amount": 0.12,
            "ip_risk": 0.05
        }
    }
    
    engine = DefaultExplainabilityEngine()
    res = engine.generate_explanation(pred_id, agent_traces)
    
    assert res["prediction_id"] == pred_id
    assert res["explainability_score"] == 1.00 # all elements present
    assert "events" in res["decision_timeline"]
    assert len(res["decision_timeline"]["events"]) == 2
    assert "nodes" in res["evidence_graph"]
    assert len(res["evidence_graph"]["nodes"]) == 4
    assert res["feature_importance"]["amount"] == 0.12
    assert len(res["contributing_agents"]["agents"]) >= 1
    assert "compliance-policy" not in [n["id"] for n in res["evidence_graph"]["nodes"]] # verify default layout

def test_explainability_warnings_adaptation() -> None:
    """
    Verifies that warnings alter graph node state risk levels.
    """
    pred_id = uuid.uuid4()
    agent_traces = {
        "warnings": ["Warning: Terminal emulator active", "Policy Limit Breached"],
        "feature_importance": {
            "amount": 0.15,
            "unsupported_currency": 0.85
        }
    }
    
    engine = DefaultExplainabilityEngine()
    res = engine.generate_explanation(pred_id, agent_traces)
    
    # Check that warnings adapt the graph
    nodes = res["evidence_graph"]["nodes"]
    device_node = next(n for n in nodes if n["type"] == "device")
    policy_node = next(n for n in nodes if n["type"] == "policy")
    
    assert device_node["status"] == "risk"
    assert policy_node["status"] == "failed"
    assert "emulator" in res["human_readable"].lower()
