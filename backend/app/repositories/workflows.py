import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.workflows import Workflow, WorkflowVersion, WorkflowNode, WorkflowEdge, WorkflowRun, WorkflowLog
from app.schemas.workflows import WorkflowCreate, WorkflowUpdate

class WorkflowRepository:
    """
    Handles all CRUD operations for AI Governance Workflows.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db

    # -------------------------------------
    # Workflows
    # -------------------------------------
    async def create_workflow(self, workflow_data: WorkflowCreate, user_id: Optional[uuid.UUID] = None) -> Workflow:
        db_workflow = Workflow(
            name=workflow_data.name,
            description=workflow_data.description,
            is_template=workflow_data.is_template,
            created_by_id=user_id,
            status="draft"
        )
        self.db.add(db_workflow)
        await self.db.commit()
        await self.db.refresh(db_workflow)
        
        # Initialize with Version 1 automatically
        await self.create_workflow_version(db_workflow.id, version_number=1)
        return await self.get_workflow(db_workflow.id)

    async def get_workflow(self, workflow_id: uuid.UUID) -> Optional[Workflow]:
        stmt = select(Workflow).options(
            selectinload(Workflow.versions).selectinload(WorkflowVersion.nodes),
            selectinload(Workflow.versions).selectinload(WorkflowVersion.edges)
        ).where(Workflow.id == workflow_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_workflows(self, skip: int = 0, limit: int = 100, is_template: Optional[bool] = None) -> List[Workflow]:
        stmt = select(Workflow).options(
            selectinload(Workflow.versions)
        ).order_by(desc(Workflow.created_at)).offset(skip).limit(limit)
        
        if is_template is not None:
            stmt = stmt.where(Workflow.is_template == is_template)
            
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_workflow(self, workflow_id: uuid.UUID, update_data: WorkflowUpdate) -> Optional[Workflow]:
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            return None
            
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(workflow, key, value)
            
        await self.db.commit()
        await self.db.refresh(workflow)
        return workflow

    async def delete_workflow(self, workflow_id: uuid.UUID) -> bool:
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            return False
            
        await self.db.delete(workflow)
        await self.db.commit()
        return True

    # -------------------------------------
    # Workflow Versions, Nodes, Edges
    # -------------------------------------
    async def create_workflow_version(self, workflow_id: uuid.UUID, version_number: int) -> WorkflowVersion:
        db_version = WorkflowVersion(
            workflow_id=workflow_id,
            version_number=version_number,
            is_active=True
        )
        self.db.add(db_version)
        await self.db.commit()
        await self.db.refresh(db_version)
        return db_version
        
    async def save_workflow_graph(
        self, 
        version_id: uuid.UUID, 
        graph_data: Dict[str, Any],
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ) -> Optional[WorkflowVersion]:
        stmt = select(WorkflowVersion).where(WorkflowVersion.id == version_id)
        result = await self.db.execute(stmt)
        version = result.scalars().first()
        if not version:
            return None
            
        version.graph_data = graph_data
        
        # Clear existing nodes and edges
        await self.db.execute(WorkflowNode.__table__.delete().where(WorkflowNode.version_id == version_id))
        await self.db.execute(WorkflowEdge.__table__.delete().where(WorkflowEdge.version_id == version_id))
        
        # Re-insert nodes
        node_id_mapping = {} # React Flow string IDs mapped to UUIDs
        for n in nodes:
            db_node = WorkflowNode(
                version_id=version_id,
                node_type=n.get("type", "custom"),
                name=n.get("data", {}).get("label", "Node"),
                configuration=n.get("data", {}).get("config", {}),
                ui_position=n.get("position", {})
            )
            self.db.add(db_node)
            await self.db.flush()
            node_id_mapping[n["id"]] = db_node.id
            
        # Re-insert edges
        for e in edges:
            source_uuid = node_id_mapping.get(e.get("source"))
            target_uuid = node_id_mapping.get(e.get("target"))
            if source_uuid and target_uuid:
                db_edge = WorkflowEdge(
                    version_id=version_id,
                    source_node_id=source_uuid,
                    target_node_id=target_uuid,
                    condition=e.get("data", {}).get("condition", None)
                )
                self.db.add(db_edge)
                
        await self.db.commit()
        await self.db.refresh(version)
        return version

    # -------------------------------------
    # Execution Runs & Logs
    # -------------------------------------
    async def create_run(self, version_id: uuid.UUID, transaction_id: Optional[uuid.UUID], input_data: Dict[str, Any]) -> WorkflowRun:
        run = WorkflowRun(
            version_id=version_id,
            transaction_id=transaction_id,
            input_data=input_data,
            status="running"
        )
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run
        
    async def log_node_execution(
        self, 
        run_id: uuid.UUID, 
        node_id: uuid.UUID, 
        status: str, 
        execution_time_ms: float, 
        output: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> WorkflowLog:
        log = WorkflowLog(
            run_id=run_id,
            node_id=node_id,
            status=status,
            execution_time_ms=execution_time_ms,
            node_output=output,
            error_message=error
        )
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log
        
    async def finalize_run(self, run_id: uuid.UUID, status: str, output_data: Optional[Dict[str, Any]] = None) -> WorkflowRun:
        stmt = select(WorkflowRun).where(WorkflowRun.id == run_id)
        result = await self.db.execute(stmt)
        run = result.scalars().first()
        
        if run:
            from datetime import datetime
            run.status = status
            run.output_data = output_data
            run.completed_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(run)
        return run
