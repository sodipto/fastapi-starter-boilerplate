from pydantic import BaseModel, Field
from typing import Any


class CacheSetRequest(BaseModel):
    """Request model for setting a cache value."""
    value: Any = Field(..., description="The value to cache")
    sliding_expiration: int | None = Field(
        None,
        description="Optional expiration time in seconds. If provided, the cache entry will expire after this many seconds of inactivity.",
        ge=1
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "value": {"user_id": 123, "name": "John Doe"},
                    "sliding_expiration": 3600
                },
                {
                    "value": "simple string value",
                    "sliding_expiration": None
                }
            ]
        }
    }


class CacheGetResponse(BaseModel):
    """Response model for getting a cache value."""
    key: str = Field(..., description="The cache key")
    value: Any | None = Field(..., description="The cached value, or null if not found")
    found: bool = Field(..., description="Whether the key was found in the cache")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "key": "user:123",
                    "value": {"user_id": 123, "name": "John Doe"},
                    "found": True
                },
                {
                    "key": "nonexistent",
                    "value": None,
                    "found": False
                }
            ]
        }
    }


class CacheDeleteResponse(BaseModel):
    """Response model for deleting a cache entry."""
    key: str = Field(..., description="The cache key")
    deleted: bool = Field(..., description="Whether the key was successfully deleted")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "key": "user:123",
                    "deleted": True
                }
            ]
        }
    }


class CacheRefreshResponse(BaseModel):
    """Response model for refreshing a cache entry."""
    key: str = Field(..., description="The cache key")
    refreshed: bool = Field(..., description="Whether the key's expiration was successfully refreshed")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "key": "user:123",
                    "refreshed": True
                }
            ]
        }
    }


class CacheStatsResponse(BaseModel):
    """Response model for cache statistics."""
    type: str = Field(..., description="The cache type (memory or redis)")
    stats: dict[str, Any] = Field(..., description="Cache-specific statistics")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": "memory",
                    "stats": {
                        "total_entries": 100,
                        "active_entries": 95,
                        "expired_entries": 5
                    }
                },
                {
                    "type": "redis",
                    "stats": {
                        "total_keys": 1000,
                        "expires": 500,
                        "connected": True
                    }
                }
            ]
        }
    }
