"""Conversations API endpoints - Final Time Fix."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel
from uuid import UUID
from typing import List, Union
from datetime import datetime

from ..core.database import get_session
from ..auth.dependencies import get_user_from_jwt
from ..models.user import User

router = APIRouter(tags=["conversations"])

class ConversationSummary(BaseModel):
    id: UUID
    created_at: str  # Forced to string for ISO consistency
    updated_at: str
    message_count: int

class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: str

class ConversationDetail(BaseModel):
    id: UUID
    created_at: str
    updated_at: str
    messages: List[MessageResponse]

@router.get("/", response_model=List[ConversationSummary])
async def list_conversations(
    current_user: User = Depends(get_user_from_jwt),
    db: AsyncSession = Depends(get_session),
    limit: int = 20,
    offset: int = 0
):
    from ..services.conversation_service import ConversationService
    from ..services.message_service import MessageService

    conversations = await ConversationService.list_user_conversations(
        db, current_user.id, limit, offset
    )

    summaries = []
    for conv in conversations:
        count = await MessageService.get_message_count(db, conv.id)
        summaries.append({
            "id": conv.id,
            "created_at": conv.created_at.isoformat() + "Z",
            "updated_at": conv.updated_at.isoformat() + "Z",
            "message_count": count
        })
    return summaries

@router.get("/{conversation_id}/", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_user_from_jwt),
    db: AsyncSession = Depends(get_session),
):
    from ..services.conversation_service import ConversationService
    from ..services.message_service import MessageService

    conversation = await ConversationService.get_conversation(db, conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await MessageService.get_messages_by_conversation(db, conversation_id, limit=1000)

    return {
        "id": conversation.id,
        "created_at": conversation.created_at.isoformat() + "Z",
        "updated_at": conversation.updated_at.isoformat() + "Z",
        "messages": [
            {
                "id": msg.id,
                "role": msg.role.value if hasattr(msg.role, 'value') else msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat() + "Z"
            } for msg in messages
        ]
    }