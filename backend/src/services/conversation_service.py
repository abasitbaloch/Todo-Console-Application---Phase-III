"""Conversation service for managing chat sessions."""

from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from ..models.conversation import Conversation


class ConversationService:
    """Service for conversation operations.

    Handles creation, retrieval, and listing of conversations.
    All operations enforce user isolation by filtering on user_id.
    """

    @staticmethod
    async def create_conversation(db: Session, user_id: UUID) -> Conversation:
        """Create a new conversation for a user.

        Args:
            db: Database session
            user_id: UUID of the user creating the conversation

        Returns:
            Created Conversation object
        """
        conversation = Conversation(user_id=user_id)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def get_conversation(
        db: Session,
        conversation_id: UUID,
        user_id: UUID
    ) -> Optional[Conversation]:
        """Get a conversation by ID, ensuring it belongs to the user.

        Args:
            db: Database session
            conversation_id: UUID of the conversation
            user_id: UUID of the user (for security check)

        Returns:
            Conversation object if found and belongs to user, None otherwise
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id  # Security: user isolation
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_user_conversations(
        db: Session,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        """List all conversations for a user, ordered by most recent.

        Args:
            db: Database session
            user_id: UUID of the user
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip (for pagination)

        Returns:
            List of Conversation objects
        """
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    async def update_conversation_timestamp(
        db: Session,
        conversation_id: UUID
    ) -> None:
        """Update the updated_at timestamp for a conversation.

        Called when new messages are added to maintain accurate sorting.

        Args:
            db: Database session
            conversation_id: UUID of the conversation to update
        """
        statement = select(Conversation).where(Conversation.id == conversation_id)
        result = await db.execute(statement)
        conversation = result.scalar_one_or_none()

        if conversation:
            conversation.updated_at = datetime.utcnow()
            db.add(conversation)
            await db.commit()
