import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.governance import Explanation

class ExplainabilityRepository:
    """
    Handles database operations for the Explanation entities.
    """
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def save_explanation(
        self,
        prediction_id: uuid.UUID,
        human_readable: str,
        machine_readable: Dict[str, Any],
        decision_timeline: Dict[str, Any],
        evidence_graph: Dict[str, Any],
        feature_importance: Dict[str, Any],
        confidence_reasoning: str,
        supporting_policies: Dict[str, Any],
        contributing_agents: Dict[str, Any],
        explainability_score: float,
        explanation_vector: Optional[List[float]] = None
    ) -> Explanation:
        """
        Persists a newly generated Explainability metadata record to the database.
        """
        explanation_record = Explanation(
            prediction_id=prediction_id,
            human_readable=human_readable,
            machine_readable=machine_readable,
            decision_timeline=decision_timeline,
            evidence_graph=evidence_graph,
            feature_importance=feature_importance,
            confidence_reasoning=confidence_reasoning,
            supporting_policies=supporting_policies,
            contributing_agents=contributing_agents,
            explainability_score=explainability_score,
            explanation_vector=explanation_vector
        )
        self.db.add(explanation_record)
        await self.db.commit()
        await self.db.refresh(explanation_record)
        return explanation_record

    async def get_explanation_by_prediction_id(self, prediction_id: uuid.UUID) -> Optional[Explanation]:
        """
        Retrieves the Explainability record associated with a prediction.
        """
        result = await self.db.execute(
            select(Explanation).where(Explanation.prediction_id == prediction_id)
        )
        return result.scalars().first()

    async def list_explanations_history(self, limit: int = 50) -> List[Explanation]:
        """
        Fetches historical Explainability summaries.
        """
        result = await self.db.execute(
            select(Explanation)
            .order_by(Explanation.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
