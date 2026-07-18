import uuid
from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.simulation import (
    SimulationScenario, SimulationRun, SimulationResult,
    SimulationMetric, SimulationEvent
)
from app.schemas.simulation import SimulationScenarioCreate, SimulationScenarioUpdate

class SimulationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # -------------------
    # Scenarios
    # -------------------
    async def create_scenario(self, data: SimulationScenarioCreate, user_id: Optional[uuid.UUID] = None) -> SimulationScenario:
        scenario = SimulationScenario(**data.model_dump(), created_by_id=user_id)
        self.db.add(scenario)
        await self.db.commit()
        await self.db.refresh(scenario)
        return scenario

    async def get_scenarios(self) -> List[SimulationScenario]:
        stmt = select(SimulationScenario).order_by(desc(SimulationScenario.created_at))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_scenario(self, scenario_id: uuid.UUID) -> Optional[SimulationScenario]:
        stmt = select(SimulationScenario).where(SimulationScenario.id == scenario_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    # -------------------
    # Runs
    # -------------------
    async def create_run(self, scenario_id: uuid.UUID) -> SimulationRun:
        run = SimulationRun(scenario_id=scenario_id, status="pending")
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def get_runs_for_scenario(self, scenario_id: uuid.UUID) -> List[SimulationRun]:
        stmt = select(SimulationRun).options(
            selectinload(SimulationRun.results)
        ).where(SimulationRun.scenario_id == scenario_id).order_by(desc(SimulationRun.started_at))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_run(self, run_id: uuid.UUID) -> Optional[SimulationRun]:
        stmt = select(SimulationRun).options(
            selectinload(SimulationRun.results),
            selectinload(SimulationRun.scenario)
        ).where(SimulationRun.id == run_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()
        
    async def update_run_status(self, run_id: uuid.UUID, status: str, completed: bool = False):
        run = await self.get_run(run_id)
        if run:
            from datetime import datetime
            run.status = status
            if status == "running" and not run.started_at:
                run.started_at = datetime.utcnow()
            if completed:
                run.completed_at = datetime.utcnow()
            await self.db.commit()

    # -------------------
    # Results & Metrics
    # -------------------
    async def save_result(self, run_id: uuid.UUID, data: dict) -> SimulationResult:
        result = SimulationResult(run_id=run_id, **data)
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        return result
        
    async def get_metrics(self, run_id: uuid.UUID) -> List[SimulationMetric]:
        stmt = select(SimulationMetric).where(SimulationMetric.run_id == run_id).order_by(SimulationMetric.timestamp)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
        
    async def get_events(self, run_id: uuid.UUID, limit: int = 100) -> List[SimulationEvent]:
        stmt = select(SimulationEvent).where(SimulationEvent.run_id == run_id).order_by(desc(SimulationEvent.timestamp)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
