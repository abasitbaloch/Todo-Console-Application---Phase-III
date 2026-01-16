"""Agent orchestrator for AI chatbot - Optimized for Free OpenRouter Models."""

from typing import List, Dict, Any, Optional
from uuid import UUID
import os
import json
import asyncio
from openai import AsyncOpenAI
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models.message import Message, MessageRole
from ..mcp.server import TodoMCPServer
from ..mcp import tools as mcp_tools
from ..agent.prompts import get_system_prompt
from ..errors.handlers import OpenAIAPIError, MCPToolError


class AgentOrchestrator:
    """Orchestrates AI agent interactions with OpenRouter Free Models."""

    def __init__(self, db: AsyncSession):
        """Initialize agent orchestrator."""
        self.db = db
        # OpenRouter requires a specific base_url
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
        self.mcp_server = self._initialize_mcp_server()

    def _initialize_mcp_server(self) -> TodoMCPServer:
        """Initialize and register all MCP tools."""
        server = TodoMCPServer()

        # Tool: Add Task
        server.register_tool(
            name="add_task",
            description="Create a new task. Use this when the user wants to add something.",
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The task title"}
                },
                "required": ["title"]
            },
            function=lambda title, user_id: mcp_tools.add_task(self.db, user_id, title)
        )

        # Tool: List Tasks
        server.register_tool(
            name="list_tasks",
            description="List all tasks for the user.",
            parameters={
                "type": "object",
                "properties": {
                    "filter_completed": {"type": "boolean"}
                },
                "required": []
            },
            function=lambda user_id, filter_completed=None: mcp_tools.list_tasks(self.db, user_id, filter_completed)
        )

        return server

    def _build_messages(self, history: List[Message], new_message: str) -> List[Dict[str, Any]]:
        """Build message array for OpenRouter API."""
        messages = [{"role": "system", "content": get_system_prompt()}]

        # Only take the last 10 messages to save tokens (Free Tier limit)
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
        """Process message with settings optimized for Free models."""
        
        # MODEL: Use a reliable FREE model from OpenRouter
        # You can also use "google/gemini-2.0-flash-exp:free" or "mistralai/mistral-7b-instruct:free"
        target_model = os.getenv("CHAT_MODEL", "google/gemini-2.0-flash-exp:free")

        for attempt in range(max_retries):
            try:
                messages = self._build_messages(conversation_history, new_message)

                # Call OpenRouter with strict token limits
                response = await self.client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    tools=self.mcp_server.get_tool_definitions(),
                    tool_choice="auto",
                    max_tokens=512, # Low token count ensures the "Free" request is accepted
                    extra_headers={
                        "HTTP-Referer": "https://vercel.app", # Required by OpenRouter
                        "X-Title": "Todo AI Assistant"
                    }
                )

                assistant_message = response.choices[0].message
                tool_calls_data = []
                tool_results_data = []

                # Handle Tool Calls
                if assistant_message.tool_calls:
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        args = json.loads(tool_call.function.arguments)
                        args["user_id"] = user_id 

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

                    # Get final response after tools
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

                return {
                    "content": assistant_message.content,
                    "tool_calls": None,
                    "tool_results": None
                }

            except Exception as e:
                # Catch specifically for 402/limit errors and retry once with even smaller context
                if ("402" in str(e) or "limit" in str(e).lower()) and attempt == 0:
                    continue
                
                print(f"Orchestrator Error: {str(e)}")
                raise OpenAIAPIError(message=str(e), status_code=getattr(e, "status_code", 500))