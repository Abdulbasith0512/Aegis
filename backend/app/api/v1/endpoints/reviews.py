import uuid
from typing import List, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.review import ReviewAssignRequest, ReviewActionRequest, ReviewQueueResponse, ReviewDetailResponse
from app.repositories.review import ReviewRepository
from app.repositories.audit import AuditRepository
from app.models.users import User

router: APIRouter = APIRouter(prefix="/reviews", tags=["Human Review Center"])

@router.get("/queue", response_model=List[ReviewQueueResponse])
async def get_review_queue(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("read:transactions"))
) -> List[ReviewQueueResponse]:
    """
    Get list of pending and escalated compliance reviews.
    Requires 'read:transactions' permission.
    """
    repo = ReviewRepository(db)
    records = await repo.list_review_queue()

    response = []
    for r in records:
        # Resolve customer name
        customer_name = "Unknown Customer"
        if r.transaction and r.transaction.account and r.transaction.account.customer:
            c = r.transaction.account.customer
            customer_name = f"{c.first_name} {c.last_name}"

        # Resolve trust score
        trust = 100.0
        if r.transaction and r.transaction.trust_scores:
            trust = r.transaction.trust_scores[0].trust_score

        # Resolve reviewer name
        reviewer_name = None
        if r.reviewer:
            reviewer_name = f"{r.reviewer.first_name} {r.reviewer.last_name}"

        # Check if SLA deadline is breached
        is_sla_breached = datetime.utcnow() > r.sla_deadline

        response.append(ReviewQueueResponse(
            id=r.id,
            transaction_id=r.transaction_id,
            amount=float(r.transaction.amount) if r.transaction else 0.0,
            currency=r.transaction.currency if r.transaction else "USD",
            customer_name=customer_name,
            trust_score=trust,
            status=r.status,
            reviewer_name=reviewer_name,
            assigned_at=r.assigned_at,
            sla_deadline=r.sla_deadline,
            is_sla_breached=is_sla_breached
        ))
    return response

@router.get("/history", response_model=List[ReviewQueueResponse])
async def get_review_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("read:transactions"))
) -> List[ReviewQueueResponse]:
    """
    Get resolved audit history log.
    Requires 'read:transactions' permission.
    """
    repo = ReviewRepository(db)
    records = await repo.list_review_history()

    response = []
    for r in records:
        customer_name = "Unknown Customer"
        if r.transaction and r.transaction.account and r.transaction.account.customer:
            c = r.transaction.account.customer
            customer_name = f"{c.first_name} {c.last_name}"

        trust = 100.0
        if r.transaction and r.transaction.trust_scores:
            trust = r.transaction.trust_scores[0].trust_score

        reviewer_name = None
        if r.reviewer:
            reviewer_name = f"{r.reviewer.first_name} {r.reviewer.last_name}"

        is_sla_breached = r.reviewed_at > r.sla_deadline if r.reviewed_at else False

        response.append(ReviewQueueResponse(
            id=r.id,
            transaction_id=r.transaction_id,
            amount=float(r.transaction.amount) if r.transaction else 0.0,
            currency=r.transaction.currency if r.transaction else "USD",
            customer_name=customer_name,
            trust_score=trust,
            status=r.status,
            reviewer_name=reviewer_name,
            assigned_at=r.assigned_at,
            sla_deadline=r.sla_deadline,
            is_sla_breached=is_sla_breached
        ))
    return response

@router.get("/{review_id}", response_model=ReviewDetailResponse)
async def get_review_details(
    review_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("read:transactions"))
) -> ReviewDetailResponse:
    """
    Fetch comprehensive audit logs details including dynamic graphs, timelines, and compliance rules status.
    Requires 'read:transactions' permission.
    """
    repo = ReviewRepository(db)
    r = await repo.get_detailed_review(review_id)
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Human Review record not found."
        )

    # 1. Resolve Customer
    customer_name = "Unknown Customer"
    if r.transaction and r.transaction.account and r.transaction.account.customer:
        c = r.transaction.account.customer
        customer_name = f"{c.first_name} {c.last_name}"

    # 2. Resolve Trust score details
    trust = 100.0
    warnings = []
    if r.transaction and r.transaction.trust_scores:
        t_record = r.transaction.trust_scores[0]
        trust = t_record.trust_score
        warnings = t_record.details.get("warnings", []) if t_record.details else []

    # 3. Resolve Explainability Traces
    exp_human = "No explanation trace logged for this prediction."
    exp_timeline = []
    exp_graph = {"nodes": [], "edges": []}
    exp_shap = {}

    if r.transaction and r.transaction.predictions:
        p_record = r.transaction.predictions[0]
        if p_record.explanations:
            e_record = p_record.explanations[0]
            exp_human = e_record.human_readable
            exp_timeline = e_record.decision_timeline.get("events", [])
            exp_graph = e_record.evidence_graph
            exp_shap = e_record.feature_importance

    # 4. Resolve compliance policy results
    policy_checks = []
    if r.transaction and r.transaction.policy_checks:
        for pc in r.transaction.policy_checks:
            policy_checks.append({
                "rule_id": pc.rule_id,
                "status": pc.status,
                "details": pc.details
            })

    is_sla_breached = (r.reviewed_at > r.sla_deadline) if r.reviewed_at else (datetime.utcnow() > r.sla_deadline)

    return ReviewDetailResponse(
        id=r.id,
        transaction_id=r.transaction_id,
        amount=float(r.transaction.amount) if r.transaction else 0.0,
        currency=r.transaction.currency if r.transaction else "USD",
        customer_name=customer_name,
        status=r.status,
        comments=r.comments,
        assigned_at=r.assigned_at,
        reviewed_at=r.reviewed_at,
        sla_deadline=r.sla_deadline,
        is_sla_breached=is_sla_breached,
        trust_score=trust,
        trust_warnings=warnings,
        explanation_human=exp_human,
        explanation_timeline=exp_timeline,
        explanation_graph=exp_graph,
        explanation_shap=exp_shap,
        policy_checks=policy_checks
    )

@router.post("/{review_id}/assign", response_model=Dict[str, str])
async def assign_case_auditor(
    review_id: uuid.UUID,
    payload: ReviewAssignRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("write:policies"))
) -> Dict[str, str]:
    """
    Assign compliance auditor reviewer.
    Requires 'write:policies' permission.
    """
    repo = ReviewRepository(db)
    audit_repo = AuditRepository(db)

    # Verify target reviewer exists
    reviewer = await db.get(User, payload.reviewer_id)
    if not reviewer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target reviewer user account not found."
        )

    res = await repo.assign_reviewer(review_id, payload.reviewer_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_440_NOT_FOUND,
            detail="Case review not found."
        )

    # Audit log entry
    await audit_repo.log_action(
        actor_id=current_user.id,
        action_type="assign_reviewer",
        description=f"Case {review_id} assigned to reviewer {reviewer.first_name} {reviewer.last_name}",
        resource_id=str(review_id)
    )

    return {"message": "Auditor assigned successfully."}

@router.post("/{review_id}/action", response_model=Dict[str, str])
async def submit_case_action(
    review_id: uuid.UUID,
    payload: ReviewActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("write:policies"))
) -> Dict[str, str]:
    """
    Submits auditor decisions: Approve, Reject (Decline), or Escalate.
    Requires 'write:policies' permission.
    """
    repo = ReviewRepository(db)
    audit_repo = AuditRepository(db)

    res = await repo.submit_review_verdict(review_id, payload.status, payload.comments)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case review not found."
        )

    # Log action to cryptographic ledger
    await audit_repo.log_action(
        actor_id=current_user.id,
        action_type=f"review_{payload.status}",
        description=f"Case {review_id} resolved with status {payload.status.upper()}",
        resource_id=str(review_id),
        metadata={"comments": payload.comments}
    )

    return {"message": f"Auditor action '{payload.status}' submitted successfully."}
