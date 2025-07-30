from app.core.db import get_db_pool
import logging

logger = logging.getLogger("db_init")


async def init_db_schema() -> None:
    """Initialize the database schema or run migrations."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        try:
            # Put your schema creation or migration logic here if needed
            pass
        except Exception as e:
            logger.error(f"Error initializing DB schema: {e}")
