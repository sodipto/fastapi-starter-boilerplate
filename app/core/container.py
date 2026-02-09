"""
Dependency Injection Container

Production-grade DI container using declarative configuration pattern.
All dependencies are defined upfront with proper lifecycle management.

Key Design Principles:
    1. Declarative Configuration: All providers defined at class level
    2. No Runtime Overrides: Use Resource providers for async initialization
    3. Lazy Resolution: Use providers.Dependency() for circular prevention
    4. Testability: Override at container level, not runtime

Cyclic Dependency Prevention:
    - Services that may need each other use the ServiceMediator pattern
    - Use providers.Dependency() for optional late-binding
    - Singleton services are created once and shared
"""
from dependency_injector import containers, providers

from app.core.database.session import async_session, get_db
from app.repositories import UserRepository, EmailLogRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.permission_repository import PermissionRepository
from app.services import UserService, AuthService, EmailService, SchedulerService
from app.services.profile_service import ProfileService
from app.services.token_service import TokenService
from app.services.role_service import RoleService
from app.services.permission_service import PermissionService
from app.services.AWS_s3_document_storage_service import AwsS3DocumentStorageService
from app.services.email_template_service import EmailTemplateService
from app.services.cache.cache_resource import cache_service_resource
from app.services.rate_limit_service import RateLimitService


class Container(containers.DeclarativeContainer):
    """
    Application DI container with declarative, lifecycle-managed providers.
    
    Provider Types Used:
        - Resource: Async lifecycle-managed dependencies (db, cache)
        - Factory: New instance per injection (services with request scope)
        - Singleton: Single instance for app lifetime (token service)
        - Dependency: Late-bound dependencies to prevent cycles
    """
    
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.endpoints.v1.user",
            "app.api.endpoints.v1.auth",
            "app.api.endpoints.v1.role",
            "app.api.endpoints.v1.document",
            "app.api.endpoints.v1.profile",
            "app.core.rbac.dependencies",  # RBAC permission dependencies
            "app.core.rate_limiting.rate_limit",  # Per-route rate limiting
            "app.core.middlewares.rate_limit_middleware",  # Global rate limiting middleware
        ]
    )

    # ========================================================================
    # Infrastructure Layer - Lifecycle-managed resources
    # ========================================================================
    
    # Provide the sessionmaker (callable) so repositories can create sessions on demand
    db_session_factory = providers.Object(async_session)

    # Cache service - declarative async resource (no runtime override needed)
    cache_service = providers.Resource(cache_service_resource)

    # ========================================================================
    # Repository Layer - Factory providers (new instance per request)
    # ========================================================================
    
    user_repository = providers.Factory(
        UserRepository,
        db_factory=db_session_factory
    )

    role_repository = providers.Factory(
        RoleRepository,
        db_factory=db_session_factory
    )

    email_log_repository = providers.Factory(
        EmailLogRepository,
        db_factory=db_session_factory
    )

    permission_repository = providers.Factory(
        PermissionRepository,
        db_factory=db_session_factory
    )

    # ========================================================================
    # Service Layer - Singletons and Factories
    # ========================================================================
    
    token_service = providers.Singleton(TokenService)

    email_template_service = providers.Singleton(EmailTemplateService)

    email_service = providers.Factory(
        EmailService,
        db=db_session_factory
    )

    # User service - uses repositories, not other services directly
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
        role_repository=role_repository,
        email_service=email_service,
        email_template_service=email_template_service
    )

    profile_service = providers.Factory(
        ProfileService,
        user_repository=user_repository
    )

    role_service = providers.Factory(
        RoleService,
        role_repository=role_repository
    )

    # RBAC: Permission service with caching for authorization
    permission_service = providers.Factory(
        PermissionService,
        permission_repository=permission_repository,
        cache_service=cache_service
    )

    # Auth service - depends on repositories and utility services
    auth_service = providers.Factory(
        AuthService,
        user_repository=user_repository,
        token_service=token_service,
        cache_service=cache_service,
        email_service=email_service,
        email_template_service=email_template_service
    )

    document_storage_service = providers.Singleton(AwsS3DocumentStorageService)

    scheduler_service = providers.Singleton(SchedulerService)

    # Rate limiting service - uses cache for storage (memory or Redis)
    rate_limit_service = providers.Factory(
        RateLimitService,
        cache_service=cache_service
    )


