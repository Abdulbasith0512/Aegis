import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict

# -----------------
# Scenario Schemas
# -----------------
class SimulationScenarioBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    simulation_type: str = Field(..., description="e.g., normal, high_fraud_day, festival_spike")
    
    num_customers: int = Field(default=1000, ge=1, le=1000000)
    num_accounts: int = Field(default=1200, ge=1, le=1000000)
    num_transactions: int = Field(default=5000, ge=1, le=1000000)
    
    fraud_percentage: float = Field(default=0.01, ge=0.0, le=1.0)
    aml_risk_level: str = Field(default="low")
    drift_percentage: float = Field(default=0.0, ge=0.0, le=1.0)
    target_tps: int = Field(default=10, ge=1, le=10000)
    
    injected_failures: List[str] = Field(default_factory=list)

class SimulationScenarioCreate(SimulationScenarioBase):
    pass

class SimulationScenarioRead(SimulationScenarioBase):
    id: uuid.UUID
    created_at: datetime
    created_by_id: Optional[uuid.UUID]
    
    model_config = ConfigDict(from_attributes=True)

class SimulationScenarioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    num_transactions: Optional[int] = None
    target_tps: Optional[int] = None

# -----------------
# Run Schemas
# -----------------
class SimulationRunBase(BaseModel):
    status: str = "pending"

class SimulationRunCreate(BaseModel):
    scenario_id: uuid.UUID

class SimulationRunRead(SimulationRunBase):
    id: uuid.UUID
    scenario_id: uuid.UUID
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

# -----------------
# Result Schemas
# -----------------
class SimulationResultRead(BaseModel):
    id: uuid.UUID
    run_id: uuid.UUID
    total_transactions: int
    fraud_detected: int
    aml_alerts: int
    false_positives: int
    false_negatives: int
    avg_latency_ms: float
    peak_tps: float
    trust_score_impact: float
    report_data: Optional[Dict[str, Any]]
    
    model_config = ConfigDict(from_attributes=True)

# -----------------
# Metric & Event Schemas
# -----------------
class SimulationMetricRead(BaseModel):
    id: uuid.UUID
    timestamp: datetime
    metric_type: str
    value: float
    tags: Optional[Dict[str, Any]]
    
    model_config = ConfigDict(from_attributes=True)

class SimulationEventRead(BaseModel):
    id: uuid.UUID
    timestamp: datetime
    event_type: str
    severity: str
    message: str
    details: Optional[Dict[str, Any]]
    
    model_config = ConfigDict(from_attributes=True)
