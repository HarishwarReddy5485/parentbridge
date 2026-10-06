from app.schemas.auth import LoginRequest, AdminRegisterRequest, TokenResponse, RefreshTokenRequest, CurrentUserResponse
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse, AssignTeacherRequest
from app.schemas.teacher import TeacherResponse, ClassTeacherResponse
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate, AssignmentResponse
from app.schemas.grade import GradeCreate, GradeUpdate, GradeResponse
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate, AttendanceResponse
from app.schemas.notice import NoticeCreate, NoticeUpdate, NoticeResponse
from app.schemas.message import MessageCreate, MessageResponse
from app.schemas.progress import StudentProgressResponse, SubjectGradeSummary

__all__ = [
    "LoginRequest",
    "AdminRegisterRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "CurrentUserResponse",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "StudentCreate",
    "StudentUpdate",
    "StudentResponse",
    "AssignTeacherRequest",
    "TeacherResponse",
    "ClassTeacherResponse",
    "AssignmentCreate",
    "AssignmentUpdate",
    "AssignmentResponse",
    "GradeCreate",
    "GradeUpdate",
    "GradeResponse",
    "AttendanceCreate",
    "AttendanceUpdate",
    "AttendanceResponse",
    "NoticeCreate",
    "NoticeUpdate",
    "NoticeResponse",
    "MessageCreate",
    "MessageResponse",
    "StudentProgressResponse",
    "SubjectGradeSummary"
]
