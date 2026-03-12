"""Cache service for Redis operations."""

import json
from typing import Optional, Any
from redis import asyncio as aioredis
from config.config import get_settings

settings = get_settings()

_redis: Optional[aioredis.Redis] = None


async def init_redis(redis_url: str = None):
    """Initialize Redis connection."""
    global _redis
    url = redis_url or settings.REDIS_URL
    _redis = await aioredis.from_url(url)


async def get_cache(key: str) -> Optional[Any]:
    """Get value from cache."""
    if _redis:
        cached = await _redis.get(key)
        return cached.decode() if cached else None
    return None


async def set_cache(key: str, value: Any, expire_seconds: int = 60):
    """Set value in cache with expiration."""
    if _redis:
        await _redis.set(key, json.dumps(value), ex=expire_seconds)


async def close_redis():
    """Close Redis connection."""
    global _redis
    if _redis:
        await _redis.close()
        _redis = None


__all__ = ["init_redis", "get_cache", "set_cache", "close_redis"]