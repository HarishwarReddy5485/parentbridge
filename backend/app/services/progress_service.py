from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from decimal import Decimal
from typing import Optional
from app.models.student import Student
from app.models.grade import Grade
from app.models.attendance import Attendance
from app.schemas.progress import StudentProgressResponse, SubjectGradeSummary


def calculate_letter_grade(percentage: float) -> str:
    """Helper to convert numeric percentage into standard letter grade."""
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    else:
        return "F"


async def get_student_progress_summary(student_id: UUID, db: AsyncSession) -> Optional[StudentProgressResponse]:
    """Calculate cumulative progress, grades, and attendance rate for a student."""
    # 1. Fetch student
    stmt_student = select(Student).where(Student.student_id == student_id)
    res_student = await db.execute(stmt_student)
    student = res_student.scalars().first()
    if not student:
        return None

    # 2. Fetch all grades for this student
    stmt_grades = select(Grade).where(Grade.student_id == student_id)
    res_grades = await db.execute(stmt_grades)
    grades = res_grades.scalars().all()

    total_obtained = Decimal("0.00")
    total_possible = Decimal("0.00")
    grade_summaries = []

    for g in grades:
        total_obtained += g.marks_obtained
        total_possible += g.total_marks
        sub_pct = (float(g.marks_obtained) / float(g.total_marks) * 100) if g.total_marks > 0 else 0.0
        grade_summaries.append(
            SubjectGradeSummary(
                subject=g.subject,
                exam_type=g.exam_type,
                marks_obtained=g.marks_obtained,
                total_marks=g.total_marks,
                percentage=round(sub_pct, 2),
                grade=g.grade or calculate_letter_grade(sub_pct)
            )
        )

    overall_pct = (float(total_obtained) / float(total_possible) * 100) if total_possible > 0 else 0.0

    # 3. Calculate Attendance Rate
    stmt_att_total = select(func.count(Attendance.attendance_id)).where(Attendance.student_id == student_id)
    res_att_total = await db.execute(stmt_att_total)
    total_days = res_att_total.scalar() or 0

    stmt_att_present = select(func.count(Attendance.attendance_id)).where(
        Attendance.student_id == student_id,
        Attendance.status.in_(["present", "late"])
    )
    res_att_present = await db.execute(stmt_att_present)
    present_days = res_att_present.scalar() or 0

    attendance_pct = (present_days / total_days * 100) if total_days > 0 else 100.0

    return StudentProgressResponse(
        student_id=student.student_id,
        student_name=student.full_name,
        class_name=student.class_name,
        section=student.section,
        total_marks_obtained=total_obtained,
        total_max_marks=total_possible,
        overall_percentage=round(overall_pct, 2),
        overall_grade=calculate_letter_grade(overall_pct),
        attendance_rate=round(attendance_pct, 2),
        grades=grade_summaries
    )
