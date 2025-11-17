from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import User, get_db
from services.password_service import verify_password


async def authenticate_user(
    username: str, password: str, db: AsyncSession = Depends(get_db)
) -> User:
    """
    Authenticate a user by username and password.

    Args:
        username: Username to authenticate
        password: Plain text password
        db: Database session

    Returns:
        User object if authentication successful

    Raises:
        HTTPException: If authentication fails
    """
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return user
