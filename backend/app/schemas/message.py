from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class MessageCreate(BaseModel):
    receiver_id: UUID
    receiver_role: UserRole
    student_id: Optional[UUID] = None
    subject: Optional[str] = None
    message: str


class MessageResponse(BaseModel):
    message_id: UUID
    conversation_id: UUID
    sender_id: UUID
    sender_role: UserRole
    receiver_id: UUID
    receiver_role: UserRole
    student_id: Optional[UUID] = None
    subject: Optional[str] = None
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
