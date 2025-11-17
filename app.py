"""
FastAPI Application Entry Point

This module contains the main FastAPI application configuration and setup.
It initializes the database, configures middleware, sets up routing, and
handles application lifecycle events.

Key Features:
- Async database initialization
- CORS middleware configuration
- Request logging and health check middleware
- Static file serving and HTML template rendering
- Custom 404 error handling
- Comprehensive logging setup

Author: Gabomfim
License: MIT
"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import Response as StarletteResponse
from starlette.templating import _TemplateResponse

from api.v1.api import api_router
from config import settings
from database.connection import init_database
from utils.logging_config import get_logger, setup_logging
from utils.middleware import HealthCheckMiddleware, RequestLoggingMiddleware


def render_template(
    request: Request, template_name: str, status_code: int = 200
) -> _TemplateResponse:
    """Helper function to render templates with proper typing"""
    return templates.TemplateResponse(
        request, template_name, status_code=status_code
    )  # type: ignore


# Setup logging using Pydantic settings
setup_logging(app_name=settings.app.name)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage the application lifecycle with startup and shutdown events.

    This function handles database initialization on startup and cleanup
    on shutdown. It uses an async context manager to ensure proper
    resource management.

    Args:
        app (FastAPI): The FastAPI application instance

    Yields:
        None: Control is yielded during application runtime

    Raises:
        Exception: Any exception during database initialization

    Example:
        This function is automatically called by FastAPI during
        application startup and shutdown.
    """
    # Log application startup
    logger.info("Application starting up")

    try:
        # Initialize database on startup
        await init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(
            "Failed to initialize database", extra={"error": str(e)}, exc_info=True
        )
        raise

    logger.info("Application startup completed")
    yield

    # Log application shutdown
    logger.info("Application shutting down")


app = FastAPI(
    title=settings.app.name,
    description=settings.app.description,
    version=settings.app.version,
    debug=settings.app.debug,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.cors_origins,
    allow_credentials=True,
    allow_methods=settings.app.cors_methods,
    allow_headers=settings.app.cors_headers,
)

# Add logging middleware
app.add_middleware(RequestLoggingMiddleware, exclude_paths=["/health", "/metrics"])
app.add_middleware(HealthCheckMiddleware, health_path="/health")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include API v1 routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request) -> StarletteResponse:
    """
    Serve the root HTML page of the application.

    This endpoint serves the main landing page using Jinja2 templates.
    It provides a user-friendly interface with application information
    and navigation links.

    Args:
        request (Request): The FastAPI request object containing client information

    Returns:
        StarletteResponse: Rendered HTML template with application content

    Example:
        GET / HTTP/1.1
        Host: localhost:8000

        Response: HTML page with application interface
    """
    logger.info("Serving root page")
    return render_template(request, "index.html")


# Custom error handler for non-API 404s only
@app.middleware("http")
async def custom_404_middleware(
    request: Request, call_next: Callable[[Request], Any]
) -> Response:
    """
    Custom middleware to handle 404 errors with HTML responses.

    This middleware intercepts 404 errors and returns a custom HTML
    error page when the client accesses non-API routes. For API requests,
    it lets the default JSON error response through.

    Args:
        request (Request): The incoming HTTP request
        call_next (Callable): The next middleware or endpoint in the chain

    Returns:
        Response: Either the original response or custom 404 HTML page

    Raises:
        Exception: Re-raises any unhandled exceptions after logging

    Example:
        GET /nonexistent-page HTTP/1.1
        Accept: text/html

        Response: Custom 404 HTML page
    """
    try:
        response = await call_next(request)
        # If it's a 404 on a non-API route, return custom HTML page
        if response.status_code == 404 and not request.url.path.startswith("/api/"):
            logger.info(
                "Serving custom 404 page",
                extra={"path": request.url.path, "method": request.method},
            )
            return render_template(request, "404.html", status_code=404)
        return response  # type: ignore
    except Exception as e:
        logger.error(
            "Unhandled exception in middleware",
            extra={"path": request.url.path, "method": request.method, "error": str(e)},
            exc_info=True,
        )
        # Let FastAPI handle all exceptions normally
        raise e
