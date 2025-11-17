import pytest
from fastapi.testclient import TestClient
from fastapi import status
from services.auth_service import _blacklisted_tokens


@pytest.fixture(autouse=True)
def clear_token_blacklist():
    """Clear the token blacklist before each test"""
    _blacklisted_tokens.clear()
    yield
    _blacklisted_tokens.clear()


class TestAuthenticationAPI:
    """Test Authentication API endpoints"""

    def test_login_success(self, client: TestClient, sample_user):
        """Test successful login"""
        # Create user first
        client.post("/api/v1/users", json=sample_user)

        # Login
        login_data = {
            "username": sample_user["username"],
            "password": sample_user["password"]
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Login successful"
        assert "token" in data
        assert "user" in data
        assert data["token"]["token_type"] == "bearer"
        assert "access_token" in data["token"]
        assert data["user"]["username"] == sample_user["username"]

    def test_login_invalid_username(self, client: TestClient):
        """Test login with invalid username"""
        login_data = {
            "username": "nonexistent_user",
            "password": "password123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid username or password" in data["detail"]

    def test_login_invalid_password(self, client: TestClient, sample_user):
        """Test login with invalid password"""
        # Create user first
        client.post("/api/v1/users", json=sample_user)

        # Try login with wrong password
        login_data = {
            "username": sample_user["username"],
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid username or password" in data["detail"]

    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing fields"""
        # Missing password
        response = client.post("/api/v1/auth/login", json={"username": "testuser"})
        assert response.status_code == 422

        # Missing username
        response = client.post("/api/v1/auth/login", json={"password": "password123"})
        assert response.status_code == 422

    def test_logout_success(self, client: TestClient, sample_user):
        """Test successful logout"""
        # Create user and login
        client.post("/api/v1/users", json=sample_user)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user["username"],
            "password": sample_user["password"]
        })
        token = login_response.json()["token"]["access_token"]

        # Logout
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/v1/auth/logout", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logout successful"

    def test_logout_no_token(self, client: TestClient):
        """Test logout without token"""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 401

    def test_logout_invalid_token(self, client: TestClient):
        """Test logout with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post("/api/v1/auth/logout", headers=headers)
        assert response.status_code == 401

    def test_token_blacklist_after_logout(self, client: TestClient, sample_user):
        """Test that token is blacklisted after logout"""
        # Create user and login
        client.post("/api/v1/users", json=sample_user)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user["username"],
            "password": sample_user["password"]
        })
        token = login_response.json()["token"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Verify token works before logout
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200

        # Logout
        client.post("/api/v1/auth/logout", headers=headers)

        # Try to use token after logout - should fail
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
        assert "Token has been revoked" in response.json()["detail"]

    def test_get_current_user_info(self, client: TestClient, sample_user):
        """Test getting current user info"""
        # Create user and login
        client.post("/api/v1/users", json=sample_user)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user["username"],
            "password": sample_user["password"]
        })
        token = login_response.json()["token"]["access_token"]

        # Get current user info
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == sample_user["username"]
        assert data["age"] == sample_user["age"]
        assert data["description"] == sample_user["description"]

    def test_get_current_user_info_no_token(self, client: TestClient):
        """Test getting current user info without token"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_protected_endpoint_without_auth(self, client: TestClient):
        """Test accessing protected endpoint without authentication"""
        response = client.get("/api/v1/users/testuser")
        assert response.status_code == 401

    def test_protected_endpoint_with_auth(self, client: TestClient, sample_user):
        """Test accessing protected endpoint with authentication"""
        # Create user and login
        client.post("/api/v1/users", json=sample_user)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user["username"],
            "password": sample_user["password"]
        })
        token = login_response.json()["token"]["access_token"]

        # Access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(f"/api/v1/users/{sample_user['username']}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == sample_user["username"]

    def test_user_creation_still_public(self, client: TestClient, sample_user):
        """Test that user creation endpoint is still public"""
        # User creation should work without authentication
        response = client.post("/api/v1/users", json=sample_user)
        assert response.status_code == 201

    def test_multiple_logins_same_user(self, client: TestClient, sample_user):
        """Test multiple login sessions for same user"""
        # Create user
        client.post("/api/v1/users", json=sample_user)
        login_data = {
            "username": sample_user["username"],
            "password": sample_user["password"]
        }

        # Login twice
        response1 = client.post("/api/v1/auth/login", json=login_data)
        response2 = client.post("/api/v1/auth/login", json=login_data)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        token1 = response1.json()["token"]["access_token"]
        token2 = response2.json()["token"]["access_token"]
        
        # Both tokens should work
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        response1 = client.get("/api/v1/auth/me", headers=headers1)
        response2 = client.get("/api/v1/auth/me", headers=headers2)
        
        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_change_password_requires_auth(self, client: TestClient, sample_user):
        """Test that password change requires authentication"""
        # Create user
        client.post("/api/v1/users", json=sample_user)

        # Try to change password without auth
        password_change_data = {
            "current_password": sample_user["password"],
            "new_password": "NewPassword123!@#",
            "confirm_password": "NewPassword123!@#"
        }
        response = client.put(
            f"/api/v1/users/{sample_user['username']}/password",
            json=password_change_data
        )
        assert response.status_code == 401