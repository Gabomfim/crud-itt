from fastapi.testclient import TestClient


class TestUserAPI:
    """Test User API endpoints"""

    def test_get_root_page(self, client: TestClient):
        """Test GET / returns HTML page"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "User Management API" in response.text

    def test_create_user_success(self, client: TestClient, sample_user):
        """Test successful user creation"""
        response = client.post("/api/v1/users", json=sample_user)
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "User created successfully"

    def test_create_user_invalid_data(self, client: TestClient):
        """Test user creation with invalid data"""
        invalid_user = {
            "username": "ab",  # too short
            "password": "weak",  # doesn't meet complexity
            "age": 0,  # invalid age
            "description": "a" * 201,  # too long
        }
        response = client.post("/api/v1/users", json=invalid_user)
        assert response.status_code == 422

    def test_create_duplicate_user(self, client: TestClient, sample_user):
        """Test creating user with duplicate username"""
        # Create first user
        response = client.post("/api/v1/users", json=sample_user)
        assert response.status_code == 201

        # Try to create duplicate
        response = client.post("/api/v1/users", json=sample_user)
        assert response.status_code == 400
        data = response.json()
        assert "Username already exists" in data["detail"]

    def test_get_user_success(self, client: TestClient, sample_user):
        """Test successful user retrieval"""
        # Create user first
        client.post("/api/v1/users", json=sample_user)

        # Get user
        response = client.get(f"/api/v1/users/{sample_user['username']}")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == sample_user["username"]
        assert data["age"] == sample_user["age"]
        assert data["description"] == sample_user["description"]
        assert "id" in data
        assert "password" not in data  # Should not return password

    def test_get_user_not_found(self, client: TestClient):
        """Test getting non-existent user"""
        response = client.get("/api/v1/users/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert "User not found" in data["detail"]

    def test_get_users_by_minimum_age(self, client: TestClient):
        """Test getting users by minimum age"""
        # Create test users
        users = [
            {
                "username": "young",
                "password": "TestPass123!",
                "age": 18,
                "description": "Young user",
            },
            {
                "username": "middle",
                "password": "TestPass123!",
                "age": 30,
                "description": "Middle aged user",
            },
            {
                "username": "old",
                "password": "TestPass123!",
                "age": 50,
                "description": "Old user",
            },
        ]

        for user in users:
            client.post("/api/v1/users", json=user)

        # Test minimum age filter
        response = client.get("/api/v1/users?minimum_age=25")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Should return middle and old users
        usernames = [user["username"] for user in data]
        assert "middle" in usernames
        assert "old" in usernames
        assert "young" not in usernames

    def test_get_users_no_match(self, client: TestClient, sample_user):
        """Test getting users with no matches"""
        # Create a young user
        client.post("/api/v1/users", json=sample_user)

        # Search for users older than the created user
        response = client.get("/api/v1/users?minimum_age=100")
        assert response.status_code == 404
        data = response.json()
        assert "No users found" in data["detail"]

    def test_update_user_success(self, client: TestClient, sample_user):
        """Test successful user update"""
        # Create user first
        client.post("/api/v1/users", json=sample_user)

        # Update user
        updated_data = {
            "username": "updateduser",
            "password": "NewPass456!",
            "age": 30,
            "description": "Updated description",
        }
        response = client.put(
            f"/api/v1/users/{sample_user['username']}", json=updated_data
        )
        assert response.status_code == 204

    def test_update_user_not_found(self, client: TestClient):
        """Test updating non-existent user"""
        update_data = {
            "username": "newname",
            "password": "TestPass123!",
            "age": 25,
            "description": "New description",
        }
        response = client.put("/api/v1/users/nonexistent", json=update_data)
        assert response.status_code == 404
        data = response.json()
        assert "User not found" in data["detail"]

    def test_delete_user_success(self, client: TestClient, sample_user):
        """Test successful user deletion"""
        # Create user first
        client.post("/api/v1/users", json=sample_user)

        # Delete user
        response = client.delete(f"/api/v1/users/{sample_user['username']}")
        assert response.status_code == 204

        # Verify user is deleted
        response = client.get(f"/api/v1/users/{sample_user['username']}")
        assert response.status_code == 404

    def test_delete_user_not_found(self, client: TestClient):
        """Test deleting non-existent user"""
        response = client.delete("/api/v1/users/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert "User not found" in data["detail"]

    def test_404_page(self, client: TestClient):
        """Test 404 error page"""
        response = client.get("/nonexistent-page")
        assert response.status_code == 404
        assert "text/html" in response.headers["content-type"]
        assert "Page Not Found" in response.text
