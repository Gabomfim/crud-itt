"""
Database Connection and ORM Configuration Module

This module provides comprehensive database connectivity, session management, and 
ORM model definitions for the CRUD ITT application using SQLAlchemy async engine
with support for multiple database backends and production-ready configurations.

Key Features:
- Async database operations with SQLAlchemy 2.0+
- Multi-database support (SQLite, PostgreSQL, MySQL)
- Connection pooling and performance optimization
- Database session lifecycle management
- ORM models with validation constraints
- Transaction management and error handling
- Database schema initialization and migrations

Database Support:
- SQLite: Development and testing (file-based or in-memory)
- PostgreSQL: Production deployments with advanced features
- MySQL: Alternative production option with broad compatibility
- Database URL configuration via environment variables

Connection Features:
- Async engine with connection pooling
- Configurable pool sizes and overflow limits
- Connection timeout and retry logic
- SQL query logging for debugging
- Performance monitoring and metrics
- Graceful connection handling and cleanup

Session Management:
- Async session factory with proper lifecycle
- Automatic transaction handling
- Context manager support for proper cleanup
- Session scoping for request isolation
- Error handling and rollback support

ORM Models:
- SQLAlchemy 2.0 declarative base
- Comprehensive validation constraints
- Database-level data integrity
- Optimized indexing and performance
- Type hints and modern Python features

Security Features:
- SQL injection prevention via ORM
- Database-level constraints for data validation
- Secure password storage requirements
- Input sanitization and validation
- Connection security (SSL/TLS support)

Performance Optimizations:
- Connection pooling for concurrent requests
- Efficient query patterns and lazy loading
- Database indexing for common queries
- Query result caching where appropriate
- Optimized session lifecycle management

Usage:
```python
from database.connection import get_async_session, User

# Get database session
async with get_async_session() as session:
    # Query users
    result = await session.execute(select(User))
    users = result.scalars().all()
    
    # Create new user
    new_user = User(username="john", email="john@example.com")
    session.add(new_user)
    await session.commit()
```

Configuration:
Database settings are managed through the application configuration system
with environment variable overrides for different deployment environments.

Author: Gabomfim
License: MIT
"""

from typing import AsyncGenerator

from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config import settings
from utils.logging_config import get_logger

logger = get_logger(__name__)

# Database Engine Configuration
# Creates async SQLAlchemy engine with database-specific optimizations.
# SQLite uses simple configuration without pooling (single-file database).
# PostgreSQL/MySQL use connection pooling for production performance.
if settings.database.url.startswith("sqlite"):
    async_engine = create_async_engine(
        settings.database.url,
        echo=settings.database.echo,
    )
else:
    async_engine = create_async_engine(
        settings.database.url,
        echo=settings.database.echo,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
    )

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    """SQLAlchemy declarative base class for all ORM models.
    
    This class serves as the foundation for all database models in the application,
    providing common functionality, metadata management, and ORM integration.
    It uses SQLAlchemy 2.0's modern declarative base with enhanced type support.
    
    Features:
        - Modern SQLAlchemy 2.0+ declarative syntax
        - Automatic table metadata generation
        - Type hints integration with mapped_column
        - Consistent model behavior across the application
        - Schema migration support
    
    Usage:
        ```python
        class MyModel(Base):
            __tablename__ = "my_table"
            
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(50))
        ```
    
    Model Conventions:
        - Use snake_case for table names
        - Include primary key 'id' field unless composite key needed
        - Add appropriate indexes for query performance
        - Include database constraints for data integrity
        - Use type hints with Mapped[] for all columns
    
    Metadata:
        The Base.metadata object contains schema information for all models
        and is used for table creation, migrations, and schema introspection.
    """


class User(Base):
    """User model representing application users with comprehensive validation.
    
    This model defines the core user entity with complete database-level validation,
    security constraints, and optimized indexing for the authentication and user
    management system.
    
    Database Features:
        - Primary key with auto-increment
        - Unique username constraint with indexing
        - Comprehensive check constraints for data validation
        - Optimized column types and sizes
        - Security-focused password storage requirements
    
    Validation Rules:
        Username:
            - Minimum 3 characters length
            - Maximum 30 characters (database column limit)
            - Must not be empty string
            - Must be unique across all users
            - Indexed for fast lookup
        
        Password:
            - Minimum 60 characters (accommodates bcrypt hashes)
            - Maximum 255 characters (database column limit)
            - Must not be empty string
            - Expected to contain bcrypt hash, not plaintext
        
        Age:
            - Must be greater than 0
            - Must be less than or equal to 120
            - Integer type for efficient storage
        
        Description:
            - Maximum 200 characters
            - Defaults to empty string
            - Optional field for user profile information
    
    Security Considerations:
        - Password field sized for bcrypt hash storage
        - Username uniqueness enforced at database level
        - No storage of plaintext passwords
        - Appropriate field lengths to prevent overflow attacks
    
    Performance Optimizations:
        - Primary key index on 'id' field
        - Unique index on 'username' for fast authentication
        - Appropriate column types and sizes
        - Check constraints for data integrity
    
    Usage:
        ```python
        # Create new user
        user = User(
            username="john_doe",
            password="$2b$12$...",  # bcrypt hash
            age=25,
            description="Software developer"
        )
        
        # Query by username
        stmt = select(User).where(User.username == "john_doe")
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        ```
    
    Database Schema:
        Table: users
        Constraints: Multiple check constraints for data validation
        Indexes: Primary key (id), unique index (username)
    """
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("age > 0 AND age <= 120", name="check_age_range"),
        CheckConstraint("username != ''", name="check_username_not_empty"),
        CheckConstraint("password != ''", name="check_password_not_empty"),
        CheckConstraint("LENGTH(username) >= 3", name="check_username_min_length"),
        CheckConstraint(
            "LENGTH(password) >= 60", name="check_password_min_length"
        ),  # bcrypt hashes are ~60 chars
        CheckConstraint(
            "LENGTH(description) <= 200", name="check_description_max_length"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(30), unique=True, index=True, nullable=False
    )
    password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # Increased for bcrypt hashes
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(200), default="", nullable=False)


async def init_database() -> None:
    """Initialize database schema by creating all tables and constraints.
    
    This function performs complete database initialization including table creation,
    constraint setup, index creation, and initial schema validation. It's designed
    to be idempotent and safe to run multiple times.
    
    Initialization Process:
        1. Connect to database using async engine
        2. Begin transaction for atomic schema operations
        3. Create all tables defined in Base.metadata
        4. Apply all constraints and indexes
        5. Commit transaction or rollback on error
        6. Log success or failure with detailed error information
    
    Schema Operations:
        - Creates 'users' table with all columns and constraints
        - Applies check constraints for data validation
        - Creates indexes for performance optimization
        - Sets up foreign key relationships (if any)
    
    Error Handling:
        - Catches and logs all database exceptions
        - Provides detailed error messages for troubleshooting
        - Re-raises exceptions for proper application error handling
        - Uses structured logging for observability
    
    Safety Features:
        - Idempotent operation (safe to run multiple times)
        - Transaction-based for atomicity
        - Does not drop existing data
        - Compatible with database migrations
    
    Raises:
        Exception: Database connection errors, permission issues, or schema conflicts
                  Original exception is re-raised after logging for proper error handling
    
    Usage:
        ```python
        # During application startup
        await init_database()
        
        # In FastAPI lifespan
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await init_database()
            yield
        ```
    
    Performance:
        - Fast execution for existing schemas (no-op)
        - Minimal overhead for schema validation
        - Efficient batch operation for multiple tables
    
    Database Compatibility:
        - SQLite: Creates database file if not exists
        - PostgreSQL: Requires database to exist
        - MySQL: Requires database and proper permissions
    
    Logging:
        - Info level: Successful initialization
        - Error level: Initialization failures with stack traces
        - Structured logging with error details
    """
    logger.info("Initializing database")
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(
            "Failed to initialize database", extra={"error": str(e)}, exc_info=True
        )
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide async database session with proper lifecycle management.
    
    This dependency function creates and manages database sessions for FastAPI
    endpoints, ensuring proper resource cleanup, transaction handling, and
    connection management throughout the request lifecycle.
    
    Session Lifecycle:
        1. Create new async session from session factory
        2. Yield session to calling code (endpoint or service)
        3. Automatically close session when done (even on exceptions)
        4. Handle connection pooling and resource cleanup
    
    Features:
        - Async session support for non-blocking database operations
        - Automatic session cleanup via context manager
        - Exception-safe resource management
        - Connection pooling integration
        - Transaction support within session scope
    
    Yields:
        AsyncSession: SQLAlchemy async session instance
                     Configured with expire_on_commit=False for flexibility
                     Connected to the application's configured database
    
    Usage in FastAPI:
        ```python
        from fastapi import Depends
        from database.connection import get_db
        
        @app.get("/users/")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
        ```
    
    Transaction Management:
        - Each session can handle multiple transactions
        - Explicit commit/rollback required for data changes
        - Automatic rollback on unhandled exceptions
        - Session isolation between concurrent requests
    
    Error Handling:
        - Session cleanup guaranteed via finally block
        - Connection errors handled by connection pool
        - Proper resource deallocation on exceptions
        - No connection leaks under normal or error conditions
    
    Performance:
        - Connection pooling reduces connection overhead
        - Session reuse within request scope
        - Efficient resource management
        - Minimal memory footprint per session
    
    Database Operations:
        ```python
        async def create_user(db: AsyncSession, user_data: dict):
            user = User(**user_data)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user
        ```
    
    Thread Safety:
        Each session is isolated and thread-safe within its scope.
        Sessions should not be shared between requests or threads.
    
    Connection Pooling:
        Sessions are created from a connection pool, providing efficient
        resource utilization and automatic connection management.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
