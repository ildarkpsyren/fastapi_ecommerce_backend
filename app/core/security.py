"""Security helpers for authentication and password hashing."""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def create_access_token(data: Dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token."""

    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """Decode a JWT token and return its payload."""

    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.PyJWTError as exc:  # pragma: no cover - defensive branch
        raise ValueError("Invalid token") from exc
    return payload


def get_password_hash(password: str) -> str:
    """Return a password hash using Argon2."""

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hash."""

    return pwd_context.verify(plain_password, hashed_password)
