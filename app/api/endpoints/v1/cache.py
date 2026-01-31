from fastapi import APIRouter, HTTPException, status

from app.services.cache.cache_factory import get_cache_service
from app.schema.request.cache import (
    CacheSetRequest,
    CacheGetResponse,
    CacheDeleteResponse,
    CacheRefreshResponse,
    CacheStatsResponse
)

router = APIRouter(
    prefix="/cache",
    tags=["Cache"],
)


@router.get(
    "/{key}",
    summary="Get cached value",
    description="Retrieve a value from the cache by key. Returns null if the key is not found or has expired.",
    response_model=CacheGetResponse
)
async def get_cache(key: str) -> CacheGetResponse:
    """
    Get a cached value by key.
    
    Args:
        key: The cache key to retrieve.
        
    Returns:
        CacheGetResponse containing the key, value, and whether it was found.
    """
    cache_service = await get_cache_service()
    value = await cache_service.get(key)
    
    return CacheGetResponse(
        key=key,
        value=value,
        found=value is not None
    )


@router.post(
    "/{key}",
    summary="Set cached value",
    description="Store a value in the cache with an optional sliding expiration time.",
    status_code=status.HTTP_201_CREATED
)
async def set_cache(key: str, request: CacheSetRequest) -> dict:
    """
    Set a cached value.
    
    Args:
        key: The cache key.
        request: The request body containing the value and optional expiration.
        
    Returns:
        Success message with the key.
    """
    cache_service = await get_cache_service()
    await cache_service.set(
        key=key,
        value=request.value,
        sliding_expiration=request.sliding_expiration
    )
    
    return {
        "message": "Value cached successfully",
        "key": key,
        "sliding_expiration": request.sliding_expiration
    }


@router.delete(
    "/{key}",
    summary="Delete cached value",
    description="Remove a value from the cache by key.",
    response_model=CacheDeleteResponse
)
async def delete_cache(key: str) -> CacheDeleteResponse:
    """
    Delete a cached value by key.
    
    Args:
        key: The cache key to delete.
        
    Returns:
        CacheDeleteResponse indicating whether the key was deleted.
    """
    cache_service = await get_cache_service()
    deleted = await cache_service.remove(key)
    
    return CacheDeleteResponse(
        key=key,
        deleted=deleted
    )


@router.post(
    "/{key}/refresh",
    summary="Refresh cache expiration",
    description="Reset the sliding expiration timer for a cached value.",
    response_model=CacheRefreshResponse
)
async def refresh_cache(key: str) -> CacheRefreshResponse:
    """
    Refresh the expiration time for a cached value.
    
    Args:
        key: The cache key to refresh.
        
    Returns:
        CacheRefreshResponse indicating whether the key was refreshed.
    """
    cache_service = await get_cache_service()
    refreshed = await cache_service.refresh(key)
    
    return CacheRefreshResponse(
        key=key,
        refreshed=refreshed
    )


@router.get(
    "",
    summary="Check if key exists",
    description="Check if a cache key exists without retrieving the value."
)
async def check_cache_exists(key: str) -> dict:
    """
    Check if a key exists in the cache.
    
    Args:
        key: The cache key to check.
        
    Returns:
        Dictionary indicating whether the key exists.
    """
    cache_service = await get_cache_service()
    exists = await cache_service.exists(key)
    
    return {
        "key": key,
        "exists": exists
    }


@router.get(
    "/stats/info",
    summary="Get cache statistics",
    description="Get statistics about the cache (type, size, etc.).",
    response_model=CacheStatsResponse
)
async def get_cache_stats() -> CacheStatsResponse:
    """
    Get cache statistics.
    
    Returns:
        CacheStatsResponse containing cache type and statistics.
    """
    cache_service = await get_cache_service()
    stats = await cache_service.get_stats()
    
    return CacheStatsResponse(
        type=stats.pop("type", "unknown"),
        stats=stats
    )


@router.delete(
    "",
    summary="Clear all cache",
    description="Clear all entries from the cache. Use with caution!"
)
async def clear_cache() -> dict:
    """
    Clear all entries from the cache.
    
    Returns:
        Success message.
    """
    cache_service = await get_cache_service()
    await cache_service.clear()
    
    return {"message": "Cache cleared successfully"}
