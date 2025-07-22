import asyncio


class UserRepository:
    async def get_user_name_by_id(self, user_id: int) -> str:
        await asyncio.sleep(1)
        return f"sodipto {user_id}"
