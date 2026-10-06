from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User, UserRole
from app.models.grade import Grade
from app.models.teacher import Teacher
from app.schemas.grade import GradeCreate, GradeUpdate, GradeResponse
from app.services.progress_service import calculate_letter_grade
from app.security.deps import get_current_user, require_roles

router = APIRouter(prefix="/grades", tags=["Grades"])


@router.post("", response_model=GradeResponse, status_code=status.HTTP_201_CREATED)
async def create_grade(
    grade_in: GradeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.CLASS_TEACHER, UserRole.ADMIN))
):
    """Teachers submit or record exam/test grades for a student."""
    t_res = await db.execute(select(Teacher).where(Teacher.user_id == current_user.user_id))
    teacher = t_res.scalars().first()
    t_id = teacher.teacher_id if teacher else current_user.user_id

    # Compute letter grade if not provided
    auto_letter = grade_in.grade
    if not auto_letter and grade_in.total_marks > 0:
        pct = float(grade_in.marks_obtained) / float(grade_in.total_marks) * 100
        auto_letter = calculate_letter_grade(pct)

    grade = Grade(
        student_id=grade_in.student_id,
        teacher_id=t_id,
        subject=grade_in.subject,
        exam_type=grade_in.exam_type,
        marks_obtained=grade_in.marks_obtained,
        total_marks=grade_in.total_marks,
        grade=auto_letter,
        remarks=grade_in.remarks,
        exam_date=grade_in.exam_date
    )
    db.add(grade)
    await db.commit()
    await db.refresh(grade)
    return grade


@router.put("/{grade_id}", response_model=GradeResponse)
async def update_grade(
    grade_id: UUID,
    grade_in: GradeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.CLASS_TEACHER, UserRole.ADMIN))
):
    """Update student grade entry."""
    result = await db.execute(select(Grade).where(Grade.grade_id == grade_id))
    grade = result.scalars().first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade entry not found")

    for key, value in grade_in.model_dump(exclude_unset=True).items():
        setattr(grade, key, value)

    # Recalculate letter grade
    if grade.total_marks > 0:
        pct = float(grade.marks_obtained) / float(grade.total_marks) * 100
        grade.grade = calculate_letter_grade(pct)

    await db.commit()
    await db.refresh(grade)
    return grade


@router.get("/student/{student_id}", response_model=List[GradeResponse])
async def list_student_grades(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all grades awarded to a specific student."""
    result = await db.execute(select(Grade).where(Grade.student_id == student_id).order_by(Grade.created_at.desc()))
    return result.scalars().all()
