import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

class Branch(Base):
    """
    Physical or digital branch tracking nodes.
    """
    __tablename__ = "branches"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    branch_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="branch")

class Merchant(Base):
    """
    Corporate receiver of transaction payment.
    """
    __tablename__ = "merchants"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    merchant_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True) # MCC (Merchant Category Code)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="merchant")

class Customer(Base):
    """
    Bank customer demographic profiling records.
    """
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    risk_level: Mapped[str] = mapped_column(String(50), default="medium") # low, medium, high
    status: Mapped[str] = mapped_column(String(50), default="active") # active, suspended, closed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    accounts: Mapped[List["Account"]] = relationship(back_populates="customer")

class Account(Base):
    """
    Customer credit, savings, or checking accounts.
    """
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    account_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    account_type: Mapped[str] = mapped_column(String(50), nullable=False) # checking, savings, loan
    balance: Mapped[float] = mapped_column(Numeric(15, 2), default=0.00)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    status: Mapped[str] = mapped_column(String(50), default="active") # active, frozen, closed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer: Mapped[Customer] = relationship(back_populates="accounts")
    beneficiaries: Mapped[List["Beneficiary"]] = relationship(back_populates="account")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="account")

class Beneficiary(Base):
    """
    Customer designated recipient details.
    """
    __tablename__ = "beneficiaries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    nickname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    beneficiary_account_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    bank_code: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    account: Mapped[Account] = relationship(back_populates="beneficiaries")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="beneficiary")
