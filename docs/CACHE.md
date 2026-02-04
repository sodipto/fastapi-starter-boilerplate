# Cache Service

In-memory or Redis caching with sliding expiration support.

## Table of Contents

- [Configuration](#configuration)
- [Interface](#interface)
- [Usage](#usage)
- [REST API](#rest-api)
- [Redis Setup](#redis-setup)

---

## Configuration

```env
CACHE_TYPE=memory          # memory or redis
REDIS_URL=redis://localhost:6379
```

| Type | Description | Use Case |
|------|-------------|----------|
| `memory` | Python dict with asyncio.Lock | Development, single instance |
| `redis` | Distributed Redis cache | Production, multiple instances |

---

## Interface

```python
class ICacheService(ABC):
    async def get(self, key: str) -> Any | None: ...
    async def set(self, key: str, value: Any, sliding_expiration: int | None = None) -> None: ...
    async def refresh(self, key: str) -> bool: ...
    async def remove(self, key: str) -> bool: ...
    async def exists(self, key: str) -> bool: ...
    async def clear(self) -> None: ...
    async def get_stats(self) -> dict[str, Any]: ...
```

| Method | Description |
|--------|-------------|
| `get(key)` | Retrieve value, returns `None` if expired |
| `set(key, value, sliding_expiration)` | Store with optional TTL (seconds) |
| `refresh(key)` | Reset expiration timer |
| `remove(key)` | Delete a key |
| `exists(key)` | Check if key exists |
| `clear()` | Clear all entries |
| `get_stats()` | Get cache statistics |

---

## Usage

### Basic Example

```python
from app.services.cache.cache_factory import get_cache_service

async def my_endpoint():
    cache = await get_cache_service()
    
    # Set with 5-minute sliding expiration
    await cache.set("user:123", {"name": "John"}, sliding_expiration=300)
    
    # Get value (resets expiration)
    user = await cache.get("user:123")
    
    # Refresh expiration without retrieving
    await cache.refresh("user:123")
    
    # Remove
    await cache.remove("user:123")
```

### From Request State

```python
from fastapi import Request

@router.get("/example")
async def example(request: Request):
    cache = request.app.state.cache_service
    value = await cache.get("my_key")
    return {"value": value}
```

### Session Caching Pattern

```python
# Cache session with 30-minute sliding expiration
await cache.set(f"session:{session_id}", session_data, sliding_expiration=1800)

# Each access extends the session
session = await cache.get(f"session:{session_id}")
```

---

## REST API

Endpoints under `/api/v1/cache`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{key}` | Get cached value |
| POST | `/{key}` | Set cached value |
| DELETE | `/{key}` | Delete cached value |
| POST | `/{key}/refresh` | Refresh expiration |
| GET | `?key={key}` | Check if key exists |
| GET | `/stats/info` | Get statistics |
| DELETE | `/` | Clear all cache |

### Set Value

```bash
curl -X POST "http://localhost:8000/api/v1/cache/user:123" \
  -H "Content-Type: application/json" \
  -d '{"value": {"name": "John"}, "sliding_expiration": 3600}'
```

### Get Value

```bash
curl "http://localhost:8000/api/v1/cache/user:123"
```

---

## Redis Setup

### Connection URL Formats

```
redis://localhost:6379                    # Basic
redis://localhost:6379/0                  # With database
redis://user:password@localhost:6379      # With auth
rediss://localhost:6379                   # TLS/SSL
```

### Docker

```bash
docker run -d --name redis -p 6379:6379 redis:alpine
```

---

## Best Practices

1. **Use meaningful key prefixes** — `user:123`, `session:abc`, `config:app`
2. **Set appropriate TTLs** — avoid caching indefinitely
3. **Handle cache misses** — always check for `None`
4. **Use Redis in production** — in-memory is not shared across instances
5. **Monitor statistics** — use `/cache/stats/info` endpoint
