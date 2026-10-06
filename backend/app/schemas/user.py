from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    role: UserRole

    # Role specific fields for seamless creation by admin
    employee_id: Optional[str] = None
    assigned_class: Optional[str] = None
    assigned_section: Optional[str] = None
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    subjects: Optional[List[str]] = None
    classes: Optional[List[str]] = None
    is_super_admin: Optional[bool] = False


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    user_id: UUID
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
