"""Pydantic schemas related to users and authentication."""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRoleEnum


class UserBase(BaseModel):
    """Base schema shared across user representations."""

    email: EmailStr
    role: UserRoleEnum
    is_active: bool
    is_verified: bool

    model_config = {"from_attributes": True}


class UserRead(UserBase):
    """Full representation of a user for API responses."""

    id: int
    created_at: datetime


class UserCreate(BaseModel):
    """Payload required for user registration."""

    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    """Login request payload."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Response returned upon successful authentication."""

    access_token: str
    token_type: str = "bearer"


class UserRoleUpdate(BaseModel):
    """Request schema for updating a user's role."""

    role: UserRoleEnum


class VerificationRequest(BaseModel):
    """Payload used to confirm the email address of a newly registered user."""

    email: EmailStr
    token: str


class Message(BaseModel):
    """Simple message response schema."""

    detail: str
