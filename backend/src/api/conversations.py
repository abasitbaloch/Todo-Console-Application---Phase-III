"""Conversations API endpoints for managing chat history."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel
from uuid import UUID
from typing import List
from datetime import datetime

from ..core.database import get_session
from ..auth.dependencies import get_user_from_jwt
from ..models.user import User
from ..models.conversation import Conversation
from ..models.message import Message, MessageRole

# FIX: REMOVED prefix="/conversations" so it doesn't double up with main.py
router = APIRouter(tags=["conversations"])


class ConversationSummary(BaseModel):
    """Summary of a conversation for list view."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    message_count: int


class MessageResponse(BaseModel):
    """Message response model."""
    id: UUID
    role: MessageRole
    content: str
    created_at: datetime


class ConversationDetail(BaseModel):
    """Detailed conversation with messages."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse]


@router.get("/", response_model=List[ConversationSummary])
async def list_conversations(
    current_user: User = Depends(get_user_from_jwt),
    db: AsyncSession = Depends(get_session),
    limit: int = 20,
    offset: int = 0
):
    """List all conversations for the authenticated user."""
    from ..services.conversation_service import ConversationService
    from ..services.message_service import MessageService

    # Get conversations for user
    conversations = await ConversationService.list_user_conversations(
        db, current_user.id, limit, offset
    )

    # Build summaries with message counts
    summaries = []
    for conv in conversations:
        message_count = await MessageService.get_message_count(db, conv.id)
        summaries.append(ConversationSummary(
            id=conv.id,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=message_count
        ))

    return summaries


@router.get("/{conversation_id}/", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_user_from_jwt),
    db: AsyncSession = Depends(get_session),
):
    """Get a specific conversation with all messages."""
    from ..services.conversation_service import ConversationService
    from ..services.message_service import MessageService

    # Get conversation (with user isolation check)
    conversation = await ConversationService.get_conversation(
        db, conversation_id, current_user.id
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get all messages for conversation
    messages = await MessageService.get_messages_by_conversation(
        db, conversation_id, limit=1000
    )

    # Build response
    return ConversationDetail(
        id=conversation.id,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at
            )
            for msg in messages
        ]
    )