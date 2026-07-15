from fastapi import APIRouter
from typing import Dict
from app.config.loader import settings

router: APIRouter = APIRouter(prefix="/version", tags=["System Control"])

@router.get("", response_model=Dict[str, str])
async def get_version() -> Dict[str, str]:
    """
    Returns application system and meta configurations version profiles.
    """
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }
