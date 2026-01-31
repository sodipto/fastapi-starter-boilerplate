from abc import ABC, abstractmethod
from typing import Any


class ICacheService(ABC):
    """
    Abstract base class for cache service implementations.
    Similar to .NET ICacheService pattern.
    All operations are async and thread-safe.
    """

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """
        Retrieve a value from the cache.
        
        Args:
            key: The cache key to retrieve.
            
        Returns:
            The cached value if found, None otherwise.
        """
        pass

    @abstractmethod
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
                               If provided, the cache entry will expire after
                               this many seconds of inactivity.
        """
        pass

    @abstractmethod
    async def refresh(self, key: str) -> bool:
        """
        Refresh the expiration time for a cache entry.
        This resets the sliding expiration timer.
        
        Args:
            key: The cache key to refresh.
            
        Returns:
            True if the key was found and refreshed, False otherwise.
        """
        pass

    @abstractmethod
    async def remove(self, key: str) -> bool:
        """
        Remove a value from the cache.
        
        Args:
            key: The cache key to remove.
            
        Returns:
            True if the key was found and removed, False otherwise.
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.
        
        Args:
            key: The cache key to check.
            
        Returns:
            True if the key exists, False otherwise.
        """
        pass

    @abstractmethod
    async def clear(self) -> None:
        """
        Clear all entries from the cache.
        """
        pass

    @abstractmethod
    async def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary containing cache-specific statistics.
        """
        pass
