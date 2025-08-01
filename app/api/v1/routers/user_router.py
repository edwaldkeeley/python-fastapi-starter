from fastapi import APIRouter, HTTPException, status, Depends
from app.api.deps import get_current_user
from app.domains.user.service import (
    fetch_user,
    create_user,
    get_all_users,
    update_user_service,
    delete_user,
    UserNotFoundError,  # Import the custom exception
)
from app.domains.user.models import (
    UserCreate,
    UserOut,
    UserUpdate,
    UserWithToken,
    LoginRequest,
)
from typing import List
from uuid import UUID
from app.core.jwt import create_access_token
from app.domains.user.repository import get_user_by_email
from app.core.security import verify_password

router = APIRouter(tags=["Users"])


@router.post("/", response_model=UserWithToken, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user: UserCreate):
    """Create a new user with email and password."""
    existing_user = await get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

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
    token = create_access_token({"sub": str(user_id)})
    return UserWithToken(user=created_user, access_token=token)


@router.get("/profile", response_model=UserOut)
async def get_profile(current_user: UserOut = Depends(get_current_user)):
    """Get authenticated user's profile."""
    return current_user


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


@router.post("/login", response_model=UserWithToken)
async def login(data: LoginRequest):
    user = await get_user_by_email(data.email)
    if user is None or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Convert to UserOut model to ensure consistent format
    user_out = UserOut(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        created_at=user["created_at"],
        updated_at=user["updated_at"],
    )
    token = create_access_token({"sub": str(user["id"])})
    return UserWithToken(user=user_out, access_token=token)
