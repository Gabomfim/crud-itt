from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db, User
from models.requests import UserRequest, PasswordChangeRequest
from models.responses import UserResponse
from services.auth_service import get_current_user
from services.user_service import (
    create_new_user,
    delete_user_by_username,
    get_user_by_username,
    get_users_by_minimum_age,
    update_user_by_username,
    change_user_password,
)

router = APIRouter()


@router.get("/{username}", response_model=UserResponse)
async def get_user_information(
    username: str, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Get user information by username (requires authentication)"""
    return await get_user_by_username(username, db)


@router.get("", response_model=list[UserResponse])
async def get_with_minimum_age(
    minimum_age: int, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> list[UserResponse]:
    """Get users with minimum age (requires authentication)"""
    return await get_users_by_minimum_age(minimum_age, db)


@router.post("", status_code=201)
async def create_user(
    user_request: UserRequest, db: AsyncSession = Depends(get_db)
) -> dict:
    """Create a new user"""
    return await create_new_user(user_request, db)


@router.delete("/{username}", status_code=204)
async def delete_user(
    username: str, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete a user by username (requires authentication)"""
    await delete_user_by_username(username, db)
    return None


@router.put("/{username}", status_code=204)
async def update_user(
    username: str, 
    user_request: UserRequest, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """Update user information (requires authentication)"""
    await update_user_by_username(username, user_request, db)
    return None


@router.put("/{username}/password")
async def change_password(
    username: str, 
    password_request: PasswordChangeRequest, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    """Change user password (requires authentication)"""
    return await change_user_password(username, password_request, db)
