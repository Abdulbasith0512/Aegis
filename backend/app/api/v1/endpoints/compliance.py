import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.policy import PolicySimulationRequest, PolicySimulationResponse, OverrideRequest
from app.repositories.policy import PolicyRepository
from app.repositories.audit import AuditRepository
from app.services.policy_engine import PolicyEngine
from app.models.users import User

router: APIRouter = APIRouter(prefix="/compliance", tags=["Compliance"])

@router.get("/policies", response_model=List[Dict[str, Any]])
async def get_compliance_rules(
    current_user: User = Depends(require_permission("read:transactions"))
) -> List[Dict[str, Any]]:
    """
    Get all active regulatory compliance policies loaded in the YAML config.
    Requires 'read:transactions' permission.
    """
    engine = PolicyEngine()
    return engine.policies

@router.post("/simulate", response_model=PolicySimulationResponse)
async def simulate_policy_check(
    payload: PolicySimulationRequest,
    current_user: User = Depends(require_permission("read:transactions"))
) -> PolicySimulationResponse:
    """
    Dry-run simulation of YAML compliance policies against a custom transaction object.
    Requires 'read:transactions' permission.
    """
    engine = PolicyEngine()
    return engine.evaluate_transaction(payload.transaction)

@router.get("/violations", response_model=List[Dict[str, Any]])
async def get_policy_violations(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("read:transactions"))
) -> List[Dict[str, Any]]:
    """
    Retrieves history logs of transaction checks that triggered policy failures (violations).
    Requires 'read:transactions' permission.
    """
    policy_repo = PolicyRepository(db)
    violations = await policy_repo.list_violations(limit=limit)
    
    return [
        {
            "id": str(v.id),
            "transaction_id": str(v.transaction_id),
            "rule_id": v.rule_id,
            "status": v.status,
            "details": v.details,
            "executed_at": v.executed_at.isoformat()
        }
        for v in violations
    ]

@router.post("/override", status_code=status.HTTP_201_CREATED)
async def create_policy_override(
    payload: OverrideRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("write:policies"))
) -> Dict[str, str]:
    """
    Log an administrative override, bypassing a blocked rule with auditor comments.
    Requires 'write:policies' permission.
    """
    policy_repo = PolicyRepository(db)
    audit_repo = AuditRepository(db)

    # Persist the decision override in human review tables
    review = await policy_repo.create_decision_override(
        transaction_id=payload.transaction_id,
        reviewer_id=current_user.id,
        comments=payload.comments
    )

    # Log to cryptographic audit chains
    await audit_repo.log_action(
        actor_id=current_user.id,
        action_type="policy_override",
        description=f"Administrative policy override applied for transaction {payload.transaction_id}",
        resource_id=str(review.id),
        metadata={"rule_id": payload.rule_id, "comments": payload.comments}
    )

    return {
        "message": "Administrative override logged successfully.",
        "review_id": str(review.id)
    }
