"""FastAPI application entry-point."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.exceptions import sqlalchemy_exception_handler, validation_exception_handler
from app.core.middleware import RequestLoggingMiddleware

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title=settings.APP_NAME,
    swagger_ui_parameters={
        "persistAuthorization": True,
    },
)

app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.add_middleware(RequestLoggingMiddleware)

security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
