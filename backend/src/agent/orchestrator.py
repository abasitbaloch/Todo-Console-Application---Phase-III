"""
Agent Orchestrator - Production Version
Fixes: Tool Output Mapping, Fallbacks, and User Sync
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
from ..errors.handlers import OpenAIAPIError

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
        self.mcp_server = self._initialize_mcp_server()

    def _initialize_mcp_server(self) -> TodoMCPServer:
        server = TodoMCPServer()
        
        server.register_tool(
            name="add_task",
            description="Create a new task with a title.",
            parameters={
                "type": "object",
                "properties": {"title": {"type": "string"}},
                "required": ["title"]
            },
            function=lambda title, user_id: mcp_tools.add_task(self.db, user_id, title)
        )

        server.register_tool(
            name="list_tasks",
            description="List all tasks for the current user.",
            parameters={"type": "object", "properties": {"filter_completed": {"type": "boolean"}}},
            function=lambda user_id, filter_completed=None: mcp_tools.list_tasks(self.db, user_id, filter_completed)
        )

        return server

    def _build_messages(self, history: List[Message], new_message: str) -> List[Dict[str, Any]]:
        messages = [{"role": "system", "content": get_system_prompt()}]
        
        # Only keep last 5 messages for token efficiency
        for msg in history[-5:]:
            msg_dict = {"role": msg.role.value, "content": msg.content or ""}
            
            # Reconstruct tool calls if they exist in history
            if msg.tool_calls:
                msg_dict["tool_calls"] = msg.tool_calls
            
            messages.append(msg_dict)
            
            # Reconstruct tool results if they exist in history
            if msg.tool_results:
                for result in msg.tool_results:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": result["tool_call_id"],
                        "content": json.dumps(result["content"])
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
        
        # Priority list of free models
        models = [
            os.getenv("CHAT_MODEL", "google/gemini-2.0-flash-exp:free"),
            "deepseek/deepseek-chat:free",
            "openrouter/auto"
        ]

        last_error = None
        for model in models:
            try:
                messages = self._build_messages(conversation_history, new_message)

                # API Call 1
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=self.mcp_server.get_tool_definitions(),
                    tool_choice="auto",
                    max_tokens=500,
                    extra_headers={"HTTP-Referer": "https://vercel.app", "X-Title": "Todo AI"}
                )

                assistant_msg = response.choices[0].message
                
                if assistant_msg.tool_calls:
                    # Capture the assistant's request for tool calls
                    messages.append(assistant_msg)
                    
                    tool_calls_summary = []
                    tool_results_summary = []

                    for tool_call in assistant_msg.tool_calls:
                        name = tool_call.function.name
                        try:
                            args = json.loads(tool_call.function.arguments)
                            args["user_id"] = user_id 
                        except:
                            continue
                        
                        # Execute the logic
                        result = await self.mcp_server.execute_tool(name, args)

                        # Create the correct tool-role message for the API
                        tool_result_msg = {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result)
                        }
                        messages.append(tool_result_msg)

                        # Save for database storage
                        tool_calls_summary.append({
                            "id": tool_call.id,
                            "type": "function",
                            "function": {"name": name, "arguments": tool_call.function.arguments}
                        })
                        tool_results_summary.append({
                            "tool_call_id": tool_call.id,
                            "content": result
                        })

                    # Final API call to summarize results
                    final_resp = await self.client.chat.completions.create(
                        model=model,
                        messages=messages,
                        max_tokens=500
                    )

                    return {
                        "content": final_resp.choices[0].message.content,
                        "tool_calls": tool_calls_data if 'tool_calls_data' in locals() else tool_calls_summary,
                        "tool_results": tool_results_data if 'tool_results_data' in locals() else tool_results_summary
                    }

                return {"content": assistant_msg.content, "tool_calls": None, "tool_results": None}

            except Exception as e:
                last_error = e
                logger.warning(f"Model {model} failed. Error: {str(e)}")
                await asyncio.sleep(1)
                continue

        raise OpenAIAPIError(message=f"AI busy or tool error: {str(last_error)}", status_code=500)