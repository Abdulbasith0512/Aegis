import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.self_healing import IncidentResponse, TriggerFailureRequest
from app.repositories.self_healing import SelfHealingRepository
from app.services.self_healing import SelfHealingEngine
from app.models.users import User

router: APIRouter = APIRouter(prefix="/self-healing", tags=["Self-Healing Engine"])

@router.get("/incidents", response_model=List[IncidentResponse])
async def get_active_incidents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("read:transactions"))
) -> List[IncidentResponse]:
    """
    Get active self-healing incidents currently unresolved (detected, healing, or failed).
    Requires 'read:transactions' permission.
    """
    repo = SelfHealingRepository(db)
    records = await repo.list_active_incidents()
    
    response = []
    for r in records:
        actions = []
        for act in r.recovery_actions:
            actions.append({
                "id": act.id,
                "incident_id": act.incident_id,
                "action_step": act.action_step,
                "status": act.status,
                "details": act.details,
                "executed_at": act.executed_at
            })

        response.append(IncidentResponse(
            id=r.id,
            agent_name=r.agent_name,
            failure_type=r.failure_type,
            status=r.status,
            description=r.description,
            created_at=r.created_at,
            resolved_at=r.resolved_at,
            recovery_actions=actions
        ))
    return response

@router.get("/incidents/{incident_id}", response_model=IncidentResponse)
async def get_incident_details(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("read:transactions"))
) -> IncidentResponse:
    """
    Retrieves full details of a specific self-healing event.
    Requires 'read:transactions' permission.
    """
    repo = SelfHealingRepository(db)
    r = await repo.get_incident_details(incident_id)
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident log not found."
        )

    actions = []
    for act in r.recovery_actions:
        actions.append({
            "id": act.id,
            "incident_id": act.incident_id,
            "action_step": act.action_step,
            "status": act.status,
            "details": act.details,
            "executed_at": act.executed_at
        })

    return IncidentResponse(
        id=r.id,
        agent_name=r.agent_name,
        failure_type=r.failure_type,
        status=r.status,
        description=r.description,
        created_at=r.created_at,
        resolved_at=r.resolved_at,
        recovery_actions=actions
    )

@router.post("/trigger", status_code=status.HTTP_202_ACCEPTED)
async def trigger_agent_failure(
    payload: TriggerFailureRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("write:policies"))
) -> Dict[str, str]:
    """
    Triggers simulated agent failure to invoke automated self-healing workflows.
    Requires 'write:policies' permission.
    """
    engine = SelfHealingEngine(db)
    incident_id = await engine.trigger_failure(payload.agent_name, payload.failure_type)
    
    return {
        "message": "Failure event published successfully. Automated recovery in progress.",
        "incident_id": str(incident_id)
    }
