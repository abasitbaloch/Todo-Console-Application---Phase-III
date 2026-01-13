"""Conversation model for AI chat sessions."""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .user import User
    from .message import Message


class Conversation(SQLModel, table=True):
    """Conversation model.

    Represents a chat session between a user and the AI agent.
    Each conversation contains multiple messages and maintains context across turns.
    All conversations are isolated by user_id for security.
    """
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    # user: "User" = Relationship(back_populates="conversations")
    # messages: List["Message"] = Relationship(
    #     back_populates="conversation",
    #     sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    # )
