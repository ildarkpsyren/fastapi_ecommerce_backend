"""User management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.user import Message, UserRead, UserRoleUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead, summary="Retrieve current user")
def get_me(current_user: User = Depends(get_current_user)) -> User:
    """Return the profile of the authenticated user."""

    return current_user


@router.get("/", response_model=list[UserRead], summary="List users")
def list_users(
    _: User = Depends(get_current_admin), db: Session = Depends(get_db)
) -> list[User]:
    """Return all users. Only administrators can access this endpoint."""

    return db.query(User).all()


@router.patch("/{user_id}/role", response_model=Message, summary="Update user role")
def update_role(
    user_id: int,
    payload: UserRoleUpdate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Message:
    """Allow administrators to update the role of any user."""

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.role = payload.role
    db.add(user)
    db.commit()
    return Message(detail="User role updated")
