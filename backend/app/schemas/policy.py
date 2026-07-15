import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class RuleCheckResult(BaseModel):
    """Result status of an individual rule evaluation."""
    field: str
    operator: str
    expected: Any
    actual: Any
    status: str = Field(..., description="'pass' or 'fail'.")

class PolicyCheckResult(BaseModel):
    """Result details of a single policy check evaluation."""
    policy_id: str
    name: str
    type: str
    status: str = Field(..., description="'pass' or 'fail'.")
    rules_checked: List[RuleCheckResult] = []

class PolicySimulationRequest(BaseModel):
    """Request payload containing custom transaction parameters for rules simulation."""
    transaction: Dict[str, Any] = Field(..., description="Transaction properties including nested customer data.")

class PolicySimulationResponse(BaseModel):
    """Aggregated response of policy checks simulation."""
    overall_status: str = Field(..., description="'pass' or 'fail'.")
    policies_checked: List[PolicyCheckResult] = []

class OverrideRequest(BaseModel):
    """Request payload to manually sign off and override a decision policy block."""
    transaction_id: uuid.UUID
    rule_id: str
    comments: str = Field(..., min_length=10, description="Detailed auditor comments explaining the override decision.")
