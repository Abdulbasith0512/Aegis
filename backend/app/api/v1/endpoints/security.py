from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from app.services.security_layer import security_service
from app.core.dependencies import get_current_user
from app.models.users import User

router = APIRouter(prefix="/security", tags=["security"])

class ScanRequest(BaseModel):
    text: str = Field(..., description="The prompt or text snippet to validate.")

class ScanResponse(BaseModel):
    is_blocked: bool
    rules_fired: List[str]
    sanitized: Optional[str]

class ConfigUpdateRequest(BaseModel):
    prompt_injection_enabled: Optional[bool] = None
    pii_detection_enabled: Optional[bool] = None
    secret_detection_enabled: Optional[bool] = None
    jailbreak_detection_enabled: Optional[bool] = None
    input_validation_enabled: Optional[bool] = None
    output_validation_enabled: Optional[bool] = None
    max_prompt_length: Optional[int] = None

@router.get("/metrics")
async def get_security_metrics(user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Returns threat counts and block summaries for the security dashboard.
    """
    total_blocked = len(security_service.threat_logs)
    injection_count = sum(1 for log in security_service.threat_logs if log["match_type"] == "prompt_injection")
    jailbreak_count = sum(1 for log in security_service.threat_logs if log["match_type"] == "jailbreak")
    pii_count = sum(1 for log in security_service.threat_logs if log["match_type"] == "pii_leak")
    secret_count = sum(1 for log in security_service.threat_logs if log["match_type"] == "secret_leak")

    return {
        "totalBlocked": total_blocked,
        "promptInjections": injection_count,
        "jailbreaks": jailbreak_count,
        "piiViolations": pii_count,
        "secretLeaks": secret_count,
        "activeRules": security_service.config,
    }

@router.get("/logs")
async def get_threat_logs(user: User = Depends(get_current_user)) -> List[Dict[str, Any]]:
    """
    Returns list of the latest threat audit records.
    """
    return security_service.threat_logs

@router.post("/scan", response_model=ScanResponse)
async def scan_text_payload(
    payload: ScanRequest,
    request: Request,
    user: User = Depends(get_current_user)
) -> ScanResponse:
    """
    Runs direct testing scanner on custom text strings. Used by the developers sandbox.
    """
    actor_ip = request.client.host if request.client else "127.0.0.1"
    is_blocked, rules, sanitized = security_service.scan_prompt(payload.text, actor_ip)
    return ScanResponse(
        is_blocked=is_blocked,
        rules_fired=rules,
        sanitized=sanitized
    )

@router.post("/rules")
async def update_security_rules(
    rules: ConfigUpdateRequest,
    user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dynamically updates active security firewall features.
    """
    update_data = {k: v for k, v in rules.model_dump().items() if v is not None}
    security_service.update_config(update_data)
    return {
        "status": "success",
        "message": "AI Security Layer configuration updated.",
        "config": security_service.config
    }
