import pytest
import uuid
from app.services.workflow_engine import WorkflowExecutionEngine
from app.models.workflows import WorkflowVersion, WorkflowNode, WorkflowEdge

class DummyRepo:
    async def create_run(self, version_id, transaction_id, input_data):
        pass
    async def log_node_execution(self, *args, **kwargs):
        pass
    async def finalize_run(self, *args, **kwargs):
        pass

def test_dag_validation_success():
    engine = WorkflowExecutionEngine(DummyRepo())
    
    start_node = WorkflowNode(id=uuid.uuid4(), node_type="start")
    agent_node = WorkflowNode(id=uuid.uuid4(), node_type="fraud_agent")
    end_node = WorkflowNode(id=uuid.uuid4(), node_type="end")
    
    edge1 = WorkflowEdge(source_node_id=start_node.id, target_node_id=agent_node.id)
    edge2 = WorkflowEdge(source_node_id=agent_node.id, target_node_id=end_node.id)
    
    version = WorkflowVersion(
        id=uuid.uuid4(),
        nodes=[start_node, agent_node, end_node],
        edges=[edge1, edge2]
    )
    
    assert engine.validate_dag(version) == True
    order = engine.topological_sort(version)
    assert len(order) == 3
    assert order[0] == str(start_node.id)
    assert order[-1] == str(end_node.id)

def test_dag_validation_missing_start():
    engine = WorkflowExecutionEngine(DummyRepo())
    
    agent_node = WorkflowNode(id=uuid.uuid4(), node_type="fraud_agent")
    end_node = WorkflowNode(id=uuid.uuid4(), node_type="end")
    
    edge = WorkflowEdge(source_node_id=agent_node.id, target_node_id=end_node.id)
    
    version = WorkflowVersion(
        id=uuid.uuid4(),
        nodes=[agent_node, end_node],
        edges=[edge]
    )
    
    with pytest.raises(ValueError, match="Workflow is missing a Start node"):
        engine.validate_dag(version)

def test_dag_validation_circular_dependency():
    engine = WorkflowExecutionEngine(DummyRepo())
    
    start_node = WorkflowNode(id=uuid.uuid4(), node_type="start")
    node_a = WorkflowNode(id=uuid.uuid4(), node_type="decision")
    node_b = WorkflowNode(id=uuid.uuid4(), node_type="decision")
    end_node = WorkflowNode(id=uuid.uuid4(), node_type="end")
    
    edge1 = WorkflowEdge(source_node_id=start_node.id, target_node_id=node_a.id)
    edge2 = WorkflowEdge(source_node_id=node_a.id, target_node_id=node_b.id)
    edge3 = WorkflowEdge(source_node_id=node_b.id, target_node_id=node_a.id) # cycle
    edge4 = WorkflowEdge(source_node_id=node_b.id, target_node_id=end_node.id)
    
    version = WorkflowVersion(
        id=uuid.uuid4(),
        nodes=[start_node, node_a, node_b, end_node],
        edges=[edge1, edge2, edge3, edge4]
    )
    
    with pytest.raises(ValueError, match="Workflow contains a circular dependency"):
        engine.validate_dag(version)
