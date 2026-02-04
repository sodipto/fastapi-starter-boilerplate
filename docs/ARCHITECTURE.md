# Architecture Guide

This document describes the architecture, design patterns, and code organization of the FastAPI boilerplate.

## Table of Contents

- [Overview](#overview)
- [Layers](#layers)
- [Dependency Injection](#dependency-injection)
- [Request Lifecycle](#request-lifecycle)
- [Folder Structure](#folder-structure)

---

## Overview

The application follows a **Clean Architecture** approach with clear separation of concerns. Each layer has a specific responsibility:

```
┌─────────────────────────────────────────────┐
│              API Layer                      │
│     (Endpoints, Routes, Middleware)         │
├─────────────────────────────────────────────┤
│            Service Layer                    │
│        (Business Logic)                     │
├─────────────────────────────────────────────┤
│          Repository Layer                   │
│         (Data Access)                       │
├─────────────────────────────────────────────┤
│            Model Layer                      │
│      (SQLAlchemy Entities)                  │
├─────────────────────────────────────────────┤
│            Database                         │
│     (PostgreSQL / SQL Server)               │
└─────────────────────────────────────────────┘
```

---

## Layers

### 1. API Layer (`app/api/`)

Handles HTTP requests and responses. Contains:

- **Endpoints:** Route handlers organized by version (`v1/`)
- **Routes:** Route aggregation and registration
- **Schemas:** Pydantic models for request/response validation

```python
# app/api/endpoints/v1/auth.py
@router.post("/login", response_model=TokenResponse)
@inject
async def login(
    request: LoginRequest,
    auth_service: IAuthService = Depends(Provide[Container.auth_service])
):
    return await auth_service.login(request.email, request.password)
```

### 2. Service Layer (`app/services/`)

Contains all business logic. Services:

- Orchestrate operations across repositories
- Implement business rules and validations
- Return domain-specific exceptions

Each service implements an interface for testability:

```python
# app/services/interfaces/auth_service_interface.py
class IAuthService(ABC):
    @abstractmethod
    async def login(self, email: str, password: str) -> TokenResponse:
        pass

# app/services/auth_service.py
class AuthService(IAuthService):
    def __init__(self, user_repository: IUserRepository, ...):
        self._user_repository = user_repository
    
    async def login(self, email: str, password: str) -> TokenResponse:
        # Business logic here
```

### 3. Repository Layer (`app/repositories/`)

Handles all database operations. Repositories:

- Abstract away SQLAlchemy queries
- Provide CRUD operations
- Extend `BaseRepository` for common operations

```python
# app/repositories/user_repository.py
class UserRepository(BaseRepository[User], IUserRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
```

### 4. Model Layer (`app/models/`)

SQLAlchemy ORM models representing database tables:

```python
# app/models/user.py
class User(AuditableEntity):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    full_name: Mapped[str] = mapped_column(String(100))
    # ...
```

### 5. Core Layer (`app/core/`)

Foundation components:

| Component | Purpose |
|-----------|---------|
| `config.py` | Application settings from environment |
| `container.py` | Dependency injection container |
| `database/` | Database connection and session management |
| `middlewares/` | Exception handling, validation |
| `rbac/` | Role-based access control |
| `seeders/` | Initial data seeding |

---

## Dependency Injection

The application uses `dependency-injector` for managing dependencies.

### Container Configuration

```python
# app/core/container.py
class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["app.api.endpoints"]
    )
    
    # Database session
    db_session = providers.Resource(get_db_session)
    
    # Repositories
    user_repository = providers.Factory(
        UserRepository,
        session=db_session
    )
    
    # Services
    auth_service = providers.Factory(
        AuthService,
        user_repository=user_repository
    )
```

### Using Dependencies

```python
from dependency_injector.wiring import Depends, Provide, inject
from app.core.container import Container

@router.post("/login")
@inject
async def login(
    auth_service: IAuthService = Depends(Provide[Container.auth_service])
):
    ...
```

---

## Request Lifecycle

1. **Request received** by FastAPI
2. **Middleware executes** (authentication, exception handling)
3. **Route handler invoked** with injected dependencies
4. **Service processes** business logic
5. **Repository performs** database operations
6. **Response serialized** via Pydantic schema
7. **Middleware post-processing** and response sent

```
Request → Middleware → Router → Service → Repository → DB
                                    ↓
Response ← Middleware ← Router ← Service ← Repository ← DB
```

---

## Folder Structure

```
app/
├── api/
│   └── endpoints/
│       ├── routes.py           # Combines all routers
│       └── v1/
│           ├── auth.py         # Auth endpoints
│           ├── users.py        # User endpoints
│           └── ...
│
├── core/
│   ├── config.py               # Settings class
│   ├── container.py            # DI container
│   ├── identity.py             # Current user context
│   ├── jwt_security.py         # JWT utilities
│   ├── logger.py               # Structured logging
│   ├── open_api.py             # OpenAPI customization
│   ├── constants/              # Application constants
│   ├── database/               # DB session, providers
│   ├── middlewares/            # Exception handlers
│   ├── rbac/                   # Roles, permissions
│   └── seeders/                # Data seeders
│
├── jobs/
│   ├── registry.py             # Job registration
│   └── health_check.py         # Example job
│
├── models/
│   ├── __init__.py             # Model exports
│   ├── user.py
│   ├── role.py
│   └── ...
│
├── repositories/
│   ├── base_repository.py      # Generic CRUD
│   ├── user_repository.py
│   └── interfaces/             # Repository interfaces
│
├── schema/
│   ├── request/                # Request DTOs
│   └── response/               # Response DTOs
│
├── services/
│   ├── auth_service.py
│   ├── user_service.py
│   ├── email_service.py
│   ├── email_template_service.py
│   └── interfaces/             # Service interfaces
│
├── templates/
│   └── emails/                 # Jinja2 email templates
│
├── utils/
│   ├── auth_utils.py
│   └── exception_utils.py
│
└── main.py                     # Application entry point
```

---

## Key Design Decisions

### Why Interfaces?

All services and repositories implement interfaces:

- **Testability:** Easy to mock in unit tests
- **Loose coupling:** Swap implementations without changing consumers
- **Documentation:** Interfaces document the contract

### Why `dependency-injector`?

- Type-safe dependency resolution
- Scoped resources (request, singleton)
- Built-in support for async factories
- Clean separation from FastAPI's `Depends`

### Why Repository Pattern?

- Centralized data access logic
- Database-agnostic business logic
- Simplified testing with mock repositories
- Single place for query optimization
