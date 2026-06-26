import asyncio
from database import SessionLocal
from sqlalchemy import text

async def check():
    async with SessionLocal() as db:
        res = await db.execute(text("SELECT COUNT(*) FROM doctors"))
        print(res.scalar())

asyncio.run(check())
