"""Database model for application users."""
from datetime import datetime
from enum import Enum
from typing import List

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class UserRoleEnum(str, Enum):
    """Enumeration of supported user roles."""

    ADMIN = "admin"
    CUSTOMER = "customer"


class User(Base):
    """Application user model.

    The model stores user credentials, the assigned role, and metadata used for
    email verification.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(512), nullable=False)
    role: Mapped[UserRoleEnum] = mapped_column(
        SqlEnum(UserRoleEnum), default=UserRoleEnum.CUSTOMER
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_token: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user")
