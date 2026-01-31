"""
Permission Service Implementation

Provides permission checking with in-memory caching for performance.
This service is the core of the RBAC system, handling:
- Permission loading from database
- Permission caching with configurable TTL
- Permission verification for authorization

Performance Optimizations:
1. In-memory cache with sliding expiration
2. Batch permission loading (all at once, not one-by-one)
3. Cache invalidation on permission changes
"""

from uuid import UUID

from app.repositories.interfaces.permission_repository_interface import IPermissionRepository
from app.services.interfaces.permission_service_interface import IPermissionService
from app.services.interfaces.cache_service_interface import ICacheService


class PermissionService(IPermissionService):
    """
    Permission service with caching support.
    
    Implements permission checking with an optional cache layer
    for high-performance authorization checks.
    
    Cache Strategy:
    - Permissions are cached per user with sliding expiration
    - Cache key format: "permissions:{user_id}"
    - Default cache TTL: 5 minutes (configurable)
    - Cache is invalidated when permissions change
    """

    # Cache configuration
    CACHE_KEY_PREFIX = "permissions"
    CACHE_TTL_SECONDS = 300  # 5 minutes sliding expiration

    def __init__(
        self,
        permission_repository: IPermissionRepository,
        cache_service: ICacheService | None = None
    ):
        """
        Initialize the permission service.
        
        Args:
            permission_repository: Repository for database operations
            cache_service: Optional cache service for permission caching
                          If None, permissions are loaded from DB each time
        """
        self._repository = permission_repository
        self._cache = cache_service

    def _get_cache_key(self, user_id: UUID) -> str:
        """
        Generate cache key for user permissions.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Cache key string in format "permissions:{user_id}"
        """
        return f"{self.CACHE_KEY_PREFIX}:{str(user_id)}"

    async def get_user_permissions(self, user_id: UUID) -> set[str]:
        """
        Get all permissions for a user with caching.
        
        Flow:
        1. Check cache for existing permissions
        2. If cache miss, load from database
        3. Store in cache with sliding expiration
        4. Return permission set
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Set of permission strings
        """
        cache_key = self._get_cache_key(user_id)
        
        # Try to get from cache first
        if self._cache is not None:
            cached_permissions = await self._cache.get(cache_key)
            if cached_permissions is not None:
                # Cache hit - return cached permissions
                return set(cached_permissions)
        
        # Cache miss - load from database (role-based permissions only)
        permissions = await self._repository.get_user_permissions(user_id)
        
        # Store in cache for future requests
        if self._cache is not None:
            # Convert set to list for JSON serialization
            await self._cache.set(
                cache_key,
                list(permissions),
                sliding_expiration=self.CACHE_TTL_SECONDS
            )
        
        return permissions

    async def has_permission(self, user_id: UUID, permission: str) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            user_id: UUID of the user
            permission: Permission string to check
            
        Returns:
            True if user has the permission
        """
        permissions = await self.get_user_permissions(user_id)
        return permission in permissions

    async def has_any_permission(self, user_id: UUID, permissions: list[str]) -> bool:
        """
        Check if a user has ANY of the specified permissions (OR logic).
        
        Useful for endpoints that can be accessed with multiple permissions.
        Example: Allow access if user has USERS_VIEW OR USERS_MANAGE
        
        Args:
            user_id: UUID of the user
            permissions: List of permission strings to check
            
        Returns:
            True if user has at least one of the permissions
        """
        user_permissions = await self.get_user_permissions(user_id)
        return bool(user_permissions & set(permissions))

    async def has_all_permissions(self, user_id: UUID, permissions: list[str]) -> bool:
        """
        Check if a user has ALL of the specified permissions (AND logic).
        
        Useful for endpoints requiring multiple permissions.
        Example: Require both USERS_VIEW AND AUDIT_VIEW
        
        Args:
            user_id: UUID of the user
            permissions: List of permission strings to check
            
        Returns:
            True if user has all specified permissions
        """
        user_permissions = await self.get_user_permissions(user_id)
        return set(permissions).issubset(user_permissions)

    async def invalidate_user_permissions_cache(self, user_id: UUID) -> None:
        """
        Invalidate cached permissions for a specific user.
        
        Call this when:
        - User roles are added/removed
        - User direct claims are added/removed
        
        Args:
            user_id: UUID of the user
        """
        if self._cache is not None:
            cache_key = self._get_cache_key(user_id)
            await self._cache.remove(cache_key)

    async def invalidate_role_permissions_cache(self, role_id: UUID) -> None:
        """
        Invalidate cached permissions for all users with a specific role.
        
        Call this when role permissions are modified.
        This ensures all affected users get fresh permissions on next check.
        
        Args:
            role_id: UUID of the role
        """
        if self._cache is None:
            return
            
        # Get all users with this role
        user_ids = await self._repository.get_users_by_role(role_id)
        
        # Invalidate cache for each user
        for user_id in user_ids:
            await self.invalidate_user_permissions_cache(user_id)
