from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    organization_id: int


class UserResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    email: str
    role: str
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
