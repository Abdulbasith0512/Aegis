import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator

class ReviewAssignRequest(BaseModel):
    """Payload to assign or reassign a human auditor reviewer to a case queue item."""
    reviewer_id: uuid.UUID = Field(..., description="UUID of the assigning auditor user.")

class ReviewActionRequest(BaseModel):
    """Auditor decision action request payload."""
    status: str = Field(..., description="Action verdict: 'approved', 'rejected', or 'escalated'.")
    comments: str = Field(..., min_length=10, description="Remarks justification for audit verification trail.")

    @field_validator("status")
    @classmethod
    def validate_action_status(cls, v: str) -> str:
        if v.lower() not in ["approved", "rejected", "escalated"]:
            raise ValueError("Status action must be 'approved', 'rejected', or 'escalated'")
        return v.lower()

class ReviewQueueResponse(BaseModel):
    """Case queue summary response schema."""
    id: uuid.UUID
    transaction_id: uuid.UUID
    amount: float
    currency: str
    customer_name: str
    trust_score: float
    status: str
    reviewer_name: Optional[str] = None
    assigned_at: datetime
    sla_deadline: datetime
    is_sla_breached: bool

class ReviewDetailResponse(BaseModel):
    """Detailed case telemetry payload feeding the Evidence Viewer."""
    id: uuid.UUID
    transaction_id: uuid.UUID
    amount: float
    currency: str
    customer_name: str
    status: str
    comments: Optional[str] = None
    assigned_at: datetime
    reviewed_at: Optional[datetime] = None
    sla_deadline: datetime
    is_sla_breached: bool
    
    # Eagerly loaded telemetry structures
    trust_score: Optional[float] = None
    trust_warnings: List[str] = []
    
    # Explainability trace
    explanation_human: Optional[str] = None
    explanation_timeline: List[Dict[str, Any]] = []
    explanation_graph: Dict[str, Any] = {}
    explanation_shap: Dict[str, float] = {}

    # Policy evaluations
    policy_checks: List[Dict[str, Any]] = []
