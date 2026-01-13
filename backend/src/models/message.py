"""Message model for conversation history."""

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Text, JSON, Enum as SQLEnum
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .conversation import Conversation


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(SQLModel, table=True):
    """Message model.

    Represents a single message in a conversation.
    Messages can be from the user, the AI assistant, or system notifications.
    Messages also store tool calls and their results for full conversation replay.
    Messages are immutable once created (no updates).
    """
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: MessageRole = Field(sa_column=Column(SQLEnum(MessageRole)))
    content: str = Field(sa_column=Column(Text))
    tool_calls: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    tool_results: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    # conversation: "Conversation" = Relationship(back_populates="messages")
