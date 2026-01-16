"""MCP tools for task management operations - Optimized for Phase III."""

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Dict, Any, List, Optional
from ..models.task import Task
from difflib import SequenceMatcher
from datetime import datetime


async def add_task(
    db: AsyncSession,
    user_id: UUID,
    title: str
) -> Dict[str, Any]:
    """MCP tool: Create a new task for the AI."""
    try:
        task = Task(
            user_id=user_id,
            title=title,
            is_completed=False,
            # FIX: Ensure AI-created tasks use Zulu/UTC time
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)

        return {
            "success": True,
            "task_id": str(task.id),
            "title": task.title,
            "is_completed": task.is_completed,
            "created_at": task.created_at.isoformat() + "Z"
        }
    except Exception as e:
        await db.rollback()
        return {
            "success": False,
            "error": f"Failed to create task: {str(e)}"
        }


async def list_tasks(
    db: AsyncSession,
    user_id: UUID,
    filter_completed: Optional[bool] = None
) -> Dict[str, Any]:
    """MCP tool: List all tasks for a user."""
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
                    "created_at": task.created_at.isoformat() + "Z"
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
    """Calculate fuzzy match score."""
    return SequenceMatcher(None, task_title.lower(), search_string.lower()).ratio()


async def find_task_by_fuzzy_match(
    db: AsyncSession,
    user_id: UUID,
    task_identifier: str
) -> Optional[Task]:
    """Find a task using fuzzy matching."""
    statement = select(Task).where(Task.user_id == user_id)
    result = await db.execute(statement)
    tasks = list(result.scalars().all())

    if not tasks:
        return None

    best_match = None
    best_score = 0.0

    for task in tasks:
        score = fuzzy_match_task(task.title, task_identifier)
        if score > best_score:
            best_score = score
            best_match = task

    return best_match if best_score > 0.6 else None


async def complete_task(
    db: AsyncSession,
    user_id: UUID,
    task_identifier: str
) -> Dict[str, Any]:
    """MCP tool: Mark a task as completed."""
    try:
        task = await find_task_by_fuzzy_match(db, user_id, task_identifier)

        if not task:
            return {"success": False, "error": f"Task '{task_identifier}' not found."}

        task.is_completed = True
        task.updated_at = datetime.utcnow()
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
        return {"success": False, "error": str(e)}


async def update_task(
    db: AsyncSession,
    user_id: UUID,
    task_identifier: str,
    new_title: str
) -> Dict[str, Any]:
    """MCP tool: Update title."""
    try:
        task = await find_task_by_fuzzy_match(db, user_id, task_identifier)

        if not task:
            return {"success": False, "error": "Task not found."}

        old_title = task.title
        task.title = new_title
        task.updated_at = datetime.utcnow()
        db.add(task)
        await db.commit()
        await db.refresh(task)

        return {"success": True, "old_title": old_title, "new_title": task.title}
    except Exception as e:
        await db.rollback()
        return {"success": False, "error": str(e)}


async def delete_task(
    db: AsyncSession,
    user_id: UUID,
    task_identifier: str
) -> Dict[str, Any]:
    """MCP tool: Delete a task."""
    try:
        task = await find_task_by_fuzzy_match(db, user_id, task_identifier)

        if not task:
            return {"success": False, "error": "Task not found."}

        task_title = task.title
        await db.delete(task)
        await db.commit()

        return {"success": True, "title": task_title}
    except Exception as e:
        await db.rollback()
        return {"success": False, "error": str(e)}
    
    