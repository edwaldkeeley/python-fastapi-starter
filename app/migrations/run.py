import os
import asyncio
from app.core.db import get_db_pool

MIGRATIONS_DIR = os.path.dirname(__file__)

async def run_migrations():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        for filename in sorted(os.listdir(MIGRATIONS_DIR)):
            if filename.endswith(".sql"):
                filepath = os.path.join(MIGRATIONS_DIR, filename)
                with open(filepath, "r") as f:
                    sql = f.read()
                    await conn.execute(sql)
                    print(f"✅ Ran {filename}")

if __name__ == "__main__":
    asyncio.run(run_migrations())