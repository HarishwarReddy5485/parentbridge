from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User, UserRole
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.notice import Notice
from app.schemas.student import StudentResponse
from app.schemas.notice import NoticeCreate, NoticeResponse
from app.security.deps import require_roles, get_current_user

router = APIRouter(
    prefix="/teacher",
    tags=["Teacher"],
    dependencies=[Depends(require_roles(UserRole.TEACHER, UserRole.CLASS_TEACHER, UserRole.ADMIN))]
)


@router.get("/students", response_model=List[StudentResponse])
async def list_teacher_students(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List students taught or assigned to the teacher."""
    if current_user.role == UserRole.ADMIN:
        result = await db.execute(select(Student).order_by(Student.class_name, Student.roll_number))
        return result.scalars().all()

    # Get teacher record
    t_res = await db.execute(select(Teacher).where(Teacher.user_id == current_user.user_id))
    teacher = t_res.scalars().first()
    if not teacher:
        return []

    # Get students linked by teacher_id or enrolled in teacher's assigned classes
    stmt = select(Student).where(
        (Student.teacher_id == teacher.teacher_id) |
        (Student.class_name.in_(teacher.classes if teacher.classes else []))
    )
    result = await db.execute(stmt.order_by(Student.class_name, Student.roll_number))
    return result.scalars().all()


@router.get("/students/{student_id}", response_model=StudentResponse)
async def get_teacher_student_detail(student_id: UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve details for a single student."""
    result = await db.execute(select(Student).where(Student.student_id == student_id))
    student = result.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.post("/notices", response_model=NoticeResponse, status_code=status.HTTP_201_CREATED)
async def send_subject_notice(
    notice_in: NoticeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Teacher sends a subject or class-specific notice."""
    notice = Notice(
        created_by=current_user.user_id,
        title=notice_in.title,
        content=notice_in.content,
        target_role=notice_in.target_role,
        target_class_name=notice_in.target_class_name,
        target_section=notice_in.target_section
    )
    db.add(notice)
    await db.commit()
    await db.refresh(notice)
    return notice
