"""Errors package initialization."""

from .handlers import (
    ChatbotError,
    MCPToolError,
    OpenAIAPIError,
    ConversationNotFoundError,
    InvalidMessageError,
    handle_chatbot_error
)

__all__ = [
    "ChatbotError",
    "MCPToolError",
    "OpenAIAPIError",
    "ConversationNotFoundError",
    "InvalidMessageError",
    "handle_chatbot_error"
]
