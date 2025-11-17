import pytest
from fastapi import HTTPException

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

    def test_create_new_user_success(self, client):
        """Test successful user creation in service"""
        from tests.conftest import TestingSessionLocal

        db = TestingSessionLocal()
        user_request = UserRequest(
            username="servicetest",
            password="TestPass123!",
            age=25,
            description="Service test user",
        )

        result = create_new_user(user_request, db)
        assert result["message"] == "User created successfully"

        # Verify user was created
        user = db.query(User).filter(User.username == "servicetest").first()
        assert user is not None
        assert user.username == "servicetest"
        assert user.age == 25

        db.close()

    def test_create_duplicate_user_service(self, client):
        """Test creating duplicate user in service"""
        from tests.conftest import TestingSessionLocal

        db = TestingSessionLocal()
        user_request = UserRequest(
            username="duplicate", password="TestPass123!", age=25
        )

        # Create first user
        create_new_user(user_request, db)

        # Try to create duplicate
        with pytest.raises(HTTPException) as exc_info:
            create_new_user(user_request, db)

        assert exc_info.value.status_code == 400
        assert "Username already exists" in exc_info.value.detail

        db.close()

    def test_get_user_by_username_success(self, client):
        """Test getting user by username"""
        from tests.conftest import TestingSessionLocal

        db = TestingSessionLocal()

        # Create user first
        user_request = UserRequest(
            username="gettest",
            password="TestPass123!",
            age=30,
            description="Get test user",
        )
        create_new_user(user_request, db)

        # Get user
        result = get_user_by_username("gettest", db)
        assert isinstance(result, UserResponse)
        assert result.username == "gettest"
        assert result.age == 30
        assert result.description == "Get test user"

        db.close()

    def test_get_user_not_found_service(self, client):
        """Test getting non-existent user"""
        from tests.conftest import TestingSessionLocal

        db = TestingSessionLocal()

        with pytest.raises(HTTPException) as exc_info:
            get_user_by_username("nonexistent", db)

        assert exc_info.value.status_code == 404
        assert "User not found" in exc_info.value.detail

        db.close()

    def test_get_users_by_minimum_age_service(self, client):
        """Test getting users by minimum age"""
        from tests.conftest import TestingSessionLocal

        db = TestingSessionLocal()

        # Create test users
        users = [
            UserRequest(username="young", password="TestPass123!", age=20),
            UserRequest(username="middle", password="TestPass123!", age=35),
            UserRequest(username="old", password="TestPass123!", age=50),
        ]

        for user in users:
            create_new_user(user, db)

        # Test filtering
        result = get_users_by_minimum_age(30, db)
        assert len(result) == 2
        usernames = [user.username for user in result]
        assert "middle" in usernames
        assert "old" in usernames
        assert "young" not in usernames

        db.close()

    def test_update_user_service(self, client):
        """Test updating user"""
        from tests.conftest import TestingSessionLocal

        db = TestingSessionLocal()

        # Create user
        user_request = UserRequest(
            username="updatetest", password="TestPass123!", age=25
        )
        create_new_user(user_request, db)

        # Update user
        update_request = UserRequest(
            username="updated",
            password="NewPass456!",
            age=30,
            description="Updated description",
        )
        result = update_user_by_username("updatetest", update_request, db)
        assert result["message"] == "User updated successfully"

        # Verify update
        updated_user = db.query(User).filter(User.username == "updated").first()
        assert updated_user is not None
        assert updated_user.age == 30
        assert updated_user.description == "Updated description"

        db.close()

    def test_delete_user_service(self, client):
        """Test deleting user"""
        from tests.conftest import TestingSessionLocal

        db = TestingSessionLocal()

        # Create user
        user_request = UserRequest(
            username="deletetest", password="TestPass123!", age=25
        )
        create_new_user(user_request, db)

        # Delete user
        result = delete_user_by_username("deletetest", db)
        assert result["message"] == "User deleted successfully"

        # Verify deletion
        deleted_user = db.query(User).filter(User.username == "deletetest").first()
        assert deleted_user is None

        db.close()
