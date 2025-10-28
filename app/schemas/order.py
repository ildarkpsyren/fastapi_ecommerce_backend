"""Pydantic schemas for order operations."""
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    """Payload describing an order line item."""

    product_stock_id: int
    quantity: int = Field(gt=0)


class OrderItemRead(BaseModel):
    """Read schema for order line items."""

    id: int
    product_id: int
    quantity: int
    price_at_order: float

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    """Schema used when creating an order."""

    items: List[OrderItemCreate]


class OrderRead(BaseModel):
    """Representation of an order for responses."""

    id: int
    user_id: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemRead]

    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    """Schema to mutate order statuses."""

    status: OrderStatus
