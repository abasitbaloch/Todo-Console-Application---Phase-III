"""Agent orchestrator for AI chatbot."""

from typing import List, Dict, Any, Optional
from uuid import UUID
import os
from openai import AsyncOpenAI
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models.message import Message, MessageRole
from ..mcp.server import TodoMCPServer
from ..mcp import tools as mcp_tools
from ..agent.prompts import get_system_prompt
from ..errors.handlers import OpenAIAPIError, MCPToolError


class AgentOrchestrator:
    """Orchestrates AI agent interactions with OpenAI and MCP tools.

    Handles conversation flow, tool execution, and response generation.
    Stateless - all context retrieved from database on each request.
    """

    def __init__(self, db: AsyncSession):
        """Initialize agent orchestrator.

        Args:
            db: Database session for tool execution
        """
        self.db = db
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.mcp_server = self._initialize_mcp_server()

    def _initialize_mcp_server(self) -> TodoMCPServer:
        """Initialize and register all MCP tools.

        Returns:
            Configured TodoMCPServer instance
        """
        server = TodoMCPServer()

        # Register add_task tool
        server.register_tool(
            name="add_task",
            description="Create a new task with a title. Use this when the user wants to add, create, or remember something.",
            parameters={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The task title or description"
                    }
                },
                "required": ["title"]
            },
            function=lambda title, user_id: mcp_tools.add_task(self.db, user_id, title)
        )

        # Register list_tasks tool
        server.register_tool(
            name="list_tasks",
            description="List all tasks for the user. Can optionally filter by completion status.",
            parameters={
                "type": "object",
                "properties": {
                    "filter_completed": {
                        "type": "boolean",
                        "description": "Optional: true for completed tasks only, false for incomplete tasks only, null for all tasks"
                    }
                },
                "required": []
            },
            function=lambda user_id, filter_completed=None: mcp_tools.list_tasks(self.db, user_id, filter_completed)
        )

        # Register complete_task tool
        server.register_tool(
            name="complete_task",
            description="Mark a task as completed. Use fuzzy matching to find the task by title.",
            parameters={
                "type": "object",
                "properties": {
                    "task_identifier": {
                        "type": "string",
                        "description": "The task title or partial title to match"
                    }
                },
                "required": ["task_identifier"]
            },
            function=lambda task_identifier, user_id: mcp_tools.complete_task(self.db, user_id, task_identifier)
        )

        # Register update_task tool
        server.register_tool(
            name="update_task",
            description="Update a task's title. Use fuzzy matching to find the task.",
            parameters={
                "type": "object",
                "properties": {
                    "task_identifier": {
                        "type": "string",
                        "description": "The current task title or partial title to match"
                    },
                    "new_title": {
                        "type": "string",
                        "description": "The new title for the task"
                    }
                },
                "required": ["task_identifier", "new_title"]
            },
            function=lambda task_identifier, new_title, user_id: mcp_tools.update_task(self.db, user_id, task_identifier, new_title)
        )

        # Register delete_task tool
        server.register_tool(
            name="delete_task",
            description="Permanently delete a task. Use fuzzy matching to find the task.",
            parameters={
                "type": "object",
                "properties": {
                    "task_identifier": {
                        "type": "string",
                        "description": "The task title or partial title to match"
                    }
                },
                "required": ["task_identifier"]
            },
            function=lambda task_identifier, user_id: mcp_tools.delete_task(self.db, user_id, task_identifier)
        )

        return server

    def _build_messages(
        self,
        history: List[Message],
        new_message: str
    ) -> List[Dict[str, Any]]:
        """Build message array for OpenAI API from conversation history.

        Args:
            history: List of previous messages in chronological order
            new_message: New user message to add

        Returns:
            List of message dictionaries in OpenAI format
        """
        messages = [
            {"role": "system", "content": get_system_prompt()}
        ]

        # Add conversation history
        for msg in history:
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })

            # Add tool calls and results if present
            if msg.tool_calls:
                messages[-1]["tool_calls"] = msg.tool_calls
            if msg.tool_results:
                for tool_result in msg.tool_results:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_result["tool_call_id"],
                        "content": tool_result["content"]
                    })

        # Add new user message
        messages.append({
            "role": "user",
            "content": new_message
        })

        return messages

    async def process_message(
        self,
        user_id: UUID,
        conversation_history: List[Message],
        new_message: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Process a user message and generate AI response with retry logic.

        Args:
            user_id: UUID of the user
            conversation_history: Previous messages in chronological order
            new_message: New user message
            max_retries: Maximum number of retries for rate limit errors

        Returns:
            Dictionary with response content and tool calls

        Raises:
            OpenAIAPIError: If OpenAI API call fails after retries
            MCPToolError: If tool execution fails
        """
        import asyncio

        for attempt in range(max_retries):
            try:
                # Build messages for OpenAI
                messages = self._build_messages(conversation_history, new_message)

                # Call OpenAI with tools
                response = await self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=messages,
                    tools=self.mcp_server.get_tool_definitions(),
                    tool_choice="auto"
                )

                assistant_message = response.choices[0].message
                tool_calls = []
                tool_results = []

                # Execute tool calls if present
                if assistant_message.tool_calls:
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = eval(tool_call.function.arguments)  # Parse JSON arguments
                        tool_args["user_id"] = user_id  # Inject user_id for security

                        try:
                            # Execute tool
                            result = await self.mcp_server.execute_tool(tool_name, tool_args)

                            tool_calls.append({
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": tool_name,
                                    "arguments": tool_call.function.arguments
                                }
                            })

                            tool_results.append({
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "content": str(result)
                            })

                        except Exception as e:
                            raise MCPToolError(
                                tool_name=tool_name,
                                message=str(e),
                                user_message=f"I had trouble {tool_name.replace('_', ' ')}. Could you try again?"
                            )

                    # If tools were called, make another API call to get final response
                    if tool_results:
                        messages.append({
                            "role": "assistant",
                            "content": assistant_message.content or "",
                            "tool_calls": tool_calls
                        })

                        for tool_result in tool_results:
                            messages.append(tool_result)

                        # Get final response with retry logic
                        for final_attempt in range(max_retries):
                            try:
                                final_response = await self.client.chat.completions.create(
                                    model="gpt-4-turbo-preview",
                                    messages=messages
                                )

                                return {
                                    "content": final_response.choices[0].message.content,
                                    "tool_calls": tool_calls,
                                    "tool_results": tool_results
                                }
                            except Exception as e:
                                if "rate_limit" in str(e).lower() and final_attempt < max_retries - 1:
                                    # Exponential backoff: 1s, 2s, 4s
                                    wait_time = 2 ** final_attempt
                                    await asyncio.sleep(wait_time)
                                    continue
                                raise

                # No tools called, return direct response
                return {
                    "content": assistant_message.content,
                    "tool_calls": None,
                    "tool_results": None
                }

            except Exception as e:
                # Handle rate limit errors with exponential backoff
                if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                    continue

                # Other OpenAI errors
                if "openai" in str(type(e)).lower():
                    raise OpenAIAPIError(
                        message=str(e),
                        status_code=getattr(e, "status_code", None)
                    )
                raise
