import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.trust import TrustCalculationRequest, TrustCalculationResponse
from app.repositories.trust import TrustRepository
from app.repositories.audit import AuditRepository
from app.services.trust_engine import WeightedTrustEngine
from app.models.users import User

router: APIRouter = APIRouter(prefix="/trust", tags=["Trust Score Engine"])

@router.post("/calculate", response_model=TrustCalculationResponse, status_code=status.HTTP_201_CREATED)
async def calculate_trust_score(
    payload: TrustCalculationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("write:policies"))
) -> TrustCalculationResponse:
    """
    Computes and stores a new Trust Score index evaluating transaction telemetry.
    Requires 'write:policies' permission.
    """
    trust_repo = TrustRepository(db)
    audit_repo = AuditRepository(db)
    engine = WeightedTrustEngine()

    # Compute trust parameters using service
    score, weights, reasons = engine.calculate_score(payload)

    # Persist in PostgreSQL
    trust_record = await trust_repo.save_trust_score(
        transaction_id=payload.transaction_id,
        score=score,
        weights=weights,
        reasons=reasons
    )

    # Log to cryptographic audit chains
    await audit_repo.log_action(
        actor_id=current_user.id,
        action_type="calculate_trust",
        description=f"Trust Score calculated for transaction {payload.transaction_id}: {score}/100",
        resource_id=str(trust_record.id),
        metadata={"score": score, "warnings_count": len(reasons.get("warnings", []))}
    )

    return TrustCalculationResponse(
        id=trust_record.id,
        transaction_id=trust_record.transaction_id,
        score=trust_record.score,
        weights_configuration=trust_record.weights_configuration,
        reasons=trust_record.reasons,
        created_at=trust_record.created_at
    )

@router.get("/history", response_model=List[TrustCalculationResponse])
async def read_trust_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("read:transactions"))
) -> List[TrustCalculationResponse]:
    """
    List historical trust scoring outputs for trend visualizations.
    Requires 'read:transactions' permission.
    """
    trust_repo = TrustRepository(db)
    records = await trust_repo.list_trust_history(limit=limit)
    
    return [
        TrustCalculationResponse(
            id=r.id,
            transaction_id=r.transaction_id,
            score=r.score,
            weights_configuration=r.weights_configuration,
            reasons=r.reasons,
            created_at=r.created_at
        )
        for r in records
    ]

@router.get("/transaction/{transaction_id}", response_model=TrustCalculationResponse)
async def read_transaction_trust(
    transaction_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("read:transactions"))
) -> TrustCalculationResponse:
    """
    Retrieves the Trust Score index associated with a specific transaction.
    Requires 'read:transactions' permission.
    """
    trust_repo = TrustRepository(db)
    record = await trust_repo.get_trust_by_transaction_id(transaction_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trust Score not found for the specified transaction."
        )
        
    return TrustCalculationResponse(
        id=record.id,
        transaction_id=record.transaction_id,
        score=record.score,
        weights_configuration=record.weights_configuration,
        reasons=record.reasons,
        created_at=record.created_at
    )
