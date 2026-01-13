"""MCP Server base class for Todo operations."""

from typing import Dict, List, Any, Callable
from uuid import UUID


class TodoMCPServer:
    """Base class for Model Context Protocol (MCP) server.

    Provides tool registration and OpenAI-compatible tool definitions
    for task management operations. Tools are called by the AI agent
    to perform CRUD operations on tasks.
    """

    def __init__(self):
        """Initialize MCP server with empty tool registry."""
        self.tools: Dict[str, Callable] = {}
        self.tool_definitions: List[Dict[str, Any]] = []

    def register_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        function: Callable
    ) -> None:
        """Register a tool with the MCP server.

        Args:
            name: Tool name (e.g., "add_task")
            description: Human-readable description of what the tool does
            parameters: JSON schema for tool parameters
            function: Callable that implements the tool logic
        """
        # Store the function
        self.tools[name] = function

        # Create OpenAI-compatible tool definition
        tool_def = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }
        self.tool_definitions.append(tool_def)

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get all registered tool definitions in OpenAI format.

        Returns:
            List of tool definitions compatible with OpenAI API
        """
        return self.tool_definitions

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a registered tool with given arguments.

        Args:
            tool_name: Name of the tool to execute
            arguments: Dictionary of arguments to pass to the tool

        Returns:
            Tool execution result as dictionary

        Raises:
            ValueError: If tool is not registered
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' is not registered")

        tool_function = self.tools[tool_name]
        result = await tool_function(**arguments)
        return result

    def list_tools(self) -> List[str]:
        """Get list of all registered tool names.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())
