import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, ForeignKey, DateTime, Integer, Float, Column
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

class ConsensusVote(Base):
    """
    Consolidated agent voting summaries evaluating a transaction.
    """
    __tablename__ = "consensus_votes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    decision_verdict: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # approve, decline
    vote_details: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False) # split vote counts
    consensus_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    transaction: Mapped["Transaction"] = relationship(back_populates="consensus_votes")

class TrustScore(Base):
    """
    Aggregated safety scoring outputs computed by the trust engine.
    """
    __tablename__ = "trust_scores"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False, index=True) # 0 to 100
    weights_configuration: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    reasons: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    transaction: Mapped["Transaction"] = relationship(back_populates="trust_scores")

class PolicyCheck(Base):
    """
    Rule evaluations run by the policy validator engine.
    """
    __tablename__ = "policy_checks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # pass, fail, warn
    details: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    transaction: Mapped["Transaction"] = relationship(back_populates="policy_checks")

class Explanation(Base):
    """
    Explainability attributions, timelines, and graphs generated for agent decisions.
    """
    __tablename__ = "explanations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    prediction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False, index=True)
    human_readable: Mapped[str] = mapped_column(String(1000), nullable=False)
    machine_readable: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    decision_timeline: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    evidence_graph: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    feature_importance: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    confidence_reasoning: Mapped[str] = mapped_column(String(1000), nullable=False)
    supporting_policies: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    contributing_agents: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    explainability_score: Mapped[float] = mapped_column(Float, nullable=False)
    explanation_vector: Mapped[Optional[list[float]]] = mapped_column(ARRAY(Float), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    prediction: Mapped["Prediction"] = relationship(back_populates="explanations")

class HumanReview(Base):
    """
    Human auditor intervention records for low trust score escalations.
    """
    __tablename__ = "human_reviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True) # pending, approved, declined
    comments: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    sla_deadline: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationships
    transaction: Mapped["Transaction"] = relationship(back_populates="human_reviews")
    reviewer: Mapped[Optional["User"]] = relationship(back_populates="human_reviews")

class AuditLog(Base):
    """
    Cryptographic audit logs for operational action tracking.
    """
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    audit_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSONB, nullable=True)
    ledger_hash: Mapped[str] = mapped_column(String(64), nullable=False) # sha-256 integrity chain
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    actor: Mapped[Optional["User"]] = relationship(back_populates="audit_logs")

class ComplianceReport(Base):
    """
    Generated export records certifying policy conformity.
    """
    __tablename__ = "compliance_reports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    generated_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # SOC2, GDPR, etc.
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    report_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    generated_by: Mapped["User"] = relationship(back_populates="compliance_reports")
