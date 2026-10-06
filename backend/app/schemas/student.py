from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional
from datetime import date, datetime


class StudentCreate(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = "Student@123"  # Default password if user account is created
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    class_name: str
    section: Optional[str] = None
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    roll_number: Optional[str] = None
    admission_number: Optional[str] = None
    admission_date: Optional[date] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    teacher_id: Optional[UUID] = None
    parent_user_id: Optional[UUID] = None  # Optional link to parent


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    class_name: Optional[str] = None
    section: Optional[str] = None
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    roll_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    teacher_id: Optional[UUID] = None


class StudentResponse(BaseModel):
    student_id: UUID
    user_id: Optional[UUID] = None
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    class_name: str
    section: Optional[str] = None
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    roll_number: Optional[str] = None
    admission_number: Optional[str] = None
    admission_date: Optional[date] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    teacher_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AssignTeacherRequest(BaseModel):
    teacher_id: UUID
