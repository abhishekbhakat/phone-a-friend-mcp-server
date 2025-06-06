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

    with tempfile.TemporaryDirectory() as temp_dir:
        result = await tool.run(
            all_related_context="We have a complex software architecture decision to make",
            any_additional_context="The team has experience with microservices",
            task="Help us choose between monolith and microservices architecture",
            output_directory=temp_dir,
        )

        assert result["status"] == "success"
        assert "file_path" in result
        assert result["file_name"] == "fax_a_friend.md"
        assert result["output_directory"] == temp_dir
        assert "instructions" in result
        assert result["prompt_length"] > 0
        assert result["context_length"] > 0
        assert result["task"] == "Help us choose between monolith and microservices architecture"

        expected_file_path = os.path.join(temp_dir, "fax_a_friend.md")
        assert os.path.exists(expected_file_path)

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
        initial_file_path = os.path.join(temp_dir, "fax_a_friend.md")
        with open(initial_file_path, "w") as f:
            f.write("Old content")

        result = await tool.run(all_related_context="New context", task="New task", output_directory=temp_dir)

        assert result["status"] == "success"

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
    )

    assert result["status"] == "failed"
    assert "output_directory parameter is required" in result["error"]


@pytest.mark.asyncio
async def test_fax_a_friend_tool_invalid_output_directory(config):
    """Test that the fax a friend tool handles invalid output directories."""
    tool = FaxAFriendTool(config)

    result = await tool.run(all_related_context="Some context", task="Some task", output_directory="/root/nonexistent/deeply/nested/path")

    assert result["status"] == "failed"
    assert "Cannot create directory" in result["error"]


@pytest.mark.asyncio
async def test_fax_a_friend_tool_user_path_expansion(config):
    """Test that the fax a friend tool properly expands user paths."""
    tool = FaxAFriendTool(config)

    with tempfile.TemporaryDirectory() as temp_dir:
        user_dir = os.path.join(temp_dir, "user_home")
        os.makedirs(user_dir)

        import unittest.mock

        with unittest.mock.patch("os.path.expanduser", return_value=user_dir):
            result = await tool.run(
                all_related_context="Some context",
                task="Some task",
                output_directory="~/Documents",
            )

        assert result["status"] == "success"
        assert result["output_directory"] == user_dir
        expected_file_path = os.path.join(user_dir, "fax_a_friend.md")
        assert os.path.exists(expected_file_path)


def test_config_default_temperature():
    """Test that default temperature is applied for Gemini 2.5 Pro."""
    config = PhoneAFriendConfig(api_key="test-key", provider="google", model="gemini-2.5-pro")

    assert config.get_temperature() == 0.0

    config2 = PhoneAFriendConfig(api_key="test-key", provider="openai", model="gpt-4")
    assert config2.get_temperature() is None


def test_config_custom_temperature():
    """Test custom temperature via parameter."""
    config = PhoneAFriendConfig(api_key="test-key", provider="openai", model="gpt-4", temperature=0.7)

    assert config.get_temperature() == 0.7

    config2 = PhoneAFriendConfig(api_key="test-key", provider="google", model="gemini-2.5-pro", temperature=0.5)
    assert config2.get_temperature() == 0.5


def test_config_invalid_temperature():
    """Test that invalid temperature raises ValueError."""
    with pytest.raises(ValueError, match="must be between 0.0 and 2.0"):
        PhoneAFriendConfig(api_key="test-key", temperature=3.0)

    with pytest.raises(ValueError, match="must be between 0.0 and 2.0"):
        PhoneAFriendConfig(api_key="test-key", temperature=-0.1)


def test_config_temperature_from_env(monkeypatch):
    """Test temperature from environment variable."""
    monkeypatch.setenv("PHONE_A_FRIEND_TEMPERATURE", "0.3")

    config = PhoneAFriendConfig(api_key="test-key", provider="openai", model="gpt-4")

    assert config.get_temperature() == 0.3


def test_config_invalid_temperature_from_env(monkeypatch):
    """Test invalid temperature from environment variable."""
    monkeypatch.setenv("PHONE_A_FRIEND_TEMPERATURE", "not_a_number")

    with pytest.raises(ValueError, match="Invalid temperature value"):
        PhoneAFriendConfig(api_key="test-key", provider="openai", model="gpt-4")
