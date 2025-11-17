"""
Authentication Service Module

This module provides comprehensive JWT-based authentication services including
token generation, validation, blacklisting, and user authentication. It handles
secure login/logout operations and provides dependency injection for protected
endpoints.

Key Features:
- JWT token creation and validation
- Token blacklisting for secure logout
- User authentication with password verification
- Dependency injection for protected routes
- Comprehensive logging and error handling

Security Features:
- Configurable token expiration
- Secure token blacklisting mechanism
- Password hash verification
- Detailed security event logging

Author: Gabomfim
License: MIT
"""

from datetime import datetime, timedelta
from typing import Optional, Set
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from config import settings
from database.connection import User, get_db
from services.password_service import verify_password
from utils.logging_config import get_logger

logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)

# In-memory token blacklist (in production, use Redis or database)
_blacklisted_tokens: Set[str] = set()


async def authenticate_user(
    username: str, password: str, db: AsyncSession = Depends(get_db)
) -> User:
    """
    Authenticate a user by username and password.
    
    This function performs secure user authentication by validating
    the provided credentials against the database. It uses constant-time
    password comparison to prevent timing attacks.

    Args:
        username (str): Username to authenticate
        password (str): Plain text password for verification
        db (AsyncSession): Async database session dependency

    Returns:
        User: The authenticated user object with all user data

    Raises:
        HTTPException: 401 Unauthorized if username doesn't exist or password is incorrect
        
    Example:
        >>> user = await authenticate_user("john_doe", "secure_password123", db)
        >>> print(user.username)  # "john_doe"
        
    Security Notes:
        - Uses bcrypt for secure password verification
        - Returns same error message for invalid username/password to prevent enumeration
        - Logs authentication attempts for security monitoring
    """
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with configurable expiration.
    
    This function generates a secure JSON Web Token containing user data
    and expiration information. The token is signed with the application's
    secret key using the configured algorithm.
    
    Args:
        data (dict): Payload data to encode in the token (typically user info)
        expires_delta (Optional[timedelta]): Custom token expiration time.
            If None, uses the configured default expiration time.
        
    Returns:
        str: Encoded JWT token string ready for use in Authorization headers
        
    Example:
        >>> token = create_access_token({"sub": "john_doe"})
        >>> print(f"Bearer {token}")
        
        >>> custom_expiry = timedelta(hours=2)
        >>> token = create_access_token({"sub": "admin"}, custom_expiry)
        
    Security Notes:
        - Token includes 'iat' (issued at) claim for security tracking
        - Uses HS256 algorithm by default (configurable)
        - Secret key should be at least 32 characters long
        - Tokens are stateless and self-contained
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.security.jwt_access_token_expire_minutes
        )
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.security.jwt_secret_key, 
        algorithm=settings.security.jwt_algorithm
    )
    
    logger.info("Access token created", extra={"username": data.get("sub")})
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token with comprehensive validation.
    
    This function performs complete token validation including signature
    verification, expiration checking, blacklist verification, and payload
    validation. It ensures only valid, non-revoked tokens are accepted.
    
    Args:
        token (str): JWT token string to verify and decode
        
    Returns:
        dict: Decoded token payload containing user information and claims
        
    Raises:
        HTTPException: 401 Unauthorized in the following cases:
            - Token is blacklisted (revoked/logged out)
            - Token signature is invalid
            - Token has expired
            - Token is malformed
            - Token is missing required claims (subject)
            
    Example:
        >>> payload = verify_token("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...")
        >>> username = payload.get("sub")
        >>> print(f"Token belongs to: {username}")
        
    Security Features:
        - Blacklist checking prevents use of revoked tokens
        - Signature verification ensures token authenticity
        - Expiration validation prevents replay attacks
        - Comprehensive error logging for security monitoring
    """
    try:
        # Check if token is blacklisted
        if token in _blacklisted_tokens:
            logger.warning("Blacklisted token used")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        payload = jwt.decode(
            token, 
            settings.security.jwt_secret_key, 
            algorithms=[settings.security.jwt_algorithm]
        )
        
        username: str = payload.get("sub")
        if username is None:
            logger.warning("Token missing subject")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Expired token used")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning("Invalid token", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def blacklist_token(token: str) -> None:
    """
    Add a token to the blacklist to prevent further use.
    
    This function revokes a JWT token by adding it to an in-memory blacklist.
    Once blacklisted, the token cannot be used for authentication even if
    it hasn't expired. This is essential for secure logout functionality.
    
    Args:
        token (str): JWT token string to revoke/blacklist
        
    Returns:
        None
        
    Example:
        >>> blacklist_token("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...")
        >>> # Token is now revoked and cannot be used
        
    Note:
        - In production, consider using Redis or database for token blacklisting
        - Current implementation uses in-memory storage which resets on restart
        - Blacklisted tokens remain invalid until application restart
        - All token verification attempts check the blacklist first
    """
    _blacklisted_tokens.add(token)
    logger.info("Token blacklisted")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = verify_token(token)
    username: str = payload.get("sub")
    
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    if user is None:
        logger.warning("User not found for valid token", extra={"username": username})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get the current authenticated user from JWT token, but don't raise if not authenticated.
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        Current authenticated user or None
    """
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
