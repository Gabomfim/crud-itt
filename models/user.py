"""
User Data Model Module

This module defines the core User data model class for the CRUD ITT application.
This is a simple Python data class used for data transfer and manipulation,
separate from the SQLAlchemy ORM model defined in database.connection.

NOTE: This appears to be a legacy or alternative User class. The primary
User model is defined as an SQLAlchemy ORM model in database/connection.py.
Consider consolidating these models or clarifying their different purposes.

Key Features:
- Simple Python class for user data representation
- Basic field validation through type hints
- Minimal dependencies for lightweight data handling
- Compatible with serialization/deserialization

Usage Context:
This model may be used for:
- Data transfer objects (DTOs)
- API request/response serialization
- Business logic operations
- Testing and mock data

For database operations, use the SQLAlchemy User model from database.connection.

Author: Gabomfim
License: MIT
"""


class User:
    """Simple User data model for data transfer and manipulation.

    This class provides a basic Python representation of user data without
    database ORM functionality. It's designed for lightweight data operations,
    serialization, and business logic processing.

    NOTE: This is separate from the SQLAlchemy User model in database.connection.
    Consider whether both models are needed or if they serve different purposes.

    Attributes:
        username: Unique username for authentication and identification
                 Expected to be 3-30 characters, alphanumeric with underscores
        password: User password (should be hashed, never store plaintext)
                 For bcrypt hashes, should be ~60 characters
        age: User age in years, expected to be positive integer 1-120
        description: Optional user profile description, max 200 characters
                    Defaults to empty string if not provided

    Validation:
        Type hints provide basic validation, but no runtime validation is
        performed. For strict validation, use Pydantic models in models/requests.py
        and models/responses.py.

    Usage:
        ```python
        # Create user instance
        user = User(
            username="john_doe",
            password="$2b$12$...",  # hashed password
            age=25,
            description="Software developer"
        )

        # Access attributes
        print(f"User: {user.username}, Age: {user.age}")

        # Modify attributes
        user.description = "Senior software developer"
        ```

    Integration:
        - Compatible with JSON serialization
        - Can be converted to/from SQLAlchemy ORM models
        - Works with Pydantic models for API serialization
        - Suitable for business logic operations

    Security Notes:
        - Always hash passwords before storing in password field
        - Username should be validated for allowed characters
        - Consider input sanitization for description field
        - Age should be reasonable range (business logic validation)
    """

    def __init__(self, username: str, password: str, age: int, description: str = ""):
        """Initialize User instance with provided data.

        Args:
            username: Unique identifier for the user
            password: User password (should be pre-hashed)
            age: User age in years
            description: Optional profile description, defaults to empty string
        """
        self.username = username
        self.password = password
        self.age = age
        self.description = description
