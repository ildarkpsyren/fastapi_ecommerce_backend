"""Endpoints for managing stock locations and product stock levels."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_db
from app.models import ProductStock, Stock, User
from app.schemas.stock import (
    ProductStockCreate,
    ProductStockRead,
    ProductStockSyncRequest,
    ProductStockUpdate,
    StockCreate,
    StockRead,
)
from app.services.sync import sync_product_stock_from_external_api

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/", response_model=list[StockRead], summary="List stock locations")
def list_stocks(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Stock]:
    """Return all stock locations."""

    return db.query(Stock).all()


@router.post("/", response_model=StockRead, summary="Create stock location")
def create_stock(
    payload: StockCreate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Stock:
    """Create a new stock location. Only administrators can perform this action."""

    stock = Stock(**payload.model_dump())
    db.add(stock)
    db.commit()
    db.refresh(stock)
    return stock


@router.post(
    "/product-stock",
    response_model=ProductStockRead,
    summary="Create product stock entry",
)
def create_product_stock(
    payload: ProductStockCreate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProductStock:
    """Create a new product stock association."""

    product_stock = ProductStock(**payload.model_dump())
    db.add(product_stock)
    db.commit()
    db.refresh(product_stock)
    return product_stock


@router.patch(
    "/product-stock/{product_stock_id}",
    response_model=ProductStockRead,
    summary="Update product stock",
)
def update_product_stock(
    product_stock_id: int,
    payload: ProductStockUpdate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProductStock:
    """Update product stock quantity or price. Intended primarily for sync results."""

    product_stock = db.query(ProductStock).filter(ProductStock.id == product_stock_id).first()
    if product_stock is None:
        raise HTTPException(status_code=404, detail="Product stock not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product_stock, field, value)
    db.add(product_stock)
    db.commit()
    db.refresh(product_stock)
    return product_stock


@router.get(
    "/product-stock",
    response_model=list[ProductStockRead],
    summary="List product stock entries",
)
def list_product_stock(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[ProductStock]:
    """List product stock entries across all locations."""

    return db.query(ProductStock).all()


@router.post(
    "/product-stock/sync",
    response_model=list[ProductStockRead],
    summary="Sync product stock from external API",
)
def sync_product_stock(
    payload: ProductStockSyncRequest,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[ProductStock]:
    """Sync product stock price and quantity values via the mocked external API."""

    updated = sync_product_stock_from_external_api(db, payload.product_stock_ids)
    return updated
