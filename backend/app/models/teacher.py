from sqlalchemy import Column, String, Boolean, DateTime, Date, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Teacher(Base):
    __tablename__ = "teachers"

    teacher_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    employee_id = Column(String, unique=True, nullable=True)
    qualification = Column(String, nullable=True)
    specialization = Column(String, nullable=True)
    subjects = Column(ARRAY(String), default=list, nullable=False)
    classes = Column(ARRAY(String), default=list, nullable=False)
    joining_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
