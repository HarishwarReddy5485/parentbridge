from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from decimal import Decimal


class SubjectGradeSummary(BaseModel):
    subject: str
    exam_type: str
    marks_obtained: Decimal
    total_marks: Decimal
    percentage: float
    grade: Optional[str] = None


class StudentProgressResponse(BaseModel):
    student_id: UUID
    student_name: str
    class_name: str
    section: Optional[str] = None
    total_marks_obtained: Decimal
    total_max_marks: Decimal
    overall_percentage: float
    overall_grade: str
    attendance_rate: float
    grades: List[SubjectGradeSummary] = []
