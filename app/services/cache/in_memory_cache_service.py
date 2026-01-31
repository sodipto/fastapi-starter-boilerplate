import asyncio
import time
from typing import Any
from dataclasses import dataclass

from app.services.interfaces.cache_service_interface import ICacheService


@dataclass
class CacheEntry:
    """Represents a cached item with expiration metadata."""
    value: Any
    sliding_expiration: int | None
    last_accessed: float

    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.sliding_expiration is None:
            return False
        return (time.time() - self.last_accessed) > self.sliding_expiration

    def refresh(self) -> None:
        """Refresh the last accessed time."""
        self.last_accessed = time.time()


class InMemoryCacheService(ICacheService):
    """
    In-memory cache implementation using Python dict with asyncio.Lock.
    Supports sliding expiration for cache entries.
    Thread-safe for async operations.
    """

    def __init__(self) -> None:
        self._cache: dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: asyncio.Task | None = None
        self._cleanup_interval: int = 60  # Cleanup every 60 seconds

    async def start_cleanup_task(self) -> None:
        """Start the background cleanup task for expired entries."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop_cleanup_task(self) -> None:
        """Stop the background cleanup task."""
        if self._cleanup_task is not None:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

    async def _cleanup_loop(self) -> None:
        """Background loop to clean up expired cache entries."""
        while True:
            await asyncio.sleep(self._cleanup_interval)
            await self._cleanup_expired()

    async def _cleanup_expired(self) -> None:
        """Remove all expired entries from the cache."""
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]

    async def get(self, key: str) -> Any | None:
        """
        Retrieve a value from the cache.
        
        Args:
            key: The cache key to retrieve.
            
        Returns:
            The cached value if found and not expired, None otherwise.
        """
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            
            if entry.is_expired():
                del self._cache[key]
                return None
            
            # Refresh the sliding expiration
            entry.refresh()
            return entry.value

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
            value: The value to cache.
            sliding_expiration: Optional expiration time in seconds.
        """
        async with self._lock:
            self._cache[key] = CacheEntry(
                value=value,
                sliding_expiration=sliding_expiration,
                last_accessed=time.time()
            )

    async def refresh(self, key: str) -> bool:
        """
        Refresh the expiration time for a cache entry.
        
        Args:
            key: The cache key to refresh.
            
        Returns:
            True if the key was found and refreshed, False otherwise.
        """
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return False
            
            if entry.is_expired():
                del self._cache[key]
                return False
            
            entry.refresh()
            return True

    async def remove(self, key: str) -> bool:
        """
        Remove a value from the cache.
        
        Args:
            key: The cache key to remove.
            
        Returns:
            True if the key was found and removed, False otherwise.
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.
        
        Args:
            key: The cache key to check.
            
        Returns:
            True if the key exists and is not expired, False otherwise.
        """
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return False
            
            if entry.is_expired():
                del self._cache[key]
                return False
            
            return True

    async def clear(self) -> None:
        """Clear all entries from the cache."""
        async with self._lock:
            self._cache.clear()

    async def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary containing cache statistics.
        """
        async with self._lock:
            total_entries = len(self._cache)
            expired_entries = sum(
                1 for entry in self._cache.values()
                if entry.is_expired()
            )
            return {
                "type": "memory",
                "total_entries": total_entries,
                "active_entries": total_entries - expired_entries,
                "expired_entries": expired_entries
            }
