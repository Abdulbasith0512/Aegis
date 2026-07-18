import pytest
import uuid
from typing import Dict, Any, List
from app.services.research import ResearchService

class MockResearchRepository:
    def __init__(self) -> None:
        self.reputations = []
        self.governance_scores = []
        self.benchmarks = []

    async def list_agent_reputations(self) -> List[Any]:
        class AgentMock:
            def __init__(self, name, score):
                self.agent_name = name
                self.score = score
        return [
            AgentMock("fraud-agent", 92.5),
            AgentMock("kyc-agent", 96.4),
            AgentMock("device-agent", 95.0),
            AgentMock("aml-agent", 88.0),
            AgentMock("explainability-agent", 94.2)
        ]

    async def save_agent_reputation(self, data: Dict[str, Any]) -> None:
        self.reputations.append(data)

    async def get_latest_governance_score(self) -> None:
        return None

    async def get_governance_history(self, limit: int) -> List[Any]:
        return []

    async def save_governance_score(self, data: Dict[str, Any]) -> Any:
        class ScoreMock:
            def __init__(self, d):
                self.overall_score = d["overall_score"]
                self.grade = d["grade"]
                self.trust_score = d["trust_score"]
                self.policy_compliance = d["policy_compliance"]
                self.explainability_score = d["explainability_score"]
                self.model_health = d["model_health"]
                self.agent_health = d["agent_health"]
                self.drift_score = d["drift_score"]
                self.security_score = d["security_score"]
                self.recovery_score = d["recovery_score"]
                self.incident_frequency = d["incident_frequency"]
                self.human_review_rate = d["human_review_rate"]
                self.created_at = None
        return ScoreMock(data)

    async def list_benchmarks(self) -> List[Any]:
        return []

    async def get_latest_failure_index(self) -> None:
        return None

    async def save_failure_index(self, data: Dict[str, Any]) -> Any:
        class FailMock:
            def __init__(self, d):
                self.failure_index = d["failure_index"]
                self.severity = d["severity"]
                self.model_failures = d.get("model_failures", 0)
                self.infra_failures = d.get("infra_failures", 0)
                self.policy_violations = d.get("policy_violations", 0)
                self.agent_failures = d.get("agent_failures", 0)
                self.consensus_failures = d.get("consensus_failures", 0)
                self.recovery_failures = d.get("recovery_failures", 0)
                self.drift_events = d.get("drift_events", 0)
                self.security_events = d.get("security_events", 0)
                self.root_cause_summary = d.get("root_cause_summary", "")
                self.created_at = None
        return FailMock(data)

    async def get_latest_maturity_assessment(self) -> None:
        return None

    async def save_maturity_assessment(self, data: Dict[str, Any]) -> Any:
        class MatMock:
            def __init__(self, d):
                self.maturity_level = d["maturity_level"]
                self.scores = d["scores"]
                self.recommendations = d["recommendations"]
                self.created_at = None
        return MatMock(data)

    async def create_run(self, *args, **kwargs) -> Any:
        class RunMock:
            id = uuid.uuid4()
        return RunMock()

    async def create_benchmark_result(self, *args, **kwargs) -> Any:
        pass


def test_governance_score_calculation() -> None:
    """Verifies that the score compiler bounds inputs and returns the correct grade."""
    service = ResearchService(MockResearchRepository())
    
    # Standard profile mapping
    inputs = {
        "trust_score": 85.0,
        "policy_compliance": 90.0,
        "explainability_score": 80.0,
        "model_health": 95.0,
        "agent_health": 100.0,
        "drift_score": 90.0,
        "security_score": 95.0,
        "recovery_score": 85.0,
        "incident_frequency": 0.0,
        "human_review_rate": 15.0
    }
    
    report = service.calculate_governance_score(inputs)
    assert report["overall_score"] >= 80.0
    assert report["grade"] in ["A", "B", "C"]
    
    # Check low ratings
    low_inputs = {k: 10.0 for k in inputs.keys()}
    low_report = service.calculate_governance_score(low_inputs)
    assert low_report["overall_score"] < 50.0
    assert low_report["grade"] == "F"


@pytest.mark.anyio
async def test_agent_reputation_scoring() -> None:
    """Checks reputation engine metrics updates and output validations."""
    repo = MockResearchRepository()
    service = ResearchService(repo)
    
    telemetry = {
        "accuracy": 0.96,
        "avg_confidence": 0.90,
        "latency_ms": 12.5,
        "success_count": 480,
        "failure_count": 0,
        "false_positives": 2,
        "false_negatives": 1,
        "human_overrides": 1,
        "policy_violations": 0,
        "drift_events": 0,
        "recovery_success": 0
    }
    
    rep = await service.update_agent_reputation("fraud-agent", telemetry)
    assert rep["score"] > 80.0
    assert rep["agent_name"] == "fraud-agent"
    assert len(repo.reputations) == 1


@pytest.mark.anyio
async def test_consensus_v2_weighted_votes() -> None:
    """Verifies dynamic reputation voting outcomes."""
    repo = MockResearchRepository()
    service = ResearchService(repo)
    
    # 4 approve, 1 decline (the decline comes from device-agent with low confidence)
    agent_votes = [
        {"agent_name": "fraud-agent", "decision": "approve", "confidence": 0.95, "is_healthy": True, "has_drift": False},
        {"agent_name": "kyc-agent", "decision": "approve", "confidence": 0.90, "is_healthy": True, "has_drift": False},
        {"agent_name": "device-agent", "decision": "decline", "confidence": 0.40, "is_healthy": True, "has_drift": False},
        {"agent_name": "aml-agent", "decision": "approve", "confidence": 0.98, "is_healthy": True, "has_drift": False},
        {"agent_name": "explainability-agent", "decision": "approve", "confidence": 0.92, "is_healthy": True, "has_drift": False}
      ]

    res = await service.simulate_consensus_v2(agent_votes)
    assert res["verdict"] == "approve"
    assert res["consensus_confidence"] > 0.60
    assert res["decision_stability"] > 0.50
    assert "fraud-agent" in res["confidence_matrix"]
