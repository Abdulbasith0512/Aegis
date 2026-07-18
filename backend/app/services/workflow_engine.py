import uuid
import time
from typing import Dict, Any, List, Optional, Set
from fastapi import HTTPException
from app.models.workflows import WorkflowVersion
from app.repositories.workflows import WorkflowRepository
import logging

logger = logging.getLogger(__name__)

class WorkflowExecutionEngine:
    """
    Executes a Workflow Directed Acyclic Graph (DAG).
    """

    def __init__(self, repository: WorkflowRepository):
        self.repo = repository

    def validate_dag(self, version: WorkflowVersion) -> bool:
        """
        Validates that the workflow contains a start node, end node,
        and no circular dependencies.
        """
        nodes = {str(n.id): n for n in version.nodes}
        edges = version.edges
        
        has_start = any(n.node_type == "start" for n in version.nodes)
        has_end = any(n.node_type == "end" for n in version.nodes)
        
        if not has_start:
            raise ValueError("Workflow is missing a Start node")
        if not has_end:
            raise ValueError("Workflow is missing an End node")

        # Check for circular dependencies using DFS
        adjacency_list = {str(n.id): [] for n in version.nodes}
        for edge in edges:
            adjacency_list[str(edge.source_node_id)].append(str(edge.target_node_id))

        visited = set()
        rec_stack = set()

        def is_cyclic(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            for neighbor in adjacency_list.get(node_id, []):
                if neighbor not in visited:
                    if is_cyclic(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        for node_id in nodes:
            if node_id not in visited:
                if is_cyclic(node_id):
                    raise ValueError("Workflow contains a circular dependency")

        return True

    def topological_sort(self, version: WorkflowVersion) -> List[str]:
        """
        Returns a linearly ordered list of node IDs based on the DAG edges.
        """
        adjacency_list = {str(n.id): [] for n in version.nodes}
        in_degree = {str(n.id): 0 for n in version.nodes}
        
        for edge in version.edges:
            adjacency_list[str(edge.source_node_id)].append(str(edge.target_node_id))
            in_degree[str(edge.target_node_id)] += 1

        queue = [node_id for node_id, deg in in_degree.items() if deg == 0]
        sorted_nodes = []

        while queue:
            current = queue.pop(0)
            sorted_nodes.append(current)
            
            for neighbor in adjacency_list.get(current, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(sorted_nodes) != len(version.nodes):
            raise ValueError("Graph has cycles or disconnected components")
            
        return sorted_nodes

    async def execute_run(self, version: WorkflowVersion, transaction_id: Optional[uuid.UUID], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the workflow synchronously for MVP.
        In a full production environment, this could dispatch to Celery/Temporal.
        """
        try:
            self.validate_dag(version)
            execution_order = self.topological_sort(version)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        run = await self.repo.create_run(version.id, transaction_id, input_data)
        
        # State to pass between nodes
        state = {"global": input_data, "node_outputs": {}}
        nodes_dict = {str(n.id): n for n in version.nodes}
        
        try:
            for node_id in execution_order:
                node = nodes_dict[node_id]
                start_time = time.time()
                
                # In a real system, we'd invoke the actual agents here
                # For MVP, we simulate execution
                try:
                    output = await self._execute_node(node, state)
                    state["node_outputs"][node_id] = output
                    
                    # Update global state if it's the start node
                    if node.node_type == "start":
                        state["global"].update(output)
                        
                    duration_ms = (time.time() - start_time) * 1000
                    await self.repo.log_node_execution(run.id, node.id, "success", duration_ms, output=output)
                    
                except Exception as node_err:
                    duration_ms = (time.time() - start_time) * 1000
                    await self.repo.log_node_execution(run.id, node.id, "failed", duration_ms, error=str(node_err))
                    raise node_err

            # Finalize
            final_output = state["node_outputs"].get(execution_order[-1], {})
            await self.repo.finalize_run(run.id, "completed", final_output)
            return {"status": "success", "run_id": str(run.id), "output": final_output}

        except Exception as e:
            await self.repo.finalize_run(run.id, "failed")
            logger.error(f"Workflow run failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

    async def _execute_node(self, node: Any, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulated node execution router.
        Integrates with fraud agent, aml agent, policy engine, etc.
        """
        import asyncio
        await asyncio.sleep(0.1) # Simulate network/inference latency
        
        if node.node_type == "start":
            return state.get("global", {})
        elif node.node_type == "end":
            return {"final_decision": "approved", "completed": True}
        elif node.node_type == "fraud_agent":
            return {"fraud_score": 0.05, "is_fraud": False}
        elif node.node_type == "aml_agent":
            return {"aml_risk": "low"}
        elif node.node_type == "policy_engine":
            return {"policy_passed": True}
        elif node.node_type == "decision":
            # Simple rules engine simulation
            return {"branch": "approve"}
        
        return {"status": "executed"}
