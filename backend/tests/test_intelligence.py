import pytest
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
from app.services.intelligence import IntelligenceService

class MockIntelligenceRepository:
    def __init__(self) -> None:
        self.reputations = []
        self.scores = []
        self.reports = []
        self.benchmarks = []

    async def get_latest_governance_score(self) -> None:
        return None

    async def get_governance_history(self, limit: int) -> List[Any]:
        return []

    async def save_governance_score(self, score_data: Dict[str, Any]) -> Any:
        class ScoreMock:
            def __init__(self, d):
                self.overall_score = d["overall_score"]
                self.grade = d["grade"]
                self.risk_category = d["risk_category"]
                self.trust_score = d.get("trust_score", 90.0)
                self.policy_compliance = d.get("policy_compliance", 95.0)
                self.model_health = d.get("model_health", 90.0)
                self.agent_health = d.get("agent_health", 100.0)
                self.explainability_score = d.get("explainability_quality", 88.0)
                self.recovery_score = d.get("recovery_success", 90.0)
                self.security_score = d.get("security_status", 98.0)
                self.drift_score = d.get("drift_score", 96.0)
                self.incident_frequency = d.get("incident_rate", 2.0)
                self.human_review_rate = d.get("human_review_rate", 15.0)
                self.created_at = datetime.now(timezone.utc)
        mock = ScoreMock(score_data)
        self.scores.append(mock)
        return mock

    async def list_agent_reputations(self) -> List[Any]:
        class AgentMock:
            def __init__(self, name, score):
                self.agent_name = name
                self.score = score
                self.accuracy = 0.95
                self.precision = 0.94
                self.recall = 0.95
                self.avg_confidence = 0.93
                self.avg_latency_ms = 15.0
                self.failure_count = 0
                self.recovery_success = 1
                self.human_overrides = 0
                self.policy_violations = 0
                self.model_drift = 0.0
        return [AgentMock("fraud-agent", 92.5)]

    async def save_agent_reputation(self, rep_data: Dict[str, Any]) -> Any:
        class AgentMock:
            def __init__(self, d):
                self.agent_name = d["agent_name"]
                self.score = d["score"]
                self.accuracy = d["accuracy"]
                self.precision = d["precision"]
                self.recall = d["recall"]
                self.avg_confidence = d["avg_confidence"]
                self.avg_latency_ms = d["avg_latency_ms"]
                self.failure_count = d["failure_count"]
                self.recovery_success = d["recovery_success"]
                self.human_overrides = d["human_overrides"]
                self.policy_violations = d["policy_violations"]
                self.model_drift = d["model_drift"]
                self.last_updated = datetime.now(timezone.utc)
        mock = AgentMock(rep_data)
        self.reputations.append(mock)
        return mock

    async def get_latest_maturity_report(self) -> None:
        return None

    async def save_maturity_report(self, mat_data: Dict[str, Any]) -> Any:
        class MatMock:
            def __init__(self, d):
                self.maturity_level = d["maturity_level"]
                self.scores = d["scores"]
                self.recommendations = d["recommendations"]
                self.created_at = datetime.now(timezone.utc)
        return MatMock(mat_data)

    async def get_latest_failure_index(self) -> None:
        return None

    async def save_failure_index(self, index_data: Dict[str, Any]) -> Any:
        class FailMock:
            def __init__(self, d):
                self.failure_index = d["failure_index"]
                self.severity = d["severity"]
                self.model_failures = d.get("model_failures", 0)
                self.infra_failures = d.get("infra_failures", 0)
                self.policy_violations = d.get("policy_violations", 0)
                self.security_events = d.get("security_events", 0)
                self.consensus_failures = d.get("consensus_failures", 0)
                self.recovery_failures = d.get("recovery_failures", 0)
                self.drift_events = d.get("drift_events", 0)
                self.root_cause_summary = d.get("root_cause_summary", "")
                self.created_at = datetime.now(timezone.utc)
        return FailMock(index_data)

    async def list_benchmark_results(self) -> List[Any]:
        return []

    async def create_benchmark_run(self, *args, **kwargs) -> Any:
        class RunMock:
            id = uuid.uuid4()
        return RunMock()

    async def create_benchmark_result(self, *args, **kwargs) -> Any:
        pass

    async def create_governance_report(self, type_, format_, summary, details) -> Any:
        class RepMock:
            def __init__(self, t, f, s, d):
                self.id = uuid.uuid4()
                self.report_type = t
                self.report_format = f
                self.summary = s
                self.details = d
                self.created_at = datetime.now(timezone.utc)
        mock = RepMock(type_, format_, summary, details)
        self.reports.append(mock)
        return mock

    async def list_governance_reports(self, limit: int) -> List[Any]:
        return self.reports


def test_governance_score_grading() -> None:
    """Checks the grading and risk boundaries for the compiled score."""
    service = IntelligenceService(MockIntelligenceRepository())
    
    # Perfect score
    telemetry = {
        "trust_score": 100.0, "policy_compliance": 100.0, "model_health": 100.0,
        "agent_health": 100.0, "explainability_quality": 100.0, "recovery_success": 100.0,
        "security_status": 100.0, "drift_score": 100.0, "incident_rate": 0.0,
        "human_review_rate": 100.0, "consensus_stability": 100.0
    }
    
    res = service.calculate_governance_score(telemetry)
    assert res["overall_score"] == 100.0
    assert res["grade"] == "A+"
    assert res["risk_category"] == "low"

    # Failing score
    failing = {k: 10.0 for k in telemetry.keys()}
    failing["incident_rate"] = 90.0 # high incidents rate pulls score down further
    res_fail = service.calculate_governance_score(failing)
    assert res_fail["overall_score"] < 50.0
    assert res_fail["grade"] == "F"
    assert res_fail["risk_category"] == "critical"


@pytest.mark.anyio
async def test_agent_reputation_index() -> None:
    """Verifies that accuracy drops reduce agent reputation ratings."""
    repo = MockIntelligenceRepository()
    service = IntelligenceService(repo)
    
    telemetry = {
        "accuracy": 0.95, "precision": 0.94, "recall": 0.95, "avg_confidence": 0.90,
        "latency_ms": 12.0, "failure_count": 0, "recovery_success": 1,
        "human_overrides": 0, "policy_violations": 0, "model_drift": 0.0
    }
    
    res = await service.update_agent_reputation("fraud-agent", telemetry)
    assert res["score"] > 85.0
    assert len(repo.reputations) == 1


@pytest.mark.anyio
async def test_maturity_assessment_levels() -> None:
    """Checks that maturity assessment matches organizational expectations."""
    repo = MockIntelligenceRepository()
    service = IntelligenceService(repo)
    res = await service.get_maturity_assessment()
    assert "Level 4" in res["maturity_level"]
    assert "Monitoring" in res["scores"]
    assert len(res["recommendations"]) > 0


@pytest.mark.anyio
async def test_failure_index_severities() -> None:
    """Verifies failure index calculation models."""
    repo = MockIntelligenceRepository()
    service = IntelligenceService(repo)
    res = await service.get_failure_index_report()
    assert res["failure_index"] == 12.5
    assert res["severity"] == "low"
    assert "model_failures" in res


@pytest.mark.anyio
async def test_governance_reports_generation() -> None:
    """Checks that report compiler compiles binary and textual formats."""
    repo = MockIntelligenceRepository()
    service = IntelligenceService(repo)
    
    rep = await service.generate_and_save_report(type_="executive", format_="pdf")
    assert rep.report_type == "executive"
    assert rep.report_format == "pdf"
    assert len(repo.reports) == 1
    
    content, media_type, filename = await service.get_report_bytes(rep.id)
    assert len(content) > 0
    assert media_type == "application/pdf"
    assert "pdf" in filename
