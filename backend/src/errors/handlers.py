"""Error handlers for chatbot operations."""

from typing import Optional


class ChatbotError(Exception):
    """Base exception for chatbot-related errors.

    All chatbot errors should inherit from this class.
    Provides user-friendly error messages without exposing technical details.
    """

    def __init__(self, message: str, user_message: Optional[str] = None):
        """Initialize chatbot error.

        Args:
            message: Technical error message (for logging)
            user_message: User-friendly message (shown to user)
        """
        super().__init__(message)
        self.message = message
        self.user_message = user_message or "Something went wrong. Please try again."


class MCPToolError(ChatbotError):
    """Exception raised when MCP tool execution fails.

    Used when a tool (add_task, list_tasks, etc.) encounters an error.
    """

    def __init__(self, tool_name: str, message: str, user_message: Optional[str] = None):
        """Initialize MCP tool error.

        Args:
            tool_name: Name of the tool that failed
            message: Technical error message
            user_message: User-friendly message
        """
        self.tool_name = tool_name
        default_user_message = f"I had trouble with that operation. Could you try again?"
        super().__init__(
            message=f"MCP tool '{tool_name}' failed: {message}",
            user_message=user_message or default_user_message
        )


class OpenAIAPIError(ChatbotError):
    """Exception raised when OpenAI API calls fail.

    Used when the AI agent encounters errors communicating with OpenAI.
    """

    def __init__(self, message: str, status_code: Optional[int] = None):
        """Initialize OpenAI API error.

        Args:
            message: Technical error message
            status_code: HTTP status code from OpenAI API
        """
        self.status_code = status_code
        user_message = "I'm having trouble thinking right now. Please try again in a moment."
        super().__init__(
            message=f"OpenAI API error (status {status_code}): {message}",
            user_message=user_message
        )


class ConversationNotFoundError(ChatbotError):
    """Exception raised when a conversation cannot be found.

    Used when user tries to access a conversation that doesn't exist
    or doesn't belong to them.
    """

    def __init__(self, conversation_id: str):
        """Initialize conversation not found error.

        Args:
            conversation_id: UUID of the conversation that wasn't found
        """
        self.conversation_id = conversation_id
        super().__init__(
            message=f"Conversation {conversation_id} not found",
            user_message="I couldn't find that conversation. Please start a new one."
        )


class InvalidMessageError(ChatbotError):
    """Exception raised when message validation fails.

    Used when user input doesn't meet validation requirements.
    """

    def __init__(self, message: str):
        """Initialize invalid message error.

        Args:
            message: Description of validation failure
        """
        super().__init__(
            message=f"Invalid message: {message}",
            user_message="Your message couldn't be processed. Please try rephrasing it."
        )


def handle_chatbot_error(error: Exception) -> dict:
    """Convert any exception to a user-friendly error response.

    Args:
        error: The exception that occurred

    Returns:
        Dictionary with error details for API response
    """
    if isinstance(error, ChatbotError):
        return {
            "error": True,
            "message": error.user_message,
            "type": error.__class__.__name__
        }

    # Unknown error - don't expose details
    return {
        "error": True,
        "message": "An unexpected error occurred. Please try again.",
        "type": "UnknownError"
    }
