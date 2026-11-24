import functools
import json
import logging
from typing import Any, Callable
from fastapi import Request, Response
from app.core.config import settings
import redis

logger = logging.getLogger("app.core.cache")

try:
    redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.warning(f"Could not connect to Redis for caching: {e}")
    redis_client = None


def cache_response(expire_seconds: int = 300) -> Callable[..., Any]:
    """
    Decorator to cache FastAPI endpoint responses in Redis.
    Derives cache key from the request path and query parameters.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Locate Request object in parameter signature
            request = kwargs.get("request")
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            # If no request object found or Redis is not connected, run function normally
            if not request or not redis_client:
                return await func(*args, **kwargs)

            # Generate unique cache key based on URL path and sorted query params
            query_params = sorted(list(request.query_params.items()))
            params_str = "&".join([f"{k}={v}" for k, v in query_params])
            cache_key = f"api_cache:{request.url.path}:{params_str}"

            try:
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    logger.debug(f"Cache Hit for key: {cache_key}")
                    return json.loads(cached_data)
            except Exception as e:
                logger.error(f"Error checking cache: {e}")

            logger.debug(f"Cache Miss for key: {cache_key}")
            result = await func(*args, **kwargs)

            try:
                # Save result JSON in Redis with expiry
                redis_client.setex(cache_key, expire_seconds, json.dumps(result))
            except Exception as e:
                logger.error(f"Error saving to cache: {e}")

            return result
        return wrapper
    return decorator


def invalidate_cache_prefix(prefix: str) -> None:
    """
    Invalidates all cache keys sharing a specific prefix pattern.
    Useful when fresh data is loaded via ETL.
    """
    if not redis_client:
        return
    try:
        keys = redis_client.keys(f"api_cache:{prefix}*")
        if keys:
            redis_client.delete(*keys)
            logger.info(f"Invalidated {len(keys)} cache keys matching prefix: {prefix}")
    except Exception as e:
        logger.error(f"Error invalidating cache: {e}")
