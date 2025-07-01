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
from phone_a_friend_mcp_server.utils.context_builder import build_code_context


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
        return """🚨🚨🚨 **EXCLUSIVE USE ONLY** 🚨🚨🚨

**USE ONLY WHEN USER EXPLICITLY ASKS TO "phone a friend"**
**DO NOT use as fallback if fax_a_friend fails**
**DO NOT auto-switch between phone/fax tools**
**If this tool fails, ask user for guidance - do NOT try fax_a_friend**

Purpose: pair-programming caliber *coding help* — reviews, debugging,
refactors, design, migrations.

Hard restrictions:
  • Friend AI sees *only* the context you provide.
  • No memory, no internet, no tools.
  • You must spell out every fact it should rely on.
Replies must be exhaustively detailed. Do **NOT** include files ignored by .gitignore (e.g., *.pyc).

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
                        "General context for the friend AI. Include known constraints "
                        "(Python version, allowed deps, etc.), failing test output, tracebacks, "
                        "or code snippets for reference. For complete files, use file_list instead."
                    ),
                },
                "file_list": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Optional but recommended. A list of file paths or glob patterns to be included in the code context. "
                        "The tool will automatically read these files, filter them against .gitignore, and build the context. "
                        "Better and faster than including complete files in all_related_context."
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
        file_list = kwargs.get("file_list", [])
        task = kwargs.get("task", "")

        code_context = build_code_context(file_list)
        master_prompt = self._create_master_prompt(all_related_context, code_context, task)

        try:
            agent = self._create_agent()
            temperature = self.config.get_temperature()

            if temperature is not None:
                result = await agent.run(master_prompt, model_settings={"temperature": temperature})
            else:
                result = await agent.run(master_prompt)

            return {
                "response": result.data,
                "status": "success",
                "provider": self.config.provider,
                "model": self.config.model,
                "temperature": temperature,
                "context_length": len(master_prompt),
                "task": task,
            }

        except Exception as e:
            temperature = self.config.get_temperature()
            return {
                "error": str(e),
                "status": "failed",
                "provider": self.config.provider,
                "model": self.config.model,
                "temperature": temperature,
                "context_length": len(master_prompt),
                "task": task,
                "master_prompt": master_prompt,
            }

    def _create_agent(self) -> Agent:
        """Create Pydantic-AI agent with appropriate provider."""
        if self.config.provider == "openrouter":
            provider_kwargs = {"api_key": self.config.api_key}
            if self.config.base_url:
                provider_kwargs["base_url"] = self.config.base_url
            provider = OpenRouterProvider(**provider_kwargs)
            model = OpenAIModel(self.config.model, provider=provider)
        elif self.config.provider == "anthropic":
            provider_kwargs = {"api_key": self.config.api_key}
            provider = AnthropicProvider(**provider_kwargs)
            model = AnthropicModel(self.config.model, provider=provider)
        elif self.config.provider == "google":
            provider_kwargs = {"api_key": self.config.api_key}
            provider = GoogleProvider(**provider_kwargs)
            model = GoogleModel(self.config.model, provider=provider)
        else:
            provider_kwargs = {"api_key": self.config.api_key}
            if self.config.base_url:
                provider_kwargs["base_url"] = self.config.base_url
            provider = OpenAIProvider(**provider_kwargs)
            model = OpenAIModel(self.config.model, provider=provider)

        return Agent(model)

    def _create_master_prompt(self, all_related_context: str, code_context: str, task: str) -> str:
        """Create a comprehensive prompt for the external AI."""

        prompt_parts = [
            "You are a highly capable AI assistant being consulted for critical thinking, complex reasoning and pair-programming caliber coding help.",
            "You have no memory of previous conversations, so all necessary context is provided below.",
            "",
            "=== TASK ===",
            task,
            "",
            "=== GENERAL CONTEXT ===",
            all_related_context,
            "",
            "=== CODE CONTEXT ===",
            code_context,
        ]

        prompt_parts.extend(
            [
                "",
                "=== INSTRUCTIONS ===",
                "- Provide exhaustive, step-by-step reasoning.",
                "- Never include files matching .gitignore patterns.",
                "- Analyze the code and requirements step-by-step.",
                "- Show your reasoning and propose concrete changes.",
                '- Provide updated code using the XML format (<file_tree> plus <file="…"> blocks).',
                "- Be explicit and practical.",
                "",
                "Please provide your analysis and updated code:",
            ]
        )

        return "\n".join(prompt_parts)
