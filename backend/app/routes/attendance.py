from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User, UserRole
from app.models.attendance import Attendance
from app.models.teacher import Teacher
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate, AttendanceResponse
from app.security.deps import get_current_user, require_roles

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def record_attendance(
    att_in: AttendanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.CLASS_TEACHER, UserRole.ADMIN))
):
    """Teachers record student attendance."""
    # Check if entry exists for this date
    existing = await db.execute(
        select(Attendance).where(Attendance.student_id == att_in.student_id, Attendance.date == att_in.date)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Attendance already recorded for this student on this date")

    t_res = await db.execute(select(Teacher).where(Teacher.user_id == current_user.user_id))
    teacher = t_res.scalars().first()
    t_id = teacher.teacher_id if teacher else current_user.user_id

    attendance = Attendance(
        student_id=att_in.student_id,
        teacher_id=t_id,
        date=att_in.date,
        status=att_in.status.lower(),
        remarks=att_in.remarks
    )
    db.add(attendance)
    await db.commit()
    await db.refresh(attendance)
    return attendance


@router.put("/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance_record(
    attendance_id: UUID,
    att_in: AttendanceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.CLASS_TEACHER, UserRole.ADMIN))
):
    """Update an attendance record."""
    result = await db.execute(select(Attendance).where(Attendance.attendance_id == attendance_id))
    att = result.scalars().first()
    if not att:
        raise HTTPException(status_code=404, detail="Attendance entry not found")

    if att_in.status is not None:
        att.status = att_in.status.lower()
    if att_in.remarks is not None:
        att.remarks = att_in.remarks

    await db.commit()
    await db.refresh(att)
    return att


@router.get("/student/{student_id}", response_model=List[AttendanceResponse])
async def list_student_attendance(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all attendance logs for a student."""
    result = await db.execute(select(Attendance).where(Attendance.student_id == student_id).order_by(Attendance.date.desc()))
    return result.scalars().all()
