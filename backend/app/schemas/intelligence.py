import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field

class ScoreBreakdown(BaseModel):
    trust_score: float
    policy_compliance: float
    model_health: float
    agent_health: float
    explainability_quality: float
    recovery_success: float
    security_status: float
    drift_score: float
    incident_rate: float
    human_review_rate: float
    consensus_stability: float

class GovernanceScoreResponse(BaseModel):
    overall_score: float
    grade: str
    historical_trend: str # e.g. improving, stable, declining
    weekly_trend: str
    monthly_trend: str
    risk_category: str # e.g. low, medium, high, critical
    breakdown: ScoreBreakdown
    evaluated_at: datetime


class AgentReputationRecord(BaseModel):
    agent_name: str
    reputation_score: float
    accuracy: float
    precision: float
    recall: float
    avg_confidence: float
    avg_latency_ms: float
    failure_count: int
    recovery_success: int
    human_overrides: int
    policy_violations: int
    model_drift: float
    rank: Optional[int] = None

class AgentLeaderboardResponse(BaseModel):
    agents: List[AgentReputationRecord]
    leaderboard_date: datetime


class MaturityReportResponse(BaseModel):
    maturity_level: str # Level 1 - Initial to Level 5 - Optimized
    scores: Dict[str, float]
    recommendations: List[str]
    assessed_at: datetime


class FailureIndexResponse(BaseModel):
    failure_index: float
    severity: str # low, medium, high, critical
    trend: str # stable, increasing, decreasing
    model_failures: int
    infra_failures: int
    policy_violations: int
    security_events: int
    consensus_failures: int
    recovery_failures: int
    human_escalations: int
    service_downtime_sec: int
    root_cause_analysis: str
    recommendations: List[str]
    calculated_at: datetime


class BenchmarkRunCreate(BaseModel):
    parameters: Optional[Dict[str, Any]] = None

class BenchmarkRunOut(BaseModel):
    id: uuid.UUID
    status: str
    parameters: Dict[str, Any]
    metrics: Dict[str, Any]
    started_at: datetime
    completed_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class BenchmarkResultRecord(BaseModel):
    algorithm_name: str
    algorithm_type: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    latency_ms: float
    memory_usage_mb: float
    cpu_usage_pct: float
    inference_time_ms: float
    recovery_time_ms: float

class BenchmarksReportResponse(BaseModel):
    run_id: uuid.UUID
    results: List[BenchmarkResultRecord]
    created_at: datetime


class ReportGenerateRequest(BaseModel):
    report_type: str # executive, benchmark, agent, weekly, monthly
    report_format: str # pdf, csv, json
    parameters: Optional[Dict[str, Any]] = None

class GovernanceReportOut(BaseModel):
    id: uuid.UUID
    report_type: str
    report_format: str
    summary: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
