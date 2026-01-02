from app.core.database.session import async_session
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.utils.auth_utils import get_password_hash

class ApplicationSeeder:
    def __init__(self):
        self.seeders = [
            self.seed_admin_user
        ]

    async def seed_data(self):
        async with async_session() as session:
            for seeder in self.seeders:
                await seeder(session)

    async def seed_admin_user(self, session: AsyncSession):
        user = User(
            Email="sa@example.com",
            FullName="Super Admin",
            Hashed_Password=get_password_hash("123456"),
        )
        stmt = select(User).where(User.Email == user.Email)
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if not existing_user:
            session.add(user)
            await session.commit()
            print("User seeded successfully.")
        else:
            existing_user.FullName = user.FullName
            existing_user.Hashed_Password = user.Hashed_Password
            session.add(existing_user)
            await session.commit()
            print("User updated successfully.")