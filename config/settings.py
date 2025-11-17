"""
Application Configuration Management Module

This module provides comprehensive, type-safe configuration management using
Pydantic models and environment variables. It centralizes all application
settings with proper validation, type checking, and documentation.

Key Features:
- Type-safe environment variable loading
- Comprehensive validation with sensible defaults
- Organized settings categories (app, database, security, server, etc.)
- Easy access patterns with property-based getters
- Production-ready configuration management

Configuration Categories:
- Application: Basic app metadata and environment settings
- Database: Connection strings, pool settings, and database configuration
- Security: Password policies, JWT settings, and authentication configuration
- Server: Host, port, worker, and performance settings
- CORS: Cross-origin resource sharing configuration
- Logging: Log levels and output configuration

Environment Variables:
All settings can be overridden via environment variables using uppercase
naming convention (e.g., APP_NAME, DATABASE_URL, JWT_SECRET_KEY).

Usage:
```python
from config import settings

# Access application settings
print(settings.app.name)
print(settings.app.environment)

# Access database settings
db_url = settings.database.url

# Access security settings
secret_key = settings.security.secret_key
jwt_expiry = settings.security.jwt_access_token_expire_minutes
```

Author: Gabomfim
License: MIT
"""

import os
from enum import Enum
from functools import lru_cache
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class LogLevel(str, Enum):
    """Available logging levels for application logging configuration.

    This enum defines the standard Python logging levels that can be used
    to control the verbosity of application logs. Each level filters messages
    at that level and above.

    Attributes:
        CRITICAL: Only critical errors that may cause the application to crash
        ERROR: Error conditions that don't require immediate shutdown
        WARNING: Warning messages for potentially harmful situations
        INFO: General informational messages about application operation
        DEBUG: Detailed diagnostic information for troubleshooting

    Usage:
        LOG_LEVEL=DEBUG for development environments
        LOG_LEVEL=INFO for production environments
        LOG_LEVEL=ERROR for minimal logging in production
    """

    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class Environment(str, Enum):
    """Application deployment environments with specific behavior configurations.

    This enum defines the different environments where the application can run,
    each with its own configuration profile and behavior characteristics.

    Attributes:
        DEVELOPMENT: Local development environment with debug features enabled
        TESTING: Automated testing environment with test-specific configurations
        STAGING: Pre-production environment that mirrors production settings
        PRODUCTION: Live production environment with optimized security and performance

    Environment-Specific Behaviors:
        - DEVELOPMENT: Debug mode, auto-reload, verbose logging, relaxed security
        - TESTING: Mock services, in-memory databases, predictable test data
        - STAGING: Production-like settings with additional monitoring and logging
        - PRODUCTION: Optimized performance, strict security, minimal logging

    Usage:
        Set APP_ENVIRONMENT=production for production deployments
        Set APP_ENVIRONMENT=development for local development
    """

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseModel):
    """Comprehensive application configuration management.

    This class provides a centralized, type-safe way to manage all application
    configuration settings. It automatically loads values from environment variables
    with sensible defaults, validates data types, and provides convenient access
    patterns for different configuration categories.

    Configuration Categories:
        - Application: Basic app metadata (name, version, environment)
        - Database: Connection settings, pool configuration, query options
        - Logging: Log levels, output formats, file destinations
        - Security: Password policies, encryption settings, authentication
        - JWT: Token configuration, expiration times, algorithms
        - Server: Host, port, worker processes, performance settings
        - CORS: Cross-origin resource sharing permissions

    Environment Variable Loading:
        All settings can be overridden via environment variables using uppercase
        naming with underscores (e.g., APP_NAME, DATABASE_URL, JWT_SECRET_KEY).
        Boolean values are parsed from strings ("true"/"false").
        Lists are parsed from comma-separated strings.

    Validation:
        - Type checking for all configuration values
        - Enum validation for constrained choices
        - Automatic type conversion where appropriate
        - Fallback to sensible defaults for missing values

    Usage:
        ```python
        # Direct instantiation
        settings = Settings()

        # Access configuration
        db_url = settings.database_url
        is_debug = settings.app_debug

        # Environment checks
        if settings.is_production():
            # Production-specific logic
            pass
        ```

    Security Notes:
        - Never commit secret keys to version control
        - Use strong, unique secret keys in production
        - Rotate JWT secret keys periodically
        - Use environment-specific configuration files
    """

    # Application settings
    app_name: str = Field(default="CRUD ITT")
    app_version: str = Field(default="1.0.0")
    app_description: str = Field(
        default="A comprehensive FastAPI application with user management"
    )
    app_environment: Environment = Field(default=Environment.DEVELOPMENT)
    app_debug: bool = Field(default=False)

    # Database settings
    database_url: str = Field(default="sqlite+aiosqlite:///./database/users.db")
    database_echo: bool = Field(default=False)
    database_pool_size: int = Field(default=10)
    database_max_overflow: int = Field(default=20)

    # Logging settings
    log_level: LogLevel = Field(default=LogLevel.INFO)
    log_json_logs: bool = Field(default=False)
    log_file: Optional[str] = Field(default=None)

    # Security settings
    security_secret_key: str = Field(
        default="your-super-secret-key-change-this-in-production-min-32-chars"
    )
    security_bcrypt_rounds: int = Field(default=12)
    security_password_min_length: int = Field(default=8)
    security_password_require_uppercase: bool = Field(default=True)
    security_password_require_lowercase: bool = Field(default=True)
    security_password_require_digits: bool = Field(default=True)
    security_password_require_special: bool = Field(default=True)

    # JWT settings
    jwt_secret_key: str = Field(
        default="your-jwt-secret-key-change-this-in-production-min-32-chars"
    )
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30)
    jwt_refresh_token_expire_days: int = Field(default=7)

    # Server settings
    server_host: str = Field(default="0.0.0.0")
    server_port: int = Field(default=8000)
    server_workers: int = Field(default=1)
    server_reload: bool = Field(default=False)
    server_access_log: bool = Field(default=True)

    # CORS settings
    cors_origins: List[str] = Field(default=["*"])
    cors_methods: List[str] = Field(default=["GET", "POST", "PUT", "DELETE", "PATCH"])
    cors_headers: List[str] = Field(default=["*"])

    def __init__(self, **kwargs: Any) -> None:
        """Initialize settings by loading from environment variables and defaults.

        This constructor automatically loads configuration from environment variables,
        providing fallback defaults for any missing values. It supports type conversion
        for booleans, integers, enums, and lists from string representations.

        Args:
            **kwargs: Additional keyword arguments to override environment/default
                     values. Useful for testing or programmatic configuration
                     overrides

        Environment Variable Mapping:
            - APP_* variables for application settings
            - DATABASE_* variables for database configuration
            - LOG_* variables for logging configuration
            - SECURITY_* variables for security settings
            - JWT_* variables for JWT token settings
            - SERVER_* variables for server configuration
            - CORS_* variables for CORS settings

        Type Conversion Rules:
            - Strings: Used as-is from environment
            - Booleans: "true"/"false" (case-insensitive) converted to bool
            - Integers: String numbers converted to int with validation
            - Enums: String values validated against enum choices
            - Lists: Comma-separated strings split into lists

        Raises:
            ValidationError: If environment variables contain invalid values
            ValueError: If numeric conversions fail

        Example:
            ```python
            # Load from environment
            settings = Settings()

            # Override specific values
            test_settings = Settings(app_debug=True, database_url="sqlite:///:memory:")
            ```
        """
        # Load from environment variables with fallback to defaults
        env_values = {
            # Application
            "app_name": os.getenv("APP_NAME", "CRUD ITT"),
            "app_version": os.getenv("APP_VERSION", "1.0.0"),
            "app_description": os.getenv(
                "APP_DESCRIPTION",
                "A comprehensive FastAPI application with user management",
            ),
            "app_environment": Environment(os.getenv("APP_ENVIRONMENT", "development")),
            "app_debug": os.getenv("APP_DEBUG", "false").lower() == "true",
            # Database
            "database_url": os.getenv(
                "DATABASE_URL", "sqlite+aiosqlite:///./database/users.db"
            ),
            "database_echo": os.getenv("DATABASE_ECHO", "false").lower() == "true",
            "database_pool_size": int(os.getenv("DATABASE_POOL_SIZE", "10")),
            "database_max_overflow": int(os.getenv("DATABASE_MAX_OVERFLOW", "20")),
            # Logging
            "log_level": LogLevel(os.getenv("LOG_LEVEL", "INFO").upper()),
            "log_json_logs": os.getenv("LOG_JSON_LOGS", "false").lower() == "true",
            "log_file": os.getenv("LOG_LOG_FILE") or None,
            # Security
            "security_secret_key": os.getenv(
                "SECURITY_SECRET_KEY",
                "your-super-secret-key-change-this-in-production-min-32-chars",
            ),
            "security_bcrypt_rounds": int(os.getenv("SECURITY_BCRYPT_ROUNDS", "12")),
            "security_password_min_length": int(
                os.getenv("SECURITY_PASSWORD_MIN_LENGTH", "8")
            ),
            "security_password_require_uppercase": os.getenv(
                "SECURITY_PASSWORD_REQUIRE_UPPERCASE", "true"
            ).lower()
            == "true",
            "security_password_require_lowercase": os.getenv(
                "SECURITY_PASSWORD_REQUIRE_LOWERCASE", "true"
            ).lower()
            == "true",
            "security_password_require_digits": os.getenv(
                "SECURITY_PASSWORD_REQUIRE_DIGITS", "true"
            ).lower()
            == "true",
            "security_password_require_special": os.getenv(
                "SECURITY_PASSWORD_REQUIRE_SPECIAL", "true"
            ).lower()
            == "true",
            # JWT
            "jwt_secret_key": os.getenv(
                "JWT_SECRET_KEY",
                "your-jwt-secret-key-change-this-in-production-min-32-chars",
            ),
            "jwt_algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
            "jwt_access_token_expire_minutes": int(
                os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
            ),
            "jwt_refresh_token_expire_days": int(
                os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")
            ),
            # Server
            "server_host": os.getenv("SERVER_HOST", "0.0.0.0"),
            "server_port": int(os.getenv("SERVER_PORT", "8000")),
            "server_workers": int(os.getenv("SERVER_WORKERS", "1")),
            "server_reload": os.getenv("SERVER_RELOAD", "false").lower() == "true",
            "server_access_log": os.getenv("SERVER_ACCESS_LOG", "true").lower()
            == "true",
            # CORS
            "cors_origins": self._parse_list(os.getenv("APP_CORS_ORIGINS", "*")),
            "cors_methods": self._parse_list(
                os.getenv("APP_CORS_METHODS", "GET,POST,PUT,DELETE,PATCH")
            ),
            "cors_headers": self._parse_list(os.getenv("APP_CORS_HEADERS", "*")),
        }

        # Merge with provided kwargs
        env_values.update(kwargs)
        super().__init__(**env_values)

    @staticmethod
    def _parse_list(value: str) -> List[str]:
        """Parse comma-separated string into list of strings.

        This utility method converts comma-separated environment variable values
        into Python lists, handling whitespace trimming and empty values gracefully.

        Args:
            value: Comma-separated string to parse (e.g., "GET,POST,PUT,DELETE")

        Returns:
            List[str]: List of trimmed string values
                      Empty list if input is empty or None

        Examples:
            >>> Settings._parse_list("GET,POST,PUT")
            ["GET", "POST", "PUT"]

            >>> Settings._parse_list("  item1  ,  item2  ")
            ["item1", "item2"]

            >>> Settings._parse_list("")
            []
        """
        if not value:
            return []
        return [item.strip() for item in value.split(",")]

    def is_development(self) -> bool:
        """Check if the application is running in development environment.

        Development environment typically enables debug features, auto-reload,
        verbose logging, and relaxed security settings for easier development.

        Returns:
            bool: True if app_environment is Environment.DEVELOPMENT, False otherwise

        Usage:
            ```python
            if settings.is_development():
                # Enable debug middleware
                # Use verbose logging
                # Allow CORS from any origin
                pass
            ```
        """
        return self.app_environment == Environment.DEVELOPMENT

    def is_production(self) -> bool:
        """Check if the application is running in production environment.

        Production environment enforces strict security settings, optimized
        performance configurations, and minimal logging for live deployments.

        Returns:
            bool: True if app_environment is Environment.PRODUCTION, False otherwise

        Usage:
            ```python
            if settings.is_production():
                # Enforce HTTPS
                # Use minimal logging
                # Enable security headers
                # Disable debug features
                pass
            ```
        """
        return self.app_environment == Environment.PRODUCTION

    def is_testing(self) -> bool:
        """Check if the application is running in testing environment.

        Testing environment is used for automated tests with specific configurations
        like in-memory databases, mock services, and predictable test data.

        Returns:
            bool: True if app_environment is Environment.TESTING, False otherwise

        Usage:
            ```python
            if settings.is_testing():
                # Use in-memory database
                # Mock external services
                # Disable authentication for test endpoints
                pass
            ```
        """
        return self.app_environment == Environment.TESTING


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings instance with environment variable loading.

    This factory function creates and caches a Settings instance, ensuring that
    configuration is loaded only once during application startup. The caching
    improves performance by avoiding repeated environment variable parsing.

    The function uses Python's lru_cache decorator to provide singleton-like
    behavior while maintaining testability through cache clearing capabilities.

    Returns:
        Settings: Cached application configuration instance with all settings
                 loaded from environment variables and defaults

    Caching Behavior:
        - First call: Creates Settings instance and caches it
        - Subsequent calls: Returns the same cached instance
        - Cache can be cleared: get_settings.cache_clear()

    Usage:
        ```python
        # Standard usage throughout the application
        from config import get_settings

        settings = get_settings()
        database_url = settings.database_url

        # For testing - clear cache to reload settings
        get_settings.cache_clear()
        test_settings = get_settings()
        ```

    Thread Safety:
        This function is thread-safe due to the lru_cache implementation.
        Multiple threads can safely call this function simultaneously.

    Performance Notes:
        - Environment variable parsing occurs only on first call
        - Subsequent calls have O(1) performance
        - Memory usage is minimal (single Settings instance)
    """
    return Settings()


# Create convenience objects for easier access
class AppSettings:
    """Application settings accessor."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def name(self) -> str:
        return self._settings.app_name

    @property
    def version(self) -> str:
        return self._settings.app_version

    @property
    def description(self) -> str:
        return self._settings.app_description

    @property
    def environment(self) -> Environment:
        return self._settings.app_environment

    @property
    def debug(self) -> bool:
        return self._settings.app_debug

    @property
    def cors_origins(self) -> List[str]:
        return self._settings.cors_origins

    @property
    def cors_methods(self) -> List[str]:
        return self._settings.cors_methods

    @property
    def cors_headers(self) -> List[str]:
        return self._settings.cors_headers


class DatabaseSettings:
    """Database settings accessor."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def url(self) -> str:
        return self._settings.database_url

    @property
    def echo(self) -> bool:
        return self._settings.database_echo

    @property
    def pool_size(self) -> int:
        return self._settings.database_pool_size

    @property
    def max_overflow(self) -> int:
        return self._settings.database_max_overflow


class LoggingSettings:
    """Logging settings accessor."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def level(self) -> LogLevel:
        return self._settings.log_level

    @property
    def json_logs(self) -> bool:
        return self._settings.log_json_logs

    @property
    def log_file(self) -> Optional[str]:
        return self._settings.log_file


class ServerSettings:
    """Server settings accessor."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def host(self) -> str:
        return self._settings.server_host

    @property
    def port(self) -> int:
        return self._settings.server_port

    @property
    def workers(self) -> int:
        return self._settings.server_workers

    @property
    def reload(self) -> bool:
        return self._settings.server_reload

    @property
    def access_log(self) -> bool:
        return self._settings.server_access_log


class SecuritySettings:
    """Security settings accessor."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def secret_key(self) -> str:
        return self._settings.security_secret_key

    @property
    def bcrypt_rounds(self) -> int:
        return self._settings.security_bcrypt_rounds

    @property
    def password_min_length(self) -> int:
        return self._settings.security_password_min_length

    @property
    def password_require_uppercase(self) -> bool:
        return self._settings.security_password_require_uppercase

    @property
    def password_require_lowercase(self) -> bool:
        return self._settings.security_password_require_lowercase

    @property
    def password_require_digits(self) -> bool:
        return self._settings.security_password_require_digits

    @property
    def password_require_special(self) -> bool:
        return self._settings.security_password_require_special

    @property
    def jwt_secret_key(self) -> str:
        return self._settings.jwt_secret_key

    @property
    def jwt_algorithm(self) -> str:
        return self._settings.jwt_algorithm

    @property
    def jwt_access_token_expire_minutes(self) -> int:
        return self._settings.jwt_access_token_expire_minutes

    @property
    def jwt_refresh_token_expire_days(self) -> int:
        return self._settings.jwt_refresh_token_expire_days


class SettingsWithAccessors:
    """Settings wrapper with convenient sub-settings access."""

    def __init__(self) -> None:
        self._core = get_settings()

        # Create convenience accessors
        self.app = AppSettings(self._core)
        self.database = DatabaseSettings(self._core)
        self.logging = LoggingSettings(self._core)
        self.security = SecuritySettings(self._core)
        self.server = ServerSettings(self._core)

    def __getattr__(self, name: str) -> Any:
        """Delegate to core settings for direct access."""
        return getattr(self._core, name)


# Override the original settings with our accessor wrapper
settings = SettingsWithAccessors()
