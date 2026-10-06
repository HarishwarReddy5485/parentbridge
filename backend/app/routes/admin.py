from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User, UserRole
from app.models.admin import Admin
from app.models.class_teacher import ClassTeacher
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.notice import Notice
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.student import StudentResponse, AssignTeacherRequest
from app.schemas.notice import NoticeCreate, NoticeUpdate, NoticeResponse
from app.security.password import hash_password
from app.security.deps import require_roles

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_roles(UserRole.ADMIN))]
)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_by_admin(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Admin creates user account and corresponding role profile (Admin, Teacher, Class Teacher, Student, Parent)."""
    # Check if email exists
    existing = await db.execute(select(User).where(User.email == user_in.email))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        phone=user_in.phone,
        role=user_in.role,
        is_active=True
    )
    db.add(new_user)
    await db.flush()

    # Create associated role table
    if user_in.role == UserRole.ADMIN:
        admin_profile = Admin(
            user_id=new_user.user_id,
            full_name=new_user.full_name,
            email=new_user.email,
            phone=new_user.phone,
            employee_id=user_in.employee_id,
            is_super_admin=user_in.is_super_admin or False
        )
        db.add(admin_profile)

    elif user_in.role == UserRole.CLASS_TEACHER:
        ct_profile = ClassTeacher(
            user_id=new_user.user_id,
            full_name=new_user.full_name,
            email=new_user.email,
            phone=new_user.phone,
            employee_id=user_in.employee_id,
            assigned_class=user_in.assigned_class,
            assigned_section=user_in.assigned_section
        )
        db.add(ct_profile)

    elif user_in.role == UserRole.TEACHER:
        teacher_profile = Teacher(
            user_id=new_user.user_id,
            full_name=new_user.full_name,
            email=new_user.email,
            phone=new_user.phone,
            employee_id=user_in.employee_id,
            qualification=user_in.qualification,
            specialization=user_in.specialization,
            subjects=user_in.subjects or [],
            classes=user_in.classes or []
        )
        db.add(teacher_profile)

    elif user_in.role == UserRole.STUDENT:
        student_profile = Student(
            user_id=new_user.user_id,
            full_name=new_user.full_name,
            email=new_user.email,
            phone=new_user.phone,
            class_name=user_in.assigned_class or "10",
            section=user_in.assigned_section or "A"
        )
        db.add(student_profile)

    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.get("/users", response_model=List[UserResponse])
async def list_all_users(db: AsyncSession = Depends(get_db)):
    """List all user accounts."""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve details for a specific user."""
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: UUID, user_in: UserUpdate, db: AsyncSession = Depends(get_db)):
    """Update user account details."""
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_in.full_name is not None:
        user.full_name = user_in.full_name
    if user_in.phone is not None:
        user.phone = user_in.phone
    if user_in.is_active is not None:
        user.is_active = user_in.is_active
    if user_in.password is not None:
        user.password_hash = hash_password(user_in.password)

    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_or_deactivate_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Deactivate or remove a user account."""
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    await db.commit()
    return {"message": "User successfully deactivated"}


@router.put("/students/{student_id}/teacher", response_model=StudentResponse)
async def assign_student_teacher(student_id: UUID, req: AssignTeacherRequest, db: AsyncSession = Depends(get_db)):
    """Assign or update a student's assigned teacher."""
    result = await db.execute(select(Student).where(Student.student_id == student_id))
    student = result.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Verify teacher exists
    t_result = await db.execute(select(Teacher).where(Teacher.teacher_id == req.teacher_id))
    if not t_result.scalars().first():
        raise HTTPException(status_code=404, detail="Teacher not found")

    student.teacher_id = req.teacher_id
    await db.commit()
    await db.refresh(student)
    return student


@router.post("/notices", response_model=NoticeResponse, status_code=status.HTTP_201_CREATED)
async def create_admin_notice(
    notice_in: NoticeCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_roles(UserRole.ADMIN))
):
    """Admin creates and publishes school-wide or targeted notice."""
    notice = Notice(
        created_by=admin_user.user_id,
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


@router.get("/notices", response_model=List[NoticeResponse])
async def list_admin_notices(db: AsyncSession = Depends(get_db)):
    """List all notices created."""
    result = await db.execute(select(Notice).order_by(Notice.created_at.desc()))
    return result.scalars().all()


@router.put("/notices/{notice_id}", response_model=NoticeResponse)
async def update_notice(notice_id: UUID, notice_in: NoticeUpdate, db: AsyncSession = Depends(get_db)):
    """Update an existing notice."""
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
    if notice_in.target_section is not None:
        notice.target_section = notice_in.target_section

    await db.commit()
    await db.refresh(notice)
    return notice


@router.delete("/notices/{notice_id}", status_code=status.HTTP_200_OK)
async def delete_notice(notice_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a notice."""
    result = await db.execute(select(Notice).where(Notice.notice_id == notice_id))
    notice = result.scalars().first()
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")

    await db.delete(notice)
    await db.commit()
    return {"message": "Notice deleted successfully"}
