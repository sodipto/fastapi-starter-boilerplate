"""
Rate Limiting Middleware

Production-grade rate limiting using fixed window algorithm.
Configurable via environment variables and works with both
in-memory (single instance) and Redis (multi-instance) cache backends.

Configuration:
    RATE_LIMIT_ENABLED: Enable/disable rate limiting
    RATE_LIMIT_REQUESTS: Max requests per window
    RATE_LIMIT_WINDOW_SECONDS: Window duration in seconds
    RATE_LIMIT_EXEMPT_PATHS: List of path prefixes to exempt
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from dependency_injector.wiring import inject, Provide

from app.core.config import settings
from app.core.container import Container
from app.services.interfaces.rate_limit_service_interface import IRateLimitService
from app.schema.response.error import ErrorBody, ErrorResponse
from app.utils.ip_utils import get_client_ip


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    HTTP middleware for rate limiting requests.
    
    Uses fixed window algorithm with configurable limits.
    Adds standard rate limit headers to all responses.
    
    Headers:
        X-RateLimit-Limit: Maximum requests allowed per window
        X-RateLimit-Remaining: Remaining requests in current window
        X-RateLimit-Reset: Unix timestamp when window resets
        Retry-After: Seconds until retry allowed (only on 429)
    """

    def _is_exempt_path(self, path: str) -> bool:
        """Check if the request path is exempt from rate limiting."""
        for exempt_path in settings.RATE_LIMIT_EXEMPT_PATHS:
            if path.startswith(exempt_path):
                return True
        return False

    @inject
    async def dispatch(
        self, 
        request: Request, 
        call_next,
        rate_limit_service: IRateLimitService = Provide[Container.rate_limit_service]
    ):
        """
        Process request through rate limiter.
        
        If rate limit exceeded, returns 429 with Retry-After header.
        Otherwise, adds rate limit headers to response.
        """
        # Skip rate limiting if disabled
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        # Skip exempt paths
        if self._is_exempt_path(request.url.path):
            return await call_next(request)
        
        # Get client identifier (IP address)
        client_ip = get_client_ip(request)
        
        # Check rate limit
        result = await rate_limit_service.check_rate_limit(client_ip)
        
        if result.is_limited:
            # Return 429 Too Many Requests
            error_response = ErrorResponse(
                error=ErrorBody(
                    logId="",
                    statusCode=429,
                    type="TooManyRequestsException",
                    messages={
                        "RateLimit": f"Too many requests. Please retry after {result.retry_after} seconds."
                    }
                )
            )
            
            return JSONResponse(
                status_code=429,
                content=error_response.model_dump(),
                headers={
                    "X-RateLimit-Limit": str(result.limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(result.reset_at),
                    "Retry-After": str(result.retry_after)
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(result.limit)
        response.headers["X-RateLimit-Remaining"] = str(result.remaining)
        response.headers["X-RateLimit-Reset"] = str(result.reset_at)
        
        return response