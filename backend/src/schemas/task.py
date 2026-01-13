"""Task Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class TaskCreate(BaseModel):
    """Schema for task creation request."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)


class TaskUpdate(BaseModel):
    """Schema for task update request."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    is_completed: Optional[bool] = None


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)
