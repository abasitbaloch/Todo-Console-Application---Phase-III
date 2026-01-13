"""Task repository for in-memory storage.

This module provides data access operations for Task entities using an in-memory
dictionary as storage. Follows the Repository pattern to separate data access
from business logic.
"""

from typing import Dict, List, Optional
from ..models.task import Task


class TaskRepository:
    """Manages Task entities in memory using dictionary-based storage.

    Provides CRUD operations and task ID generation. All data is stored in memory
    and will be lost when the application terminates.
    """

    def __init__(self):
        """Initialize empty task storage and ID counter."""
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def add_task(self, title: str, description: Optional[str] = None) -> Task:
        """Create and store a new task with auto-generated ID.

        Args:
            title: Required task title
            description: Optional task description

        Returns:
            The newly created Task instance

        Raises:
            ValueError: If title is empty or whitespace-only
        """
        task = Task(
            id=self._next_id,
            title=title,
            description=description,
            completed=False
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks in the repository.

        Returns:
            List of all Task instances, ordered by ID
        """
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Retrieve a specific task by its ID.

        Args:
            task_id: The unique identifier of the task

        Returns:
            The Task instance if found, None otherwise
        """
        return self._tasks.get(task_id)

    def update_task(self, task_id: int, title: Optional[str] = None,
                   description: Optional[str] = None) -> bool:
        """Update an existing task's title and/or description.

        Args:
            task_id: The unique identifier of the task to update
            title: New title (None to keep current)
            description: New description (None to keep current)

        Returns:
            True if task was found and updated, False if task not found

        Raises:
            ValueError: If provided title is empty or whitespace-only
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            return False

        task.update(title=title, description=description)
        return True

    def delete_task(self, task_id: int) -> bool:
        """Remove a task from the repository.

        Args:
            task_id: The unique identifier of the task to delete

        Returns:
            True if task was found and deleted, False if task not found
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def toggle_complete(self, task_id: int) -> bool:
        """Toggle a task's completion status.

        Args:
            task_id: The unique identifier of the task

        Returns:
            True if task was found and toggled, False if task not found
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            return False

        task.toggle_completion()
        return True

    def task_exists(self, task_id: int) -> bool:
        """Check if a task with the given ID exists.

        Args:
            task_id: The unique identifier to check

        Returns:
            True if task exists, False otherwise
        """
        return task_id in self._tasks
