from app.domains.user.repository import get_user_by_id
from uuid import UUID


async def user_exists_checker(user_id: UUID) -> bool:
    user = await get_user_by_id(user_id)
    return user is not None
