from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.assignment import Assignment
from app.models.grade import Grade
from app.models.attendance import Attendance
from app.schemas.assignment import AssignmentResponse
from app.schemas.grade import GradeResponse
from app.schemas.attendance import AttendanceResponse
from app.schemas.progress import StudentProgressResponse
from app.services.progress_service import get_student_progress_summary
from app.security.deps import require_roles, get_current_user

router = APIRouter(
    prefix="/student",
    tags=["Student"],
    dependencies=[Depends(require_roles(UserRole.STUDENT, UserRole.ADMIN))]
)


async def get_my_student_record(current_user: User, db: AsyncSession) -> Student:
    """Retrieve the Student profile linked to the logged-in student user."""
    stmt = select(Student).where(Student.user_id == current_user.user_id)
    result = await db.execute(stmt)
    student = result.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found for this account")
    return student


@router.get("/assignments", response_model=List[AssignmentResponse])
async def get_my_assignments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Student views homework and assignments for their class."""
    student = await get_my_student_record(current_user, db)
    stmt = select(Assignment).where(
        Assignment.class_name == student.class_name,
        Assignment.is_active == True
    ).order_by(Assignment.due_date.asc())

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/grades", response_model=List[GradeResponse])
async def get_my_grades(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Student views all their test/exam grades."""
    student = await get_my_student_record(current_user, db)
    result = await db.execute(select(Grade).where(Grade.student_id == student.student_id).order_by(Grade.created_at.desc()))
    return result.scalars().all()


@router.get("/attendance", response_model=List[AttendanceResponse])
async def get_my_attendance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Student views their attendance record."""
    student = await get_my_student_record(current_user, db)
    result = await db.execute(select(Attendance).where(Attendance.student_id == student.student_id).order_by(Attendance.date.desc()))
    return result.scalars().all()


@router.get("/progress", response_model=StudentProgressResponse)
async def get_my_progress(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Student views their cumulative progress and percentage."""
    student = await get_my_student_record(current_user, db)
    progress = await get_student_progress_summary(student.student_id, db)
    if not progress:
        raise HTTPException(status_code=404, detail="Progress records not found")
    return progress
