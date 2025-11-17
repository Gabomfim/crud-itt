from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import User, get_db
from models.requests import PasswordChangeRequest, UserRequest
from models.responses import UserResponse
from services.password_service import hash_password, verify_password
from utils.logging_config import get_logger

logger = get_logger(__name__)


async def get_user_by_username(
    username: str, db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Get user information by username"""
    logger.info("Fetching user by username", extra={"username": username})

    try:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user:
            logger.warning("User not found", extra={"username": username})
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(
            "User found successfully", extra={"username": username, "user_id": user.id}
        )

        return UserResponse(
            id=user.id,
            username=user.username,
            age=user.age,
            description=user.description,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error fetching user by username",
            extra={"username": username, "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_users_by_minimum_age(
    minimum_age: int, db: AsyncSession = Depends(get_db)
) -> list[UserResponse]:
    """Get users with minimum age"""
    logger.info("Fetching users by minimum age", extra={"minimum_age": minimum_age})

    try:
        result = await db.execute(select(User).where(User.age >= minimum_age))
        users = result.scalars().all()

        if not users:
            logger.warning(
                "No users found with minimum age", extra={"minimum_age": minimum_age}
            )
            raise HTTPException(
                status_code=404, detail="No users found with the specified minimum age"
            )

        logger.info(
            "Users found successfully",
            extra={"minimum_age": minimum_age, "user_count": len(users)},
        )

        return [
            UserResponse(
                id=user.id,
                username=user.username,
                age=user.age,
                description=user.description,
            )
            for user in users
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error fetching users by minimum age",
            extra={"minimum_age": minimum_age, "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")


async def create_new_user(
    user_request: UserRequest, db: AsyncSession = Depends(get_db)
) -> dict:
    """Create a new user"""
    logger.info("Creating new user", extra={"username": user_request.username})

    try:
        # Check if username already exists
        result = await db.execute(
            select(User).where(User.username == user_request.username)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            logger.warning(
                "Username already exists", extra={"username": user_request.username}
            )
            raise HTTPException(status_code=400, detail="Username already exists")

        # Hash the password before storing
        hashed_password = hash_password(user_request.password)

        new_user = User(
            username=user_request.username,
            password=hashed_password,
            age=user_request.age,
            description=user_request.description,
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        logger.info(
            "User created successfully",
            extra={"username": user_request.username, "user_id": new_user.id},
        )

        return {"message": "User created successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error creating user",
            extra={"username": user_request.username, "error": str(e)},
            exc_info=True,
        )
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


async def delete_user_by_username(
    username: str, db: AsyncSession = Depends(get_db)
) -> dict:
    """Delete a user by username"""
    logger.info("Deleting user by username", extra={"username": username})

    try:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user:
            logger.warning("User not found for deletion", extra={"username": username})
            raise HTTPException(status_code=404, detail="User not found")

        db.delete(user)  # type: ignore
        await db.commit()

        logger.info(
            "User deleted successfully",
            extra={"username": username, "user_id": user.id},
        )

        return {"message": "User deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error deleting user",
            extra={"username": username, "error": str(e)},
            exc_info=True,
        )
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


async def update_user_by_username(
    username: str, user_request: UserRequest, db: AsyncSession = Depends(get_db)
) -> dict:
    """Update user information by username"""
    logger.info("Updating user by username", extra={"username": username})

    try:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user:
            logger.warning("User not found for update", extra={"username": username})
            raise HTTPException(status_code=404, detail="User not found")

        # Update user fields
        if user_request.password:
            user.password = hash_password(user_request.password)
        if user_request.age is not None:
            user.age = user_request.age
        if user_request.description is not None:
            user.description = user_request.description

        await db.commit()
        await db.refresh(user)

        logger.info(
            "User updated successfully",
            extra={"username": username, "user_id": user.id},
        )

        return {"message": "User updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error updating user",
            extra={"username": username, "error": str(e)},
            exc_info=True,
        )
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


async def change_user_password(
    username: str,
    password_request: PasswordChangeRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Change user password after verifying current password"""
    logger.info("Changing password for user", extra={"username": username})

    try:
        # Get user from database
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user:
            logger.warning(
                "User not found for password change", extra={"username": username}
            )
            raise HTTPException(status_code=404, detail="User not found")

        # Verify current password
        if not verify_password(password_request.current_password, user.password):
            logger.warning(
                "Invalid current password provided", extra={"username": username}
            )
            raise HTTPException(status_code=400, detail="Current password is incorrect")

        # Check if new password is the same as current password
        if verify_password(password_request.new_password, user.password):
            logger.warning(
                "New password same as current password", extra={"username": username}
            )
            raise HTTPException(
                status_code=400,
                detail="New password must be different from current password",
            )

        # Hash new password and update user
        hashed_new_password = hash_password(password_request.new_password)
        user.password = hashed_new_password

        await db.commit()
        await db.refresh(user)

        logger.info(
            "Password changed successfully",
            extra={"username": username, "user_id": user.id},
        )

        return {"message": "Password changed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error changing user password",
            extra={"username": username, "error": str(e)},
            exc_info=True,
        )
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
