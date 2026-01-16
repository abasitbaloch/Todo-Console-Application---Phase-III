"""Agent orchestrator for AI chatbot - Optimized for Free OpenRouter Models."""

from typing import List, Dict, Any, Optional
from uuid import UUID
import os
import json
import asyncio
import logging
from openai import AsyncOpenAI
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models.message import Message, MessageRole
from ..mcp.server import TodoMCPServer
from ..mcp import tools as mcp_tools
from ..agent.prompts import get_system_prompt
from ..errors.handlers import OpenAIAPIError, MCPToolError

# Configure logging for debugging AI behavior
logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Orchestrates AI agent interactions with OpenRouter Free Models."""

    def __init__(self, db: AsyncSession):
        """Initialize agent orchestrator with database and OpenRouter client."""
        self.db = db
        # Set OpenRouter base URL
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
        self.mcp_server = self._initialize_mcp_server()

    def _initialize_mcp_server(self) -> TodoMCPServer:
        """Initialize and register all MCP tools for the agent to use."""
        server = TodoMCPServer()

        # Tool 1: Add Task
        server.register_tool(
            name="add_task",
            description="Create a new task. Use this when the user wants to add or remember something.",
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The task title"}
                },
                "required": ["title"]
            },
            function=lambda title, user_id: mcp_tools.add_task(self.db, user_id, title)
        )

        # Tool 2: List Tasks
        server.register_tool(
            name="list_tasks",
            description="List all current tasks for the user.",
            parameters={
                "type": "object",
                "properties": {
                    "filter_completed": {"type": "boolean", "description": "Optional filter"}
                },
                "required": []
            },
            function=lambda user_id, filter_completed=None: mcp_tools.list_tasks(self.db, user_id, filter_completed)
        )

        # Tool 3: Delete Task (Newly Added)
        server.register_tool(
            name="delete_task",
            description="Delete a task by searching for its title.",
            parameters={
                "type": "object",
                "properties": {
                    "task_identifier": {"type": "string", "description": "The title of the task to delete"}
                },
                "required": ["task_identifier"]
            },
            function=lambda task_identifier, user_id: mcp_tools.delete_task(self.db, user_id, task_identifier)
        )

        return server

    def _build_messages(self, history: List[Message], new_message: str) -> List[Dict[str, Any]]:
        """Build message array for OpenRouter API, optimized for Free Tier limits."""
        messages = [{"role": "system", "content": get_system_prompt()}]

        # Keep context small (last 10 messages) to avoid token limit errors
        for msg in history[-10:]:
            messages.append({"role": msg.role.value, "content": msg.content})
            if msg.tool_calls:
                messages[-1]["tool_calls"] = msg.tool_calls
            if msg.tool_results:
                for tool_result in msg.tool_results:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_result["tool_call_id"],
                        "content": str(tool_result["content"])
                    })

        messages.append({"role": "user", "content": new_message})
        return messages

    async def process_message(
        self,
        user_id: UUID,
        conversation_history: List[Message],
        new_message: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Process message with optimized logic for Free models and tool handling."""
        
        target_model = os.getenv("CHAT_MODEL", "google/gemini-2.0-flash-exp:free")

        for attempt in range(max_retries):
            try:
                messages = self._build_messages(conversation_history, new_message)

                # API Call 1: Get initial response or tool calls
                response = await self.client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    tools=self.mcp_server.get_tool_definitions(),
                    tool_choice="auto",
                    max_tokens=512, # Low limit for free tier
                    extra_headers={
                        "HTTP-Referer": "https://vercel.app", 
                        "X-Title": "Todo AI Assistant"
                    }
                )

                assistant_message = response.choices[0].message
                tool_calls_data = []
                tool_results_data = []

                if assistant_message.tool_calls:
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        
                        # SAFE JSON PARSING
                        try:
                            args = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            logger.error(f"AI provided invalid JSON for tool: {tool_name}")
                            continue

                        args["user_id"] = user_id 

                        # Execute the tool
                        result = await self.mcp_server.execute_tool(tool_name, args)

                        tool_calls_data.append({
                            "id": tool_call.id,
                            "type": "function",
                            "function": {"name": tool_name, "arguments": tool_call.function.arguments}
                        })
                        tool_results_data.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "content": json.dumps(result)
                        })

                    # If tools were used, call the AI again to get the final text response
                    messages.append(assistant_message)
                    for result in tool_results_data:
                        messages.append(result)

                    final_response = await self.client.chat.completions.create(
                        model=target_model,
                        messages=messages,
                        max_tokens=512
                    )

                    return {
                        "content": final_response.choices[0].message.content,
                        "tool_calls": tool_calls_data,
                        "tool_results": tool_results_data
                    }

                # Direct response if no tools were called
                return {
                    "content": assistant_message.content,
                    "tool_calls": None,
                    "tool_results": None
                }

            except Exception as e:
                # Handle rate limits or temporary free tier blocks
                if ("429" in str(e) or "limit" in str(e).lower()) and attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt) # Backoff
                    continue
                
                logger.error(f"Final Orchestrator Failure: {str(e)}")
                raise OpenAIAPIError(message=str(e), status_code=getattr(e, "status_code", 500))