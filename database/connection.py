from typing import AsyncGenerator

from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from utils.logging_config import get_logger

logger = get_logger(__name__)

# Database URL - using async SQLite
DATABASE_URL = "sqlite+aiosqlite:///./database/users.db"

# Create async engine
async_engine = create_async_engine(DATABASE_URL, echo=False)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


# Declarative base class
class Base(DeclarativeBase):
    pass


# User model
class User(Base):
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


# Create tables (async initialization)
async def init_database() -> None:
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


# Dependency to get async database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
