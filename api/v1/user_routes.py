from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from models.requests import UserRequest
from models.responses import UserResponse
from services.user_service import (
    create_new_user,
    delete_user_by_username,
    get_user_by_username,
    get_users_by_minimum_age,
    update_user_by_username,
)

router = APIRouter()


@router.get("/{username}", response_model=UserResponse)
async def get_user_information(
    username: str, db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Get user information by username"""
    return await get_user_by_username(username, db)


@router.get("", response_model=list[UserResponse])
async def get_with_minimum_age(
    minimum_age: int, db: AsyncSession = Depends(get_db)
) -> list[UserResponse]:
    """Get users with minimum age"""
    return await get_users_by_minimum_age(minimum_age, db)


@router.post("", status_code=201)
async def create_user(
    user_request: UserRequest, db: AsyncSession = Depends(get_db)
) -> dict:
    """Create a new user"""
    return await create_new_user(user_request, db)


@router.delete("/{username}", status_code=204)
async def delete_user(username: str, db: AsyncSession = Depends(get_db)) -> dict:
    """Delete a user by username"""
    return await delete_user_by_username(username, db)


@router.put("/{username}", status_code=204)
async def update_user(
    username: str, user_request: UserRequest, db: AsyncSession = Depends(get_db)
) -> dict:
    """Update user information"""
    return await update_user_by_username(username, user_request, db)
