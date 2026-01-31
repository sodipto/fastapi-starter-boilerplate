from typing import Any

from fastapi import Request
from redis.asyncio import Redis

from app.core.config import settings
from app.services.interfaces.cache_service_interface import ICacheService
from app.services.cache.in_memory_cache_service import InMemoryCacheService
from app.services.cache.redis_cache_service import RedisCacheService


async def _create_redis_client() -> Redis:
    """Create a new Redis client instance."""
    return Redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=False
    )


async def init_cache_service() -> ICacheService:
    """
    Initialize and return the cache service during application startup.
    This should be called in the lifespan context and stored in app.state.
    
    Returns:
        The initialized cache service (singleton for the app lifecycle).
    """
    cache_type = settings.CACHE_TYPE.lower()
    
    if cache_type == "redis":
        redis_client = await _create_redis_client()
        cache_service = RedisCacheService(redis_client)
    else:
        cache_service = InMemoryCacheService()
        await cache_service.start_cleanup_task()
    
    return cache_service


async def shutdown_cache_service(cache_service: ICacheService) -> None:
    """
    Shutdown the cache service during application shutdown.
    This should be called in the lifespan context.
    
    Args:
        cache_service: The cache service instance from app.state.
    """
    if isinstance(cache_service, InMemoryCacheService):
        await cache_service.stop_cleanup_task()
    elif isinstance(cache_service, RedisCacheService):
        await cache_service.close()


async def get_cache_service(request: Request) -> ICacheService:
    """
    FastAPI dependency to get the cache service from app.state.
    Use with Depends(get_cache_service) in endpoints.
    
    Args:
        request: The FastAPI request object.
        
    Returns:
        The cache service instance.
        
    Raises:
        RuntimeError: If cache service is not initialized.
    """
    cache_service = getattr(request.app.state, "cache_service", None)
    if cache_service is None:
        raise RuntimeError("Cache service not initialized. Check app lifespan.")
    return cache_service
