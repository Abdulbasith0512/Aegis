import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.governance import ChaosExperiment

class ChaosRepository:
    """
    Handles database operations for ChaosExperiment log entities.
    """
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def schedule_experiment(
        self,
        experiment_type: str,
        target_agent: Optional[str] = None,
        scheduled_at: Optional[datetime] = None
    ) -> ChaosExperiment:
        """
        Saves a newly planned fault-injection scenario.
        """
        record = ChaosExperiment(
            experiment_type=experiment_type,
            target_agent=target_agent,
            scheduled_at=scheduled_at or datetime.utcnow(),
            status="scheduled"
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def start_experiment(self, experiment_id: uuid.UUID) -> Optional[ChaosExperiment]:
        """
        Sets experiment status to 'running'.
        """
        record = await self.db.get(ChaosExperiment, experiment_id)
        if not record:
            return None
        record.status = "running"
        record.started_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def complete_experiment(
        self,
        experiment_id: uuid.UUID,
        metrics: Dict[str, Any],
        failed: bool = False
    ) -> Optional[ChaosExperiment]:
        """
        Registers experiment completion and outputs metrics indicators.
        """
        record = await self.db.get(ChaosExperiment, experiment_id)
        if not record:
            return None
        record.status = "failed" if failed else "completed"
        record.completed_at = datetime.utcnow()
        record.metrics = metrics
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def get_experiment(self, experiment_id: uuid.UUID) -> Optional[ChaosExperiment]:
        """Retrieves a single experiment execution log."""
        return await self.db.get(ChaosExperiment, experiment_id)

    async def list_experiments_history(self, limit: int = 50) -> List[ChaosExperiment]:
        """Lists historical fault injection trials."""
        result = await self.db.execute(
            select(ChaosExperiment)
            .order_by(ChaosExperiment.scheduled_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
