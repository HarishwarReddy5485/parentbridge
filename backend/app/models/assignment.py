from sqlalchemy import Column, String, Boolean, DateTime, Date, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Assignment(Base):
    __tablename__ = "assignments"

    assignment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.teacher_id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    description = Column(String, nullable=True)
    class_name = Column(String, nullable=False, index=True)
    section = Column(String, nullable=True)
    assigned_date = Column(Date, default=func.current_date(), nullable=False)
    due_date = Column(Date, nullable=False)
    total_marks = Column(Numeric(10, 2), default=100.0, nullable=False)
    attachment_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
