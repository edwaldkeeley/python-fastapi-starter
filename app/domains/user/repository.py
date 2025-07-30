from pypika import Query, Table, functions as fn
from uuid import UUID
from typing import Optional, List, Dict, Any
from app.core.db import get_db_pool
from app.domains.user.models import UserOut, UserInDB
import logging

logger = logging.getLogger("user_repository")

# Define table once to avoid duplication
users_table = Table("users")


async def get_user_by_id(user_id: UUID) -> Optional[Dict[str, Any]]:
    """Get user by ID from database"""
    db = await get_db_pool()
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
    async with db.acquire() as conn:
        row = await conn.fetchrow(str(q))
        return dict(row) if row else None


async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email from database"""
    db = await get_db_pool()
    q = (
        Query.from_(users_table)
        .select(
            users_table.id,
            users_table.name,
            users_table.email,
            users_table.created_at,
            users_table.updated_at,
        )
        .where(users_table.email == email)
    )
    async with db.acquire() as conn:
        row = await conn.fetchrow(str(q))
        return dict(row) if row else None


async def get_user_by_id_with_password(user_id: UUID) -> Optional[Dict[str, Any]]:
    """Get user by ID with password from database"""
    db = await get_db_pool()
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
    async with db.acquire() as conn:
        row = await conn.fetchrow(str(q))
        return dict(row) if row else None


async def update_user(
    user_id: UUID, name: Optional[str] = None, email: Optional[str] = None
) -> bool:
    """Update user information"""
    db = await get_db_pool()
    if name is None and email is None:
        return False
    q = Query.update(users_table)
    if name is not None:
        q = q.set(users_table.name, name)
    if email is not None:
        q = q.set(users_table.email, email)
    q = q.set(users_table.updated_at, fn.Now())
    q = q.where(users_table.id == user_id)
    async with db.acquire() as conn:
        result = await conn.execute(str(q))
        return result is not None


async def create_user(user_id: UUID, name: str, email: str, password: str) -> bool:
    """Create a new user"""
    query = """
        INSERT INTO users (id, name, email, password, created_at, updated_at)
        VALUES ($1, $2, $3, $4, NOW(), NOW())
    """
    pool = await get_db_pool()
    try:
        await pool.execute(query, user_id, name, email, password)
        return True
    except Exception:
        return False


async def delete_user_by_id(user_id: UUID) -> bool:
    """Delete user by ID. Returns True if a user was deleted, False otherwise."""
    db = await get_db_pool()
    q = Query.from_(users_table).delete().where(users_table.id == user_id)
    async with db.acquire() as conn:
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


async def get_all_users() -> List[Dict[str, Any]]:
    """Get all users from database"""
    db = await get_db_pool()
    q = Query.from_(users_table).select(
        users_table.id,
        users_table.name,
        users_table.email,
        users_table.created_at,
        users_table.updated_at,
    )
    async with db.acquire() as conn:
        rows = await conn.fetch(str(q))
        return [dict(row) for row in rows]


async def user_exists(user_id: UUID) -> bool:
    """Check if user exists"""
    db = await get_db_pool()
    q = Query.from_(users_table).select(users_table.id).where(users_table.id == user_id)
    async with db.acquire() as conn:
        row = await conn.fetchrow(str(q))
        exists = row is not None
        logger.info(f"user_exists check for id={user_id}: {exists}")
        return exists
