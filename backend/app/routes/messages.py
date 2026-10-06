from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageResponse
from app.security.deps import get_current_user

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message_rest(
    msg_in: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a persistent direct message between parent/teacher/student."""
    msg = Message(
        sender_id=current_user.user_id,
        sender_role=current_user.role,
        receiver_id=msg_in.receiver_id,
        receiver_role=msg_in.receiver_role,
        student_id=msg_in.student_id,
        subject=msg_in.subject,
        message=msg_in.message,
        is_read=False
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


@router.get("", response_model=List[MessageResponse])
async def list_user_messages(
    other_user_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve message history for the authenticated user."""
    stmt = select(Message).where(
        or_(
            Message.sender_id == current_user.user_id,
            Message.receiver_id == current_user.user_id
        )
    )

    if other_user_id:
        stmt = stmt.where(
            or_(
                and_(Message.sender_id == current_user.user_id, Message.receiver_id == other_user_id),
                and_(Message.sender_id == other_user_id, Message.receiver_id == current_user.user_id)
            )
        )

    result = await db.execute(stmt.order_by(Message.created_at.asc()))
    return result.scalars().all()


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """View details of a specific message."""
    result = await db.execute(select(Message).where(Message.message_id == message_id))
    msg = result.scalars().first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    # Authorize sender or receiver
    if msg.sender_id != current_user.user_id and msg.receiver_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return msg


@router.put("/{message_id}/read", response_model=MessageResponse)
async def mark_message_as_read(
    message_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a received message as read."""
    result = await db.execute(select(Message).where(Message.message_id == message_id))
    msg = result.scalars().first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    if msg.receiver_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Only recipient can mark message as read")

    msg.is_read = True
    await db.commit()
    await db.refresh(msg)
    return msg
