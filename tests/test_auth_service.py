import pytest
from fastapi import HTTPException

from models.requests import UserRequest
from services.auth_service import authenticate_user
from services.user_service import create_new_user


class TestAuthService:
    """Test authentication service"""

    def test_authenticate_user_success(self, client):
        """Test successful user authentication"""
        from tests.conftest import TestingSessionLocal

        db = TestingSessionLocal()

        # Create a test user first
        user_request = UserRequest(
            username="authtest",
            password="TestPass123!",
            age=25,
            description="Auth test user",
        )
        create_new_user(user_request, db)

        # Test authentication with correct credentials
        authenticated_user = authenticate_user("authtest", "TestPass123!", db)
        assert authenticated_user.username == "authtest"
        assert authenticated_user.age == 25

        db.close()

    def test_authenticate_user_wrong_username(self, client):
        """Test authentication with wrong username"""
        from tests.conftest import TestingSessionLocal

        db = TestingSessionLocal()

        # Try to authenticate non-existent user
        with pytest.raises(HTTPException) as exc_info:
            authenticate_user("nonexistent", "TestPass123!", db)

        assert exc_info.value.status_code == 401
        assert "Invalid username or password" in exc_info.value.detail

        db.close()

    def test_authenticate_user_wrong_password(self, client):
        """Test authentication with wrong password"""
        from tests.conftest import TestingSessionLocal

        db = TestingSessionLocal()

        # Create a test user first
        user_request = UserRequest(
            username="authtest2", password="TestPass123!", age=25
        )
        create_new_user(user_request, db)

        # Try to authenticate with wrong password
        with pytest.raises(HTTPException) as exc_info:
            authenticate_user("authtest2", "WrongPass456!", db)

        assert exc_info.value.status_code == 401
        assert "Invalid username or password" in exc_info.value.detail

        db.close()
