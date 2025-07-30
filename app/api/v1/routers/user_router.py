from fastapi import APIRouter, HTTPException, status
from app.domains.user.service import (
    fetch_user,
    create_user,
    get_all_users,
    update_user_service,
    delete_user,
    UserNotFoundError,  # Import the custom exception
)
from app.domains.user.models import UserCreate, UserOut, UserUpdate
from typing import List
from uuid import UUID

router = APIRouter(tags=["Users"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user: UserCreate):
    """Create a new user with email and password."""
    user_id = await create_user(user)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create user"
        )
    created_user = await fetch_user(user_id)
    if created_user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User created but could not be retrieved",
        )
    return created_user


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: UUID):
    """Get a user by ID."""
    user = await fetch_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.delete("/{user_id}", response_model=dict)
async def delete_user_route(user_id: UUID):
    """Delete a user by ID. Returns a message on success, or 404 if not found."""
    deleted = await delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return {"message": "User deleted successfully"}


@router.patch("/{user_id}", response_model=dict)
async def update_user_route(user_id: UUID, user_update: UserUpdate):
    """Update a user's name or email."""
    if user_update.name is None and user_update.email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field (name or email) is required for update",
        )
    try:
        success = await update_user_service(user_id, user_update)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update failed. No fields updated or unknown error.",
            )
        return {"message": "User updated successfully"}
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )


@router.get("/", response_model=List[UserOut])
async def fetch_users():
    """Get all users."""
    return await get_all_users()
