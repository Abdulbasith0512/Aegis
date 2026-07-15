from fastapi import APIRouter
from typing import Dict, List

router: APIRouter = APIRouter(prefix="/compliance", tags=["Compliance"])

@router.get("/rules", response_model=List[Dict[str, str]])
async def get_compliance_rules() -> List[Dict[str, str]]:
    """
    Get active regulatory compliance policies (Scaffolding).
    """
    return [
        {"id": "rule-1", "regulation": "GDPR-Art22", "description": "Automated decision limitations"},
        {"id": "rule-2", "regulation": "Patriot-Sec326", "description": "Identity verification (KYC)"}
    ]
