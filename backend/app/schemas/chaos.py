import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator

class ChaosExperimentCreate(BaseModel):
    """Payload to schedule a new AI fault-injection experiment."""
    experiment_type: str = Field(..., description="Target fault: 'kill_agent', 'database_failure', 'redis_failure', 'network_delay', 'high_latency', 'prompt_injection', 'model_drift', 'data_poisoning', 'adversarial_samples', 'api_failure'.")
    target_agent: Optional[str] = Field(default=None, description="Identifying label of agent targeted (if applicable).")
    scheduled_at: datetime = Field(default_factory=datetime.utcnow, description="Scheduled ISO timestamp.")

    @field_validator("experiment_type")
    @classmethod
    def validate_scenario_type(cls, v: str) -> str:
        valid_types = [
            "kill_agent", "database_failure", "redis_failure", 
            "network_delay", "high_latency", "prompt_injection", 
            "model_drift", "data_poisoning", "adversarial_samples", "api_failure"
        ]
        if v.lower() not in valid_types:
            raise ValueError(f"Chaos scenario must be one of: {', '.join(valid_types)}")
        return v.lower()

class ChaosExperimentResponse(BaseModel):
    """Detailed chaos experiment metrics audit payload."""
    id: uuid.UUID
    experiment_type: str
    status: str
    target_agent: Optional[str] = None
    scheduled_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metrics: Optional[Dict[str, Any]] = Field(default=None, description="Measured Recovery Time, Trust Drop, Consensus Failures, and Policy violations count.")
