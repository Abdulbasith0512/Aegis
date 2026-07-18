import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, ForeignKey, DateTime, Integer, Float, Boolean, Text, JSON
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

class ResearchProject(Base):
    """
    Groups experiments and research efforts around specific governance themes.
    """
    __tablename__ = "research_projects"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    experiments: Mapped[List["ResearchExperiment"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class ResearchExperiment(Base):
    """
    Defines a research experiment setup, targeting governance parameter combinations.
    """
    __tablename__ = "research_experiments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    version_string: Mapped[str] = mapped_column(String(50), default="1.0.0")
    config_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["ResearchProject"] = relationship(back_populates="experiments")
    runs: Mapped[List["ExperimentRun"]] = relationship(back_populates="experiment", cascade="all, delete-orphan")


class ExperimentRun(Base):
    """
    An execution run instance of a ResearchExperiment.
    """
    __tablename__ = "experiment_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    experiment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research_experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True) # pending, running, paused, completed, archived
    
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    metrics: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    experiment: Mapped["ResearchExperiment"] = relationship(back_populates="runs")
    benchmark_results: Mapped[List["BenchmarkResult"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class BenchmarkResult(Base):
    """
    Performance benchmarking parameters for model/algorithm comparisons.
    """
    __tablename__ = "benchmark_results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("experiment_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    algorithm_name: Mapped[str] = mapped_column(String(100), nullable=False)
    algorithm_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. fraud, aml, trust, consensus, explainability
    
    accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    precision: Mapped[float] = mapped_column(Float, default=0.0)
    recall: Mapped[float] = mapped_column(Float, default=0.0)
    f1_score: Mapped[float] = mapped_column(Float, default=0.0)
    roc_auc: Mapped[float] = mapped_column(Float, default=0.0)
    
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    throughput: Mapped[float] = mapped_column(Float, default=0.0)
    cpu_usage: Mapped[float] = mapped_column(Float, default=0.0)
    memory_usage: Mapped[float] = mapped_column(Float, default=0.0)
    recovery_time_ms: Mapped[float] = mapped_column(Float, default=0.0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    run: Mapped["ExperimentRun"] = relationship(back_populates="benchmark_results")


class GovernanceScore(Base):
    """
    Calculated overall governance index rating, combining multiple telemetry vectors.
    """
    __tablename__ = "governance_scores"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    grade: Mapped[str] = mapped_column(String(10), nullable=False) # A, B, C, D, F
    
    trust_score: Mapped[float] = mapped_column(Float, nullable=False)
    policy_compliance: Mapped[float] = mapped_column(Float, nullable=False)
    explainability_score: Mapped[float] = mapped_column(Float, nullable=False)
    model_health: Mapped[float] = mapped_column(Float, nullable=False)
    agent_health: Mapped[float] = mapped_column(Float, nullable=False)
    drift_score: Mapped[float] = mapped_column(Float, nullable=False)
    security_score: Mapped[float] = mapped_column(Float, nullable=False)
    recovery_score: Mapped[float] = mapped_column(Float, nullable=False)
    incident_frequency: Mapped[float] = mapped_column(Float, nullable=False)
    human_review_rate: Mapped[float] = mapped_column(Float, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class GovernanceHistory(Base):
    """
    Stores historical snapshots of overall governance levels for dynamic charts and regression forecasts.
    """
    __tablename__ = "governance_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    metrics_snapshot: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class AgentReputation(Base):
    """
    Dynamic reputation scores assigned and calculated for each AI agent node.
    """
    __tablename__ = "agent_reputation"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    score: Mapped[float] = mapped_column(Float, default=100.0) # 0 to 100
    
    accuracy: Mapped[float] = mapped_column(Float, default=1.0)
    avg_confidence: Mapped[float] = mapped_column(Float, default=1.0)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    false_positives: Mapped[int] = mapped_column(Integer, default=0)
    false_negatives: Mapped[int] = mapped_column(Integer, default=0)
    human_overrides: Mapped[int] = mapped_column(Integer, default=0)
    policy_violations: Mapped[int] = mapped_column(Integer, default=0)
    drift_events: Mapped[int] = mapped_column(Integer, default=0)
    recovery_success: Mapped[int] = mapped_column(Integer, default=0)
    
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ReputationHistory(Base):
    """
    Historical logs tracking how agent reputations evolve.
    """
    __tablename__ = "reputation_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FailureIndex(Base):
    """
    Platform-wide index rating of AI system failures and anomalies.
    """
    __tablename__ = "failure_indices"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    failure_index: Mapped[float] = mapped_column(Float, nullable=False) # 0 to 100 (100 = complete collapse)
    severity: Mapped[str] = mapped_column(String(50), default="low") # low, medium, high, critical
    
    model_failures: Mapped[int] = mapped_column(Integer, default=0)
    infra_failures: Mapped[int] = mapped_column(Integer, default=0)
    policy_violations: Mapped[int] = mapped_column(Integer, default=0)
    agent_failures: Mapped[int] = mapped_column(Integer, default=0)
    consensus_failures: Mapped[int] = mapped_column(Integer, default=0)
    recovery_failures: Mapped[int] = mapped_column(Integer, default=0)
    drift_events: Mapped[int] = mapped_column(Integer, default=0)
    security_events: Mapped[int] = mapped_column(Integer, default=0)
    
    root_cause_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MaturityAssessment(Base):
    """
    Maturity levels across automation, compliance, explainability, oversight categories.
    """
    __tablename__ = "maturity_assessments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    maturity_level: Mapped[str] = mapped_column(String(50), nullable=False) # Initial, Managed, Defined, Quantitatively Managed, Optimized
    
    scores: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    recommendations: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AlgorithmVersion(Base):
    """
    Tracks registered and active algorithm logic versions.
    """
    __tablename__ = "algorithm_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    algorithm_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    algorithm_type: Mapped[str] = mapped_column(String(100), nullable=False)
    version_string: Mapped[str] = mapped_column(String(50), nullable=False)
    parameters_config: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ComparisonReport(Base):
    """
    Comparison reports analyzing performance of different version parameters.
    """
    __tablename__ = "comparison_reports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    comparison_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BenchmarkRun(Base):
    """
    Execution instance tracking dedicated benchmarking comparisons.
    """
    __tablename__ = "benchmark_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True) # pending, running, completed, failed
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    metrics: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class GovernanceReport(Base):
    """
    Registry for compiled governance reports.
    """
    __tablename__ = "governance_reports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    report_type: Mapped[str] = mapped_column(String(100), nullable=False) # executive, benchmark, agent, weekly, monthly
    report_format: Mapped[str] = mapped_column(String(50), nullable=False) # pdf, csv, json
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    details: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MaturityReport(Base):
    """
    Organizational AI governance maturity report.
    """
    __tablename__ = "maturity_reports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    maturity_level: Mapped[str] = mapped_column(String(50), nullable=False)
    scores: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    recommendations: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

