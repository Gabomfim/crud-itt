"""
Módulo de Modelos de Requisição

Este módulo define modelos Pydantic para validação e serialização de
requisições da API. Todos os modelos de requisição incluem validação
abrangente, restrições de campo e verificações de segurança para garantir
integridade de dados e segurança da aplicação.

Recursos Principais:
- Validação de entrada forte com restrições de campo
- Validação de complexidade de senha
- Validação de formato de nome de usuário
- Correspondência de campos de confirmação
- Métodos de validação customizados

Modelos:
- UserRequest: Dados completos de registro/atualização de usuário
- PasswordChangeRequest: Mudança de senha segura com validação
- LoginRequest: Credenciais simples de autenticação

Autor: Gabomfim
Licença: MIT
"""

import re

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class UserRequest(BaseModel):
    """
    Modelo de requisição de registro e atualização de usuário.

    Este modelo valida requisições de registro de usuário e atualização
    de perfil. Inclui validação abrangente para formato de nome de usuário,
    complexidade de senha, restrições de idade e comprimento de descrição.

    Atributos:
        username (str): Nome de usuário único com caracteres alfanuméricos e sublinhados
        password (str): Senha segura atendendo requisitos de complexidade
        age (int): Idade do usuário entre 1 e 120 anos
        description (str): Descrição opcional do usuário até 200 caracteres

    Regras de Validação:
        - Nome de usuário: 3-30 caracteres, apenas alfanuméricos + sublinhados
        - Senha: Mínimo 8 caracteres com requisitos de complexidade
        - Idade: Deve estar entre 1 e 120
        - Descrição: Máximo 200 caracteres, opcional

    Exemplo:
        ```python
        user_data = UserRequest(
            username="joao_silva",
            password="SenhaSegura123!",
            age=25,
            description="Desenvolvedor de software"
        )
        ```
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Username: 3-30 characters, letters, numbers, and underscores only",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description=(
            "Password: minimum 8 characters with uppercase, lowercase, "
            "number, and symbol"
        ),
    )
    age: int = Field(
        ..., gt=0, le=120, description="Age: must be between 1 and 120 years"
    )
    description: str = Field(
        default="",
        max_length=200,
        description="Optional description (max 200 characters)",
    )

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """
        Validate password complexity based on security settings.
        """
        from config import settings

        # Length validation
        if len(v) < settings.security.password_min_length:
            raise ValueError(
                f"Password must be at least "
                f"{settings.security.password_min_length} characters long"
            )

        # Uppercase validation
        if settings.security.password_require_uppercase and not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        # Lowercase validation
        if settings.security.password_require_lowercase and not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        # Digit validation
        if settings.security.password_require_digits and not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")

        # Special character validation
        if settings.security.password_require_special and not re.search(
            r'[!@#$%^&*(),.?":{}|<>]', v
        ):
            raise ValueError(
                "Password must contain at least one special character "
                '(!@#$%^&*(),.?":{}|<>)'
            )

        return v


class PasswordChangeRequest(BaseModel):
    """
    Password change request model with security validation.

    This model handles secure password change requests by validating
    the current password, ensuring new password complexity, and
    confirming password matching.

    Attributes:
        current_password (str): Current password for identity verification
        new_password (str): New password meeting complexity requirements
        confirm_password (str): Confirmation that must match new_password

    Security Features:
        - Current password verification required
        - New password complexity validation
        - Password confirmation matching
        - Prevents password reuse (handled at service level)

    Validation Rules:
        - Current password: Required for security verification
        - New password: Must meet all complexity requirements
        - Confirmation: Must exactly match new password

    Example:
        ```python
        password_change = PasswordChangeRequest(
            current_password="OldPassword123!",
            new_password="NewSecurePass456@",
            confirm_password="NewSecurePass456@"
        )
        ```
    """

    current_password: str = Field(..., description="Current password for verification")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description=(
            "New password: minimum 8 characters with uppercase, lowercase, "
            "number, and symbol"
        ),
    )
    confirm_password: str = Field(..., description="Confirmation of the new password")

    @field_validator("new_password")
    @classmethod
    def validate_new_password_complexity(cls, v: str) -> str:
        """
        Validate new password complexity based on security settings.
        """
        from config import settings

        # Length validation
        if len(v) < settings.security.password_min_length:
            raise ValueError(
                f"Password must be at least "
                f"{settings.security.password_min_length} characters long"
            )

        # Uppercase validation
        if settings.security.password_require_uppercase and not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        # Lowercase validation
        if settings.security.password_require_lowercase and not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        # Digit validation
        if settings.security.password_require_digits and not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")

        # Special character validation
        if settings.security.password_require_special and not re.search(
            r'[!@#$%^&*(),.?":{}|<>]', v
        ):
            raise ValueError(
                "Password must contain at least one special character "
                '(!@#$%^&*(),.?":{}|<>)'
            )

        return v

    @field_validator("confirm_password")
    @classmethod
    def validate_password_match(cls, v: str, info: ValidationInfo) -> str:
        """
        Validate that confirm_password matches new_password.
        """
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Password confirmation does not match new password")
        return v


class LoginRequest(BaseModel):
    """
    User authentication login request model.

    This model validates user login credentials for authentication.
    It performs basic input validation while keeping the interface
    simple for authentication purposes.

    Attributes:
        username (str): Username for authentication (3-30 characters)
        password (str): Password for authentication (no complexity validation here)

    Note:
        Password complexity is not validated in login requests since
        users may have accounts created with older password policies.
        Validation occurs during password creation/change operations.

    Example:
        ```python
        login_data = LoginRequest(
            username="john_doe",
            password="user_password"
        )
        ```

    Security:
        - Username length validation prevents extremely long inputs
        - Password is accepted as-is for existing user verification
        - Authentication security handled at service layer
    """

    username: str = Field(
        ..., min_length=3, max_length=30, description="Username for authentication"
    )
    password: str = Field(..., description="Password for authentication")
