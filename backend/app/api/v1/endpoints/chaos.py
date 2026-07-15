import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.chaos import ChaosExperimentCreate, ChaosExperimentResponse
from app.repositories.chaos import ChaosRepository
from app.repositories.audit import AuditRepository
from app.services.chaos_engine import DynamicChaosEngine
from app.models.users import User

router: APIRouter = APIRouter(prefix="/chaos", tags=["Chaos Engine"])

@router.post("/schedule", response_model=ChaosExperimentResponse, status_code=status.HTTP_201_CREATED)
async def schedule_chaos_experiment(
    payload: ChaosExperimentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("write:policies"))
) -> ChaosExperimentResponse:
    """
    Schedules a new AI fault-injection scenario.
    Requires 'write:policies' permission.
    """
    repo = ChaosRepository(db)
    audit_repo = AuditRepository(db)

    # Save to database
    record = await repo.schedule_experiment(
        experiment_type=payload.experiment_type,
        target_agent=payload.target_agent,
        scheduled_at=payload.scheduled_at
    )

    # Log to cryptographic audit ledger
    await audit_repo.log_action(
        actor_id=current_user.id,
        action_type="schedule_chaos",
        description=f"Chaos experiment {payload.experiment_type} scheduled for target {payload.target_agent}",
        resource_id=str(record.id)
    )

    return ChaosExperimentResponse(
        id=record.id,
        experiment_type=record.experiment_type,
        status=record.status,
        target_agent=record.target_agent,
        scheduled_at=record.scheduled_at,
        started_at=record.started_at,
        completed_at=record.completed_at,
        metrics=record.metrics
    )

@router.post("/scenarios/{experiment_id}/run", response_model=ChaosExperimentResponse)
async def trigger_chaos_experiment(
    experiment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("write:policies"))
) -> ChaosExperimentResponse:
    """
    Triggers/runs a scheduled experiment, executes fault injection, measures recovery parameters, and saves.
    Requires 'write:policies' permission.
    """
    repo = ChaosRepository(db)
    audit_repo = AuditRepository(db)
    engine = DynamicChaosEngine()

    record = await repo.get_experiment(experiment_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled chaos experiment not found."
        )

    if record.status in ["completed", "failed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chaos experiment has already been executed."
        )

    # Start experiment
    await repo.start_experiment(experiment_id)

    # Execute injection calculation simulation
    metrics = engine.execute_fault_injection(
        scenario=record.experiment_type,
        target_agent=record.target_agent or "system"
    )

    # Complete and record
    failed_flag = not metrics.get("recovery_success", True)
    updated_record = await repo.complete_experiment(
        experiment_id=experiment_id,
        metrics=metrics,
        failed=failed_flag
    )

    if not updated_record:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to finalize experiment details."
        )

    # Log to cryptographic audit ledger
    await audit_repo.log_action(
        actor_id=current_user.id,
        action_type="trigger_chaos",
        description=f"Chaos experiment {record.experiment_type} completed (Recovery Time: {metrics.get('recovery_time_seconds')}s)",
        resource_id=str(experiment_id),
        metadata=metrics
    )

    return ChaosExperimentResponse(
        id=updated_record.id,
        experiment_type=updated_record.experiment_type,
        status=updated_record.status,
        target_agent=updated_record.target_agent,
        scheduled_at=updated_record.scheduled_at,
        started_at=updated_record.started_at,
        completed_at=updated_record.completed_at,
        metrics=updated_record.metrics
    )

@router.get("/history", response_model=List[ChaosExperimentResponse])
async def read_chaos_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("read:transactions"))
) -> List[ChaosExperimentResponse]:
    """
    Lists historical chaos injections and metrics results.
    Requires 'read:transactions' permission.
    """
    repo = ChaosRepository(db)
    records = await repo.list_experiments_history(limit=limit)

    return [
        ChaosExperimentResponse(
            id=r.id,
            experiment_type=r.experiment_type,
            status=r.status,
            target_agent=r.target_agent,
            scheduled_at=r.scheduled_at,
            started_at=r.started_at,
            completed_at=r.completed_at,
            metrics=r.metrics
        )
        for r in records
    ]
