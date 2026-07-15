import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class TimelineEvent(BaseModel):
    """Event representation in a decision timeline."""
    event: str = Field(..., description="Action name or node execution description.")
    timestamp: str = Field(..., description="ISO 8601 formatted timestamp string.")
    duration_ms: float = Field(..., description="Duration of step in milliseconds.")
    status: str = Field(..., description="Execution status of this timeline step.")

class EvidenceNode(BaseModel):
    """Representing nodes in the explainability evidence graph."""
    id: str = Field(..., description="Unique node identifier.")
    type: str = Field(..., description="Node type: 'account', 'device', 'policy', 'agent'.")
    label: str = Field(..., description="Human-readable label for the node.")
    status: str = Field(..., description="Risk or passing state of the node.")

class EvidenceEdge(BaseModel):
    """Representing relationships in the explainability evidence graph."""
    source: str = Field(..., description="Source node ID.")
    target: str = Field(..., description="Target node ID.")
    label: str = Field(..., description="Relationship context label.")

class EvidenceGraph(BaseModel):
    """The full topological visual model representing transaction decision traces."""
    nodes: List[EvidenceNode] = Field(..., description="Topological nodes list.")
    edges: List[EvidenceEdge] = Field(..., description="Topological edges list.")

class ExplanationCreateRequest(BaseModel):
    """Request payload to manually compile explainability metrics."""
    prediction_id: uuid.UUID = Field(..., description="UUID of the associated decision Prediction.")
    agent_traces: Dict[str, Any] = Field(..., description="Execution traces and timing outputs from preceding agents.")

class ExplanationResponse(BaseModel):
    """Comprehensive explainability response schema."""
    id: uuid.UUID
    prediction_id: uuid.UUID
    human_readable: str = Field(..., description="Textual explainability statement.")
    machine_readable: Dict[str, Any] = Field(..., description="Raw quantitative explainability metadata (e.g. LIME).")
    decision_timeline: List[TimelineEvent] = Field(..., description="Sequential processing events trace.")
    evidence_graph: EvidenceGraph = Field(..., description="Graph representation showing telemetry associations.")
    feature_importance: Dict[str, float] = Field(..., description="SHAP feature attributions mapping.")
    confidence_reasoning: str = Field(..., description="Justification details for classifier confidence.")
    supporting_policies: List[str] = Field(..., description="Regulatory or internal limits policies matched.")
    contributing_agents: List[str] = Field(..., description="Names and version hashes of contributing agents.")
    explainability_score: float = Field(..., ge=0.0, le=1.0, description="Heuristic explainability coverage index.")
    explanation_vector: Optional[List[float]] = Field(default=None, description="Explainability embedding vector.")
    created_at: datetime
