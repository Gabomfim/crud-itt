import re

from pydantic import BaseModel, Field, validator


class UserRequest(BaseModel):
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

    @validator("password")
    def validate_password_complexity(cls, v: str) -> str:
        """
        Validate password complexity:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError(
                "Password must contain at least one special character "
                '(!@#$%^&*(),.?":{}|<>)'
            )

        return v
