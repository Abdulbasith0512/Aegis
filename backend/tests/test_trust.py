import uuid
import pytest
from app.schemas.trust import TrustCalculationRequest
from app.services.trust_engine import WeightedTrustEngine

def test_trust_engine_perfect_score() -> None:
    """
    Verifies that a flawless transaction gets a trust score of 100.
    """
    request = TrustCalculationRequest(
        transaction_id=uuid.uuid4(),
        agent_confidence=1.0,
        historical_accuracy=1.0,
        model_drift=0.0,
        data_quality=1.0,
        latency_ms=45.0, # under SLA
        policy_compliance=True,
        explainability_score=1.0,
        agent_consensus=1.0
    )
    
    engine = WeightedTrustEngine()
    score, weights, reasons = engine.calculate_score(request)
    
    assert score == 100
    assert len(reasons["warnings"]) == 0

def test_trust_engine_policy_violation() -> None:
    """
    Verifies that a policy compliance violation significantly drops the trust score.
    """
    request = TrustCalculationRequest(
        transaction_id=uuid.uuid4(),
        agent_confidence=0.95,
        historical_accuracy=0.96,
        model_drift=0.05,
        data_quality=0.98,
        latency_ms=52.0,
        policy_compliance=False, # Policy failed
        explainability_score=0.90,
        agent_consensus=0.95
    )
    
    engine = WeightedTrustEngine()
    score, weights, reasons = engine.calculate_score(request)
    
    # 20% compliance weight should be zero. Score should be around 80.
    assert score < 85
    assert "Deterministic policy check verification failed." in reasons["warnings"]

def test_trust_engine_multiple_warnings() -> None:
    """
    Verifies that multiple warning flags accrue warnings list.
    """
    request = TrustCalculationRequest(
        transaction_id=uuid.uuid4(),
        agent_confidence=0.85,
        historical_accuracy=0.92,
        model_drift=0.45, # high drift warning
        data_quality=0.82, # poor data quality warning
        latency_ms=750.0, # latency SLA warning
        policy_compliance=True,
        explainability_score=0.75,
        agent_consensus=0.55 # consensus warning
    )
    
    engine = WeightedTrustEngine()
    score, weights, reasons = engine.calculate_score(request)
    
    assert score == 79
    assert len(reasons["warnings"]) >= 4
