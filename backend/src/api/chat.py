"""Chat API endpoints for AI-powered todo chatbot."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List, Dict, Any
import logging
import time

from ..core.database import get_session
from ..auth.dependencies import get_user_from_jwt
from ..models.user import User
from ..models.message import MessageRole
from ..services.conversation_service import ConversationService
from ..services.message_service import MessageService
from ..agent.orchestrator import AgentOrchestrator
from ..errors.handlers import handle_chatbot_error, ConversationNotFoundError, InvalidMessageError


# Configure logging
logger = logging.getLogger(__name__)

# REMOVED prefix="/chat" here because it is handled in main.py
# This prevents the /api/chat/chat 404 error.
router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    conversation_id: Optional[UUID] = Field(None, description="Existing conversation ID or null for new conversation")
    message: str = Field(..., min_length=1, max_length=1000, description="User's message")


class ToolCall(BaseModel):
    """Tool call information."""
    id: str
    type: str
    function: Dict[str, Any]


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    conversation_id: UUID
    message: str
    tool_calls: Optional[List[Dict[str, Any]]] = None


@router.post("", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_user_from_jwt),
    db: AsyncSession = Depends(get_session),
):
    """
    Send a message to the AI chatbot.
    The URL for this will be: [BASE_URL]/api/chat/
    """
    start_time = time.time()

    # Log request
    logger.info(
        f"Chat request - user_id={current_user.id}, "
        f"conversation_id={request.conversation_id}, "
        f"message_length={len(request.message)}"
    )

    try:
        # Validate message
        if not request.message or len(request.message.strip()) == 0:
            raise InvalidMessageError("Message cannot be empty")

        # Step 1: Get or create conversation
        conversation = None
        if request.conversation_id:
            # Fetch existing conversation
            conversation = await ConversationService.get_conversation(
                db, request.conversation_id, current_user.id
            )
            if not conversation:
                raise ConversationNotFoundError(str(request.conversation_id))
        else:
            # Create new conversation
            conversation = await ConversationService.create_conversation(
                db, current_user.id
            )
            logger.info(f"Created new conversation - id={conversation.id}")

        # Step 2: Fetch conversation history
        history = await MessageService.get_messages_by_conversation(
            db, conversation.id, limit=50
        )

        # Step 3: Save user message
        await MessageService.save_message(
            db=db,
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=request.message
        )

        # Step 4: Call agent orchestrator
        orchestrator = AgentOrchestrator(db)
        agent_response = await orchestrator.process_message(
            user_id=current_user.id,
            conversation_history=history,
            new_message=request.message
        )

        # Step 5: Save assistant message
        await MessageService.save_message(
            db=db,
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=agent_response["content"],
            tool_calls=agent_response.get("tool_calls"),
            tool_results=agent_response.get("tool_results")
        )

        # Step 6: Update conversation timestamp
        await ConversationService.update_conversation_timestamp(
            db, conversation.id
        )

        # Log successful response
        response_time = time.time() - start_time
        logger.info(f"Chat success - response_time={response_time:.2f}s")

        # Step 7: Return response
        return ChatResponse(
            conversation_id=conversation.id,
            message=agent_response["content"],
            tool_calls=agent_response.get("tool_calls")
        )

    except (ConversationNotFoundError, InvalidMessageError) as e:
        error_response = handle_chatbot_error(e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if isinstance(e, ConversationNotFoundError) else status.HTTP_400_BAD_REQUEST,
            detail=error_response["message"]
        )
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        error_response = handle_chatbot_error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response["message"]
        )