import uuid
from datetime import datetime
from typing import Dict, Any, List
from pydantic import BaseModel, Field, field_validator

class TrustCalculationRequest(BaseModel):
    """
    Validation schema representing telemetry details used to calculate Trust.
    """
    transaction_id: uuid.UUID = Field(..., description="Unique transaction UUID.")
    agent_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence of executing ML agents.")
    historical_accuracy: float = Field(..., ge=0.0, le=1.0, description="Benchmark accuracy of deployed models.")
    model_drift: float = Field(..., ge=0.0, le=1.0, description="Feature or data drift validation index.")
    data_quality: float = Field(..., ge=0.0, le=1.0, description="Data schema completeness ratio.")
    latency_ms: float = Field(..., ge=0.0, description="Transaction routing latency in milliseconds.")
    policy_compliance: bool = Field(..., description="Verifies if transaction passed deterministic rule constraints.")
    explainability_score: float = Field(..., ge=0.0, le=1.0, description="Cohesion or fidelity of explanations.")
    agent_consensus: float = Field(..., ge=0.0, le=1.0, description="Percentage of voting consensus among nodes.")

    @field_validator("agent_confidence", "historical_accuracy", "model_drift", "data_quality", "explainability_score", "agent_consensus")
    @classmethod
    def check_normalized_probabilities(cls, v: float) -> float:
        if v < 0.0 or v > 1.0:
            raise ValueError("Telemetry inputs must be normalized values between 0.0 and 1.0")
        return v

class TrustCalculationResponse(BaseModel):
    """
    Validation schema returned on successful Trust calculation.
    """
    id: uuid.UUID = Field(..., description="Calculated Trust Score identifier.")
    transaction_id: uuid.UUID = Field(..., description="Associated transaction UUID.")
    score: int = Field(..., ge=0, le=100, description="Aggregated trust index score (0 to 100).")
    weights_configuration: Dict[str, float] = Field(..., description="Weights used during score aggregation.")
    reasons: Dict[str, Any] = Field(..., description="System warnings and attribute contributions.")
    created_at: datetime = Field(..., description="Calculation timestamp.")
