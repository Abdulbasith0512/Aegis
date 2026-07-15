import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

class ChaosTest(Base):
    """
    Simulated data drift and runtime failure experiments profiles.
    """
    __tablename__ = "chaos_tests"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    scenario_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_agents.id", ondelete="CASCADE"), nullable=False, index=True)
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending") # pending, active, completed, failed
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    target_agent: Mapped["AIAgent"] = relationship(back_populates="chaos_tests")

class Alert(Base):
    """
    Security warnings or anomalous model behavior triggers.
    """
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True, index=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # low, medium, high, critical
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    transaction: Mapped[Optional["Transaction"]] = relationship(back_populates="alerts")
    incidents: Mapped[list["Incident"]] = relationship(back_populates="alert")

class Incident(Base):
    """
    Active system faults or compliance breaches requiring resolution.
    """
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    alert_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("alerts.id", ondelete="SET NULL"), nullable=True, index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="open", index=True) # open, investigating, resolved
    severity: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    alert: Mapped[Optional[Alert]] = relationship(back_populates="incidents")
