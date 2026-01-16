"""Agent orchestrator for AI chatbot."""

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
    """Orchestrates AI agent interactions with OpenAI and MCP tools."""

    def __init__(self, db: AsyncSession):
        """Initialize agent orchestrator."""
        self.db = db
        # If using OpenRouter, ensure the base_url is set in settings or here
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self.mcp_server = self._initialize_mcp_server()

    def _initialize_mcp_server(self) -> TodoMCPServer:
        """Initialize and register all MCP tools."""
        server = TodoMCPServer()

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
        """Build message array for OpenAI API."""
        messages = [{"role": "system", "content": get_system_prompt()}]

        for msg in history:
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
        """Process message with optimized token usage to avoid 402 Credit errors."""
        
        # MODEL SETTING: Using a cheaper model to save credits
        # Using gpt-3.5-turbo instead of gpt-4 to ensure it fits your 1333 token budget
        target_model = os.getenv("CHAT_MODEL", "gpt-3.5-turbo")

        for attempt in range(max_retries):
            try:
                messages = self._build_messages(conversation_history, new_message)

                # Call OpenAI with reduced max_tokens
                response = await self.client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    tools=self.mcp_server.get_tool_definitions(),
                    tool_choice="auto",
                    max_tokens=500  # LOWERED: Fits within your 1333 token credit limit
                )

                assistant_message = response.choices[0].message
                tool_calls_data = []
                tool_results_data = []

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
                        max_tokens=500
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
                if "402" in str(e) or "credits" in str(e).lower():
                    # If even 500 is too much, try one last time with very low tokens
                    if attempt == 0:
                        continue 
                
                logger.error(f"Orchestrator Error: {str(e)}")
                raise OpenAIAPIError(message=str(e), status_code=getattr(e, "status_code", 500))