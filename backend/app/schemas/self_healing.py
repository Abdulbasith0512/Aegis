import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class RecoveryActionResponse(BaseModel):
    """Chronological step output logged during automated self-healing events."""
    id: uuid.UUID
    incident_id: uuid.UUID
    action_step: str = Field(..., description="E.g. 'detect', 'diagnose', 'rollback', 'notify'.")
    status: str = Field(..., description="'pending', 'running', 'completed', or 'failed'.")
    details: Optional[Dict[str, Any]] = None
    executed_at: datetime

class IncidentResponse(BaseModel):
    """Anomalous failure event details response schema."""
    id: uuid.UUID
    agent_name: str
    failure_type: str = Field(..., description="Fault scenario label classification.")
    status: str = Field(..., description="'detected', 'healing', 'resolved', or 'failed'.")
    description: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    recovery_actions: List[RecoveryActionResponse] = []

class TriggerFailureRequest(BaseModel):
    """Simulation request payload to trigger a mock failure event."""
    agent_name: str = Field(..., description="Target agent name.")
    failure_type: str = Field(..., description="Anomaly classification (e.g. 'kill_agent', 'network_delay', 'prompt_injection').")
