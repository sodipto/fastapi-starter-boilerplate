import time
from app.services.interfaces.rate_limit_service_interface import IRateLimitService, RateLimitResult
from app.services.interfaces.cache_service_interface import ICacheService
from app.core.config import settings


class RateLimitService(IRateLimitService):
    """
    Fixed window rate limiting service implementation.
    
    Uses the existing cache service (memory or Redis) for storage.
    Implements fixed window algorithm where requests are counted within
    discrete time windows.
    
    Example:
        With RATE_LIMIT_REQUESTS=100 and RATE_LIMIT_WINDOW_SECONDS=1:
        - Window 1 (0-1s): Up to 100 requests allowed
        - Window 2 (1-2s): Counter resets, 100 more requests allowed
    """

    CACHE_KEY_PREFIX = "ratelimit"

    def __init__(self, cache_service: ICacheService):
        self._cache = cache_service
        self._max_requests = settings.RATE_LIMIT_REQUESTS
        self._window_seconds = settings.RATE_LIMIT_WINDOW_SECONDS

    def _get_window_key(self, key: str, window_seconds: int | None = None) -> tuple[str, int]:
        """
        Generate cache key for the current time window.
        
        Args:
            key: Base key for rate limiting
            window_seconds: Custom window size (uses global setting if None)
        
        Returns:
            Tuple of (cache_key, window_reset_timestamp)
        """
        window = window_seconds if window_seconds is not None else self._window_seconds
        current_time = int(time.time())
        window_start = (current_time // window) * window
        window_end = window_start + window
        cache_key = f"{self.CACHE_KEY_PREFIX}:{key}:{window_start}"
        return cache_key, window_end

    async def check_rate_limit(self, key: str) -> RateLimitResult:
        """
        Check if the given key is rate limited and increment the counter.
        
        Uses atomic increment pattern:
        1. Increment count atomically
        2. Return limit status with metadata
        """
        cache_key, reset_at = self._get_window_key(key)
        current_time = int(time.time())
        retry_after = max(0, reset_at - current_time)
        
        # Increment count atomically (with TTL on first write)
        new_count = await self._cache.increment(
            cache_key, 
            delta=1, 
            ttl=self._window_seconds + 1
        )
        
        # Check if limited
        is_limited = new_count > self._max_requests
        remaining = max(0, self._max_requests - new_count)
        
        return RateLimitResult(
            is_limited=is_limited,
            limit=self._max_requests,
            remaining=remaining,
            reset_at=reset_at,
            retry_after=retry_after if is_limited else 0
        )

    async def get_current_count(self, key: str) -> int:
        """Get the current request count for a key without incrementing."""
        cache_key, _ = self._get_window_key(key)
        count = await self._cache.get(cache_key)
        return int(count) if count is not None else 0

    async def reset(self, key: str) -> bool:
        """Reset the rate limit counter for a key."""
        cache_key, _ = self._get_window_key(key)
        return await self._cache.remove(cache_key)

    async def check_rate_limit_custom(
        self, 
        key: str, 
        max_requests: int, 
        window_seconds: int
    ) -> RateLimitResult:
        """
        Check rate limit with custom limits (for per-route rate limiting).
        
        Args:
            key: Unique identifier (e.g., "/api/v1/auth/login:192.168.1.1")
            max_requests: Maximum requests allowed per window
            window_seconds: Window duration in seconds
        """
        cache_key, reset_at = self._get_window_key(key, window_seconds)
        current_time = int(time.time())
        retry_after = max(0, reset_at - current_time)
        
        # Increment count atomically
        new_count = await self._cache.increment(
            cache_key, 
            delta=1, 
            ttl=window_seconds + 1
        )
        
        # Check if limited
        is_limited = new_count > max_requests
        remaining = max(0, max_requests - new_count)
        
        return RateLimitResult(
            is_limited=is_limited,
            limit=max_requests,
            remaining=remaining,
            reset_at=reset_at,
            retry_after=retry_after if is_limited else 0
        )
