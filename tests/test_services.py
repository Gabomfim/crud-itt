import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy import select

from database.connection import User
from models.requests import UserRequest
from models.responses import UserResponse
from services.user_service import (
    create_new_user,
    delete_user_by_username,
    get_user_by_username,
    get_users_by_minimum_age,
    update_user_by_username,
)


class TestUserService:
    """Test user service functions"""

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
    async def test_create_new_user_success(self, async_db_session):
        """Test successful user creation in service"""
        user_request = UserRequest(
            username="servicetest",
            password="TestPass123!",
            age=25,
            description="Service test user",
        )

        result = await create_new_user(user_request, async_db_session)
        assert result["message"] == "User created successfully"

        # Verify user was created
        stmt = select(User).where(User.username == "servicetest")
        result_set = await async_db_session.execute(stmt)
        user = result_set.scalar_one_or_none()
        assert user is not None
        assert user.username == "servicetest"
        assert user.age == 25

    @pytest.mark.asyncio
    async def test_create_duplicate_user_service(self, async_db_session):
        """Test creating duplicate user in service"""
        user_request = UserRequest(
            username="duplicate", password="TestPass123!", age=25
        )

        # Create first user
        await create_new_user(user_request, async_db_session)

        # Try to create duplicate
        with pytest.raises(HTTPException) as exc_info:
            await create_new_user(user_request, async_db_session)

        assert exc_info.value.status_code == 400
        assert "Username already exists" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_user_by_username_success(self, async_db_session):
        """Test getting user by username"""
        # Create user first
        user_request = UserRequest(
            username="gettest",
            password="TestPass123!",
            age=30,
            description="Get test user",
        )
        await create_new_user(user_request, async_db_session)

        # Get user
        result = await get_user_by_username("gettest", async_db_session)
        assert isinstance(result, UserResponse)
        assert result.username == "gettest"
        assert result.age == 30
        assert result.description == "Get test user"

    @pytest.mark.asyncio
    async def test_get_user_not_found_service(self, async_db_session):
        """Test getting non-existent user"""
        with pytest.raises(HTTPException) as exc_info:
            await get_user_by_username("nonexistent", async_db_session)

        assert exc_info.value.status_code == 404
        assert "User not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_users_by_minimum_age_service(self, async_db_session):
        """Test getting users by minimum age"""
        # Create test users
        users = [
            UserRequest(username="young", password="TestPass123!", age=20),
            UserRequest(username="middle", password="TestPass123!", age=35),
            UserRequest(username="old", password="TestPass123!", age=50),
        ]

        for user in users:
            await create_new_user(user, async_db_session)

        # Test filtering
        result = await get_users_by_minimum_age(30, async_db_session)
        assert len(result) == 2
        usernames = [user.username for user in result]
        assert "middle" in usernames
        assert "old" in usernames
        assert "young" not in usernames

    @pytest.mark.asyncio
    async def test_update_user_service(self, async_db_session):
        """Test updating user"""
        # Create user
        user_request = UserRequest(
            username="updatetest", password="TestPass123!", age=25
        )
        await create_new_user(user_request, async_db_session)

        # Update user
        update_request = UserRequest(
            username="updated",
            password="NewPass456!",
            age=30,
            description="Updated description",
        )
        result = await update_user_by_username(
            "updatetest", update_request, async_db_session
        )
        assert result["message"] == "User updated successfully"

        # Refresh session to ensure we see the changes
        await async_db_session.commit()

        # Verify update
        stmt = select(User).where(User.username == "updated")
        result_set = await async_db_session.execute(stmt)
        updated_user = result_set.scalar_one_or_none()
        assert updated_user is not None
        assert updated_user.age == 30
        assert updated_user.description == "Updated description"

    @pytest.mark.asyncio
    async def test_delete_user_service(self, async_db_session):
        """Test deleting user"""
        # Create user
        user_request = UserRequest(
            username="deletetest", password="TestPass123!", age=25
        )
        await create_new_user(user_request, async_db_session)

        # Delete user
        result = await delete_user_by_username("deletetest", async_db_session)
        assert result["message"] == "User deleted successfully"

        # Verify deletion
        stmt = select(User).where(User.username == "deletetest")
        result_set = await async_db_session.execute(stmt)
        deleted_user = result_set.scalar_one_or_none()
        assert deleted_user is None
