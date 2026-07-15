from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from redis.asyncio import Redis
from qdrant_client import QdrantClient
from typing import Dict, Any
from app.core.dependencies import get_db, get_cache, get_vector_db

router: APIRouter = APIRouter(prefix="/health", tags=["System Control"])

@router.get("", response_model=Dict[str, Any])
async def check_health(
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_cache),
    qdrant: QdrantClient = Depends(get_vector_db)
) -> Dict[str, Any]:
    """
    Executes real-time ping connections to backing data storage systems.
    Returns:
        Dict[str, Any]: Status breakdown map.
    """
    health_status: Dict[str, Any] = {
        "status": "healthy",
        "postgres": "unknown",
        "redis": "unknown",
        "qdrant": "unknown"
    }

    # 1. PostgreSQL check
    try:
        await db.execute(text("SELECT 1"))
        health_status["postgres"] = "connected"
    except Exception as e:
        health_status["postgres"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # 2. Redis check
    try:
        await redis.ping()
        health_status["redis"] = "connected"
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # 3. Qdrant check
    try:
        # qdrant client is thread-safe sync call
        qdrant.get_collections()
        health_status["qdrant"] = "connected"
    except Exception as e:
        health_status["qdrant"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    if health_status["status"] != "healthy":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return health_status
