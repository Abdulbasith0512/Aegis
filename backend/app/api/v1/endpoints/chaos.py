from fastapi import APIRouter
from typing import Dict, List

router: APIRouter = APIRouter(prefix="/chaos", tags=["Chaos Engine"])

@router.get("/scenarios", response_model=List[Dict[str, str]])
async def list_chaos_scenarios() -> List[Dict[str, str]]:
    """
    Get active chaos test scenarios (Scaffolding).
    """
    return [
        {"id": "geo-drift", "status": "inactive", "target": "Fraud Agent"},
        {"id": "network-latency-simulation", "status": "inactive", "target": "Device Agent"}
    ]
