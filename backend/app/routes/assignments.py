from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.user import User, UserRole
from app.models.assignment import Assignment
from app.models.teacher import Teacher
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate, AssignmentResponse
from app.security.deps import get_current_user, require_roles

router = APIRouter(prefix="/assignments", tags=["Assignments"])


@router.post("", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assign_in: AssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.CLASS_TEACHER, UserRole.ADMIN))
):
    """Teachers create a new homework/assignment."""
    # Find teacher_id
    t_res = await db.execute(select(Teacher).where(Teacher.user_id == current_user.user_id))
    teacher = t_res.scalars().first()

    # Fallback to current user if admin
    t_id = teacher.teacher_id if teacher else current_user.user_id

    assignment = Assignment(
        teacher_id=t_id,
        title=assign_in.title,
        subject=assign_in.subject,
        description=assign_in.description,
        class_name=assign_in.class_name,
        section=assign_in.section,
        assigned_date=assign_in.assigned_date or assignment.assigned_date if hasattr(assignment, 'assigned_date') else None,
        due_date=assign_in.due_date,
        total_marks=assign_in.total_marks or 100.0,
        attachment_url=assign_in.attachment_url,
        is_active=True
    )
    if assign_in.assigned_date:
        assignment.assigned_date = assign_in.assigned_date

    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    return assignment


@router.get("", response_model=List[AssignmentResponse])
async def list_assignments(
    class_name: Optional[str] = Query(None),
    section: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List assignments filtered by class, section, or subject."""
    stmt = select(Assignment).where(Assignment.is_active == True)

    if class_name:
        stmt = stmt.where(Assignment.class_name == class_name)
    if section:
        stmt = stmt.where(Assignment.section == section)
    if subject:
        stmt = stmt.where(Assignment.subject.ilike(f"%{subject}%"))

    result = await db.execute(stmt.order_by(Assignment.due_date.asc()))
    return result.scalars().all()


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve details of an assignment."""
    result = await db.execute(select(Assignment).where(Assignment.assignment_id == assignment_id))
    assignment = result.scalars().first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: UUID,
    assign_in: AssignmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.CLASS_TEACHER, UserRole.ADMIN))
):
    """Update an assignment."""
    result = await db.execute(select(Assignment).where(Assignment.assignment_id == assignment_id))
    assignment = result.scalars().first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    for key, value in assign_in.model_dump(exclude_unset=True).items():
        setattr(assignment, key, value)

    await db.commit()
    await db.refresh(assignment)
    return assignment


@router.delete("/{assignment_id}", status_code=status.HTTP_200_OK)
async def delete_assignment(
    assignment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.CLASS_TEACHER, UserRole.ADMIN))
):
    """Deactivate or remove an assignment."""
    result = await db.execute(select(Assignment).where(Assignment.assignment_id == assignment_id))
    assignment = result.scalars().first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    assignment.is_active = False
    await db.commit()
    return {"message": "Assignment successfully removed"}
