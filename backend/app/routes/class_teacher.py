from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User, UserRole
from app.models.class_teacher import ClassTeacher
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.notice import Notice
from app.schemas.student import StudentResponse
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate, AttendanceResponse
from app.schemas.notice import NoticeCreate, NoticeUpdate, NoticeResponse
from app.schemas.progress import StudentProgressResponse
from app.services.progress_service import get_student_progress_summary
from app.security.deps import require_roles, get_current_user

router = APIRouter(
    prefix="/class-teacher",
    tags=["Class Teacher"],
    dependencies=[Depends(require_roles(UserRole.CLASS_TEACHER, UserRole.ADMIN))]
)


@router.get("/students", response_model=List[StudentResponse])
async def list_class_students(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all students in the assigned class of the class teacher."""
    if current_user.role == UserRole.ADMIN:
        result = await db.execute(select(Student).order_by(Student.roll_number))
        return result.scalars().all()

    # Find class teacher assigned class
    ct_res = await db.execute(select(ClassTeacher).where(ClassTeacher.user_id == current_user.user_id))
    ct = ct_res.scalars().first()
    if not ct or not ct.assigned_class:
        return []

    stmt = select(Student).where(Student.class_name == ct.assigned_class)
    if ct.assigned_section:
        stmt = stmt.where(Student.section == ct.assigned_section)

    result = await db.execute(stmt.order_by(Student.roll_number))
    return result.scalars().all()


@router.get("/students/{student_id}", response_model=StudentResponse)
async def get_student_details(student_id: UUID, db: AsyncSession = Depends(get_db)):
    """View details of a specific student."""
    result = await db.execute(select(Student).where(Student.student_id == student_id))
    student = result.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.get("/marks/{student_id}", response_model=StudentProgressResponse)
async def get_student_cumulative_marks(student_id: UUID, db: AsyncSession = Depends(get_db)):
    """View cumulative exam marks and progress breakdown for a student."""
    progress = await get_student_progress_summary(student_id, db)
    if not progress:
        raise HTTPException(status_code=404, detail="Student not found")
    return progress


@router.post("/attendance", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def mark_class_attendance(
    att_in: AttendanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Class Teacher marks daily attendance for a student."""
    # Check if record already exists for date
    existing = await db.execute(
        select(Attendance).where(Attendance.student_id == att_in.student_id, Attendance.date == att_in.date)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Attendance already recorded for this date")

    attendance = Attendance(
        student_id=att_in.student_id,
        teacher_id=current_user.user_id,
        date=att_in.date,
        status=att_in.status.lower(),
        remarks=att_in.remarks
    )
    db.add(attendance)
    await db.commit()
    await db.refresh(attendance)
    return attendance


@router.put("/attendance/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(
    attendance_id: UUID,
    att_in: AttendanceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an attendance record."""
    result = await db.execute(select(Attendance).where(Attendance.attendance_id == attendance_id))
    att = result.scalars().first()
    if not att:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    if att_in.status is not None:
        att.status = att_in.status.lower()
    if att_in.remarks is not None:
        att.remarks = att_in.remarks

    await db.commit()
    await db.refresh(att)
    return att


@router.post("/notices", response_model=NoticeResponse, status_code=status.HTTP_201_CREATED)
async def create_class_notice(
    notice_in: NoticeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Class Teacher publishes notice to the class."""
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


@router.put("/notices/{notice_id}", response_model=NoticeResponse)
async def update_class_notice(notice_id: UUID, notice_in: NoticeUpdate, db: AsyncSession = Depends(get_db)):
    """Class Teacher updates a notice."""
    result = await db.execute(select(Notice).where(Notice.notice_id == notice_id))
    notice = result.scalars().first()
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")

    if notice_in.title is not None:
        notice.title = notice_in.title
    if notice_in.content is not None:
        notice.content = notice_in.content
    if notice_in.target_role is not None:
        notice.target_role = notice_in.target_role
    if notice_in.target_class_name is not None:
        notice.target_class_name = notice_in.target_class_name

    await db.commit()
    await db.refresh(notice)
    return notice


@router.delete("/notices/{notice_id}", status_code=status.HTTP_200_OK)
async def delete_class_notice(notice_id: UUID, db: AsyncSession = Depends(get_db)):
    """Class Teacher deletes a notice."""
    result = await db.execute(select(Notice).where(Notice.notice_id == notice_id))
    notice = result.scalars().first()
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")

    await db.delete(notice)
    await db.commit()
    return {"message": "Notice removed successfully"}
