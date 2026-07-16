import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.agents import AIAgent, ModelVersion, MLOpsDeployment, MLflowRun, DeploymentHistory
from app.schemas.mlops import ModelVersionCreate, DeploymentConfigUpdate, MLflowRunCreate

class AgentMLOpsRepository:
    """
    Data tier operations for Model Registry, MLflow Runs, and Deployments.
    """
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def ensure_default_agents(self) -> None:
        """
        Seeds standard system agents in DB if they are missing.
        """
        default_names = ["fraud-agent", "aml-agent", "kyc-agent", "device-agent", "behavior-agent", "compliance-agent"]
        for name in default_names:
            result = await self.db.execute(select(AIAgent).where(AIAgent.name == name))
            agent = result.scalars().first()
            if not agent:
                agent = AIAgent(
                    name=name,
                    description=f"Supervised AegisAI {name.upper()} evaluation node.",
                    status="active"
                )
                self.db.add(agent)
        await self.db.commit()

    async def list_agents(self) -> List[AIAgent]:
        """
        Retrieves all registered agents.
        """
        await self.ensure_default_agents()
        result = await self.db.execute(select(AIAgent).order_by(AIAgent.name))
        return list(result.scalars().all())

    async def get_agent_by_id(self, agent_id: uuid.UUID) -> Optional[AIAgent]:
        """
        Retrieves an agent by its primary key.
        """
        result = await self.db.execute(select(AIAgent).where(AIAgent.id == agent_id))
        return result.scalars().first()

    async def get_agent_by_name(self, name: str) -> Optional[AIAgent]:
        """
        Retrieves an agent by its unique name.
        """
        result = await self.db.execute(select(AIAgent).where(AIAgent.name == name))
        return result.scalars().first()

    async def list_versions(self, agent_id: uuid.UUID) -> List[ModelVersion]:
        """
        Lists all registered versions for a specific agent.
        """
        result = await self.db.execute(
            select(ModelVersion)
            .where(ModelVersion.agent_id == agent_id)
            .order_by(ModelVersion.deployed_at.desc())
        )
        return list(result.scalars().all())

    async def get_version_by_id(self, version_id: uuid.UUID) -> Optional[ModelVersion]:
        """
        Retrieves a version by its primary key.
        """
        result = await self.db.execute(select(ModelVersion).where(ModelVersion.id == version_id))
        return result.scalars().first()

    async def create_version(self, agent_id: uuid.UUID, schema: ModelVersionCreate) -> ModelVersion:
        """
        Registers a new model version in the registry.
        """
        version = ModelVersion(
            agent_id=agent_id,
            version_string=schema.version_string,
            parameters_hash=schema.parameters_hash,
            accuracy_benchmark=schema.accuracy_benchmark,
            is_active=True,
            hyperparameters=schema.hyperparameters,
            metrics=schema.metrics
        )
        self.db.add(version)
        await self.db.commit()
        await self.db.refresh(version)
        return version

    async def get_deployment_config(self, agent_id: uuid.UUID) -> MLOpsDeployment:
        """
        Retrieves active traffic routing settings for an agent, creating default if missing.
        """
        result = await self.db.execute(select(MLOpsDeployment).where(MLOpsDeployment.agent_id == agent_id))
        config = result.scalars().first()
        if not config:
            config = MLOpsDeployment(
                agent_id=agent_id,
                deployment_type="production",
                canary_split=100,
                ab_split=50
            )
            self.db.add(config)
            await self.db.commit()
            await self.db.refresh(config)
        return config

    async def update_deployment_config(self, schema: DeploymentConfigUpdate) -> MLOpsDeployment:
        """
        Updates canary splits, A/B testing weights, shadow models, and active version bindings.
        """
        config = await self.get_deployment_config(schema.agent_id)
        config.deployment_type = schema.deployment_type
        
        if schema.active_version_id is not None:
            config.active_version_id = schema.active_version_id
        if schema.canary_version_id is not None:
            config.canary_version_id = schema.canary_version_id
        if schema.canary_split is not None:
            config.canary_split = schema.canary_split
        if schema.shadow_version_id is not None:
            config.shadow_version_id = schema.shadow_version_id
        if schema.ab_version_a_id is not None:
            config.ab_version_a_id = schema.ab_version_a_id
        if schema.ab_version_b_id is not None:
            config.ab_version_b_id = schema.ab_version_b_id
        if schema.ab_split is not None:
            config.ab_split = schema.ab_split

        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def log_history(self, agent_id: uuid.UUID, action: str, details: str, performed_by: str = "system") -> DeploymentHistory:
        """
        Appends an event tracking record to MLOps audit logs trail.
        """
        log = DeploymentHistory(
            agent_id=agent_id,
            action=action,
            details=details,
            performed_by=performed_by
        )
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def list_deployment_history(self, agent_id: Optional[uuid.UUID] = None, limit: int = 50) -> List[DeploymentHistory]:
        """
        Lists chronological model registry and promotion events.
        """
        query = select(DeploymentHistory)
        if agent_id:
            query = query.where(DeploymentHistory.agent_id == agent_id)
        result = await self.db.execute(query.order_by(DeploymentHistory.timestamp.desc()).limit(limit))
        return list(result.scalars().all())

    # --- MLflow Runs ---
    async def create_mlflow_run(self, schema: MLflowRunCreate) -> MLflowRun:
        """
        Creates an entry mimicking MLflow experiment runs.
        """
        run = MLflowRun(
            agent_id=schema.agent_id,
            run_name=schema.run_name,
            experiment_id=str(schema.agent_id),
            parameters=schema.parameters,
            metrics=schema.metrics,
            status=schema.status
        )
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def list_mlflow_runs(self, agent_id: Optional[uuid.UUID] = None, limit: int = 50) -> List[MLflowRun]:
        """
        Lists logged runs.
        """
        query = select(MLflowRun)
        if agent_id:
            query = query.where(MLflowRun.agent_id == agent_id)
        result = await self.db.execute(query.order_by(MLflowRun.created_at.desc()).limit(limit))
        return list(result.scalars().all())
