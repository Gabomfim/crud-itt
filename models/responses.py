"""
Response Models Module

This module defines Pydantic models for API response serialization and validation.
All response models ensure consistent API output format and include proper
field documentation for API consumers.

Key Features:
- Consistent response structure across all endpoints
- Comprehensive field documentation
- Type-safe response serialization
- JWT token response models
- User information models

Models:
- UserResponse: User profile information for API responses
- Token: JWT token information with expiration details
- LoginResponse: Complete authentication response with user and token data

Author: Gabomfim
License: MIT
"""

from pydantic import BaseModel, Field, ConfigDict


class UserResponse(BaseModel):
    """
    User profile response model for API endpoints.
    
    This model represents user information returned by API endpoints.
    It excludes sensitive information like passwords and includes only
    publicly shareable user data.
    
    Attributes:
        id (int): Unique user identifier from database
        username (str): User's unique username
        age (int): User's age in years
        description (str): User's profile description
        
    Configuration:
        - from_attributes=True: Allows creation from SQLAlchemy models
        - Excludes sensitive fields like password hashes
        - Consistent with UserRequest validation rules
        
    Example Response:
        ```json
        {
            "id": 123,
            "username": "john_doe",
            "age": 25,
            "description": "Software developer"
        }
        ```
        
    Usage:
        Used in all user-related GET endpoints and as part of
        authentication responses to provide user context.
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Unique user identifier")
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Username (3-30 characters, alphanumeric and underscores)",
    )
    age: int = Field(..., gt=0, le=120, description="User age (1-120 years)")
    description: str = Field(
        ..., max_length=200, description="User description (max 200 characters)"
    )


class Token(BaseModel):
    """
    JWT token response model for authentication endpoints.
    
    This model represents JWT token information returned after successful
    authentication. It includes the token itself and metadata about its
    usage and expiration.
    
    Attributes:
        access_token (str): The JWT access token string
        token_type (str): Token type, always "bearer" for JWT tokens
        expires_in (int): Token lifetime in seconds from issuance
        
    Example Response:
        ```json
        {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "token_type": "bearer",
            "expires_in": 1800
        }
        ```
        
    Usage:
        Clients should use the access_token in Authorization headers:
        Authorization: Bearer {access_token}
        
    Security Notes:
        - Token should be stored securely by the client
        - expires_in indicates when token will become invalid
        - Token type "bearer" follows OAuth 2.0 specification
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class LoginResponse(BaseModel):
    """
    Complete authentication response model for login endpoints.
    
    This model combines user information and authentication token data
    into a comprehensive login response. It provides everything a client
    needs to establish an authenticated session.
    
    Attributes:
        user (UserResponse): Complete user profile information
        token (Token): JWT token with expiration details
        message (str): Success message confirming authentication
        
    Example Response:
        ```json
        {
            "user": {
                "id": 123,
                "username": "john_doe",
                "age": 25,
                "description": "Software developer"
            },
            "token": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            },
            "message": "Login successful"
        }
        ```
        
    Client Usage:
        1. Store the access_token for subsequent API calls
        2. Use user information for UI display
        3. Track expires_in for token refresh logic
        4. Include token in Authorization header for protected endpoints
        
    Security:
        - Contains all information needed for secure session management
        - User data helps with client-side authorization decisions
        - Token provides server-side authentication capability
    """
    user: UserResponse = Field(..., description="User information")
    token: Token = Field(..., description="Authentication token")
    message: str = Field(default="Login successful", description="Success message")
