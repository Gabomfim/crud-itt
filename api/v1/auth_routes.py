"""
Authentication API Routes Module

This module defines REST API endpoints for user authentication operations
including login, logout, and user profile access. All endpoints follow
REST conventions and provide comprehensive error handling.

Endpoints:
- POST /login: Authenticate user and return JWT token
- POST /logout: Revoke JWT token and log out user
- GET /me: Get current authenticated user information

Features:
- JWT-based authentication
- Secure token management
- Comprehensive request/response validation
- Detailed logging for security monitoring
- Proper HTTP status codes and error messages

Security:
- Password verification using bcrypt
- JWT token generation with configurable expiration
- Token blacklisting for secure logout
- Request validation and sanitization

Author: Gabomfim
License: MIT
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database.connection import get_db
from models.requests import LoginRequest
from models.responses import LoginResponse, Token, UserResponse
from services.auth_service import (
    authenticate_user,
    blacklist_token,
    create_access_token,
    get_current_user,
    security,
)
from utils.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    login_request: LoginRequest, db: AsyncSession = Depends(get_db)
) -> LoginResponse:
    """
    Authenticate user and return JWT access token.

    This endpoint validates user credentials and returns a complete
    authentication response including user information and JWT token.
    The token can be used for subsequent authenticated requests.

    Args:
        login_request (LoginRequest): User credentials (username and password)
        db (AsyncSession): Database session dependency

    Returns:
        LoginResponse: Complete authentication response containing:
            - user: User profile information
            - token: JWT access token with expiration
            - message: Success confirmation

    Raises:
        HTTPException:
            - 401 Unauthorized: Invalid username or password
            - 500 Internal Server Error: Unexpected server error

    Example Request:
        ```json
        POST /api/v1/auth/login
        {
            "username": "john_doe",
            "password": "secure_password123"
        }
        ```

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

    Security Notes:
        - Password verification uses secure bcrypt hashing
        - Failed attempts are logged for security monitoring
        - Returns consistent error messages to prevent user enumeration
        - JWT tokens are signed with application secret key
    """
    logger.info("Login attempt", extra={"username": login_request.username})

    try:
        # Authenticate user
        user = await authenticate_user(
            login_request.username, login_request.password, db
        )

        # Create access token
        access_token_expires = timedelta(
            minutes=settings.security.jwt_access_token_expire_minutes
        )
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )

        # Create response
        user_response = UserResponse(
            id=user.id,
            username=user.username,
            age=user.age,
            description=user.description,
        )

        token_response = Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.security.jwt_access_token_expire_minutes * 60,
        )

        logger.info(
            "Login successful", extra={"username": user.username, "user_id": user.id}
        )

        return LoginResponse(
            user=user_response, token=token_response, message="Login successful"
        )

    except HTTPException as e:
        logger.warning(
            "Login failed",
            extra={"username": login_request.username, "error": e.detail},
        )
        raise
    except Exception as e:
        logger.error(
            "Login error",
            extra={"username": login_request.username, "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: UserResponse = Depends(get_current_user),
) -> dict[str, str]:
    """Logout user by blacklisting their token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    token = credentials.credentials
    blacklist_token(token)

    logger.info(
        "User logged out",
        extra={"username": current_user.username, "user_id": current_user.id},
    )

    return {"message": "Logout successful"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """Get current authenticated user information"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        age=current_user.age,
        description=current_user.description,
    )
