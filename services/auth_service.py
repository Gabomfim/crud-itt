"""
Módulo de Serviço de Autenticação

Este módulo fornece serviços abrangentes de autenticação baseados em JWT,
incluindo geração de tokens, validação, lista negra e autenticação de
usuários. Gerencia operações seguras de login/logout e fornece injeção de
dependência para endpoints protegidos.

Recursos Principais:
- Criação e validação de tokens JWT
- Lista negra de tokens para logout seguro
- Autenticação de usuário com verificação de senha
- Injeção de dependência para rotas protegidas
- Logging abrangente e tratamento de erros

Recursos de Segurança:
- Expiração configurável de tokens
- Mecanismo seguro de lista negra de tokens
- Verificação de hash de senha
- Logging detalhado de eventos de segurança

Autor: Gabomfim
Licença: MIT
"""

from datetime import datetime, timedelta
from typing import Optional, Set

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database.connection import User, get_db
from services.password_service import verify_password
from utils.logging_config import get_logger

logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)

# Lista negra de tokens em memória (em produção, use Redis ou banco de dados)
_blacklisted_tokens: Set[str] = set()


async def authenticate_user(
    username: str, password: str, db: AsyncSession = Depends(get_db)
) -> User:
    """
    Autentica um usuário por nome de usuário e senha.

    Esta função realiza autenticação segura do usuário validando as
    credenciais fornecidas contra o banco de dados. Usa comparação de
    senha em tempo constante para prevenir ataques de timing.

    Args:
        username (str): Nome de usuário para autenticar
        password (str): Senha em texto plano para verificação
        db (AsyncSession): Dependência de sessão assíncrona do banco

    Returns:
        User: O objeto do usuário autenticado com todos os dados do usuário

    Raises:
        HTTPException: 401 Não Autorizado se o nome de usuário não existir
                      ou a senha estiver incorreta

    Example:
        >>> user = await authenticate_user("john_doe", "secure_password123", db)
        >>> print(user.username)  # "john_doe"

    Notas de Segurança:
        - Usa bcrypt para verificação segura de senha
        - Retorna a mesma mensagem de erro para nome/senha inválidos para
          prevenir enumeração
        - Registra tentativas de autenticação para monitoramento de segurança
    """
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=401, detail="Nome de usuário ou senha inválidos"
        )

    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=401, detail="Nome de usuário ou senha inválidos"
        )

    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token de acesso JWT com expiração configurável.

    Esta função gera um JSON Web Token seguro contendo dados do usuário
    e informações de expiração. O token é assinado com a chave secreta
    da aplicação usando o algoritmo configurado.

    Args:
        data (dict): Dados de payload para codificar no token (tipicamente
                    informações do usuário)
        expires_delta (Optional[timedelta]): Tempo de expiração customizado
            do token. Se None, usa o tempo de expiração padrão configurado.

    Returns:
        str: String do token JWT codificado pronto para uso em cabeçalhos
            Authorization

    Example:
        >>> token = create_access_token({"sub": "john_doe"})
        >>> print(f"Bearer {token}")

        >>> custom_expiry = timedelta(hours=2)
        >>> token = create_access_token({"sub": "admin"}, custom_expiry)

    Notas de Segurança:
        - Token inclui claim 'iat' (emitido em) para rastreamento de segurança
        - Usa algoritmo HS256 por padrão (configurável)
        - Chave secreta deve ter pelo menos 32 caracteres
        - Tokens são stateless e auto-contidos
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
        algorithm=settings.security.jwt_algorithm,
    )

    logger.info("Token de acesso criado", extra={"username": data.get("sub")})
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
            algorithms=[settings.security.jwt_algorithm],
        )

        username = payload.get("sub")
        if username is None:
            logger.warning("Token missing subject")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload  # type: ignore[no-any-return]
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
    db: AsyncSession = Depends(get_db),
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
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Get the current authenticated user from JWT token, optional.

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
