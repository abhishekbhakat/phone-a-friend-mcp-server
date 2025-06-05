from typing import Any

from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.openrouter import OpenRouterProvider

from phone_a_friend_mcp_server.tools.base_tools import BaseTool


class PhoneAFriendTool(BaseTool):
    """
    Phone-a-Friend: Consult an external AI for critical thinking and complex reasoning.

    ⚠️  ONLY USE WHEN EXPLICITLY REQUESTED BY USER ⚠️

    This tool sends your problem to an external AI model for analysis and gets back a response.
    The external AI has no memory of previous conversations, so you must provide all relevant context.
    """

    @property
    def name(self) -> str:
        return "phone_a_friend"

    @property
    def description(self) -> str:
        return """🚨  **USE ONLY WHEN USER ASKS TO "phone a friend".**

Purpose: pair-programming caliber *coding help* — reviews, debugging,
refactors, design, migrations.

Hard restrictions:
  • Friend AI sees *only* the two context blocks you send.
  • No memory, no internet, no tools.
  • You must spell out every fact it should rely on.

Required I/O format:
```
<file_tree>
.
├── Dockerfile
├── some_doc_file.md
├── LICENSE
├── pyproject.toml
├── README.md
├── src
│   └── some_module
│       ├── **init**.py
│       ├── **main**.py
│       ├── client
│       │   └── **init**.py
│       ├── config.py
│       ├── server.py
│       └── tools
│           ├── **init**.py
│           ├── base_tools.py
│           └── tool_manager.py
├── tests
│   ├── **init**.py
│   └── test_tools.py
└── uv.lock
</file_tree>

<file="src/some_module/server.py">
# full source here …
</file>
```
The friend AI must reply in the same XML structure, adding or
replacing <file="…"> blocks as needed. Commentary goes outside those tags."""

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "all_related_context": {
                    "type": "string",
                    "description": (
                        "MANDATORY. Everything the friend AI needs to see:\n"
                        "- The full <file_tree> block (ASCII tree).\n"
                        '- One or more <file="…"> blocks with the current code.\n'
                        "- Known constraints (Python version, allowed deps, runtime limits, etc.).\n"
                        "- Any failing test output or traceback.\n"
                        "If it's not here, the friend AI can't use it."
                    ),
                },
                "any_additional_context": {
                    "type": "string",
                    "description": (
                        "Optional extras that help but aren't core code:\n"
                        "- Style guides, architecture docs, API specs.\n"
                        "- Performance targets, security rules, deployment notes.\n"
                        "- Similar past solutions or reference snippets.\n"
                        "Skip it if there's nothing useful."
                    ),
                },
                "task": {
                    "type": "string",
                    "description": (
                        "Plain-English ask. Be surgical.\n"
                        "Good examples:\n"
                        "- Refactor synchronous Flask app to async Quart. Keep py3.10.\n"
                        "- Identify and fix memory leak in src/cache.py.\n"
                        "- Add unit tests for edge cases in utils/math.py.\n"
                        'Bad: vague stuff like "make code better".'
                    ),
                },
            },
            "required": ["all_related_context", "task"],
        }

    async def run(self, **kwargs) -> dict[str, Any]:
        all_related_context = kwargs.get("all_related_context", "")
        any_additional_context = kwargs.get("any_additional_context", "")
        task = kwargs.get("task", "")

        # Create master prompt for external AI
        master_prompt = self._create_master_prompt(all_related_context, any_additional_context, task)

        try:
            # Create Pydantic-AI agent with appropriate provider
            agent = self._create_agent()

            # Send to external AI
            result = await agent.run(master_prompt)

            return {
                "response": result.data,
                "status": "success",
                "provider": self.config.provider,
                "model": self.config.model,
                "context_length": len(all_related_context + any_additional_context),
                "task": task,
            }

        except Exception as e:
            return {
                "error": str(e),
                "status": "failed",
                "provider": self.config.provider,
                "model": self.config.model,
                "context_length": len(all_related_context + any_additional_context),
                "task": task,
                "master_prompt": master_prompt,  # Include for debugging
            }

    def _create_agent(self) -> Agent:
        """Create Pydantic-AI agent with appropriate provider."""
        if self.config.provider == "openrouter":
            # OpenRouter has its own dedicated provider
            provider_kwargs = {"api_key": self.config.api_key}
            if self.config.base_url:
                provider_kwargs["base_url"] = self.config.base_url
            provider = OpenRouterProvider(**provider_kwargs)
            model = OpenAIModel(self.config.model, provider=provider)
        elif self.config.provider == "anthropic":
            # Use Anthropic directly
            provider_kwargs = {"api_key": self.config.api_key}
            provider = AnthropicProvider(**provider_kwargs)
            model = AnthropicModel(self.config.model, provider=provider)
        elif self.config.provider == "google":
            # Use Google/Gemini directly
            provider_kwargs = {"api_key": self.config.api_key}
            provider = GoogleProvider(**provider_kwargs)
            model = GoogleModel(self.config.model, provider=provider)
        else:
            # Default to OpenAI
            provider_kwargs = {"api_key": self.config.api_key}
            if self.config.base_url:
                provider_kwargs["base_url"] = self.config.base_url
            provider = OpenAIProvider(**provider_kwargs)
            model = OpenAIModel(self.config.model, provider=provider)

        return Agent(model)

    def _create_master_prompt(self, all_related_context: str, any_additional_context: str, task: str) -> str:
        """Create a comprehensive prompt for the external AI."""

        prompt_parts = [
            "You are a highly capable AI assistant being consulted for critical thinking, complex reasoning and pair-programming caliber coding help.",
            "You have no memory of previous conversations, so all necessary context is provided below.",
            "",
            "=== TASK ===",
            task,
            "",
            "=== ALL RELATED CONTEXT ===",
            all_related_context,
        ]

        if any_additional_context.strip():
            prompt_parts.extend(
                [
                    "",
                    "=== ADDITIONAL CONTEXT ===",
                    any_additional_context,
                ]
            )

        prompt_parts.extend(
            [
                "",
                "=== INSTRUCTIONS ===",
                "- Analyze the code and requirements step-by-step.",
                "- Show your reasoning and propose concrete changes.",
                '- Provide updated code using the XML format (<file_tree> plus <file="…"> blocks).',
                "- Be explicit and practical.",
                "",
                "Please provide your analysis and updated code:",
            ]
        )

        return "\n".join(prompt_parts)
