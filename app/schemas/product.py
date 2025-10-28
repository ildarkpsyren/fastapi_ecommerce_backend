"""Pydantic schemas for product resources."""
from datetime import datetime

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    """Base product payload."""

    name: str = Field(max_length=255)
    barcode: str = Field(max_length=64)
    description: str | None = None
    category_id: int

    model_config = {"from_attributes": True}


class ProductCreate(ProductBase):
    """Schema for creating products."""


class ProductUpdate(BaseModel):
    """Schema for updating products."""

    name: str | None = Field(default=None, max_length=255)
    barcode: str | None = Field(default=None, max_length=64)
    description: str | None = None
    category_id: int | None = None


class ProductRead(ProductBase):
    """Read representation of a product."""

    id: int
    created_at: datetime
    updated_at: datetime
