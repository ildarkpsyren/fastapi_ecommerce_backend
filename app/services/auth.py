"""Business logic for user registration, verification, and login."""
import secrets

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models import User, UserRoleEnum
from app.schemas.user import UserCreate, UserLogin
from app.services.email import send_verification_email


def register_user(db: Session, payload: UserCreate) -> User:
    """Create a new user and send a verification token via email."""

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    verification_token = secrets.token_urlsafe(32)
    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        role=UserRoleEnum.CUSTOMER,
        verification_token=verification_token,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    send_verification_email(user.email, verification_token)
    return user


def verify_user_email(db: Session, email: str, token: str) -> User:
    """Mark a user's email as verified when the token matches."""

    user = db.query(User).filter(User.email == email).first()
    if user is None or user.verification_token != token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token")
    user.is_verified = True
    user.verification_token = None
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, payload: UserLogin) -> str:
    """Validate user credentials and return an access token."""

    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")
    token = create_access_token({"sub": user.email})
    return token
