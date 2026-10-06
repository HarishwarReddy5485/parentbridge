from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User, UserRole
from app.models.student import Student, StudentParent
from app.models.assignment import Assignment
from app.models.grade import Grade
from app.models.attendance import Attendance
from app.schemas.student import StudentResponse
from app.schemas.assignment import AssignmentResponse
from app.schemas.grade import GradeResponse
from app.schemas.attendance import AttendanceResponse
from app.schemas.progress import StudentProgressResponse
from app.services.progress_service import get_student_progress_summary
from app.security.deps import require_roles, get_current_user

router = APIRouter(
    prefix="/parent",
    tags=["Parent"],
    dependencies=[Depends(require_roles(UserRole.PARENT, UserRole.ADMIN))]
)


async def verify_parent_access(parent_user_id: UUID, student_id: UUID, db: AsyncSession, is_admin: bool = False):
    """Ensure parent is linked to the requested child."""
    if is_admin:
        return True
    stmt = select(StudentParent).where(
        StudentParent.parent_user_id == parent_user_id,
        StudentParent.student_id == student_id
    )
    result = await db.execute(stmt)
    if not result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You do not have permission to view this student."
        )
    return True


@router.get("/children", response_model=List[StudentResponse])
async def list_children(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all children/students linked to the parent account."""
    if current_user.role == UserRole.ADMIN:
        result = await db.execute(select(Student))
        return result.scalars().all()

    stmt = select(Student).join(
        StudentParent, Student.student_id == StudentParent.student_id
    ).where(StudentParent.parent_user_id == current_user.user_id)

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/children/{student_id}/assignments", response_model=List[AssignmentResponse])
async def get_child_assignments(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """View homework and assignments for the child's class."""
    await verify_parent_access(current_user.user_id, student_id, db, is_admin=(current_user.role == UserRole.ADMIN))

    # Fetch child's class
    res_s = await db.execute(select(Student).where(Student.student_id == student_id))
    child = res_s.scalars().first()
    if not child:
        raise HTTPException(status_code=404, detail="Student not found")

    stmt = select(Assignment).where(
        Assignment.class_name == child.class_name,
        Assignment.is_active == True
    ).order_by(Assignment.due_date.asc())

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/children/{student_id}/grades", response_model=List[GradeResponse])
async def get_child_grades(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """View all exam grades and marks for the child."""
    await verify_parent_access(current_user.user_id, student_id, db, is_admin=(current_user.role == UserRole.ADMIN))
    result = await db.execute(select(Grade).where(Grade.student_id == student_id).order_by(Grade.created_at.desc()))
    return result.scalars().all()


@router.get("/children/{student_id}/attendance", response_model=List[AttendanceResponse])
async def get_child_attendance(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """View child's attendance records."""
    await verify_parent_access(current_user.user_id, student_id, db, is_admin=(current_user.role == UserRole.ADMIN))
    result = await db.execute(select(Attendance).where(Attendance.student_id == student_id).order_by(Attendance.date.desc()))
    return result.scalars().all()


@router.get("/children/{student_id}/progress", response_model=StudentProgressResponse)
async def get_child_progress(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """View child's overall academic progress percentage, totals, and breakdown."""
    await verify_parent_access(current_user.user_id, student_id, db, is_admin=(current_user.role == UserRole.ADMIN))
    progress = await get_student_progress_summary(student_id, db)
    if not progress:
        raise HTTPException(status_code=404, detail="Student not found")
    return progress
