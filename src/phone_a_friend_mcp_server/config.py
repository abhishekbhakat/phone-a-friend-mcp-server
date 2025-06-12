import os


class PhoneAFriendConfig:
    """Centralized configuration for Phone-a-Friend MCP server."""

    def __init__(self, api_key: str | None = None, model: str | None = None, base_url: str | None = None, provider: str | None = None, temperature: float | None = None) -> None:
        """Initialize configuration with provided values.

        Args:
            api_key: API key for external AI services
            model: Model to use (e.g., 'gpt-4', 'anthropic/claude-3.5-sonnet')
            base_url: Custom base URL for API (optional, providers use defaults)
            provider: Provider type ('openai', 'openrouter', 'anthropic', 'google')
            temperature: Temperature value for the model (0.0-2.0), overrides defaults
        """
        self.api_key = api_key
        self.provider = provider or self._detect_provider()
        self.model = model or self._get_default_model()
        self.base_url = base_url
        self.temperature = self._validate_temperature(temperature)

        if not self.api_key:
            raise ValueError(f"Missing required API key for {self.provider}. Set {self._get_env_var_name()} environment variable or pass --api-key")

    def _detect_provider(self) -> str:
        """Detect provider based on available environment variables."""
        if os.environ.get("OPENROUTER_API_KEY"):
            return "openrouter"
        elif os.environ.get("ANTHROPIC_API_KEY"):
            return "anthropic"
        elif os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY"):
            return "google"
        elif os.environ.get("OPENAI_API_KEY"):
            return "openai"
        else:
            return "openai"

    def _get_default_model(self) -> str:
        """Get default model based on provider."""
        models = {"openai": "o3", "openrouter": "anthropic/claude-4-opus", "anthropic": "claude-4-opus", "google": "gemini-2.5-pro-preview-06-05"}
        if self.provider not in models:
            raise ValueError(f"Unknown provider: {self.provider}. Supported providers: {list(models.keys())}")
        return models[self.provider]

    def _get_env_var_name(self) -> str:
        """Get environment variable name for the provider."""
        env_vars = {"openai": "OPENAI_API_KEY", "openrouter": "OPENROUTER_API_KEY", "anthropic": "ANTHROPIC_API_KEY", "google": "GOOGLE_API_KEY or GEMINI_API_KEY"}
        return env_vars.get(self.provider, "OPENAI_API_KEY")

    def _validate_temperature(self, temperature: float | None) -> float | None:
        """Validate temperature value or get from environment variable."""
        temp_value = temperature
        if temp_value is None:
            env_temp = os.environ.get("PHONE_A_FRIEND_TEMPERATURE")
            if env_temp is not None:
                try:
                    temp_value = float(env_temp)
                except ValueError:
                    raise ValueError(f"Invalid temperature value in PHONE_A_FRIEND_TEMPERATURE: {env_temp}")

        if temp_value is None:
            temp_value = self._get_default_temperature_for_model()

        if temp_value is not None:
            if not isinstance(temp_value, int | float):
                raise ValueError(f"Temperature must be a number, got {type(temp_value).__name__}")
            if not (0.0 <= temp_value <= 2.0):
                raise ValueError(f"Temperature must be between 0.0 and 2.0, got {temp_value}")

        return temp_value

    def _get_default_temperature_for_model(self) -> float | None:
        """Get default temperature for specific models that benefit from it."""
        default_temperatures = {
            "gemini-2.5-pro-preview-06-05": 0.0,
            "gemini-2.5-pro": 0.0,
        }

        return default_temperatures.get(self.model)

    def get_temperature(self) -> float | None:
        """Get the temperature setting for the current model.

        Returns:
            Temperature value if set, None otherwise
        """
        return self.temperature
