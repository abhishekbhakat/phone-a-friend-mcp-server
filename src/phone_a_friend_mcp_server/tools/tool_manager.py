from typing import Dict, List

from mcp.types import Tool

from phone_a_friend_mcp_server.config import PhoneAFriendConfig
from phone_a_friend_mcp_server.tools.base_tools import BaseTool
from phone_a_friend_mcp_server.tools.friend_tool import PhoneAFriendTool


class ToolManager:
    """Manages all available tools for the Phone-a-Friend MCP server."""

    def __init__(self, config: PhoneAFriendConfig):
        self.config = config
        self._tools: Dict[str, BaseTool] = {}
        self._initialize_tools()

    def _initialize_tools(self):
        """Initialize all available tools."""
        tools = [
            PhoneAFriendTool(self.config),
        ]

        for tool in tools:
            self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool:
        """Get a tool by name."""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found")
        return self._tools[name]

    def list_tools(self) -> List[Tool]:
        """List all available tools in MCP format."""
        mcp_tools = []
        for tool in self._tools.values():
            mcp_tool = Tool(
                name=tool.name,
                description=tool.description,
                inputSchema=tool.parameters
            )
            mcp_tools.append(mcp_tool)
        return mcp_tools

    def get_tool_names(self) -> List[str]:
        """Get list of all tool names."""
        return list(self._tools.keys())
