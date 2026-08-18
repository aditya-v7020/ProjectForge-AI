"""ProjectForge AI — User Schemas."""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserRegister(BaseModel):
    """Registration request."""
    username: str = Field(..., min_length=3, max_length=150, description="Username (minimum 3 characters)")
    email: str = Field(..., min_length=5, max_length=255, description="Valid email address")
    password: str = Field(..., min_length=6, max_length=128, description="Password (minimum 6 characters)")


class UserLogin(BaseModel):
    """Login request."""
    username: str = Field(..., min_length=1, description="Username or Email")
    password: str = Field(..., min_length=1, description="Password")


class UserResponse(BaseModel):
    """User info response."""
    id: int
    username: str
    email: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
