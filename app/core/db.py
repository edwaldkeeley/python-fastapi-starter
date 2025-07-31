import asyncpg
import asyncio
import logging
from typing import Optional, Callable, Any, Awaitable
from app.core.config import settings

_db_pool: Optional[asyncpg.Pool] = None  # Global singleton pool
logger = logging.getLogger("db")


async def get_db_pool() -> asyncpg.Pool:
    """Get or create the global asyncpg connection pool."""
    global _db_pool
    if _db_pool is None:
        retries = 5
        for attempt in range(retries):
            try:
                _db_pool = await asyncpg.create_pool(
                    user="postgres",
                    password="password",
                    database="app_db",
                    host="db",
                    port=5432,
                    min_size=1,
                    max_size=10,
                )
                break
            except Exception as e:
                print(f"DB connection failed ({attempt+1}/{retries}): {e}")
                await asyncio.sleep(2)
        else:
            raise ConnectionError(
                "Could not connect to the database after several attempts."
            )
    return _db_pool


async def db_query(query_func: Callable[[Any], Awaitable[Any]]) -> Any:
    """Helper to acquire a DB connection and run a query_func(conn)."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        return await query_func(conn)
