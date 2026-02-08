"""
Rate Limiting Module

Provides per-route rate limiting functionality for FastAPI applications.

Components:
    - RateLimit: FastAPI dependency for per-route rate limiting
    - rate_limit_strict: Pre-configured strict rate limit (5/sec)
    - rate_limit_normal: Pre-configured normal rate limit (20/sec)
    - rate_limit_relaxed: Pre-configured relaxed rate limit (100/sec)

Usage:
    from app.core.rate_limiting import RateLimit

    @router.post("/login", dependencies=[Depends(RateLimit(requests=5, window=1))])
    async def login(...):
        ...
"""

from app.core.rate_limiting.rate_limit import RateLimit

__all__ = [
    "RateLimit",
]
