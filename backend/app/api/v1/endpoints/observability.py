from typing import Dict, Any, List
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.observability import ObservabilitySummaryResponse, TelemetryRecordRequest
from app.services.observability import ObservabilityService
from app.models.users import User

router: APIRouter = APIRouter(prefix="/observability", tags=["AI Observability Platform"])

@router.get("/metrics")
async def get_prometheus_metrics() -> Response:
    """
    Exposes raw Grafana-ready metric parameters formatted for Prometheus.
    Accessible without credentials for Prometheus scraper daemons.
    """
    service = ObservabilityService()
    content, media_type = service.generate_prometheus_metrics()
    return Response(content=content, media_type=media_type)

@router.get("/summary", response_model=ObservabilitySummaryResponse)
async def get_observability_dashboard_summary(
    current_user: User = Depends(require_permission("read:transactions"))
) -> ObservabilitySummaryResponse:
    """
    Retrieves unified system hardware and agent-level telemetry metrics.
    Requires 'read:transactions' permission.
    """
    service = ObservabilityService()
    res = service.get_observability_summary()
    return ObservabilitySummaryResponse(**res)

@router.get("/health", response_model=Dict[str, Any])
async def check_agents_observability_health(
    current_user: User = Depends(require_permission("read:transactions"))
) -> Dict[str, Any]:
    """
    Checks agent online/offline status signals.
    Requires 'read:transactions' permission.
    """
    # Simply check if agents are flagged healthy in the Prometheus client manager
    service = ObservabilityService()
    summary = service.get_observability_summary()
    
    agent_health_states = {}
    for am in summary["agent_metrics"]:
        agent_health_states[am["agent_name"]] = "healthy" if am["health_status"] == 1 else "offline"

    return {
        "status": "healthy",
        "timestamp": float(Response().headers.get("date", 0.0)),
        "agents": agent_health_states
    }

@router.post("/record", status_code=status.HTTP_201_CREATED)
async def record_telemetry_event(
    payload: TelemetryRecordRequest,
    current_user: User = Depends(require_permission("write:policies"))
) -> Dict[str, str]:
    """
    Submits a mock simulation telemetry check to active metrics gauges.
    Requires 'write:policies' permission.
    """
    service = ObservabilityService()
    service.record_agent_execution(
        agent_name=payload.agent_name,
        duration_seconds=payload.duration_seconds,
        tokens_prompt=payload.tokens_prompt,
        tokens_completion=payload.tokens_completion,
        confidence=payload.confidence,
        trust_score=payload.trust_score,
        error_occurred=payload.error_occurred,
        drift=payload.drift,
        hallucination_rate=payload.hallucination_rate
    )
    return {"message": "Telemetry record registered successfully."}
