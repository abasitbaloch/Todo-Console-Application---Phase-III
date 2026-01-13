"""Main application entry point for the Todo Console Application.

This module initializes the application, sets up the menu, and starts the
main event loop.
"""

from .repositories.task_repository import TaskRepository
from .cli.menu import Menu
from .cli import task_handlers


def create_exit_handler(menu: Menu):
    """Create an exit handler that displays data loss warning.

    Args:
        menu: The Menu instance to stop

    Returns:
        Handler function for exit option
    """
    def handle_exit():
        print("\n⚠️  Warning: All data will be lost when you exit (no persistence).")
        confirm = input("Are you sure you want to exit? (yes/no): ").strip().lower()

        if confirm in ['yes', 'y']:
            print("\nGoodbye! Thank you for using Todo Console Application.")
            menu.stop()
            return False
        else:
            print("\nExit cancelled. Returning to menu...")
            return True

    return handle_exit


def main():
    """Initialize and run the Todo Console Application."""
    # Create repository for in-memory storage
    repository = TaskRepository()

    # Create menu
    menu = Menu()

    # Register menu options (placeholders for now, will be implemented in Phase 3)
    menu.add_option("1", "Add Task", lambda: task_handlers.handle_add_task(repository))
    menu.add_option("2", "View Tasks", lambda: task_handlers.handle_view_tasks(repository))
    menu.add_option("3", "Update Task", lambda: task_handlers.handle_update_task(repository))
    menu.add_option("4", "Delete Task", lambda: task_handlers.handle_delete_task(repository))
    menu.add_option("5", "Mark Complete/Incomplete", lambda: task_handlers.handle_toggle_complete(repository))
    menu.add_option("6", "Exit", create_exit_handler(menu))

    # Start the application
    print("\n" + "=" * 50)
    print("  Welcome to Todo Console Application - Phase I")
    print("  Demonstrating Spec-Driven Development with AI")
    print("=" * 50)

    try:
        menu.run()
    except KeyboardInterrupt:
        print("\n\nApplication terminated by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        print("Application will now exit.")


if __name__ == "__main__":
    main()
