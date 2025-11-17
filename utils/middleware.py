"""
Request logging middleware for FastAPI application.
Logs all incoming requests and outgoing responses with structured data.
"""

import time
import uuid
from typing import Any, Callable, Optional

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from utils.logging_config import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log HTTP requests and responses.
    Adds request ID to each request for tracing.
    """

    def __init__(self, app: FastAPI, exclude_paths: Optional[list[str]] = None):
        """
        Initialize the middleware.

        Args:
            app: FastAPI application instance
            exclude_paths: List of paths to exclude from logging (e.g., health checks)
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Response:
        """
        Process the request and response, adding logging.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Skip logging for excluded paths
        if request.url.path in self.exclude_paths:
            response = await call_next(request)
            return response  # type: ignore

        # Start timing
        start_time = time.time()

        # Log incoming request
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent"),
                "content_type": request.headers.get("content-type"),
            },
        )

        # Add request ID to request state for use in route handlers
        request.state.request_id = request_id

        # Process request
        response = None
        status_code = 500  # Default to server error

        try:
            response = await call_next(request)
            status_code = response.status_code

        except Exception as exc:
            # Log exception
            logger.error(
                "Request failed with exception",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                },
                exc_info=True,
            )
            raise exc

        finally:
            # Calculate request duration
            duration = time.time() - start_time

            # Determine log level based on status code
            if status_code >= 500:
                log_level = "error"
            elif status_code >= 400:
                log_level = "warning"
            else:
                log_level = "info"

            # Log response
            getattr(logger, log_level)(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "response_size": response.headers.get("content-length")
                    if response
                    else None,
                },
            )

        # Add request ID to response headers for client tracking
        if response:
            response.headers["X-Request-ID"] = request_id

        return response  # type: ignore

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request.

        Args:
            request: HTTP request

        Returns:
            Client IP address
        """
        # Check for forwarded headers (when behind a proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to direct client IP
        if request.client:
            return request.client.host

        return "unknown"


class HealthCheckMiddleware(BaseHTTPMiddleware):
    """
    Simple health check middleware that responds to health check requests
    without going through the full application stack.
    """

    def __init__(self, app: FastAPI, health_path: str = "/health"):
        """
        Initialize the health check middleware.

        Args:
            app: FastAPI application instance
            health_path: Path for health check endpoint
        """
        super().__init__(app)
        self.health_path = health_path

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Response:
        """
        Handle health check requests or pass through to next middleware.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response
        """
        if request.url.path == self.health_path and request.method == "GET":
            return Response(
                content='{"status": "healthy", "service": "crud-itt"}',
                media_type="application/json",
                status_code=200,
            )

        response = await call_next(request)
        return response  # type: ignore
