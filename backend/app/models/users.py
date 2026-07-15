import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, ForeignKey, Table, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

# Association table for Many-to-Many relationship between Roles and Permissions
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
)

class Permission(Base):
    """
    System permission identifiers (e.g. 'read:transactions', 'write:policies').
    """
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        secondary=role_permissions, back_populates="permissions"
    )

class Role(Base):
    """
    System authorization roles (e.g. 'admin', 'auditor').
    """
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    permissions: Mapped[List[Permission]] = relationship(
        secondary=role_permissions, back_populates="roles"
    )
    users: Mapped[List["User"]] = relationship(back_populates="role")

class User(Base):
    """
    System administrative and review operators.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    role: Mapped[Role] = relationship(back_populates="users")
    human_reviews: Mapped[List["HumanReview"]] = relationship(back_populates="reviewer")
    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="actor")
    compliance_reports: Mapped[List["ComplianceReport"]] = relationship(back_populates="generated_by")
