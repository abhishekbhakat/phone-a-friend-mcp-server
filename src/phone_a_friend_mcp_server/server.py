import logging
from typing import Any

import anyio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Prompt, Resource, ResourceTemplate, TextContent, Tool

from phone_a_friend_mcp_server.config import PhoneAFriendConfig
from phone_a_friend_mcp_server.tools.tool_manager import ToolManager

logger = logging.getLogger(__name__)


def _format_tool_result(result: Any) -> str:
    """Format tool result for display."""
    if isinstance(result, dict):
        formatted_result = ""
        for key, value in result.items():
            if isinstance(value, list):
                formatted_result += f"{key.title()}:\n"
                for item in value:
                    formatted_result += f"  • {item}\n"
            else:
                formatted_result += f"{key.title()}: {value}\n"
        return formatted_result.strip()
    else:
        return str(result)


async def serve(config: PhoneAFriendConfig) -> None:
    """Start the Phone-a-Friend MCP server.

    Args:
        config: Configuration object with settings
    """
    server = Server("phone-a-friend-mcp-server")
    tool_manager = ToolManager(config)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools."""
        try:
            return tool_manager.list_tools()
        except Exception as e:
            logger.error("Failed to list tools: %s", e)
            raise

    @server.list_resources()
    async def list_resources() -> list[Resource]:
        """List available resources (returns empty list for now)."""
        logger.info("Resources list requested - returning empty list")
        return []

    @server.list_resource_templates()
    async def list_resource_templates() -> list[ResourceTemplate]:
        """List available resource templates (returns empty list for now)."""
        logger.info("Resource templates list requested - returning empty list")
        return []

    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        """List available prompts (returns empty list for now)."""
        logger.info("Prompts list requested - returning empty list")
        return []

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute a tool with the given arguments."""
        try:
            logger.info(f"Calling tool: {name} with arguments: {arguments}")
            tool = tool_manager.get_tool(name)
            result = await tool.run(**arguments)
            formatted_result = _format_tool_result(result)
            return [TextContent(type="text", text=formatted_result)]

        except Exception as e:
            logger.error("Tool execution failed: %s", e)
            error_msg = f"Error executing tool '{name}': {str(e)}"
            return [TextContent(type="text", text=error_msg)]

    # Start the server
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        try:
            logger.info("Starting Phone-a-Friend MCP server...")
            await server.run(read_stream, write_stream, options, raise_exceptions=True)
        except anyio.BrokenResourceError:
            logger.error("BrokenResourceError: Stream was closed unexpectedly. Exiting gracefully.")
        except Exception as e:
            logger.error(f"Unexpected error in server.run: {e}")
            raise
