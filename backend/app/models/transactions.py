import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Numeric, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

class Device(Base):
    """
    Client terminal device digital telemetry records.
    """
    __tablename__ = "devices"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    fingerprint: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    os: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_emulator: Mapped[bool] = mapped_column(Boolean, default=False)
    location_lat: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)
    location_long: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="device")

class Transaction(Base):
    """
    Transaction events supervised by the governance engine.
    """
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False, index=True)
    beneficiary_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("beneficiaries.id", ondelete="SET NULL"), nullable=True, index=True)
    merchant_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("merchants.id", ondelete="SET NULL"), nullable=True, index=True)
    branch_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("branches.id", ondelete="SET NULL"), nullable=True, index=True)
    device_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True)
    
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # transfer, withdrawal, payment
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True) # pending, approved, declined, under_review
    reference_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    initiated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    account: Mapped["Account"] = relationship(back_populates="transactions")
    beneficiary: Mapped[Optional["Beneficiary"]] = relationship(back_populates="transactions")
    merchant: Mapped[Optional["Merchant"]] = relationship(back_populates="transactions")
    branch: Mapped[Optional["Branch"]] = relationship(back_populates="transactions")
    device: Mapped[Optional[Device]] = relationship(back_populates="transactions")
    
    predictions: Mapped[List["Prediction"]] = relationship(back_populates="transaction")
    consensus_votes: Mapped[List["ConsensusVote"]] = relationship(back_populates="transaction")
    trust_scores: Mapped[List["TrustScore"]] = relationship(back_populates="transaction")
    policy_checks: Mapped[List["PolicyCheck"]] = relationship(back_populates="transaction")
    human_reviews: Mapped[List["HumanReview"]] = relationship(back_populates="transaction")
    alerts: Mapped[List["Alert"]] = relationship(back_populates="transaction")
