"""Pydantic schemas for categories."""
from datetime import datetime

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    """Shared category attributes."""

    name: str = Field(max_length=128)
    description: str | None = Field(default=None, max_length=512)

    model_config = {"from_attributes": True}


class CategoryCreate(CategoryBase):
    """Schema for creating categories."""


class CategoryUpdate(BaseModel):
    """Schema for updating categories."""

    name: str | None = Field(default=None, max_length=128)
    description: str | None = Field(default=None, max_length=512)


class CategoryRead(CategoryBase):
    """Read-only representation of a category."""

    id: int
    created_at: datetime
    updated_at: datetime
