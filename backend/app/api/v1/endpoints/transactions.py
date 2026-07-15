from fastapi import APIRouter
from typing import Dict, List

router: APIRouter = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("/", response_model=List[Dict[str, str]])
async def list_transactions() -> List[Dict[str, str]]:
    """
    List transactions processed and supervised by AegisAI (Scaffolding).
    """
    return []
