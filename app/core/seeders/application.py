from app.core.database.session import async_session
from app.models.role import Role
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user_role import UserRole
from app.utils.auth_utils import get_password_hash

class ApplicationSeeder:
    def __init__(self):
        self.seeders = [
            self.seed_sa_role,
            self.seed_admin_user
        ]

    async def seed_data(self):
        async with async_session() as session:
            for seeder in self.seeders:
                await seeder(session)

    async def seed_admin_user(self, session: AsyncSession):
        user = User(
            email="sa@example.com",
            full_name="Super Admin",
            password=get_password_hash("123456"),
        )

        # Fetch the Super Admin role
        stmt_role = select(Role).where(Role.normalized_name == "SUPER_ADMIN")
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
            print("User seeded successfully.")
        else:
            existing_user.full_name = user.full_name
            existing_user.password = user.password
            session.add(existing_user)
            await session.commit()
            print("User updated successfully.")

    async def seed_sa_role(self, session: AsyncSession):
        role = Role(
            name="Super Admin",
            normalized_name="SUPER_ADMIN",
            description="Role with all permissions",
            is_system=True
        )

        stmt = select(Role).where(Role.normalized_name == role.normalized_name)
        result = await session.execute(stmt)
        existing_role = result.scalar_one_or_none()

        if not existing_role:
            session.add(role)
            await session.commit()
            print("Super Admin role seeded successfully.")
        else:
            existing_role.name = role.name
            existing_role.description = role.description
            existing_role.is_system = role.is_system
            session.add(existing_role)
            await session.commit()
            print("Super Admin role updated successfully.")