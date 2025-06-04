import pytest

from phone_a_friend_mcp_server.config import PhoneAFriendConfig
from phone_a_friend_mcp_server.tools.friend_tool import AskForAdviceTool, GetSuggestionsTool


@pytest.fixture
def config():
    return PhoneAFriendConfig()


@pytest.mark.asyncio
async def test_ask_for_advice_tool(config):
    """Test the ask for advice tool."""
    tool = AskForAdviceTool(config)
    
    result = await tool.run(topic="career", context="I'm considering a job change")
    
    assert "advice" in result
    assert "topic" in result
    assert result["topic"] == "career"
    assert "disclaimer" in result


@pytest.mark.asyncio
async def test_get_suggestions_tool(config):
    """Test the get suggestions tool."""
    tool = GetSuggestionsTool(config)
    
    result = await tool.run(category="books")
    
    assert "suggestions" in result
    assert "category" in result
    assert result["category"] == "books"
    assert isinstance(result["suggestions"], list)
    assert len(result["suggestions"]) > 0
