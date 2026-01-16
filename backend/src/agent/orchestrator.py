"""
Agent Orchestrator - Production Version
Optimized for OpenRouter Free Tier & Secure User Task Management
"""

import os
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
from openai import AsyncOpenAI
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models.message import Message, MessageRole
from ..mcp.server import TodoMCPServer
from ..mcp import tools as mcp_tools
from ..agent.prompts import get_system_prompt
from ..errors.handlers import OpenAIAPIError, MCPToolError

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Orchestrates AI interactions with OpenRouter Fallbacks and MCP tools."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
        self.mcp_server = self._initialize_mcp_server()

    def _initialize_mcp_server(self) -> TodoMCPServer:
        """Register all MCP tools with explicit dependency injection support."""
        server = TodoMCPServer()

        # Tool: Add Task
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
            # Explicitly pass the db and user_id to the tool
            function=lambda title, user_id: mcp_tools.add_task(self.db, user_id, title)
        )

        # Tool: List Tasks
        server.register_tool(
            name="list_tasks",
            description="List all tasks for the current user.",
            parameters={
                "type": "object",
                "properties": {
                    "filter_completed": {"type": "boolean", "description": "Optional: Filter by completion"}
                }
            },
            function=lambda user_id, filter_completed=None: mcp_tools.list_tasks(self.db, user_id, filter_completed)
        )

        # Tool: Delete Task
        server.register_tool(
            name="delete_task",
            description="Delete a task by title using fuzzy matching.",
            parameters={
                "type": "object",
                "properties": {
                    "task_identifier": {"type": "string", "description": "Title or part of the title"}
                },
                "required": ["task_identifier"]
            },
            function=lambda task_identifier, user_id: mcp_tools.delete_task(self.db, user_id, task_identifier)
        )

        return server

    def _build_messages(self, history: List[Message], new_message: str) -> List[Dict[str, Any]]:
        """Build message list with capped history to preserve tokens on Free Tier."""
        messages = [{"role": "system", "content": get_system_prompt()}]
        
        # Only keep last 5 messages for token efficiency
        for msg in history[-5:]:
            messages.append({"role": msg.role.value, "content": msg.content})
            if msg.tool_calls:
                messages[-1]["tool_calls"] = msg.tool_calls
            if msg.tool_results:
                for result in msg.tool_results:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": result["tool_call_id"],
                        "content": str(result["content"])
                    })

        messages.append({"role": "user", "content": new_message})
        return messages

    async def process_message(
        self,
        user_id: UUID,
        conversation_history: List[Message],
        new_message: str,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """Core loop with Multi-Model Fallback for OpenRouter Free Tier."""
        
        # Models to try in order (Resilience against 429 errors)
        models = [
            os.getenv("CHAT_MODEL", "google/gemini-2.0-flash-exp:free"),
            "mistralai/mistral-7b-instruct:free",
            "openrouter/auto"
        ]

        last_error = None
        for model in models:
            try:
                messages = self._build_messages(conversation_history, new_message)

                # API Call
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=self.mcp_server.get_tool_definitions(),
                    tool_choice="auto",
                    max_tokens=500, # Strict limit to fit Free Tier credits
                    extra_headers={
                        "HTTP-Referer": "https://vercel.app",
                        "X-Title": "Todo AI Assistant"
                    }
                )

                assistant_msg = response.choices[0].message
                tool_calls_data = []
                tool_results_data = []

                # Execute Tools if AI requests them
                if assistant_msg.tool_calls:
                    for tool_call in assistant_msg.tool_calls:
                        name = tool_call.function.name
                        
                        try:
                            args = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            continue

                        # INJECT USER CONTEXT: Ensure tool knows WHO is asking
                        args["user_id"] = user_id 

                        # Execute the logic
                        result = await self.mcp_server.execute_tool(name, args)

                        tool_calls_data.append({
                            "id": tool_call.id,
                            "type": "function",
                            "function": {"name": name, "arguments": tool_call.function.arguments}
                        })
                        tool_results_data.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "content": json.dumps(result)
                        })

                    # Final pass to summarize tool results
                    messages.append(assistant_msg)
                    for result in tool_results_data:
                        messages.append(result)

                    final_resp = await self.client.chat.completions.create(
                        model=model,
                        messages=messages,
                        max_tokens=500
                    )

                    return {
                        "content": final_resp.choices[0].message.content,
                        "tool_calls": tool_calls_data,
                        "tool_results": tool_results_data
                    }

                return {
                    "content": assistant_msg.content,
                    "tool_calls": None,
                    "tool_results": None
                }

            except Exception as e:
                last_error = e
                if "429" in str(e) or "limit" in str(e).lower():
                    logger.warning(f"Model {model} busy, trying next...")
                    await asyncio.sleep(1)
                    continue
                raise OpenAIAPIError(message=str(e), status_code=500)

        raise OpenAIAPIError(message=f"All models rate-limited: {str(last_error)}", status_code=429)