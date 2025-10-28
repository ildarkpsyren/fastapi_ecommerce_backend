"""Authentication and registration endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.user import Message, Token, UserCreate, UserLogin, VerificationRequest
from app.services.auth import authenticate_user, register_user, verify_user_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Message, summary="Register a new user")
def register(payload: UserCreate, db: Session = Depends(get_db)) -> Message:
    """Register a new customer and trigger the email verification flow."""

    register_user(db, payload)
    return Message(detail="Verification email sent. Please verify your account before logging in.")


@router.post("/verify", response_model=Token, summary="Verify user email")
def verify(payload: VerificationRequest, db: Session = Depends(get_db)) -> Token:
    """Verify the email address using the token that was sent by email."""

    user = verify_user_email(db, payload.email, payload.token)
    token = create_access_token({"sub": user.email})
    return Token(access_token=token)


@router.post("/login", response_model=Token, summary="Authenticate a user")
def login(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    """Issue a JWT access token for verified users."""

    token = authenticate_user(db, payload)
    return Token(access_token=token)
