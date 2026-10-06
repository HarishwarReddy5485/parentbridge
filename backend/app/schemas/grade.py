from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class GradeCreate(BaseModel):
    student_id: UUID
    subject: str
    exam_type: str
    marks_obtained: Decimal
    total_marks: Decimal
    grade: Optional[str] = None
    remarks: Optional[str] = None
    exam_date: Optional[date] = None


class GradeUpdate(BaseModel):
    subject: Optional[str] = None
    exam_type: Optional[str] = None
    marks_obtained: Optional[Decimal] = None
    total_marks: Optional[Decimal] = None
    grade: Optional[str] = None
    remarks: Optional[str] = None
    exam_date: Optional[date] = None


class GradeResponse(BaseModel):
    grade_id: UUID
    student_id: UUID
    teacher_id: UUID
    subject: str
    exam_type: str
    marks_obtained: Decimal
    total_marks: Decimal
    grade: Optional[str] = None
    remarks: Optional[str] = None
    exam_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
