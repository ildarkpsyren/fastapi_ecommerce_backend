"""Application settings module."""
from functools import lru_cache
from typing import List

from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application configuration.

    The settings object centralises configuration that can be tweaked via
    environment variables. Only a subset of values is required for the
    exercise so default values are provided.
    """

    app_name: str = "FastAPI E-commerce"
    secret_key: str = "super-secret-key"
    access_token_expire_minutes: int = 60 * 24
    algorithm: str = "HS256"
    backend_cors_origins: List[str] = ["*"]
    verification_email_sender: EmailStr | None = None

    database_url: str = "sqlite:///./dev.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()
