# Cache Service Documentation

This document describes the cache service implementation in the FastAPI boilerplate, inspired by .NET's `ICacheService` pattern.

## Overview

The cache service provides a unified interface for caching data with support for:
- **In-Memory caching** using Python dictionaries with asyncio.Lock
- **Redis caching** using the `redis.asyncio` client
- **Sliding expiration** for automatic cache invalidation
- **Thread-safe async operations**

## Configuration

Add the following environment variables to your `.env` file:

```env
# Cache settings
CACHE_TYPE=memory          # Options: memory, redis
REDIS_URL=redis://localhost:6379
```

### Cache Types

| Type | Description | Use Case |
|------|-------------|----------|
| `memory` | In-memory cache using Python dict | Development, single-instance deployments |
| `redis` | Redis-based distributed cache | Production, multi-instance deployments |

## Architecture

```
app/services/
├── interfaces/
│   └── cache_service_interface.py    # ICacheService abstract base class
└── cache/
    ├── __init__.py
    ├── cache_factory.py              # Factory and singleton management
    ├── in_memory_cache_service.py    # In-memory implementation
    └── redis_cache_service.py        # Redis implementation
```

## Interface (ICacheService)

```python
from abc import ABC, abstractmethod
from typing import Any

class ICacheService(ABC):
    async def get(self, key: str) -> Any | None: ...
    async def set(self, key: str, value: Any, sliding_expiration: int | None = None) -> None: ...
    async def refresh(self, key: str) -> bool: ...
    async def remove(self, key: str) -> bool: ...
    async def exists(self, key: str) -> bool: ...
    async def clear(self) -> None: ...
    async def get_stats(self) -> dict[str, Any]: ...
```

### Methods

| Method | Description |
|--------|-------------|
| `get(key)` | Retrieve a value from the cache. Returns `None` if not found or expired. |
| `set(key, value, sliding_expiration)` | Store a value with optional sliding expiration (seconds). |
| `refresh(key)` | Reset the sliding expiration timer for a key. |
| `remove(key)` | Remove a key from the cache. |
| `exists(key)` | Check if a key exists in the cache. |
| `clear()` | Clear all cache entries. |
| `get_stats()` | Get cache statistics. |

## Usage

### Using Dependency Injection

The cache service is automatically initialized during application startup and can be accessed via the factory function:

```python
from app.services.cache.cache_factory import get_cache_service

async def my_endpoint():
    cache = await get_cache_service()
    
    # Set a value with 5-minute sliding expiration
    await cache.set("user:123", {"name": "John"}, sliding_expiration=300)
    
    # Get the value
    user = await cache.get("user:123")
    
    # Refresh expiration
    await cache.refresh("user:123")
    
    # Remove the value
    await cache.remove("user:123")
```

### Using with FastAPI Request State

You can also access the cache service from the FastAPI app state:

```python
from fastapi import Request

@router.get("/example")
async def example(request: Request):
    cache = request.app.state.cache_service
    value = await cache.get("my_key")
    return {"value": value}
```

## REST API Endpoints

The cache service exposes the following REST endpoints under `/api/v1/cache`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cache/{key}` | Get a cached value |
| POST | `/cache/{key}` | Set a cached value |
| DELETE | `/cache/{key}` | Delete a cached value |
| POST | `/cache/{key}/refresh` | Refresh cache expiration |
| GET | `/cache?key={key}` | Check if key exists |
| GET | `/cache/stats/info` | Get cache statistics |
| DELETE | `/cache` | Clear all cache |

### Examples

#### Set a value
```bash
curl -X POST "http://localhost:8000/api/v1/cache/user:123" \
  -H "Content-Type: application/json" \
  -d '{"value": {"name": "John", "email": "john@example.com"}, "sliding_expiration": 3600}'
```

#### Get a value
```bash
curl "http://localhost:8000/api/v1/cache/user:123"
```

#### Delete a value
```bash
curl -X DELETE "http://localhost:8000/api/v1/cache/user:123"
```

## Sliding Expiration

Sliding expiration automatically extends the cache entry's lifetime whenever it is accessed:

1. When `set()` is called with `sliding_expiration=300` (5 minutes):
   - The entry expires 5 minutes after the last access
   
2. When `get()` is called:
   - The expiration timer is automatically reset
   
3. When `refresh()` is called:
   - The expiration timer is explicitly reset without retrieving the value

### Example: Session Cache

```python
# Cache user session with 30-minute sliding expiration
await cache.set(f"session:{session_id}", session_data, sliding_expiration=1800)

# Each time the user makes a request, the session is extended
session = await cache.get(f"session:{session_id}")  # Timer reset to 30 minutes
```

## Redis Configuration

For production deployments with Redis:

1. Install Redis server or use a managed Redis service
2. Configure the connection URL:

```env
CACHE_TYPE=redis
REDIS_URL=redis://username:password@hostname:6379/0
```

### Redis URL Formats

```
redis://localhost:6379                    # Basic
redis://localhost:6379/0                  # With database number
redis://username:password@localhost:6379  # With authentication
rediss://localhost:6379                   # TLS/SSL connection
```

## Thread Safety

Both implementations are thread-safe for async operations:

- **InMemoryCacheService**: Uses `asyncio.Lock` for thread-safe access
- **RedisCacheService**: Redis operations are inherently atomic

## Best Practices

1. **Use meaningful key prefixes**: `user:123`, `session:abc`, `config:app`
2. **Set appropriate expiration times**: Avoid caching data indefinitely
3. **Handle cache misses gracefully**: Always check for `None` returns
4. **Use Redis for distributed systems**: In-memory cache is not shared across instances
5. **Monitor cache statistics**: Use the `/cache/stats/info` endpoint

## Singleton Pattern

The cache service uses the singleton pattern to ensure:

- **Single Redis connection pool** across the application
- **Shared in-memory cache** state
- **Consistent cache behavior** throughout the request lifecycle

The singleton is managed via:
- `get_cache_service()` - Factory function for getting the cache service
- `init_cache_service()` - Called during app startup
- `shutdown_cache_service()` - Called during app shutdown
