import time
import logging
from typing import Dict, List, Tuple, Any, Optional
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger("app.middleware.rate_limiting")


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Applies rate limiting of 100 requests per minute per client IP address.
    Uses Redis as the primary rate limit store and falls back to memory if Redis is unavailable.
    """
    def __init__(self, app: Any = None):
        super().__init__(app)
        self.redis_client = None
        self.memory_store: Dict[str, List[float]] = {}  # Fallback: IP -> [timestamps]
        
        # Connect to Redis
        try:
            self.redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            logger.info("Rate limiter successfully connected to Redis cache.")
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}. Falling back to in-memory rate limiting.")

    async def _is_rate_limited_memory(self, client_ip: str) -> bool:
        """
        In-memory token bucket/sliding window fallback algorithm.
        """
        now = time.time()
        window = 60.0
        limit = 100
        
        if client_ip not in self.memory_store:
            self.memory_store[client_ip] = [now]
            return False
            
        timestamps = self.memory_store[client_ip]
        # Filter timestamps outside window
        timestamps = [ts for ts in timestamps if now - ts < window]
        
        if len(timestamps) >= limit:
            self.memory_store[client_ip] = timestamps
            return True
            
        timestamps.append(now)
        self.memory_store[client_ip] = timestamps
        return False

    async def _is_rate_limited_redis(self, client_ip: str) -> bool:
        """
        Redis sliding window or rate counter using INCR and EXPIRE.
        """
        if not self.redis_client:
            return await self._is_rate_limited_memory(client_ip)
            
        key = f"rate_limit:{client_ip}"
        limit = 100
        
        try:
            current_requests = await self.redis_client.get(key)
            if current_requests and int(current_requests) >= limit:
                return True
                
            async with self.redis_client.pipeline(transaction=True) as pipe:
                await pipe.incr(key)
                await pipe.expire(key, 60)
                await pipe.execute()
            return False
        except Exception as e:
            logger.error(f"Redis rate limiter failed: {e}. Falling back to memory.")
            return await self._is_rate_limited_memory(client_ip)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for API docs/spec endpoints
        if request.url.path in [settings.DOCS_URL, settings.REDOC_URL, "/openapi.json", "/api/v1/health"]:
            return await call_next(request)
            
        is_limited = await self._is_rate_limited_redis(client_ip)
        if is_limited:
            logger.warning(f"Rate limit exceeded for client IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Maximum 100 requests per minute allowed."
                },
                headers={"Retry-After": "60"}
            )
            
        return await call_next(request)
