import asyncio
from typing import Optional, Dict

class UserRepository:
    # Simulated database
    _users_db = {
        "test@example.com": {
            "email": "test@example.com",
            "hashed_password": "$2b$12$LQP.ZG5eX0HLi3TJ4o5VX.7yGHIKPwNq8zUHJyZYHzHONZCmDyXqq",  # password: testpassword
            "id": 1
        }
    }

    async def get_user_name_by_id(self, user_id: int) -> str:
        await asyncio.sleep(1)
        return f"sodipto {user_id}"
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        return self._users_db.get(email)