from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from uuid import UUID
from datetime import datetime
from app.websocket.manager import manager
from app.security.jwt import decode_access_token
from app.database import AsyncSessionLocal
from app.models.message import Message
from app.models.user import User, UserRole
from sqlalchemy import select

router = APIRouter(tags=["WebSockets"])


@router.websocket("/ws/chat/{conversation_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    token: str = Query(None)
):
    # 1. Validate JWT Token
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id_str = payload.get("sub")
    role_str = payload.get("role")
    full_name = payload.get("name", "User")

    try:
        sender_uuid = UUID(user_id_str)
        conv_uuid = UUID(conversation_id)
        sender_role = UserRole(role_str)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 2. Connect client to conversation room
    await manager.connect(conversation_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            message_text = data.get("message", "").strip()
            receiver_id_str = data.get("receiver_id")
            receiver_role_str = data.get("receiver_role")
            student_id_str = data.get("student_id")
            subject = data.get("subject", "General")

            if not message_text or not receiver_id_str:
                continue

            receiver_uuid = UUID(receiver_id_str)
            receiver_role = UserRole(receiver_role_str) if receiver_role_str else UserRole.TEACHER
            student_uuid = UUID(student_id_str) if student_id_str else None

            # 3. Persist message in Supabase Database
            async with AsyncSessionLocal() as session:
                new_msg = Message(
                    conversation_id=conv_uuid,
                    sender_id=sender_uuid,
                    sender_role=sender_role,
                    receiver_id=receiver_uuid,
                    receiver_role=receiver_role,
                    student_id=student_uuid,
                    subject=subject,
                    message=message_text,
                    is_read=False
                )
                session.add(new_msg)
                await session.commit()
                await session.refresh(new_msg)

                # 4. Broadcast event payload to room participants
                broadcast_payload = {
                    "message_id": str(new_msg.message_id),
                    "conversation_id": conversation_id,
                    "sender_id": str(sender_uuid),
                    "sender_name": full_name,
                    "sender_role": sender_role.value,
                    "receiver_id": str(receiver_uuid),
                    "receiver_role": receiver_role.value,
                    "student_id": str(student_uuid) if student_uuid else None,
                    "subject": subject,
                    "message": message_text,
                    "is_read": False,
                    "created_at": new_msg.created_at.isoformat() if new_msg.created_at else datetime.utcnow().isoformat()
                }

                await manager.broadcast(conversation_id, broadcast_payload)

    except WebSocketDisconnect:
        manager.disconnect(conversation_id, websocket)
    except Exception:
        manager.disconnect(conversation_id, websocket)
