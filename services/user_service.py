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
    """Obter informações do usuário por nome de usuário"""
    logger.info("Buscando usuário por nome de usuário", extra={"username": username})

    try:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user:
            logger.warning("Usuário não encontrado", extra={"username": username})
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        logger.info(
            "Usuário encontrado com sucesso",
            extra={"username": username, "user_id": user.id},
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
            "Erro ao buscar usuário por nome de usuário",
            extra={"username": username, "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


async def get_users_by_minimum_age(
    minimum_age: int, db: AsyncSession = Depends(get_db)
) -> list[UserResponse]:
    """Obter usuários com idade mínima"""
    logger.info(
        "Buscando usuários por idade mínima", extra={"minimum_age": minimum_age}
    )

    try:
        result = await db.execute(select(User).where(User.age >= minimum_age))
        users = result.scalars().all()

        if not users:
            logger.warning(
                "Nenhum usuário encontrado com idade mínima",
                extra={"minimum_age": minimum_age},
            )
            raise HTTPException(
                status_code=404,
                detail="Nenhum usuário encontrado com a idade mínima especificada",
            )

        logger.info(
            "Usuários encontrados com sucesso",
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
            "Erro ao buscar usuários por idade mínima",
            extra={"minimum_age": minimum_age, "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


async def create_new_user(
    user_request: UserRequest, db: AsyncSession = Depends(get_db)
) -> dict:
    """Criar um novo usuário"""
    logger.info("Criando novo usuário", extra={"username": user_request.username})

    try:
        # Verificar se o nome de usuário já existe
        result = await db.execute(
            select(User).where(User.username == user_request.username)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            logger.warning(
                "Nome de usuário já existe", extra={"username": user_request.username}
            )
            raise HTTPException(status_code=400, detail="Nome de usuário já existe")

        # Fazer hash da senha antes de armazenar
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
            "Usuário criado com sucesso",
            extra={"username": user_request.username, "user_id": new_user.id},
        )

        return {"message": "Usuário criado com sucesso"}

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

        await db.delete(user)
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
        if user_request.username:
            user.username = user_request.username
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
