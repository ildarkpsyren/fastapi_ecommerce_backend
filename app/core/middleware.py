"""Middleware for logging requests and responses."""
import logging
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all incoming requests and outgoing responses."""
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and log information."""
        
        # Log request
        start_time = time.time()
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"Query params: {dict(request.query_params)}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"Status: {response.status_code} "
                f"Duration: {process_time:.3f}s"
            )
            
            # Add custom headers
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} "
                f"Exception: {type(e).__name__}: {str(e)} "
                f"Duration: {process_time:.3f}s"
            )
            raise

