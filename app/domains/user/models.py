from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password (min 8 characters)",
    )


class UserUpdate(BaseModel):
    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="User's full name"
    )
    email: Optional[EmailStr] = Field(None, description="User's email address")


class UserOut(UserBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserInDB(UserOut):
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UserWithToken(BaseModel):
    user: UserOut
    access_token: str
    token_type: str = "bearer"
