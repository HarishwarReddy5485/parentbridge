from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class NoticeCreate(BaseModel):
    title: str
    content: str
    target_role: Optional[UserRole] = None
    target_class_name: Optional[str] = None
    target_section: Optional[str] = None


class NoticeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    target_role: Optional[UserRole] = None
    target_class_name: Optional[str] = None
    target_section: Optional[str] = None


class NoticeResponse(BaseModel):
    notice_id: UUID
    created_by: UUID
    title: str
    content: str
    target_role: Optional[UserRole] = None
    target_class_name: Optional[str] = None
    target_section: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
