"""CLI handlers for task operations.

This module provides user-facing handlers for all task management operations,
separating I/O concerns from domain logic.
"""

from typing import Optional
from ..repositories.task_repository import TaskRepository
from .menu import get_input, get_int_input


def handle_add_task(repository: TaskRepository) -> None:
    """Handle the Add Task operation with user input.

    Args:
        repository: TaskRepository instance for data operations
    """
    print("\n--- Add New Task ---")

    # Get title (required)
    title = get_input("Enter task title: ", allow_empty=False)
    if title is None:
        print("Error: Title cannot be empty.")
        return

    # Get description (optional)
    description = get_input("Enter task description (optional, press Enter to skip): ", allow_empty=True)

    # Add task to repository
    try:
        task = repository.add_task(title=title, description=description)
        print(f"\n✓ Task added successfully (ID: {task.id})")
    except ValueError as e:
        print(f"\nError: {e}")


def handle_view_tasks(repository: TaskRepository) -> None:
    """Handle the View Tasks operation and display all tasks.

    Args:
        repository: TaskRepository instance for data operations
    """
    print("\n" + "=" * 50)
    print("            Your Tasks")
    print("=" * 50)

    tasks = repository.get_all_tasks()

    if not tasks:
        print("\nNo tasks found. Add your first task to get started!")
        print()
        return

    for task in tasks:
        status = "✓ Complete" if task.completed else "○ Incomplete"
        print(f"\n[{task.id}] {task.title}")

        if task.description:
            print(f"    Description: {task.description}")

        print(f"    Status: {status}")

    print("\n" + "=" * 50)
    print()


def handle_update_task(repository: TaskRepository) -> None:
    """Handle the Update Task operation with user input.

    Args:
        repository: TaskRepository instance for data operations
    """
    print("\n--- Update Task ---")

    # Get task ID
    task_id = get_int_input("Enter task ID: ")
    if task_id is None:
        return

    # Check if task exists
    task = repository.get_task_by_id(task_id)
    if task is None:
        print(f"\nError: Task not found (ID: {task_id})")
        return

    # Show current values
    print(f"\nCurrent title: {task.title}")
    print(f"Current description: {task.description or '(none)'}")

    # Get new title
    print("\nEnter new title (press Enter to keep current):")
    new_title = get_input("New title: ", allow_empty=True)

    # Get new description
    print("Enter new description (press Enter to keep current):")
    new_description = get_input("New description: ", allow_empty=True)

    # If both are None, nothing to update
    if new_title is None and new_description is None:
        print("\nNo changes made.")
        return

    # Update task
    try:
        success = repository.update_task(
            task_id=task_id,
            title=new_title,
            description=new_description
        )

        if success:
            print(f"\n✓ Task {task_id} updated successfully")
        else:
            print(f"\nError: Task not found (ID: {task_id})")
    except ValueError as e:
        print(f"\nError: {e}")


def handle_delete_task(repository: TaskRepository) -> None:
    """Handle the Delete Task operation with user input.

    Args:
        repository: TaskRepository instance for data operations
    """
    print("\n--- Delete Task ---")

    # Get task ID
    task_id = get_int_input("Enter task ID to delete: ")
    if task_id is None:
        return

    # Delete task
    success = repository.delete_task(task_id)

    if success:
        print(f"\n✓ Task {task_id} deleted successfully")
    else:
        print(f"\nError: Task not found (ID: {task_id})")


def handle_toggle_complete(repository: TaskRepository) -> None:
    """Handle the Mark Complete/Incomplete operation with user input.

    Args:
        repository: TaskRepository instance for data operations
    """
    print("\n--- Mark Complete/Incomplete ---")

    # Get task ID
    task_id = get_int_input("Enter task ID: ")
    if task_id is None:
        return

    # Get current status before toggling
    task = repository.get_task_by_id(task_id)
    if task is None:
        print(f"\nError: Task not found (ID: {task_id})")
        return

    # Toggle completion
    success = repository.toggle_complete(task_id)

    if success:
        # Get new status
        task = repository.get_task_by_id(task_id)
        new_status = "Complete" if task.completed else "Incomplete"
        print(f"\n✓ Task {task_id} marked as {new_status}")
    else:
        print(f"\nError: Task not found (ID: {task_id})")
