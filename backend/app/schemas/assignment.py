from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class AssignmentCreate(BaseModel):
    title: str
    subject: str
    description: Optional[str] = None
    class_name: str
    section: Optional[str] = None
    due_date: date
    assigned_date: Optional[date] = None
    total_marks: Optional[Decimal] = Decimal("100.00")
    attachment_url: Optional[str] = None


class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    class_name: Optional[str] = None
    section: Optional[str] = None
    due_date: Optional[date] = None
    total_marks: Optional[Decimal] = None
    attachment_url: Optional[str] = None
    is_active: Optional[bool] = None


class AssignmentResponse(BaseModel):
    assignment_id: UUID
    teacher_id: UUID
    title: str
    subject: str
    description: Optional[str] = None
    class_name: str
    section: Optional[str] = None
    assigned_date: date
    due_date: date
    total_marks: Decimal
    attachment_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
