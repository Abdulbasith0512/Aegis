import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.governance import ConsensusVote

class ConsensusRepository:
    """
    Handles database operations for ConsensusVote logs.
    """
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def save_consensus_vote(
        self,
        transaction_id: uuid.UUID,
        decision_verdict: str,
        consensus_score: float,
        vote_details: Dict[str, Any]
    ) -> ConsensusVote:
        """
        Saves a finalized consensus decision record.
        """
        record = ConsensusVote(
            transaction_id=transaction_id,
            decision_verdict=decision_verdict,
            consensus_score=consensus_score,
            vote_details=vote_details
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def get_consensus_by_transaction_id(self, transaction_id: uuid.UUID) -> Optional[ConsensusVote]:
        """
        Retrieves the consensus evaluation for a transaction.
        """
        result = await self.db.execute(
            select(ConsensusVote).where(ConsensusVote.transaction_id == transaction_id)
        )
        return result.scalars().first()

    async def list_consensus_history(self, limit: int = 50) -> List[ConsensusVote]:
        """
        Lists historical consensus evaluations.
        """
        result = await self.db.execute(
            select(ConsensusVote)
            .order_by(ConsensusVote.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
