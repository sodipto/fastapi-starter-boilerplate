from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""
    is_limited: bool
    limit: int
    remaining: int
    reset_at: int  # Unix timestamp when the window resets
    retry_after: int  # Seconds until retry allowed (0 if not limited)


class IRateLimitService(ABC):
    """
    Abstract base class for rate limiting service implementations.
    Supports fixed window rate limiting with configurable limits.
    """

    @abstractmethod
    async def check_rate_limit(self, key: str) -> RateLimitResult:
        """
        Check if the given key is rate limited and increment the counter.
        Uses global rate limit settings.
        
        Args:
            key: Unique identifier for rate limiting (e.g., IP address, user ID).
            
        Returns:
            RateLimitResult with limit status and metadata.
        """
        pass

    @abstractmethod
    async def check_rate_limit_custom(
        self, 
        key: str, 
        max_requests: int, 
        window_seconds: int
    ) -> RateLimitResult:
        """
        Check if the given key is rate limited with custom limits.
        Used for per-route rate limiting.
        
        Args:
            key: Unique identifier for rate limiting.
            max_requests: Maximum requests allowed per window.
            window_seconds: Window duration in seconds.
            
        Returns:
            RateLimitResult with limit status and metadata.
        """
        pass

    @abstractmethod
    async def get_current_count(self, key: str) -> int:
        """
        Get the current request count for a key without incrementing.
        
        Args:
            key: Unique identifier for rate limiting.
            
        Returns:
            Current count of requests in the window.
        """
        pass

    @abstractmethod
    async def reset(self, key: str) -> bool:
        """
        Reset the rate limit counter for a key.
        
        Args:
            key: Unique identifier for rate limiting.
            
        Returns:
            True if the key was found and reset, False otherwise.
        """
        pass
