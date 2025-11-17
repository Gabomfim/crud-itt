import pytest
from pydantic import ValidationError

from models.requests import UserRequest
from models.responses import UserResponse


class TestUserRequest:
    """Test UserRequest Pydantic model validation"""

    def test_valid_user_request(self):
        """Test creating a valid user request"""
        user_data = {
            "username": "testuser",
            "password": "TestPass123!",
            "age": 25,
            "description": "Test description",
        }
        user = UserRequest(**user_data)
        assert user.username == "testuser"
        assert user.password == "TestPass123!"
        assert user.age == 25
        assert user.description == "Test description"

    def test_username_validation(self):
        """Test username validation rules"""
        base_data = {"password": "TestPass123!", "age": 25}

        # Valid usernames
        valid_usernames = ["test123", "user_name", "TestUser", "a12"]
        for username in valid_usernames:
            user = UserRequest(username=username, **base_data)
            assert user.username == username

        # Invalid usernames - too short
        with pytest.raises(ValidationError) as exc_info:
            UserRequest(username="ab", **base_data)
        assert "at least 3 characters" in str(exc_info.value)

        # Invalid usernames - too long
        with pytest.raises(ValidationError) as exc_info:
            UserRequest(username="a" * 31, **base_data)
        assert "at most 30 characters" in str(exc_info.value)

        # Invalid usernames - special characters
        with pytest.raises(ValidationError) as exc_info:
            UserRequest(username="test@user", **base_data)
        assert "String should match pattern" in str(exc_info.value)

    def test_password_complexity_validation(self):
        """Test password complexity requirements"""
        base_data = {"username": "testuser", "age": 25}

        # Valid password
        user = UserRequest(password="TestPass123!", **base_data)
        assert user.password == "TestPass123!"

        # Too short
        with pytest.raises(ValidationError) as exc_info:
            UserRequest(password="Test1!", **base_data)
        assert "at least 8 characters" in str(exc_info.value)

        # No uppercase
        with pytest.raises(ValidationError) as exc_info:
            UserRequest(password="testpass123!", **base_data)
        assert "uppercase letter" in str(exc_info.value)

        # No lowercase
        with pytest.raises(ValidationError) as exc_info:
            UserRequest(password="TESTPASS123!", **base_data)
        assert "lowercase letter" in str(exc_info.value)

        # No digit
        with pytest.raises(ValidationError) as exc_info:
            UserRequest(password="TestPass!", **base_data)
        assert "digit" in str(exc_info.value)

        # No special character
        with pytest.raises(ValidationError) as exc_info:
            UserRequest(password="TestPass123", **base_data)
        assert "special character" in str(exc_info.value)

    def test_age_validation(self):
        """Test age validation rules"""
        base_data = {"username": "testuser", "password": "TestPass123!"}

        # Valid ages
        for age in [1, 25, 120]:
            user = UserRequest(age=age, **base_data)
            assert user.age == age

        # Invalid ages - too low
        with pytest.raises(ValidationError) as exc_info:
            UserRequest(age=0, **base_data)
        assert "greater than 0" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            UserRequest(age=-5, **base_data)
        assert "greater than 0" in str(exc_info.value)

        # Invalid ages - too high
        with pytest.raises(ValidationError) as exc_info:
            UserRequest(age=121, **base_data)
        assert "less than or equal to 120" in str(exc_info.value)

    def test_description_validation(self):
        """Test description field validation"""
        base_data = {"username": "testuser", "password": "TestPass123!", "age": 25}

        # Valid descriptions
        user = UserRequest(description="", **base_data)
        assert user.description == ""

        user = UserRequest(description="Short desc", **base_data)
        assert user.description == "Short desc"

        user = UserRequest(description="a" * 200, **base_data)
        assert len(user.description) == 200

        # Invalid description - too long
        with pytest.raises(ValidationError) as exc_info:
            UserRequest(description="a" * 201, **base_data)
        assert "at most 200 characters" in str(exc_info.value)

    def test_default_description(self):
        """Test that description defaults to empty string"""
        user = UserRequest(username="testuser", password="TestPass123!", age=25)
        assert user.description == ""


class TestUserResponse:
    """Test UserResponse Pydantic model"""

    def test_valid_user_response(self):
        """Test creating a valid user response"""
        response_data = {
            "id": 1,
            "username": "testuser",
            "age": 25,
            "description": "Test description",
        }
        response = UserResponse(**response_data)
        assert response.id == 1
        assert response.username == "testuser"
        assert response.age == 25
        assert response.description == "Test description"

    def test_from_attributes_config(self):
        """Test that from_attributes is configured"""
        # This test ensures the Config class is properly set
        assert UserResponse.model_config.get("from_attributes") is True
