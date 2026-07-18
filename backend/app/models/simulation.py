import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, ForeignKey, DateTime, Integer, Float, Boolean, Text
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

class SimulationScenario(Base):
    """
    Configuration template for a simulation environment (Digital Twin setup).
    """
    __tablename__ = "simulation_scenarios"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    simulation_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., 'high_fraud_day', 'festival_spike'
    
    # Virtual Bank Configuration
    num_customers: Mapped[int] = mapped_column(Integer, default=1000)
    num_accounts: Mapped[int] = mapped_column(Integer, default=1200)
    num_transactions: Mapped[int] = mapped_column(Integer, default=5000)
    
    # Load & Behavior
    fraud_percentage: Mapped[float] = mapped_column(Float, default=0.01)
    aml_risk_level: Mapped[str] = mapped_column(String(50), default="low") # low, medium, high
    drift_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    target_tps: Mapped[int] = mapped_column(Integer, default=10) # Transactions per second
    
    # Failure Injection Config
    injected_failures: Mapped[List[str]] = mapped_column(ARRAY(String), default=list) # e.g. ['fraud_agent_crash', 'db_latency']
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    runs: Mapped[List["SimulationRun"]] = relationship(back_populates="scenario", cascade="all, delete-orphan")


class SimulationRun(Base):
    """
    An execution instance of a SimulationScenario.
    """
    __tablename__ = "simulation_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    scenario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("simulation_scenarios.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True) # pending, running, completed, failed
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    scenario: Mapped["SimulationScenario"] = relationship(back_populates="runs")
    metrics: Mapped[List["SimulationMetric"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    events: Mapped[List["SimulationEvent"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    results: Mapped[List["SimulationResult"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class SimulationMetric(Base):
    """
    Time-series data for a simulation run (CPU, memory, latency, throughput).
    """
    __tablename__ = "simulation_metrics"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    metric_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., 'latency', 'throughput', 'cpu_usage'
    value: Mapped[float] = mapped_column(Float, nullable=False)
    tags: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    run: Mapped["SimulationRun"] = relationship(back_populates="metrics")


class SimulationEvent(Base):
    """
    A specific event/log generated during the simulation (e.g., transaction evaluated, failure injected).
    """
    __tablename__ = "simulation_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    event_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., 'transaction_eval', 'failure_injection'
    severity: Mapped[str] = mapped_column(String(50), default="info") # info, warning, error, critical
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    run: Mapped["SimulationRun"] = relationship(back_populates="events")


class SimulationResult(Base):
    """
    Aggregated final results/reports for a completed run.
    """
    __tablename__ = "simulation_results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    total_transactions: Mapped[int] = mapped_column(Integer, default=0)
    fraud_detected: Mapped[int] = mapped_column(Integer, default=0)
    aml_alerts: Mapped[int] = mapped_column(Integer, default=0)
    false_positives: Mapped[int] = mapped_column(Integer, default=0)
    false_negatives: Mapped[int] = mapped_column(Integer, default=0)
    
    avg_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    peak_tps: Mapped[float] = mapped_column(Float, default=0.0)
    trust_score_impact: Mapped[float] = mapped_column(Float, default=0.0) # Delta in trust score
    
    report_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    run: Mapped["SimulationRun"] = relationship(back_populates="results")
