from app.core.database.session import async_session
from app.core.logger import get_logger
from app.core.rbac import AppPermissions, AppRoles, PermissionClaimType
from app.models.role import Role
from app.models.role_claim import RoleClaim
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user_role import UserRole
from app.utils.auth_utils import get_password_hash


class ApplicationSeeder:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.seeders = [
            self.seed_system_roles,
            self.seed_sa_user
        ]

    async def seed_data(self):
        self.logger.info("Starting application data seeding...")
        async with async_session() as session:
            for seeder in self.seeders:
                self.logger.debug(f"Running seeder: {seeder.__name__}")
                await seeder(session)
        self.logger.info("Application data seeding completed.")

    async def assign_permissions_to_role(
        self, 
        session: AsyncSession, 
        role: Role, 
        permissions: list
    ):
        """Assign a list of permissions to a role. Syncs permissions - adds new and removes old."""
        # Get existing claims for this role
        stmt = select(RoleClaim).where(RoleClaim.role_id == role.id)
        result = await session.execute(stmt)
        existing_claims = {claim.claim_name: claim for claim in result.scalars().all()}
        
        # Get the set of permission names that should exist
        target_permissions = {perm.name for perm in permissions}
        existing_permission_names = set(existing_claims.keys())
        
        # Add new permissions that don't exist
        permissions_to_add = target_permissions - existing_permission_names
        for perm in permissions:
            if perm.name in permissions_to_add:
                claim = RoleClaim(
                    role_id=role.id,
                    claim_type=PermissionClaimType.PERMISSION.value,
                    claim_name=perm.name
                )
                session.add(claim)
        
        # Remove permissions that are no longer in the list
        permissions_to_remove = existing_permission_names - target_permissions
        for perm_name in permissions_to_remove:
            claim = existing_claims[perm_name]
            await session.delete(claim)
        
        await session.flush()
        
    async def seed_sa_user(self, session: AsyncSession):
        user = User(
            email="sa@example.com",
            full_name="Super Admin",
            password=get_password_hash("123456"),
            is_active=True,
            email_confirmed=True,
        )

        # Fetch the Super Admin role
        stmt_role = select(Role).where(Role.normalized_name == AppRoles.SUPER_ADMIN)
        result_role = await session.execute(stmt_role)
        super_admin_role = result_role.scalar_one_or_none()

        stmt = select(User).where(User.email == user.email)
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if not existing_user:
            session.add(user)
            await session.flush()  # Ensure the user gets an id

            if super_admin_role:
                user_role = UserRole(user_id=user.id, role_id=super_admin_role.id)
                session.add(user_role)

            await session.commit()
            self.logger.info("User seeded successfully.")
        else:
            existing_user.full_name = user.full_name
            existing_user.password = user.password
            await session.commit()
            self.logger.info("User updated successfully.")

    async def seed_system_roles(self, session: AsyncSession):
        """Seed all system roles with their respective permissions."""
        for system_role in AppRoles.all():
            # Check if role exists
            stmt = select(Role).where(Role.normalized_name == system_role.normalized_name)
            result = await session.execute(stmt)
            existing_role = result.scalar_one_or_none()
            
            if not existing_role:
                # Create new role
                self.logger.info(f"Seeding {system_role.name} role...")
                role = Role(
                    name=system_role.name,
                    normalized_name=system_role.normalized_name,
                    description=system_role.description,
                    is_system=not system_role.is_editable
                )
                session.add(role)
                await session.flush()
            else:
                # Update existing role
                role = existing_role
                role.name = system_role.name
                role.description = system_role.description
                role.is_system = not system_role.is_editable
                session.add(role)
                await session.flush()
            
            # Assign permissions based on role
            if system_role.normalized_name == AppRoles.SUPER_ADMIN:
                await self.assign_permissions_to_role(
                    session, role, AppPermissions.super_admin()
                )
            elif system_role.normalized_name == AppRoles.ADMIN:
                await self.assign_permissions_to_role(
                    session, role, AppPermissions.admin()
                )
            elif system_role.normalized_name == AppRoles.CUSTOMER:
                await self.assign_permissions_to_role(
                    session, role, AppPermissions.customer()
                )
        
        await session.commit()
        self.logger.info("System roles seeded with permissions.")