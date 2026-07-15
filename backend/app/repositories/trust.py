import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.governance import TrustScore

class TrustRepository:
    """
    Handles database operations for the TrustScore entities.
    """
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def save_trust_score(
        self,
        transaction_id: uuid.UUID,
        score: int,
        weights: dict,
        reasons: dict
    ) -> TrustScore:
        """
        Persists a newly computed Trust Score to the database.
        """
        trust_record = TrustScore(
            transaction_id=transaction_id,
            score=score,
            weights_configuration=weights,
            reasons=reasons
        )
        self.db.add(trust_record)
        await self.db.commit()
        await self.db.refresh(trust_record)
        return trust_record

    async def get_trust_by_id(self, trust_id: uuid.UUID) -> Optional[TrustScore]:
        """
        Retrieves a Trust Score record by its UUID.
        """
        result = await self.db.execute(
            select(TrustScore).where(TrustScore.id == trust_id)
        )
        return result.scalars().first()

    async def get_trust_by_transaction_id(self, transaction_id: uuid.UUID) -> Optional[TrustScore]:
        """
        Retrieves a Trust Score record associated with a transaction.
        """
        result = await self.db.execute(
            select(TrustScore).where(TrustScore.transaction_id == transaction_id)
        )
        return result.scalars().first()

    async def list_trust_history(self, limit: int = 50) -> List[TrustScore]:
        """
        Fetches recent Trust Score results for visualization trends.
        """
        result = await self.db.execute(
            select(TrustScore)
            .order_by(TrustScore.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
