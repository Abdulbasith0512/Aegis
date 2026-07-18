import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field

class ResearchProjectBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

class ResearchProjectCreate(ResearchProjectBase):
    pass

class ResearchProjectOut(ResearchProjectBase):
    id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ResearchExperimentBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = None
    version_string: str = "1.0.0"
    config_data: Dict[str, Any] = Field(default_factory=dict)

class ResearchExperimentCreate(ResearchExperimentBase):
    project_id: uuid.UUID

class ResearchExperimentOut(ResearchExperimentBase):
    id: uuid.UUID
    project_id: uuid.UUID
    is_archived: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ExperimentRunBase(BaseModel):
    parameters: Dict[str, Any] = Field(default_factory=dict)

class ExperimentRunCreate(BaseModel):
    experiment_id: uuid.UUID
    parameters: Optional[Dict[str, Any]] = None

class ExperimentRunOut(ExperimentRunBase):
    id: uuid.UUID
    experiment_id: uuid.UUID
    status: str
    metrics: Dict[str, Any]
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class BenchmarkResultBase(BaseModel):
    algorithm_name: str
    algorithm_type: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    latency_ms: float
    throughput: float
    cpu_usage: float
    memory_usage: float
    recovery_time_ms: float

class BenchmarkResultCreate(BenchmarkResultBase):
    run_id: uuid.UUID

class BenchmarkResultOut(BenchmarkResultBase):
    id: uuid.UUID
    run_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class GovernanceScoreBase(BaseModel):
    overall_score: float
    grade: str
    trust_score: float
    policy_compliance: float
    explainability_score: float
    model_health: float
    agent_health: float
    drift_score: float
    security_score: float
    recovery_score: float
    incident_frequency: float
    human_review_rate: float

class GovernanceScoreOut(GovernanceScoreBase):
    id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class GovernanceHistoryOut(BaseModel):
    id: uuid.UUID
    timestamp: datetime
    score: float
    metrics_snapshot: Dict[str, Any]
    model_config = ConfigDict(from_attributes=True)


class AgentReputationBase(BaseModel):
    agent_name: str
    score: float
    accuracy: float
    avg_confidence: float
    latency_ms: float
    success_count: int
    failure_count: int
    false_positives: int
    false_negatives: int
    human_overrides: int
    policy_violations: int
    drift_events: int
    recovery_success: int

class AgentReputationOut(AgentReputationBase):
    id: uuid.UUID
    last_updated: datetime
    model_config = ConfigDict(from_attributes=True)


class ReputationHistoryOut(BaseModel):
    id: uuid.UUID
    agent_name: str
    score: float
    recorded_at: datetime
    model_config = ConfigDict(from_attributes=True)


class FailureIndexBase(BaseModel):
    failure_index: float
    severity: str
    model_failures: int
    infra_failures: int
    policy_violations: int
    agent_failures: int
    consensus_failures: int
    recovery_failures: int
    drift_events: int
    security_events: int
    root_cause_summary: str

class FailureIndexOut(FailureIndexBase):
    id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MaturityAssessmentBase(BaseModel):
    maturity_level: str
    scores: Dict[str, Any]
    recommendations: List[str]

class MaturityAssessmentOut(MaturityAssessmentBase):
    id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AlgorithmVersionBase(BaseModel):
    algorithm_name: str
    algorithm_type: str
    version_string: str
    parameters_config: Dict[str, Any]
    is_active: bool

class AlgorithmVersionCreate(AlgorithmVersionBase):
    pass

class AlgorithmVersionOut(AlgorithmVersionBase):
    id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ComparisonReportBase(BaseModel):
    title: str
    comparison_data: Dict[str, Any]
    summary: str

class ComparisonReportOut(ComparisonReportBase):
    id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Custom parameters for comparisons and exports
class CompareRequest(BaseModel):
    algorithm_ids: List[uuid.UUID]
    metric_keys: Optional[List[str]] = None

class ComparisonMatrixResponse(BaseModel):
    comparison_id: uuid.UUID
    title: str
    summary: str
    matrix: Dict[str, Any]
    created_at: datetime
