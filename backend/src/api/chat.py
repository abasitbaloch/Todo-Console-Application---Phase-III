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

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])

class ChatRequest(BaseModel):
    conversation_id: Optional[UUID] = Field(None)
    message: str = Field(..., min_length=1)

class ChatResponse(BaseModel):
    conversation_id: UUID
    message: str
    tool_calls: Optional[List[Dict[str, Any]]] = None

@router.post("", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_user_from_jwt),
    db: AsyncSession = Depends(get_session),
):
    start_time = time.time()
    try:
        if not request.message.strip():
            raise InvalidMessageError("Message cannot be empty")

        conversation = None
        if request.conversation_id:
            conversation = await ConversationService.get_conversation(db, request.conversation_id, current_user.id)
            if not conversation: raise ConversationNotFoundError(str(request.conversation_id))
        else:
            conversation = await ConversationService.create_conversation(db, current_user.id)

        history = await MessageService.get_messages_by_conversation(db, conversation.id, limit=50)
        
        await MessageService.save_message(db=db, conversation_id=conversation.id, role=MessageRole.USER, content=request.message)

        orchestrator = AgentOrchestrator(db)
        agent_response = await orchestrator.process_message(user_id=current_user.id, conversation_history=history, new_message=request.message)

        await MessageService.save_message(db=db, conversation_id=conversation.id, role=MessageRole.ASSISTANT, content=agent_response["content"], tool_calls=agent_response.get("tool_calls"))
        
        await ConversationService.update_conversation_timestamp(db, conversation.id)

        return ChatResponse(conversation_id=conversation.id, message=agent_response["content"], tool_calls=agent_response.get("tool_calls"))

    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")