import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, ForeignKey, DateTime, Integer, Float, Column, Boolean, Enum
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

class Workflow(Base):
    """
    Metadata for AI Governance Workflows.
    """
    __tablename__ = "workflows"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft", index=True) # draft, published, archived
    is_template: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    creator: Mapped[Optional["User"]] = relationship(foreign_keys=[created_by_id])
    versions: Mapped[List["WorkflowVersion"]] = relationship(back_populates="workflow", cascade="all, delete-orphan")


class WorkflowVersion(Base):
    """
    A specific version of a workflow, containing nodes and edges.
    """
    __tablename__ = "workflow_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workflow_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Store the entire graph configuration as JSON for easy rendering, 
    # but also provide structured nodes/edges for the execution engine.
    graph_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    # Relationships
    workflow: Mapped["Workflow"] = relationship(back_populates="versions")
    nodes: Mapped[List["WorkflowNode"]] = relationship(back_populates="version", cascade="all, delete-orphan")
    edges: Mapped[List["WorkflowEdge"]] = relationship(back_populates="version", cascade="all, delete-orphan")
    runs: Mapped[List["WorkflowRun"]] = relationship(back_populates="version", cascade="all, delete-orphan")


class WorkflowNode(Base):
    """
    Individual nodes (Agents, Decisions, etc.) within a workflow version.
    """
    __tablename__ = "workflow_nodes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflow_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    node_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., 'fraud_agent', 'decision', 'start', 'end'
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    configuration: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    ui_position: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict) # x, y coords

    # Relationships
    version: Mapped["WorkflowVersion"] = relationship(back_populates="nodes")


class WorkflowEdge(Base):
    """
    Connections between nodes, establishing the DAG.
    """
    __tablename__ = "workflow_edges"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflow_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    source_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflow_nodes.id", ondelete="CASCADE"), nullable=False)
    target_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflow_nodes.id", ondelete="CASCADE"), nullable=False)
    condition: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True) # Rules for branching

    # Relationships
    version: Mapped["WorkflowVersion"] = relationship(back_populates="edges")
    source_node: Mapped["WorkflowNode"] = relationship(foreign_keys=[source_node_id])
    target_node: Mapped["WorkflowNode"] = relationship(foreign_keys=[target_node_id])


class WorkflowRun(Base):
    """
    Tracking the execution of a specific workflow version.
    """
    __tablename__ = "workflow_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflow_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True) # pending, running, completed, failed
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Store global execution inputs/outputs
    input_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    output_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    version: Mapped["WorkflowVersion"] = relationship(back_populates="runs")
    logs: Mapped[List["WorkflowLog"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class WorkflowLog(Base):
    """
    Step-by-step audit logs of node execution inside a run.
    """
    __tablename__ = "workflow_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflow_nodes.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False) # success, failed, retrying
    execution_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    node_output: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    run: Mapped["WorkflowRun"] = relationship(back_populates="logs")
    node: Mapped["WorkflowNode"] = relationship()
