import asyncio
from typing import Optional, Dict

class UserRepository:
    # Simulated database
    _users_db = {
        "test@example.com": {
            "email": "test@example.com",
            "hashed_password": "$2b$12$wUDYNFpkySt5phBQmlTQ1OrpNn76S6/CnXoZ6Q3Blil3WL6ZEXsju",  # 123456: testpassword
            "id": 1
        }
    }

    async def get_user_name_by_id(self, user_id: int) -> str:
        await asyncio.sleep(1)
        return f"sodipto {user_id}"
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        return self._users_db.get(email)