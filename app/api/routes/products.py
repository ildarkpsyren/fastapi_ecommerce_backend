"""Endpoints for product management."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_db
from app.models import Product, User
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductRead], summary="List products")
def list_products(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Product]:
    """List all products available in the catalogue."""

    return db.query(Product).all()


@router.post("/", response_model=ProductRead, summary="Create product")
def create_product(
    payload: ProductCreate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Product:
    """Create a new product. Only administrators may perform this action."""

    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductRead, summary="Retrieve product")
def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Product:
    """Retrieve a single product by identifier."""

    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.patch("/{product_id}", response_model=ProductRead, summary="Update product")
def update_product(
    product_id: int,
    payload: ProductUpdate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Product:
    """Update product details."""

    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", response_model=ProductRead, summary="Delete product")
def delete_product(
    product_id: int,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Product:
    """Delete a product."""

    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return product
