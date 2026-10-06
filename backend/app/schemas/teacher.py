from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional, List
from datetime import date, datetime


class TeacherResponse(BaseModel):
    teacher_id: UUID
    user_id: UUID
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    employee_id: Optional[str] = None
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    subjects: List[str] = []
    classes: List[str] = []
    joining_date: Optional[date] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ClassTeacherResponse(BaseModel):
    class_teacher_id: UUID
    user_id: UUID
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    employee_id: Optional[str] = None
    assigned_class: Optional[str] = None
    assigned_section: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
