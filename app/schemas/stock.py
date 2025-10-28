"""Schemas for stock resources."""
from pydantic import BaseModel, Field


class StockBase(BaseModel):
    """Base attributes for stock locations."""

    location: str = Field(max_length=255)

    model_config = {"from_attributes": True}


class StockCreate(StockBase):
    """Schema for creating stock locations."""


class StockRead(StockBase):
    """Read representation of a stock location."""

    id: int


class ProductStockBase(BaseModel):
    """Shared attributes for product stock records."""

    product_id: int
    stock_id: int
    qty: int
    sale_price: float

    model_config = {"from_attributes": True}


class ProductStockCreate(ProductStockBase):
    """Schema for creating product stock entries."""


class ProductStockUpdate(BaseModel):
    """Schema for updating price and quantity from sync or manual changes."""

    qty: int | None = None
    sale_price: float | None = None


class ProductStockRead(ProductStockBase):
    """Read representation of product stock entries."""

    id: int


class ProductStockSyncRequest(BaseModel):
    """Request schema for syncing product stock."""

    product_stock_ids: list[int]
