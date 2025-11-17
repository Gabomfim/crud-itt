"""
Request Models Module

This module defines Pydantic models for API request validation and serialization.
All request models include comprehensive validation, field constraints, and
security checks to ensure data integrity and application security.

Key Features:
- Strong input validation with field constraints
- Password complexity validation
- Username format validation
- Confirmation field matching
- Custom validation methods

Models:
- UserRequest: Complete user registration/update data
- PasswordChangeRequest: Secure password change with validation
- LoginRequest: Simple authentication credentials

Author: Gabomfim
License: MIT
"""

import re

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class UserRequest(BaseModel):
    """
    User registration and update request model.

    This model validates user registration and profile update requests.
    It includes comprehensive validation for username format, password
    complexity, age constraints, and description length.

    Attributes:
        username (str): Unique username with alphanumeric and underscore characters
        password (str): Secure password meeting complexity requirements
        age (int): User age between 1 and 120 years
        description (str): Optional user description up to 200 characters

    Validation Rules:
        - Username: 3-30 characters, alphanumeric + underscores only
        - Password: Minimum 8 characters with complexity requirements
        - Age: Must be between 1 and 120
        - Description: Maximum 200 characters, optional

    Example:
        ```python
        user_data = UserRequest(
            username="john_doe",
            password="SecurePass123!",
            age=25,
            description="Software developer"
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
