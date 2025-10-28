"""Database session and engine helpers."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()

# Create sync engine for PostgreSQL
database_url = str(settings.DATABASE_URL).replace("postgresql+asyncpg", "postgresql")
engine = create_engine(database_url, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
