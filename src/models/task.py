"""Task domain model for the Todo application.

This module defines the Task entity representing a todo item.
Following the principle of separation of concerns, this is pure domain logic
with no I/O dependencies.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    """Represents a todo item with unique ID, title, description, and completion status.

    Attributes:
        id: Unique numeric identifier (integer, auto-generated starting from 1)
        title: Required, non-empty description of the task
        description: Optional, detailed information about the task
        completed: Status flag indicating complete (True) or incomplete (False)
    """

    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False

    def __post_init__(self):
        """Validate task data after initialization."""
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty or whitespace-only")

    def toggle_completion(self) -> None:
        """Toggle the task's completion status between complete and incomplete."""
        self.completed = not self.completed

    def update(self, title: Optional[str] = None, description: Optional[str] = None) -> None:
        """Update task title and/or description.

        Args:
            title: New title for the task (None to keep current)
            description: New description for the task (None to keep current)

        Raises:
            ValueError: If provided title is empty or whitespace-only
        """
        if title is not None:
            if not title.strip():
                raise ValueError("Task title cannot be empty or whitespace-only")
            self.title = title

        if description is not None:
            self.description = description
