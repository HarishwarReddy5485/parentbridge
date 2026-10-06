from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional

from app.database import get_db
from app.models.user import User, UserRole
from app.models.notice import Notice
from app.schemas.notice import NoticeResponse
from app.security.deps import get_current_user

router = APIRouter(prefix="/notices", tags=["Notices"])


@router.get("", response_model=List[NoticeResponse])
async def get_accessible_notices(
    class_name: Optional[str] = Query(None),
    section: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve notices targeted to the user's role or general school population."""
    # Admins see everything
    if current_user.role == UserRole.ADMIN:
        result = await db.execute(select(Notice).order_by(Notice.created_at.desc()))
        return result.scalars().all()

    # Filter notices: targeted to user's role OR global (target_role is NULL)
    stmt = select(Notice).where(
        or_(
            Notice.target_role == current_user.role,
            Notice.target_role == None  # Global notices
        )
    )

    if class_name:
        stmt = stmt.where(or_(Notice.target_class_name == class_name, Notice.target_class_name == None))
    if section:
        stmt = stmt.where(or_(Notice.target_section == section, Notice.target_section == None))

    result = await db.execute(stmt.order_by(Notice.created_at.desc()))
    return result.scalars().all()
