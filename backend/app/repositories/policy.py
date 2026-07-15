import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.governance import PolicyCheck, HumanReview

class PolicyRepository:
    """
    Handles database operations for PolicyCheck compliance logs and HumanReview overrides.
    """
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def save_policy_check(
        self,
        transaction_id: uuid.UUID,
        rule_id: str,
        status: str,
        details: dict
    ) -> PolicyCheck:
        """
        Saves a policy rule evaluation check row.
        """
        check_record = PolicyCheck(
            transaction_id=transaction_id,
            rule_id=rule_id,
            status=status,
            details=details
        )
        self.db.add(check_record)
        await self.db.commit()
        await self.db.refresh(check_record)
        return check_record

    async def list_violations(self, limit: int = 50) -> List[PolicyCheck]:
        """
        Lists historical policy failures (violations).
        """
        result = await self.db.execute(
            select(PolicyCheck)
            .where(PolicyCheck.status == "fail")
            .order_by(PolicyCheck.executed_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_policy_checks_history(self, limit: int = 50) -> List[PolicyCheck]:
        """
        Lists all run policy checks.
        """
        result = await self.db.execute(
            select(PolicyCheck)
            .order_by(PolicyCheck.executed_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_decision_override(
        self,
        transaction_id: uuid.UUID,
        reviewer_id: uuid.UUID,
        comments: str
    ) -> HumanReview:
        """
        Creates an administrative override logging review approval in database.
        """
        override_record = HumanReview(
            transaction_id=transaction_id,
            reviewer_id=reviewer_id,
            status="approved", # Override validates approval
            comments=f"Administrative Override: {comments}",
            reviewed_at=datetime.utcnow()
        )
        self.db.add(override_record)
        await self.db.commit()
        await self.db.refresh(override_record)
        return override_record
