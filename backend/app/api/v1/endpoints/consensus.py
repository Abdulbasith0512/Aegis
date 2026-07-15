import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.consensus import ConsensusRequest, ConsensusResponse
from app.repositories.consensus import ConsensusRepository
from app.repositories.audit import AuditRepository
from app.services.consensus_engine import DynamicConsensusEngine
from app.models.users import User

router: APIRouter = APIRouter(prefix="/consensus", tags=["AI Consensus Engine"])

@router.post("/evaluate", response_model=ConsensusResponse, status_code=status.HTTP_201_CREATED)
async def evaluate_consensus_verdict(
    payload: ConsensusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("write:policies"))
) -> ConsensusResponse:
    """
    Submits agent decision votes, evaluates consensus, maps dynamic reputations, and stores verdict.
    Requires 'write:policies' permission.
    """
    consensus_repo = ConsensusRepository(db)
    audit_repo = AuditRepository(db)
    engine = DynamicConsensusEngine()

    # Retrieve past evaluations to scale agent reputations dynamically
    past_db_votes = await consensus_repo.list_consensus_history(limit=50)
    past_votes = [
        {"decision_verdict": v.decision_verdict, "vote_details": v.vote_details}
        for v in past_db_votes
    ]

    # Evaluate consensus
    verdict, score, details = engine.evaluate_consensus(payload.votes, past_votes)

    # Save to PostgreSQL
    record = await consensus_repo.save_consensus_vote(
        transaction_id=payload.transaction_id,
        decision_verdict=verdict,
        consensus_score=score,
        vote_details=details
    )

    # Log to cryptographic audit ledger
    await audit_repo.log_action(
        actor_id=current_user.id,
        action_type="evaluate_consensus",
        description=f"AI Consensus resolved for transaction {payload.transaction_id}: {verdict.upper()} (score: {score:.2%})",
        resource_id=str(record.id),
        metadata={"verdict": verdict, "consensus_score": score}
    )

    return ConsensusResponse(
        id=record.id,
        transaction_id=record.transaction_id,
        decision_verdict=record.decision_verdict,
        consensus_score=record.consensus_score,
        vote_details=record.vote_details,
        created_at=record.created_at
    )

@router.get("/history", response_model=List[ConsensusResponse])
async def read_consensus_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("read:transactions"))
) -> List[ConsensusResponse]:
    """
    Lists historical AI agent voting consensus records.
    Requires 'read:transactions' permission.
    """
    consensus_repo = ConsensusRepository(db)
    records = await consensus_repo.list_consensus_history(limit=limit)

    return [
        ConsensusResponse(
            id=r.id,
            transaction_id=r.transaction_id,
            decision_verdict=r.decision_verdict,
            consensus_score=r.consensus_score,
            vote_details=r.vote_details,
            created_at=r.created_at
        )
        for r in records
    ]

@router.get("/reputations", response_model=Dict[str, float])
async def read_agent_reputations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("read:transactions"))
) -> Dict[str, float]:
    """
    Retrieves dynamic reputation scores calculated across historical decision alignments.
    Requires 'read:transactions' permission.
    """
    consensus_repo = ConsensusRepository(db)
    engine = DynamicConsensusEngine()

    past_db_votes = await consensus_repo.list_consensus_history(limit=50)
    past_votes = [
        {"decision_verdict": v.decision_verdict, "vote_details": v.vote_details}
        for v in past_db_votes
    ]

    # Dummy inputs to compile reputations
    _, _, details = engine.evaluate_consensus([], past_votes)
    return details.get("reputations", {})
