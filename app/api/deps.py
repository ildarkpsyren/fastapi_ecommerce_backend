"""Reusable FastAPI dependencies."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.db.session import get_db
from app.models import User, UserRoleEnum

security = HTTPBearer()


def get_current_user(
    credentials=Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Return the currently authenticated user based on the JWT token."""

    token = credentials.credentials
    try:
        payload = verify_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    email: str | None = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure that the current user has administrative privileges."""

    if current_user.role != UserRoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
