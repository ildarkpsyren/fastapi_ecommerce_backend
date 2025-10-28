"""Application settings module."""
from functools import lru_cache
from typing import List, Any, Optional

from pydantic import EmailStr, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application configuration.

    The settings object centralises configuration that can be tweaked via
    environment variables. Only a subset of values is required for the
    exercise so default values are provided.
    """

    APP_NAME: str = "FastAPI E-commerce"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    VERIFICATION_EMAIL_SENDER: EmailStr | None = None

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    DATABASE_URL: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_HOST"),
            port=values.data.get("POSTGRES_PORT"),
            path=f"/{values.data.get('POSTGRES_DB') or ''}",
        )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()
