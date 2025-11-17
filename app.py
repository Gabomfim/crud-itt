import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import Response as StarletteResponse

from api.v1.api import api_router
from database.connection import init_database
from utils.logging_config import get_logger, setup_logging
from utils.middleware import HealthCheckMiddleware, RequestLoggingMiddleware

# Setup logging before anything else
setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    json_logs=os.getenv("JSON_LOGS", "false").lower() == "true",
    app_name="crud-itt",
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
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
    title="User Management API",
    description="A comprehensive API for managing users with full CRUD operations",
    version="1.0.0",
    lifespan=lifespan,
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
    logger.info("Serving root page")
    return templates.TemplateResponse("index.html", {"request": request})


# Custom error handler for non-API 404s only
@app.middleware("http")
async def custom_404_middleware(
    request: Request, call_next: Callable[[Request], Any]
) -> Response:
    try:
        response = await call_next(request)
        # If it's a 404 on a non-API route, return custom HTML page
        if response.status_code == 404 and not request.url.path.startswith("/api/"):
            logger.info(
                "Serving custom 404 page",
                extra={"path": request.url.path, "method": request.method},
            )
            return templates.TemplateResponse(
                "404.html", {"request": request}, status_code=404
            )
        return response  # type: ignore
    except Exception as e:
        logger.error(
            "Unhandled exception in middleware",
            extra={"path": request.url.path, "method": request.method, "error": str(e)},
            exc_info=True,
        )
        # Let FastAPI handle all exceptions normally
        raise e
