import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import app
from database.connection import Base, get_db

# Test database URL (async in-memory SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
TestingAsyncSessionLocal = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

# For backward compatibility with tests that use TestingSessionLocal
TestingSessionLocal = TestingAsyncSessionLocal


async def override_get_db():
    async with TestingAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def async_client():
    """Create async test client with fresh database"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client():
    """Create synchronous test client for compatibility"""
    # Create tables before testing
    import asyncio

    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(create_tables())

    # Use positional argument to avoid keyword argument issues across versions
    test_client = TestClient(app)
    yield test_client

    # Clean up tables after testing
    async def drop_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    asyncio.run(drop_tables())


@pytest.fixture
def sample_user():
    """Sample user data for testing"""
    return {
        "username": "testuser",
        "password": "TestPass123!",
        "age": 25,
        "description": "Test user description",
    }


@pytest.fixture
def auth_headers(client, sample_user):
    """Create a user and return authentication headers"""
    # Create user
    client.post("/api/v1/users", json=sample_user)

    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": sample_user["username"], "password": sample_user["password"]},
    )

    token = login_response.json()["token"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
