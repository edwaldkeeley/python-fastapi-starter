import logging

logger = logging.getLogger("user_service")

from app.domains.user.repository import (
    get_user_by_id,
    get_user_by_email,
    create_user as repo_create_user,
    update_user as repo_update_user,
    delete_user_by_id,
    get_all_users as repo_get_all_users,
    user_exists,
)
from app.domains.user.models import UserCreate, UserOut, UserUpdate
from app.core.security import hash_password
from uuid import UUID, uuid4
from typing import List, Optional


class UserNotFoundError(Exception):
    pass


async def fetch_user(user_id: UUID) -> Optional[UserOut]:
    """Fetch a user by ID"""
    try:
        row = await get_user_by_id(user_id)
        if row:
            return UserOut(**row)
        return None
    except Exception:
        return None


async def fetch_user_by_email(email: str) -> Optional[UserOut]:
    """Fetch a user by email"""
    try:
        row = await get_user_by_email(email)
        if row:
            return UserOut(**row)
        return None
    except Exception:
        return None


async def update_user_service(user_id: UUID, user_update: UserUpdate) -> bool:
    """Update user information (name and/or email)"""
    try:
        exists = await user_exists(user_id)
        logger.info(f"update_user_service: user_exists({user_id}) = {exists}")
        if not exists:
            logger.warning(f"update_user_service: user_id {user_id} not found")
            raise UserNotFoundError(f"User with id {user_id} not found")
        if user_update.name is None and user_update.email is None:
            return False
        return await repo_update_user(user_id, user_update.name, user_update.email)
    except UserNotFoundError:
        raise
    except Exception as e:
        logger.error(f"update_user_service error: {e}")
        return False


async def delete_user(user_id: UUID) -> bool:
    """Delete a user by ID. Returns True if deleted, False if not found."""
    try:
        exists = await user_exists(user_id)
        logger.info(f"delete_user: user_exists({user_id}) = {exists}")
        if not exists:
            logger.warning(f"delete_user: user_id {user_id} not found")
            return False
        return await delete_user_by_id(user_id)
    except Exception as e:
        logger.error(f"delete_user error: {e}")
        return False


async def create_user(user: UserCreate) -> Optional[UUID]:
    """Create a new user with email"""
    try:
        user_id = uuid4()
        hashed_password = hash_password(user.password)
        success = await repo_create_user(
            user_id, user.name, user.email, hashed_password
        )
        if success:
            return user_id
        return None
    except Exception:
        return None


async def get_all_users() -> List[UserOut]:
    """Get all users"""
    try:
        rows = await repo_get_all_users()
        return [UserOut(**row) for row in rows]
    except Exception:
        return []


async def get_user_by_id_with_password(user_id: UUID) -> Optional[dict]:
    """Get user with password for authentication purposes"""
    try:
        from app.domains.user.repository import (
            get_user_by_id_with_password as repo_get_user_with_password,
        )

        return await repo_get_user_with_password(user_id)
    except Exception:
        return None
