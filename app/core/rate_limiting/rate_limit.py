"""
Per-Route Rate Limiting Dependency

Provides granular rate limiting at the route level using FastAPI dependencies.
Each route can have its own rate limit configuration.

Usage:
    @router.post("/login", dependencies=[Depends(RateLimit(requests=5, window=1))])
    async def login(...):
        ...

    # Or with custom key (e.g., by user ID instead of IP)
    @router.post("/action", dependencies=[Depends(RateLimit(requests=10, window=60, key_prefix="action"))])
    async def action(...):
        ...
"""
from fastapi import Request, Depends
from dependency_injector.wiring import inject, Provide

from app.core.container import Container
from app.core.config import settings
from app.services.interfaces.rate_limit_service_interface import IRateLimitService
from app.utils.exception_utils import TooManyRequestsException
from app.utils.ip_utils import get_client_ip


class RateLimit:
    """
    FastAPI dependency for per-route rate limiting.
    
    Args:
        requests: Maximum number of requests allowed per window
        window: Window duration in seconds (default: 1 = per second)
        key_prefix: Optional prefix for cache key (useful for grouping routes)
    """
    
    def __init__(self, requests: int, window: int = 1, key_prefix: str | None = None):
        self.requests = requests
        self.window = window
        self.key_prefix = key_prefix

    @inject
    async def __call__(
        self,
        request: Request,
        rate_limit_service: IRateLimitService = Depends(Provide[Container.rate_limit_service])
    ):
        """Check rate limit for the route."""
        if not settings.RATE_LIMIT_ENABLED:
            return
        
        client_ip = get_client_ip(request)
        path = request.url.path
        
        # Build unique key: prefix or path + IP
        key_prefix = self.key_prefix or path
        cache_key = f"{key_prefix}:{client_ip}"
        
        # Use route-specific rate limiting
        result = await rate_limit_service.check_rate_limit_custom(
            key=cache_key,
            max_requests=self.requests,
            window_seconds=self.window
        )
        
        if result.is_limited:
            raise TooManyRequestsException(retry_after=result.retry_after)
        
        # Store rate limit info in request state for response headers
        request.state.rate_limit_result = result

