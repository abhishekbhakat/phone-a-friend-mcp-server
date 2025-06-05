class PhoneAFriendConfig:
    """Centralized configuration for Phone-a-Friend MCP server."""

    def __init__(self, api_key: str | None = None, model: str | None = None, base_url: str | None = None, provider: str | None = None) -> None:
        """Initialize configuration with provided values.

        Args:
            api_key: API key for external AI services
            model: Model to use (e.g., 'gpt-4', 'anthropic/claude-3.5-sonnet')
            base_url: Custom base URL for API (optional, providers use defaults)
            provider: Provider type ('openai', 'openrouter', 'anthropic')
        """
        self.api_key = api_key
        self.provider = provider or self._detect_provider()
        self.model = model or self._get_default_model()
        self.base_url = base_url  # Only use if explicitly provided

        # Validate required configuration
        if not self.api_key:
            raise ValueError(f"Missing required API key for {self.provider}. Set {self._get_env_var_name()} environment variable or pass --api-key")

    def _detect_provider(self) -> str:
        """Detect provider based on available environment variables."""
        import os

        if os.environ.get("OPENROUTER_API_KEY"):
            return "openrouter"
        elif os.environ.get("ANTHROPIC_API_KEY"):
            return "anthropic"
        elif os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY"):
            return "google"
        elif os.environ.get("OPENAI_API_KEY"):
            return "openai"
        else:
            # Default to OpenAI
            return "openai"

    def _get_default_model(self) -> str:
        """Get default model based on provider."""
        models = {"openai": "o3", "openrouter": "anthropic/claude-4-opus", "anthropic": "claude-4-opus", "google": "gemini-2.5-pro-preview-05-06"}
        if self.provider not in models:
            raise ValueError(f"Unknown provider: {self.provider}. Supported providers: {list(models.keys())}")
        return models[self.provider]

    def _get_env_var_name(self) -> str:
        """Get environment variable name for the provider."""
        env_vars = {"openai": "OPENAI_API_KEY", "openrouter": "OPENROUTER_API_KEY", "anthropic": "ANTHROPIC_API_KEY", "google": "GOOGLE_API_KEY or GEMINI_API_KEY"}
        return env_vars.get(self.provider, "OPENAI_API_KEY")
