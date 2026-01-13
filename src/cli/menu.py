"""CLI menu framework for the Todo application.

This module handles menu display and user input processing, following the
separation of concerns principle by keeping I/O operations separate from
domain logic.
"""

from typing import Callable, Dict, Optional


class Menu:
    """Manages the command-line interface menu and user interactions."""

    def __init__(self):
        """Initialize the menu with available options."""
        self._options: Dict[str, tuple[str, Callable]] = {}
        self._running: bool = False

    def add_option(self, key: str, description: str, handler: Callable) -> None:
        """Register a menu option with its handler function.

        Args:
            key: The menu option key (e.g., "1", "2")
            description: Human-readable description of the option
            handler: Function to call when this option is selected
        """
        self._options[key] = (description, handler)

    def display(self) -> None:
        """Display the menu options to the user."""
        print("\n" + "=" * 35)
        print("   Todo Console Application")
        print("=" * 35)

        for key in sorted(self._options.keys()):
            description, _ = self._options[key]
            print(f"{key}. {description}")

        print()

    def get_user_choice(self) -> Optional[str]:
        """Prompt user for menu selection and validate input.

        Returns:
            The user's menu choice as a string, or None if input is invalid
        """
        try:
            choice = input("Select an option: ").strip()
            return choice if choice else None
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            return None

    def handle_choice(self, choice: str) -> bool:
        """Execute the handler for the selected menu option.

        Args:
            choice: The user's menu selection

        Returns:
            True to continue running, False to exit
        """
        if choice in self._options:
            _, handler = self._options[choice]
            try:
                result = handler()
                # Handler can return False to signal exit
                return result if result is not None else True
            except Exception as e:
                print(f"\nError: {e}")
                return True
        else:
            print(f"\nInvalid option '{choice}'. Please select a valid menu option.")
            return True

    def run(self) -> None:
        """Main menu loop - display menu and process user selections."""
        self._running = True

        while self._running:
            self.display()
            choice = self.get_user_choice()

            if choice is None:
                break

            should_continue = self.handle_choice(choice)
            if not should_continue:
                self._running = False

    def stop(self) -> None:
        """Signal the menu to stop running."""
        self._running = False


def get_input(prompt: str, allow_empty: bool = False) -> Optional[str]:
    """Get user input with optional validation.

    Args:
        prompt: The prompt message to display
        allow_empty: Whether to allow empty input

    Returns:
        User input as string, or None if empty and not allowed
    """
    try:
        value = input(prompt).strip()
        if not value and not allow_empty:
            return None
        return value if value else None
    except (EOFError, KeyboardInterrupt):
        print("\nOperation cancelled.")
        return None


def get_int_input(prompt: str) -> Optional[int]:
    """Get integer input from user with validation.

    Args:
        prompt: The prompt message to display

    Returns:
        The integer value entered by user, or None if invalid
    """
    try:
        value = input(prompt).strip()
        return int(value)
    except ValueError:
        print("Error: Please enter a valid number.")
        return None
    except (EOFError, KeyboardInterrupt):
        print("\nOperation cancelled.")
        return None
