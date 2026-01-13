"""MCP tools for task management operations."""

from sqlmodel import Session, select
from uuid import UUID
from typing import Dict, Any, List, Optional
from ..models.task import Task
from difflib import SequenceMatcher


async def add_task(
    db: Session,
    user_id: UUID,
    title: str
) -> Dict[str, Any]:
    """MCP tool: Create a new task.

    Args:
        db: Database session
        user_id: UUID of the user creating the task
        title: Task title

    Returns:
        Dictionary with success status and task details
    """
    try:
        task = Task(
            user_id=user_id,
            title=title,
            is_completed=False
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)

        return {
            "success": True,
            "task_id": str(task.id),
            "title": task.title,
            "is_completed": task.is_completed
        }
    except Exception as e:
        await db.rollback()
        return {
            "success": False,
            "error": f"Failed to create task: {str(e)}"
        }


async def list_tasks(
    db: Session,
    user_id: UUID,
    filter_completed: Optional[bool] = None
) -> Dict[str, Any]:
    """MCP tool: List all tasks for a user.

    Args:
        db: Database session
        user_id: UUID of the user
        filter_completed: Optional filter for completion status

    Returns:
        Dictionary with success status and list of tasks
    """
    try:
        statement = select(Task).where(Task.user_id == user_id)

        if filter_completed is not None:
            statement = statement.where(Task.is_completed == filter_completed)

        statement = statement.order_by(Task.created_at.desc())

        result = await db.execute(statement)
        tasks = list(result.scalars().all())

        return {
            "success": True,
            "tasks": [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "is_completed": task.is_completed,
                    "created_at": task.created_at.isoformat()
                }
                for task in tasks
            ],
            "count": len(tasks)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list tasks: {str(e)}"
        }


def fuzzy_match_task(task_title: str, search_string: str) -> float:
    """Calculate fuzzy match score between task title and search string.

    Args:
        task_title: The task title to match against
        search_string: The search string from user input

    Returns:
        Match score between 0.0 and 1.0
    """
    return SequenceMatcher(None, task_title.lower(), search_string.lower()).ratio()


async def find_task_by_fuzzy_match(
    db: Session,
    user_id: UUID,
    task_identifier: str
) -> Optional[Task]:
    """Find a task using fuzzy matching on title.

    Args:
        db: Database session
        user_id: UUID of the user
        task_identifier: Partial or full task title

    Returns:
        Best matching Task or None if no good match found
    """
    statement = select(Task).where(Task.user_id == user_id)
    result = await db.execute(statement)
    tasks = list(result.scalars().all())

    if not tasks:
        return None

    # Find best match
    best_match = None
    best_score = 0.0

    for task in tasks:
        score = fuzzy_match_task(task.title, task_identifier)
        if score > best_score:
            best_score = score
            best_match = task

    # Only return if match is reasonably good (>60% similarity)
    if best_score > 0.6:
        return best_match

    return None


async def complete_task(
    db: Session,
    user_id: UUID,
    task_identifier: str
) -> Dict[str, Any]:
    """MCP tool: Mark a task as completed.

    Args:
        db: Database session
        user_id: UUID of the user
        task_identifier: Task title or partial title for fuzzy matching

    Returns:
        Dictionary with success status and task details
    """
    try:
        task = await find_task_by_fuzzy_match(db, user_id, task_identifier)

        if not task:
            return {
                "success": False,
                "error": f"Could not find task matching '{task_identifier}'. Try viewing your task list first."
            }

        task.is_completed = True
        db.add(task)
        await db.commit()
        await db.refresh(task)

        return {
            "success": True,
            "task_id": str(task.id),
            "title": task.title,
            "is_completed": task.is_completed
        }
    except Exception as e:
        await db.rollback()
        return {
            "success": False,
            "error": f"Failed to complete task: {str(e)}"
        }


async def update_task(
    db: Session,
    user_id: UUID,
    task_identifier: str,
    new_title: str
) -> Dict[str, Any]:
    """MCP tool: Update a task's title.

    Args:
        db: Database session
        user_id: UUID of the user
        task_identifier: Task title or partial title for fuzzy matching
        new_title: New title for the task

    Returns:
        Dictionary with success status and task details
    """
    try:
        task = await find_task_by_fuzzy_match(db, user_id, task_identifier)

        if not task:
            return {
                "success": False,
                "error": f"Could not find task matching '{task_identifier}'. Try viewing your task list first."
            }

        old_title = task.title
        task.title = new_title
        db.add(task)
        await db.commit()
        await db.refresh(task)

        return {
            "success": True,
            "task_id": str(task.id),
            "old_title": old_title,
            "new_title": task.title
        }
    except Exception as e:
        await db.rollback()
        return {
            "success": False,
            "error": f"Failed to update task: {str(e)}"
        }


async def delete_task(
    db: Session,
    user_id: UUID,
    task_identifier: str
) -> Dict[str, Any]:
    """MCP tool: Delete a task permanently.

    Args:
        db: Database session
        user_id: UUID of the user
        task_identifier: Task title or partial title for fuzzy matching

    Returns:
        Dictionary with success status and deleted task details
    """
    try:
        task = await find_task_by_fuzzy_match(db, user_id, task_identifier)

        if not task:
            return {
                "success": False,
                "error": f"Could not find task matching '{task_identifier}'. Try viewing your task list first."
            }

        task_title = task.title
        task_id = str(task.id)

        await db.delete(task)
        await db.commit()

        return {
            "success": True,
            "task_id": task_id,
            "title": task_title,
            "message": f"Task '{task_title}' has been permanently deleted."
        }
    except Exception as e:
        await db.rollback()
        return {
            "success": False,
            "error": f"Failed to delete task: {str(e)}"
        }
