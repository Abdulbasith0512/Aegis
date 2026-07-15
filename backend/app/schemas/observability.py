from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class SystemMetricsSummary(BaseModel):
    """System-level hardware resource indicators."""
    cpu_percent: float = Field(..., ge=0.0, le=100.0, description="CPU usage percentage.")
    gpu_percent: float = Field(..., ge=0.0, le=100.0, description="GPU usage percentage.")
    memory_percent: float = Field(..., ge=0.0, le=100.0, description="System memory usage percentage.")

class AgentMetricsSummary(BaseModel):
    """Runtime telemetry indicators collected per evaluating agent."""
    agent_name: str
    latency_ms: float = Field(..., description="Average latency in milliseconds.")
    prompt_tokens: int = Field(..., description="Prompt token count consumption.")
    completion_tokens: int = Field(..., description="Completion token count consumption.")
    health_status: int = Field(..., description="1 if active/healthy, 0 if offline.")
    hallucination_rate: float = Field(..., ge=0.0, le=1.0, description="Hallucination frequency rate index.")
    model_drift: float = Field(..., ge=0.0, le=1.0, description="Model drift divergence index.")
    inference_errors: int = Field(..., description="Count of inference anomalies encountered.")

class ObservabilitySummaryResponse(BaseModel):
    """Unified telemetry overview response schema."""
    system_metrics: SystemMetricsSummary
    agent_metrics: List[AgentMetricsSummary]
    overall_trust_score: float = Field(..., description="Current network trust score.")
    policy_violations_total: int = Field(..., description="Aggregate policy failure counts.")
    active_alerts_count: int = Field(..., description="Count of unresolved high risk warnings.")

class TelemetryRecordRequest(BaseModel):
    """Simulation request payload to record agent executions."""
    agent_name: str
    duration_seconds: float
    tokens_prompt: int
    tokens_completion: int
    confidence: float
    trust_score: float
    error_occurred: bool = False
    drift: float = 0.0
    hallucination_rate: float = 0.0
