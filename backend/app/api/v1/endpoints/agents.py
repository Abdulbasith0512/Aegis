from fastapi import APIRouter
from typing import Dict, List

router: APIRouter = APIRouter(prefix="/agents", tags=["AI Agents"])

@router.get("/", response_model=List[Dict[str, str]])
async def list_agents() -> List[Dict[str, str]]:
    """
    List supervised banking AI agents (Scaffolding).
    """
    return [
        {"id": "fraud-agent", "status": "active"},
        {"id": "aml-agent", "status": "active"},
        {"id": "kyc-agent", "status": "active"},
        {"id": "device-agent", "status": "active"},
        {"id": "behavior-agent", "status": "active"},
        {"id": "compliance-agent", "status": "active"}
    ]
