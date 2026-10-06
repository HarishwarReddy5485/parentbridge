from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional
from app.models.user import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminRegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    employee_id: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: UserRole
    user_id: UUID
    full_name: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class CurrentUserResponse(BaseModel):
    user_id: UUID
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True
