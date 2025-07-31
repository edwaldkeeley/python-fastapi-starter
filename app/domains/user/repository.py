from pypika import Query, Table, functions as fn
from uuid import UUID
from typing import Optional, List, Dict, Any
from app.core.db import db_query
from app.core.logger import get_logger

logger = get_logger("user_repository")

# Define table once to avoid duplication
users_table = Table("users")


async def get_user_by_id(user_id: UUID) -> Optional[Dict[str, Any]]:
    """Get user by ID from database"""

    async def query(conn):
        q = (
            Query.from_(users_table)
            .select(
                users_table.id,
                users_table.name,
                users_table.email,
                users_table.created_at,
                users_table.updated_at,
            )
            .where(users_table.id == user_id)
        )
        row = await conn.fetchrow(str(q))
        return dict(row) if row else None

    return await db_query(query)


async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email from database"""

    async def query(conn):
        q = (
            Query.from_(users_table)
            .select(
                users_table.id,
                users_table.name,
                users_table.email,
                users_table.password,
                users_table.created_at,
                users_table.updated_at,
            )
            .where(users_table.email == email)
        )
        row = await conn.fetchrow(str(q))
        return dict(row) if row else None

    return await db_query(query)


async def get_user_by_id_with_password(user_id: UUID) -> Optional[Dict[str, Any]]:
    """Get user by ID with password from database"""

    async def query(conn):
        q = (
            Query.from_(users_table)
            .select(
                users_table.id,
                users_table.name,
                users_table.email,
                users_table.password,
                users_table.created_at,
                users_table.updated_at,
            )
            .where(users_table.id == user_id)
        )
        row = await conn.fetchrow(str(q))
        return dict(row) if row else None

    return await db_query(query)


async def update_user(
    user_id: UUID, name: Optional[str] = None, email: Optional[str] = None
) -> bool:
    """Update user information"""
    if name is None and email is None:
        return False

    async def query(conn):
        q = Query.update(users_table)
        if name is not None:
            q = q.set(users_table.name, name)

        if email is not None:
            q = q.set(users_table.email, email)

        q = q.set(users_table.updated_at, fn.Now())
        q = q.where(users_table.id == user_id)
        result = await conn.execute(str(q))
        return result is not None

    return await db_query(query)


async def create_user(user_id: UUID, name: str, email: str, password: str) -> bool:
    """Create a new user"""
    sql = """
        INSERT INTO users (id, name, email, password, created_at, updated_at)
        VALUES ($1, $2, $3, $4, NOW(), NOW())
    """

    async def query(conn):
        await conn.execute(sql, user_id, name, email, password)
        return True

    return await db_query(query)


async def delete_user_by_id(user_id: UUID) -> bool:
    """Delete user by ID. Returns True if a user was deleted, False otherwise."""

    async def query(conn):
        q = Query.from_(users_table).delete().where(users_table.id == user_id)
        result = await conn.execute(str(q))
        # asyncpg returns a string like 'DELETE 1' if a row was deleted
        if isinstance(result, str) and result.startswith("DELETE"):
            deleted_count = int(result.split(" ")[1])
            logger.info(
                f"delete_user_by_id for id={user_id}: deleted_count={deleted_count}"
            )
            return deleted_count > 0
        logger.info(f"delete_user_by_id for id={user_id}: deleted_count=0")
        return False

    return await db_query(query)


async def get_all_users() -> List[Dict[str, Any]]:
    """Get all users from database"""

    async def query(conn):
        q = Query.from_(users_table).select(
            users_table.id,
            users_table.name,
            users_table.email,
            users_table.created_at,
            users_table.updated_at,
        )
        rows = await conn.fetch(str(q))
        return [dict(row) for row in rows]

    return await db_query(query)


async def user_exists(user_id: UUID) -> bool:
    """Check if user exists"""
    user = await get_user_by_id(user_id)
    exists = user is not None
    logger.info(f"user_exists check for id={user_id}: {exists}")
    return exists
