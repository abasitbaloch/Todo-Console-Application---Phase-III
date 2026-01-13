"""Message service for managing conversation history."""

from sqlmodel import Session, select
from uuid import UUID
from typing import List, Optional
from ..models.message import Message, MessageRole


class MessageService:
    """Service for message operations.

    Handles creation and retrieval of messages within conversations.
    Messages are immutable once created (no updates or deletes).
    """

    @staticmethod
    async def save_message(
        db: Session,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
        tool_calls: Optional[dict] = None,
        tool_results: Optional[dict] = None
    ) -> Message:
        """Save a new message to a conversation.

        Args:
            db: Database session
            conversation_id: UUID of the parent conversation
            role: Message role (user, assistant, or system)
            content: Text content of the message
            tool_calls: Optional JSON of tool invocations
            tool_results: Optional JSON of tool execution results

        Returns:
            Created Message object
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_results=tool_results
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message

    @staticmethod
    async def get_messages_by_conversation(
        db: Session,
        conversation_id: UUID,
        limit: int = 50
    ) -> List[Message]:
        """Get messages for a conversation, ordered chronologically.

        Retrieves the last N messages in reverse chronological order,
        then returns them in chronological order (oldest first).

        Args:
            db: Database session
            conversation_id: UUID of the conversation
            limit: Maximum number of messages to return (default 50)

        Returns:
            List of Message objects in chronological order
        """
        # Fetch last N messages in reverse chronological order
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(statement)
        messages = list(result.scalars().all())

        # Return in chronological order (oldest first)
        return list(reversed(messages))

    @staticmethod
    async def get_message_count(
        db: Session,
        conversation_id: UUID
    ) -> int:
        """Get the total number of messages in a conversation.

        Args:
            db: Database session
            conversation_id: UUID of the conversation

        Returns:
            Count of messages
        """
        statement = select(Message).where(Message.conversation_id == conversation_id)
        result = await db.execute(statement)
        return len(list(result.scalars().all()))
