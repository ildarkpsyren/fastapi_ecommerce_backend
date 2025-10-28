"""Global exception handlers for the application."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InvalidRequestError,
    NoResultFound,
)
import logging

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""

    logger.warning(f"Validation error on {request.method} {request.url}: {exc.errors()}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle SQLAlchemy exceptions and return user-friendly error messages."""
    
    logger.error(f"Database error on {request.method} {request.url}: {str(exc)}")
    
    if isinstance(exc, IntegrityError):
        # Foreign key violations, unique constraints, etc.
        error_message = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
        
        if "ForeignKeyViolation" in error_message or "foreign key constraint" in error_message.lower():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": "Referenced resource does not exist",
                    "error_type": "ForeignKeyViolation",
                    "sql_error": error_message
                }
            )
        elif "UniqueViolation" in error_message or "unique constraint" in error_message.lower():
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "detail": "Resource with this value already exists",
                    "error_type": "UniqueViolation",
                    "sql_error": error_message
                }
            )
        elif "NotNullViolation" in error_message or "not-null constraint" in error_message.lower():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": "Required field is missing",
                    "error_type": "NotNullViolation",
                    "sql_error": error_message
                }
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": "Database integrity error",
                    "error_type": "IntegrityError",
                    "sql_error": error_message
                }
            )
    
    elif isinstance(exc, DataError):
        error_message = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "Invalid data format",
                "error_type": "DataError",
                "sql_error": error_message
            }
        )
    
    elif isinstance(exc, NoResultFound):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": "Resource not found",
                "error_type": "NoResultFound"
            }
        )
    
    elif isinstance(exc, DatabaseError):
        error_message = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
        logger.exception("Unexpected database error")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Database error occurred",
                "error_type": "DatabaseError",
                "sql_error": error_message
            }
        )
    
    else:
        logger.exception("Unexpected error")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An unexpected error occurred",
                "error_type": type(exc).__name__
            }
        )