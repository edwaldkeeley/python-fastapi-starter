import asyncpg
import asyncio
import logging
from app.core.config import settings
from typing import Optional

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
                    dsn=settings.database_url, min_size=1, max_size=10
                )
                break
            except Exception as e:
                logger.error(f"DB connection failed ({attempt+1}/{retries}): {e}")
                await asyncio.sleep(2)
        else:
            raise ConnectionError(
                "Could not connect to the database after several attempts."
            )
    return _db_pool
