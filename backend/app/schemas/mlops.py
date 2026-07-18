import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class ModelVersionCreate(BaseModel):
    version_string: str = Field(..., description="E.g., v1.1.0")
    parameters_hash: str = Field(..., description="Model checksum hash.")
    accuracy_benchmark: float = Field(default=0.0)
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)

class ModelVersionOut(BaseModel):
    id: uuid.UUID
    agent_id: uuid.UUID
    version_string: str
    parameters_hash: str
    accuracy_benchmark: float
    is_active: bool
    deployed_at: datetime
    hyperparameters: Dict[str, Any] = {}
    metrics: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)

class MLOpsDeploymentOut(BaseModel):
    agent_id: uuid.UUID
    agent_name: str
    deployment_type: str # production, canary, shadow, ab_testing
    active_version: Optional[ModelVersionOut] = None
    canary_version: Optional[ModelVersionOut] = None
    canary_split: int = 100
    shadow_version: Optional[ModelVersionOut] = None
    ab_version_a: Optional[ModelVersionOut] = None
    ab_version_b: Optional[ModelVersionOut] = None
    ab_split: int = 50

class MLflowRunCreate(BaseModel):
    agent_id: uuid.UUID
    run_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    status: str = "FINISHED"

class MLflowRunOut(BaseModel):
    id: uuid.UUID
    agent_id: uuid.UUID
    run_name: str
    experiment_id: str
    parameters: Dict[str, Any]
    metrics: Dict[str, Any]
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DeploymentConfigUpdate(BaseModel):
    agent_id: uuid.UUID
    deployment_type: str # production, canary, shadow, ab_testing
    active_version_id: Optional[uuid.UUID] = None
    canary_version_id: Optional[uuid.UUID] = None
    canary_split: Optional[int] = 100
    shadow_version_id: Optional[uuid.UUID] = None
    ab_version_a_id: Optional[uuid.UUID] = None
    ab_version_b_id: Optional[uuid.UUID] = None
    ab_split: Optional[int] = 50

class RollbackRequest(BaseModel):
    agent_id: uuid.UUID
    target_version_id: uuid.UUID

class DeploymentHistoryOut(BaseModel):
    id: uuid.UUID
    agent_id: uuid.UUID
    action: str # promote, rollback, create_version
    details: str
    performed_by: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
