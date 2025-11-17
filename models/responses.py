from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    id: int = Field(..., description="Unique user identifier")
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Username (3-30 characters, alphanumeric and underscores)",
    )
    age: int = Field(..., gt=0, le=120, description="User age (1-120 years)")
    description: str = Field(
        ..., max_length=200, description="User description (max 200 characters)"
    )

    class Config:
        from_attributes = True  # Allows creating from SQLAlchemy models
