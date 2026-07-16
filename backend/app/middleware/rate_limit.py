import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.database.database import get_redis

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding window rate limiting middleware using Redis.
    Limits request rates based on client IP or authenticated JWT user subject.
    """

    def __init__(
        self,
        app,
        limit: int = 60,         # Requests per window
        window_sec: int = 60,    # Sliding window size in seconds
    ) -> None:
        super().__init__(app)
        self.limit = limit
        self.window_sec = window_sec

    async def dispatch(self, request: Request, call_next):
        # Exclude documentation or health endpoints
        path = request.url.path
        if path.startswith("/docs") or path.startswith("/openapi") or path.startswith("/redoc") or path == "/health":
            return await call_next(request)

        # Identify client (authenticated user or plain IP)
        client_key = request.headers.get("x-user-id") or request.client.host
        redis_key = f"rate_limit:{client_key}:{path}"

        # Connect to Redis
        try:
            redis_gen = get_redis()
            redis = await redis_gen.__anext__()
            
            now = time.time()
            clear_before = now - self.window_sec

            # Perform Redis pipeline transaction for sliding window
            pipe = redis.pipeline()
            # Remove keys outside current window
            pipe.zremrangebyscore(redis_key, 0, clear_before)
            # Add current request score/timestamp
            pipe.zadd(redis_key, {str(now): now})
            # Count elements inside current window
            pipe.zcard(redis_key)
            # Set key TTL to window size
            pipe.expire(redis_key, self.window_sec)

            results = await pipe.execute()
            request_count = results[2]

            if request_count > self.limit:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please slow down and try again later."}
                )

        except Exception as e:
            # Safe fall-through on Redis failure to preserve availability
            pass

        return await call_next(request)
