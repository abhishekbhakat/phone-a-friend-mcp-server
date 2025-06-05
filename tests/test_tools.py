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
        result = await tool.run(
            all_related_context="We have a complex software architecture decision to make",
            any_additional_context="The team has experience with microservices",
            task="Help us choose between monolith and microservices architecture",
            output_directory=temp_dir,
        )

        # Check result structure
        assert result["status"] == "success"
        assert "file_path" in result
        assert result["file_name"] == "fax_a_friend.md"
        assert result["output_directory"] == temp_dir
        assert "instructions" in result
        assert result["prompt_length"] > 0
        assert result["context_length"] > 0
        assert result["task"] == "Help us choose between monolith and microservices architecture"

        # Check file was created in the specified directory
        expected_file_path = os.path.join(temp_dir, "fax_a_friend.md")
        assert os.path.exists(expected_file_path)

        # Check file content
        with open(expected_file_path, encoding="utf-8") as f:
            content = f.read()
            assert "=== TASK ===" in content
            assert "=== ALL RELATED CONTEXT ===" in content
            assert "=== ADDITIONAL CONTEXT ===" in content
            assert "=== INSTRUCTIONS ===" in content
            assert "complex software architecture decision" in content
            assert "microservices architecture" in content


@pytest.mark.asyncio
async def test_fax_a_friend_tool_without_additional_context(config):
    """Test the fax a friend tool without additional context."""
    tool = FaxAFriendTool(config)

    with tempfile.TemporaryDirectory() as temp_dir:
        result = await tool.run(all_related_context="Simple problem context", task="Simple task", output_directory=temp_dir)

        assert result["status"] == "success"
        expected_file_path = os.path.join(temp_dir, "fax_a_friend.md")
        assert os.path.exists(expected_file_path)

        # Check file content doesn't include additional context section
        with open(expected_file_path, encoding="utf-8") as f:
            content = f.read()
            assert "=== TASK ===" in content
            assert "=== ALL RELATED CONTEXT ===" in content
            assert "=== ADDITIONAL CONTEXT ===" not in content
            assert "=== INSTRUCTIONS ===" in content


@pytest.mark.asyncio
async def test_fax_a_friend_tool_overwrite(config):
    """Test that the fax a friend tool overwrites existing files."""
    tool = FaxAFriendTool(config)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create initial file
        initial_file_path = os.path.join(temp_dir, "fax_a_friend.md")
        with open(initial_file_path, "w") as f:
            f.write("Old content")

        result = await tool.run(all_related_context="New context", task="New task", output_directory=temp_dir)

        assert result["status"] == "success"

        # Check file was overwritten
        with open(initial_file_path, encoding="utf-8") as f:
            content = f.read()
            assert "Old content" not in content
            assert "New context" in content
            assert "New task" in content


@pytest.mark.asyncio
async def test_fax_a_friend_tool_missing_output_directory(config):
    """Test that the fax a friend tool fails when output_directory is missing."""
    tool = FaxAFriendTool(config)

    result = await tool.run(
        all_related_context="Some context",
        task="Some task",
        # Missing output_directory parameter
    )

    assert result["status"] == "failed"
    assert "output_directory parameter is required" in result["error"]


@pytest.mark.asyncio
async def test_fax_a_friend_tool_invalid_output_directory(config):
    """Test that the fax a friend tool handles invalid output directories."""
    tool = FaxAFriendTool(config)

    # Test with a path that cannot be created (assuming /root is not writable in most test environments)
    result = await tool.run(all_related_context="Some context", task="Some task", output_directory="/root/nonexistent/deeply/nested/path")

    assert result["status"] == "failed"
    assert "Cannot create directory" in result["error"]


@pytest.mark.asyncio
async def test_fax_a_friend_tool_user_path_expansion(config):
    """Test that the fax a friend tool properly expands user paths."""
    tool = FaxAFriendTool(config)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a subdirectory to simulate user home expansion
        user_dir = os.path.join(temp_dir, "user_home")
        os.makedirs(user_dir)

        # Mock expanduser to return our test directory
        import unittest.mock

        with unittest.mock.patch("os.path.expanduser", return_value=user_dir):
            result = await tool.run(
                all_related_context="Some context",
                task="Some task",
                output_directory="~/Documents",  # This will be expanded to user_dir
            )

        assert result["status"] == "success"
        assert result["output_directory"] == user_dir
        expected_file_path = os.path.join(user_dir, "fax_a_friend.md")
        assert os.path.exists(expected_file_path)
