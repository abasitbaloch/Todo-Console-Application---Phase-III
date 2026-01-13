"""User model for authentication and ownership."""

from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4


class User(SQLModel, table=True):
    """User account model.

    Represents an authenticated user who can own multiple tasks.
    Passwords are stored as bcrypt hashes, never in plaintext.
    """
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
