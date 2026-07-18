import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict

# -----------------
# Node & Edge Schemas
# -----------------

class WorkflowNodeBase(BaseModel):
    node_type: str = Field(..., description="Type of the node (e.g., fraud_agent, aml_agent, decision, start, end)")
    name: str = Field(..., description="Display name of the node")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Execution configuration logic")
    ui_position: Dict[str, Any] = Field(default_factory=dict, description="Coordinates for React Flow")

class WorkflowNodeCreate(WorkflowNodeBase):
    pass

class WorkflowNodeRead(WorkflowNodeBase):
    id: uuid.UUID
    version_id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)

class WorkflowEdgeBase(BaseModel):
    source_node_id: uuid.UUID = Field(..., description="Origin node ID")
    target_node_id: uuid.UUID = Field(..., description="Destination node ID")
    condition: Optional[Dict[str, Any]] = Field(None, description="Conditional branching rules if any")

class WorkflowEdgeCreate(WorkflowEdgeBase):
    pass

class WorkflowEdgeRead(WorkflowEdgeBase):
    id: uuid.UUID
    version_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)

# -----------------
# Workflow Version Schemas
# -----------------

class WorkflowVersionBase(BaseModel):
    is_active: bool = False
    graph_data: Dict[str, Any] = Field(default_factory=dict)

class WorkflowVersionCreate(WorkflowVersionBase):
    pass

class WorkflowVersionRead(WorkflowVersionBase):
    id: uuid.UUID
    workflow_id: uuid.UUID
    version_number: int
    created_at: datetime
    
    nodes: List[WorkflowNodeRead] = []
    edges: List[WorkflowEdgeRead] = []

    model_config = ConfigDict(from_attributes=True)

# -----------------
# Workflow Schemas
# -----------------

class WorkflowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    is_template: bool = False

class WorkflowCreate(WorkflowBase):
    pass

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    is_template: Optional[bool] = None

class WorkflowRead(WorkflowBase):
    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[uuid.UUID]
    
    versions: List[WorkflowVersionRead] = []

    model_config = ConfigDict(from_attributes=True)

# -----------------
# Execution Engine Schemas
# -----------------

class ExecuteWorkflowRequest(BaseModel):
    transaction_id: Optional[uuid.UUID] = None
    input_data: Dict[str, Any] = Field(..., description="Initial payload to feed into the workflow Start node")

class WorkflowLogRead(BaseModel):
    id: uuid.UUID
    run_id: uuid.UUID
    node_id: uuid.UUID
    status: str
    execution_time_ms: Optional[float]
    node_output: Optional[Dict[str, Any]]
    error_message: Optional[str]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class WorkflowRunRead(BaseModel):
    id: uuid.UUID
    version_id: uuid.UUID
    transaction_id: Optional[uuid.UUID]
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    logs: List[WorkflowLogRead] = []

    model_config = ConfigDict(from_attributes=True)
