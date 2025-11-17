import pytest
import pytest_asyncio
from fastapi import HTTPException

from models.requests import UserRequest
from services.auth_service import authenticate_user
from services.user_service import create_new_user


class TestAuthService:
    """Test authentication service"""

    @pytest_asyncio.fixture
    async def async_db_session(self):
        """Create async database session for testing"""
        from database.connection import Base
        from tests.conftest import TestingAsyncSessionLocal, async_engine

        # Create tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with TestingAsyncSessionLocal() as session:
            yield session

        # Clean up tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, async_db_session):
        """Test successful user authentication"""
        # Create a test user first
        user_request = UserRequest(
            username="authtest",
            password="TestPass123!",
            age=25,
            description="Auth test user",
        )
        await create_new_user(user_request, async_db_session)

        # Test authentication with correct credentials
        authenticated_user = await authenticate_user(
            "authtest", "TestPass123!", async_db_session
        )
        assert authenticated_user.username == "authtest"
        assert authenticated_user.age == 25

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_username(self, async_db_session):
        """Test authentication with wrong username"""
        # Try to authenticate non-existent user
        with pytest.raises(HTTPException) as exc_info:
            await authenticate_user("nonexistent", "TestPass123!", async_db_session)

        assert exc_info.value.status_code == 401
        assert "Invalid username or password" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, async_db_session):
        """Test authentication with wrong password"""
        # Create a test user first
        user_request = UserRequest(
            username="authtest2", password="TestPass123!", age=25
        )
        await create_new_user(user_request, async_db_session)

        # Try to authenticate with wrong password
        with pytest.raises(HTTPException) as exc_info:
            await authenticate_user("authtest2", "WrongPass456!", async_db_session)

        assert exc_info.value.status_code == 401
        assert "Invalid username or password" in exc_info.value.detail
