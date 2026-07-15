import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.explainability import ExplanationCreateRequest, ExplanationResponse
from app.repositories.explainability import ExplainabilityRepository
from app.repositories.audit import AuditRepository
from app.services.explainability import DefaultExplainabilityEngine
from app.models.users import User

router: APIRouter = APIRouter(prefix="/explainability", tags=["Explainability"])

@router.post("/generate", response_model=ExplanationResponse, status_code=status.HTTP_201_CREATED)
async def generate_explanation(
    payload: ExplanationCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("write:policies"))
) -> ExplanationResponse:
    """
    Generates and persists an explainability trace (SHAP metrics, timeline, graphs) for an AI decision.
    Requires 'write:policies' permission.
    """
    explain_repo = ExplainabilityRepository(db)
    audit_repo = AuditRepository(db)
    engine = DefaultExplainabilityEngine()

    # Compile explainability data points
    res = engine.generate_explanation(payload.prediction_id, payload.agent_traces)

    # Save to PostgreSQL
    record = await explain_repo.save_explanation(
        prediction_id=res["prediction_id"],
        human_readable=res["human_readable"],
        machine_readable=res["machine_readable"],
        decision_timeline=res["decision_timeline"],
        evidence_graph=res["evidence_graph"],
        feature_importance=res["feature_importance"],
        confidence_reasoning=res["confidence_reasoning"],
        supporting_policies=res["supporting_policies"],
        contributing_agents=res["contributing_agents"],
        explainability_score=res["explainability_score"],
        explanation_vector=res["explanation_vector"]
    )

    # Log to cryptographic audit ledger
    await audit_repo.log_action(
        actor_id=current_user.id,
        action_type="generate_explanation",
        description=f"Explainability traces generated for prediction {payload.prediction_id}",
        resource_id=str(record.id)
    )

    # Reconstruct lists from saved JSON structures
    timeline_list = record.decision_timeline.get("events", [])
    graph_data = record.evidence_graph
    policies_list = record.supporting_policies.get("policies", [])
    agents_list = record.contributing_agents.get("agents", [])

    return ExplanationResponse(
        id=record.id,
        prediction_id=record.prediction_id,
        human_readable=record.human_readable,
        machine_readable=record.machine_readable,
        decision_timeline=timeline_list,
        evidence_graph=graph_data,
        feature_importance=record.feature_importance,
        confidence_reasoning=record.confidence_reasoning,
        supporting_policies=policies_list,
        contributing_agents=agents_list,
        explainability_score=record.explainability_score,
        explanation_vector=record.explanation_vector,
        created_at=record.created_at
    )

@router.get("/decisions/{prediction_id}", response_model=ExplanationResponse)
async def get_decision_explanation(
    prediction_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("read:transactions"))
) -> ExplanationResponse:
    """
    Get explainability metrics (SHAP, timeline, graphs) for a specific agent decision.
    Requires 'read:transactions' permission.
    """
    explain_repo = ExplainabilityRepository(db)
    record = await explain_repo.get_explanation_by_prediction_id(prediction_id)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Explainability record not found for the specified prediction."
        )

    timeline_list = record.decision_timeline.get("events", [])
    graph_data = record.evidence_graph
    policies_list = record.supporting_policies.get("policies", [])
    agents_list = record.contributing_agents.get("agents", [])

    return ExplanationResponse(
        id=record.id,
        prediction_id=record.prediction_id,
        human_readable=record.human_readable,
        machine_readable=record.machine_readable,
        decision_timeline=timeline_list,
        evidence_graph=graph_data,
        feature_importance=record.feature_importance,
        confidence_reasoning=record.confidence_reasoning,
        supporting_policies=policies_list,
        contributing_agents=agents_list,
        explainability_score=record.explainability_score,
        explanation_vector=record.explanation_vector,
        created_at=record.created_at
    )

@router.get("/history", response_model=List[ExplanationResponse])
async def read_explanations_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("read:transactions"))
) -> List[ExplanationResponse]:
    """
    Lists historical explainability reports.
    Requires 'read:transactions' permission.
    """
    explain_repo = ExplainabilityRepository(db)
    records = await explain_repo.list_explanations_history(limit=limit)

    return [
        ExplanationResponse(
            id=r.id,
            prediction_id=r.prediction_id,
            human_readable=r.human_readable,
            machine_readable=r.machine_readable,
            decision_timeline=r.decision_timeline.get("events", []),
            evidence_graph=r.evidence_graph,
            feature_importance=r.feature_importance,
            confidence_reasoning=r.confidence_reasoning,
            supporting_policies=r.supporting_policies.get("policies", []),
            contributing_agents=r.contributing_agents.get("agents", []),
            explainability_score=r.explainability_score,
            explanation_vector=r.explanation_vector,
            created_at=r.created_at
        )
        for r in records
    ]
