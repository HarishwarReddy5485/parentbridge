from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import date, datetime


class AttendanceCreate(BaseModel):
    student_id: UUID
    date: date
    status: str  # 'present', 'absent', 'late', 'leave'
    remarks: Optional[str] = None


class AttendanceUpdate(BaseModel):
    status: Optional[str] = None
    remarks: Optional[str] = None


class AttendanceResponse(BaseModel):
    attendance_id: UUID
    student_id: UUID
    teacher_id: UUID
    date: date
    status: str
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
