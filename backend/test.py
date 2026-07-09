from app.shared.config import settings
from sqlalchemy import text
print("Database URL:", settings.database_url)



import asyncio
from app.shared.database import engine

async def test_connection():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print("Connection OK:", result.scalar())

asyncio.run(test_connection())



import asyncio
from app.shared.dependencies import get_db_session

async def test_session():
    async_gen = get_db_session()
    session = await async_gen.__anext__()
    print("Session is:", session)
    await async_gen.aclose()

asyncio.run(test_session())