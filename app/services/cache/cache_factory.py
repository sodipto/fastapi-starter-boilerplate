from typing import Any

from redis.asyncio import Redis

from app.core.config import settings
from app.services.interfaces.cache_service_interface import ICacheService
from app.services.cache.in_memory_cache_service import InMemoryCacheService
from app.services.cache.redis_cache_service import RedisCacheService


# Singleton Redis client instance
_redis_client: Redis | None = None

# Singleton InMemory cache instance
_memory_cache: InMemoryCacheService | None = None

# Singleton Redis cache service instance
_redis_cache: RedisCacheService | None = None


async def get_redis_client() -> Redis:
    """
    Get or create a singleton Redis client.
    
    Returns:
        The Redis async client instance.
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False
        )
    return _redis_client


async def close_redis_client() -> None:
    """Close the Redis client connection."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None


def get_memory_cache() -> InMemoryCacheService:
    """
    Get or create a singleton InMemory cache service.
    
    Returns:
        The InMemoryCacheService instance.
    """
    global _memory_cache
    if _memory_cache is None:
        _memory_cache = InMemoryCacheService()
    return _memory_cache


async def get_cache_service() -> ICacheService:
    """
    Factory function to get the appropriate cache service based on configuration.
    Returns a singleton instance of the cache service.
    
    Returns:
        ICacheService: Either RedisCacheService or InMemoryCacheService
                      based on CACHE_TYPE environment variable.
    """
    global _redis_cache
    cache_type = settings.CACHE_TYPE.lower()
    
    if cache_type == "redis":
        if _redis_cache is None:
            redis_client = await get_redis_client()
            _redis_cache = RedisCacheService(redis_client)
        return _redis_cache
    else:
        # Default to in-memory cache
        return get_memory_cache()


async def init_cache_service() -> ICacheService:
    """
    Initialize the cache service during application startup.
    This should be called in the lifespan context.
    
    Returns:
        The initialized cache service.
    """
    cache_service = await get_cache_service()
    
    # Start cleanup task for in-memory cache
    if isinstance(cache_service, InMemoryCacheService):
        await cache_service.start_cleanup_task()
    
    return cache_service


async def shutdown_cache_service() -> None:
    """
    Shutdown the cache service during application shutdown.
    This should be called in the lifespan context.
    """
    global _memory_cache, _redis_client, _redis_cache
    
    # Stop cleanup task for in-memory cache
    if _memory_cache is not None:
        await _memory_cache.stop_cleanup_task()
        _memory_cache = None
    
    # Close Redis connection
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
    
    # Clear Redis cache service reference
    _redis_cache = None
