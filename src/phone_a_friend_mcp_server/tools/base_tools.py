from abc import ABC, abstractmethod
from typing import Any

from phone_a_friend_mcp_server.config import PhoneAFriendConfig


class BaseTool(ABC):
    """Base class for all Phone-a-Friend tools."""

    def __init__(self, config: PhoneAFriendConfig):
        self.config = config

    @abstractmethod
    async def run(self, **kwargs) -> dict[str, Any]:
        """Execute the tool with given parameters."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> dict[str, Any]:
        """Tool parameters schema."""
        pass
