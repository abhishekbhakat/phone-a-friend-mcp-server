import os
import tempfile

import pytest

from phone_a_friend_mcp_server.config import PhoneAFriendConfig
from phone_a_friend_mcp_server.tools.fax_tool import FaxAFriendTool


@pytest.fixture
def config():
    """Create a mock config for testing."""
    return PhoneAFriendConfig(api_key="test-key", provider="openai", model="gpt-4")


@pytest.fixture
def temp_project():
    """Create a temporary project structure for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create .gitignore
        with open(os.path.join(temp_dir, ".gitignore"), "w") as f:
            f.write("*.pyc\n")
            f.write("__pycache__/\n")

        # Create some files
        os.makedirs(os.path.join(temp_dir, "src"))
        with open(os.path.join(temp_dir, "src", "main.py"), "w") as f:
            f.write("print('hello')\n")
        with open(os.path.join(temp_dir, "src", "main.pyc"), "w") as f:
            f.write("binary_content")
        with open(os.path.join(temp_dir, "README.md"), "w") as f:
            f.write("# Project\n")

        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            yield temp_dir
        finally:
            os.chdir(original_cwd)


@pytest.mark.asyncio
async def test_fax_a_friend_tool_with_context_builder(config, temp_project):
    """Test the fax a friend tool with the new context builder."""
    tool = FaxAFriendTool(config)

    result = await tool.run(
        all_related_context="This is the general context.",
        file_list=["src/main.py", "README.md", "src/main.pyc"],
        task="Review the code.",
        output_directory=".",
    )

    assert result["status"] == "success"
    assert result["file_name"] == "fax_a_friend.md"
    assert "instructions" in result

    expected_file_path = os.path.join(temp_project, "fax_a_friend.md")
    assert os.path.exists(expected_file_path)

    with open(expected_file_path, encoding="utf-8") as f:
        content = f.read()
        assert "=== TASK ===" in content
        assert "Review the code." in content
        assert "=== GENERAL CONTEXT ===" in content
        assert "This is the general context." in content
        assert "=== CODE CONTEXT ===" in content
        assert "<file_tree>" in content
        assert "main.py" in content
        assert "README.md" in content
        assert "main.pyc" not in content  # Should be ignored
        assert '<file="src/main.py">' in content
        assert "print('hello')" in content
        assert "=== INSTRUCTIONS ===" in content
        assert "Provide exhaustive, step-by-step reasoning." in content
        assert "Never include files matching .gitignore patterns." in content


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
