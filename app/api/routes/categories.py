"""Endpoints for category management."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_db
from app.models import Category, User
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryRead], summary="List categories")
def list_categories(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Category]:
    """Return a list of categories available for browsing."""

    return db.query(Category).all()


@router.post("/", response_model=CategoryRead, summary="Create category")
def create_category(
    payload: CategoryCreate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Category:
    """Create a new product category. Administrator only."""

    category = Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/{category_id}", response_model=CategoryRead, summary="Retrieve category")
def get_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Category:
    """Return a single category by identifier."""

    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.patch("/{category_id}", response_model=CategoryRead, summary="Update category")
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Category:
    """Update an existing category."""

    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", response_model=CategoryRead, summary="Delete category")
def delete_category(
    category_id: int,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Category:
    """Delete a category."""

    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    db.delete(category)
    db.commit()
    return category
