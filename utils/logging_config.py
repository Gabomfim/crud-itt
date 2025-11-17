"""
Logging configuration module for the CRUD application.
Provides structured logging with JSON output for production environments.
"""

import json
import logging
import logging.config
import os
import sys
from datetime import datetime, timezone
from typing import Any, MutableMapping, Optional


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id

        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = record.duration_ms

        if hasattr(record, "status_code"):
            log_entry["status_code"] = record.status_code

        if hasattr(record, "method"):
            log_entry["method"] = record.method

        if hasattr(record, "path"):
            log_entry["path"] = record.path

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


class StructuredAdapter(logging.LoggerAdapter):
    """Adapter that adds structured data to log records."""

    def process(
        self, msg: str, kwargs: MutableMapping[str, Any]
    ) -> tuple[str, MutableMapping[str, Any]]:
        """Process log message and add extra data."""
        extra = kwargs.pop("extra", {})

        # Merge context with extra data
        if self.extra:
            for key, value in self.extra.items():
                extra[key] = value

        kwargs["extra"] = extra
        return msg, kwargs


def setup_logging(
    log_level: Optional[str] = None,
    json_logs: Optional[bool] = None,
    app_name: str = "crud-itt",
) -> None:
    """
    Configure logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Whether to output logs in JSON format
        app_name: Application name to include in logs
    """
    # Get configuration from environment variables or use defaults
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    if json_logs is None:
        json_logs = os.getenv("JSON_LOGS", "false").lower() == "true"

    # Choose formatter based on environment
    if json_logs:
        formatter_class: type[logging.Formatter] = JSONFormatter
        format_string = ""  # JSONFormatter doesn't use format string
    else:
        formatter_class = logging.Formatter
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": formatter_class,
                "format": format_string,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "default": {
                "level": log_level,
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            }
        },
        "loggers": {
            "": {  # root logger
                "level": log_level,
                "handlers": ["default"],
                "propagate": False,
            },
            app_name: {
                "level": log_level,
                "handlers": ["default"],
                "propagate": False,
            },
            "uvicorn": {
                "level": log_level,
                "handlers": ["default"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "WARNING",  # Reduce uvicorn access log noise
                "handlers": ["default"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "WARNING",  # Reduce SQL query noise in production
                "handlers": ["default"],
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)

    # Log configuration
    logger = logging.getLogger(app_name)
    logger.info(
        "Logging configured",
        extra={"log_level": log_level, "json_logs": json_logs, "app_name": app_name},
    )


def get_logger(name: Optional[str] = None) -> StructuredAdapter:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (defaults to caller's module name)

    Returns:
        Configured logger adapter for structured logging
    """
    if name is None:
        # Get the caller's module name
        frame = sys._getframe(1)
        name = frame.f_globals.get("__name__", "unknown")

    logger = logging.getLogger(name)
    return StructuredAdapter(logger, {})


# Global logger instance for convenience
logger = get_logger("crud-itt")
