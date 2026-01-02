import asyncio
import asyncpg

async def test_connection():
    conn = await asyncpg.connect("postgresql://postgres:123456@localhost:5432/fastapi_boilerplate_dev")
    print("✅ Connected to DB successfully!")
    await conn.close()

asyncio.run(test_connection())
