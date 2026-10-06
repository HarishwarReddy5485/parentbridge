from sqlalchemy import Column, String, DateTime, Date, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Grade(Base):
    __tablename__ = "grades"

    grade_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.teacher_id", ondelete="CASCADE"), nullable=False)
    subject = Column(String, nullable=False)
    exam_type = Column(String, nullable=False)  # Unit Test, Midterm, Final, Quiz
    marks_obtained = Column(Numeric(10, 2), nullable=False)
    total_marks = Column(Numeric(10, 2), nullable=False)
    grade = Column(String, nullable=True)  # A, B, C, D, F
    remarks = Column(String, nullable=True)
    exam_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
