import os
import tempfile

import pytest

from phone_a_friend_mcp_server.config import PhoneAFriendConfig
from phone_a_friend_mcp_server.tools.fax_tool import FaxAFriendTool


@pytest.fixture
def config():
    """Create a mock config for testing."""
    return PhoneAFriendConfig(api_key="test-key", provider="openai", model="gpt-4")


@pytest.mark.asyncio
async def test_fax_a_friend_tool(config):
    """Test the fax a friend tool."""
    tool = FaxAFriendTool(config)

    # Test with temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            result = await tool.run(
                all_related_context="We have a complex software architecture decision to make",
                any_additional_context="The team has experience with microservices",
                task="Help us choose between monolith and microservices architecture",
            )

            # Check result structure
            assert result["status"] == "success"
            assert "file_path" in result
            assert result["file_name"] == "fax_a_friend.md"
            assert "instructions" in result
            assert result["prompt_length"] > 0
            assert result["context_length"] > 0
            assert result["task"] == "Help us choose between monolith and microservices architecture"

            # Check file was created
            assert os.path.exists("fax_a_friend.md")

            # Check file content
            with open("fax_a_friend.md", encoding="utf-8") as f:
                content = f.read()
                assert "=== TASK ===" in content
                assert "=== ALL RELATED CONTEXT ===" in content
                assert "=== ADDITIONAL CONTEXT ===" in content
                assert "=== INSTRUCTIONS ===" in content
                assert "complex software architecture decision" in content
                assert "microservices architecture" in content

        finally:
            os.chdir(original_cwd)


@pytest.mark.asyncio
async def test_fax_a_friend_tool_without_additional_context(config):
    """Test the fax a friend tool without additional context."""
    tool = FaxAFriendTool(config)

    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            result = await tool.run(all_related_context="Simple problem context", task="Simple task")

            assert result["status"] == "success"
            assert os.path.exists("fax_a_friend.md")

            # Check file content doesn't include additional context section
            with open("fax_a_friend.md", encoding="utf-8") as f:
                content = f.read()
                assert "=== TASK ===" in content
                assert "=== ALL RELATED CONTEXT ===" in content
                assert "=== ADDITIONAL CONTEXT ===" not in content
                assert "=== INSTRUCTIONS ===" in content

        finally:
            os.chdir(original_cwd)


@pytest.mark.asyncio
async def test_fax_a_friend_tool_overwrite(config):
    """Test that the fax a friend tool overwrites existing files."""
    tool = FaxAFriendTool(config)

    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            # Create initial file
            with open("fax_a_friend.md", "w") as f:
                f.write("Old content")

            result = await tool.run(all_related_context="New context", task="New task")

            assert result["status"] == "success"

            # Check file was overwritten
            with open("fax_a_friend.md", encoding="utf-8") as f:
                content = f.read()
                assert "Old content" not in content
                assert "New context" in content
                assert "New task" in content

        finally:
            os.chdir(original_cwd)
