import json
from typing import Any

from redis.asyncio import Redis

from app.services.interfaces.cache_service_interface import ICacheService


class RedisCacheService(ICacheService):
    """
    Redis-based cache implementation using redis.asyncio client.
    Uses JSON serialization for storing values.
    Thread-safe for async operations.
    """

    # Key prefix for sliding expiration metadata
    EXPIRATION_META_PREFIX = "__cache_meta:"

    def __init__(self, redis_client: Redis) -> None:
        """
        Initialize the Redis cache service.
        
        Args:
            redis_client: The Redis async client instance (singleton).
        """
        self._redis = redis_client

    async def get(self, key: str) -> Any | None:
        """
        Retrieve a value from the cache.
        
        Args:
            key: The cache key to retrieve.
            
        Returns:
            The cached value if found, None otherwise.
        """
        value = await self._redis.get(key)
        if value is None:
            return None
        
        # Refresh the expiration if sliding expiration is set
        await self._refresh_if_sliding(key)
        
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # Return raw value if not JSON
            return value.decode() if isinstance(value, bytes) else value

    async def set(
        self,
        key: str,
        value: Any,
        sliding_expiration: int | None = None
    ) -> None:
        """
        Store a value in the cache.
        
        Args:
            key: The cache key.
            value: The value to cache (will be JSON serialized).
            sliding_expiration: Optional expiration time in seconds.
        """
        serialized_value = json.dumps(value)
        
        if sliding_expiration is not None:
            # Store the value with expiration
            await self._redis.setex(key, sliding_expiration, serialized_value)
            
            # Store the sliding expiration metadata
            meta_key = f"{self.EXPIRATION_META_PREFIX}{key}"
            await self._redis.setex(meta_key, sliding_expiration, str(sliding_expiration))
        else:
            # Store without expiration
            await self._redis.set(key, serialized_value)
            
            # Remove any existing metadata
            meta_key = f"{self.EXPIRATION_META_PREFIX}{key}"
            await self._redis.delete(meta_key)

    async def increment(self, key: str, delta: int = 1, ttl: int | None = None) -> int:
        """
        Atomically increment a value in the cache.
        
        Args:
            key: The cache key.
            delta: The amount to increment by.
            ttl: Optional time to live in seconds if the key is created.
            
        Returns:
            The new value.
        """
        value = await self._redis.incrby(key, delta)
        if ttl is not None and value == delta:
            await self._redis.expire(key, ttl)
        return value

    async def _refresh_if_sliding(self, key: str) -> None:
        """
        Refresh the expiration time if sliding expiration is set.
        
        Args:
            key: The cache key.
        """
        meta_key = f"{self.EXPIRATION_META_PREFIX}{key}"
        sliding_expiration = await self._redis.get(meta_key)
        
        if sliding_expiration is not None:
            try:
                ttl = int(sliding_expiration)
                await self._redis.expire(key, ttl)
                await self._redis.expire(meta_key, ttl)
            except (ValueError, TypeError):
                pass

    async def refresh(self, key: str) -> bool:
        """
        Refresh the expiration time for a cache entry.
        
        Args:
            key: The cache key to refresh.
            
        Returns:
            True if the key was found and refreshed, False otherwise.
        """
        exists = await self._redis.exists(key)
        if not exists:
            return False
        
        meta_key = f"{self.EXPIRATION_META_PREFIX}{key}"
        sliding_expiration = await self._redis.get(meta_key)
        
        if sliding_expiration is not None:
            try:
                ttl = int(sliding_expiration)
                await self._redis.expire(key, ttl)
                await self._redis.expire(meta_key, ttl)
                return True
            except (ValueError, TypeError):
                pass
        
        return True

    async def remove(self, key: str) -> bool:
        """
        Remove a value from the cache.
        
        Args:
            key: The cache key to remove.
            
        Returns:
            True if the key was found and removed, False otherwise.
        """
        meta_key = f"{self.EXPIRATION_META_PREFIX}{key}"
        deleted = await self._redis.delete(key, meta_key)
        return deleted > 0

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.
        
        Args:
            key: The cache key to check.
            
        Returns:
            True if the key exists, False otherwise.
        """
        return await self._redis.exists(key) > 0

    async def clear(self) -> None:
        """
        Clear all entries from the cache.
        Warning: This uses FLUSHDB which clears the entire database.
        In production, consider using a key prefix pattern instead.
        """
        await self._redis.flushdb()

    async def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary containing cache statistics.
        """
        info = await self._redis.info("keyspace")
        db_info = info.get("db0", {})
        
        return {
            "type": "redis",
            "total_keys": db_info.get("keys", 0),
            "expires": db_info.get("expires", 0),
            "connected": await self._redis.ping()
        }

    async def close(self) -> None:
        """Close the Redis connection."""
        await self._redis.close()
