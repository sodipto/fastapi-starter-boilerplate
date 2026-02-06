"""
Cache Service Resource Provider

Provides a declarative, lifecycle-managed cache service using dependency-injector's
Resource pattern. This eliminates runtime DI overrides and makes the cache service
fully testable through proper container configuration.
"""
from typing import AsyncIterator
from redis.asyncio import Redis

from app.core.config import settings
from app.services.interfaces.cache_service_interface import ICacheService
from app.services.cache.in_memory_cache_service import InMemoryCacheService
from app.services.cache.redis_cache_service import RedisCacheService


async def cache_service_resource() -> AsyncIterator[ICacheService]:
    """
    Async resource that manages cache service lifecycle declaratively.
    
    This generator pattern is used by dependency-injector's Resource provider
    to properly initialize and shutdown the cache service as part of the
    container's resource lifecycle.
    
    Yields:
        Initialized cache service instance.
        
    Usage in Container:
        cache_service = providers.Resource(cache_service_resource)
        
    Benefits:
        - No runtime override() calls needed
        - Proper async initialization/shutdown
        - Testable via container.cache_service.override()
        - Declarative and predictable lifecycle
    """
    cache_service: ICacheService
    cache_type = settings.CACHE_TYPE.lower()
    
    # Initialize based on configuration
    if cache_type == "redis":
        redis_client = await Redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False
        )
        cache_service = RedisCacheService(redis_client)
    else:
        cache_service = InMemoryCacheService()
        await cache_service.start_cleanup_task()
    
    try:
        yield cache_service
    finally:
        # Cleanup on container shutdown
        if isinstance(cache_service, InMemoryCacheService):
            await cache_service.stop_cleanup_task()
        elif isinstance(cache_service, RedisCacheService):
            await cache_service.close()
