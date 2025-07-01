import os
from typing import Any

import aiofiles

from phone_a_friend_mcp_server.tools.base_tools import BaseTool
from phone_a_friend_mcp_server.utils.context_builder import build_code_context


class FaxAFriendTool(BaseTool):
    """
    Fax-a-Friend: Generate a master prompt file for manual AI consultation.

    ⚠️  ONLY USE WHEN EXPLICITLY REQUESTED BY USER ⚠️

    This tool creates a comprehensive master prompt and saves it to a file for manual
    copy-paste into external AI interfaces. It uses the same prompt structure as the
    phone_a_friend tool but requires manual intervention to get the AI response.
    """

    @property
    def name(self) -> str:
        return "fax_a_friend"

    @property
    def description(self) -> str:
        return """🚨🚨🚨 **EXCLUSIVE USE ONLY** 🚨🚨🚨

**USE ONLY WHEN USER EXPLICITLY ASKS TO "fax a friend"**
**DO NOT use as fallback if phone_a_friend fails**
**DO NOT auto-switch between fax/phone tools**
**If this tool fails, ask user for guidance - do NOT try phone_a_friend**

Purpose: pair-programming caliber *coding help* — reviews, debugging,
refactors, design, migrations.

This tool creates a file for manual AI consultation. After file creation,
wait for the user to return with the external AI's response.
Replies must be exhaustively detailed. Do **NOT** include files ignored by .gitignore (e.g., *.pyc).

Hard restrictions:
  • Generated prompt includes *only* the context you provide.
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
The generated prompt expects AI to reply in the same XML structure, adding or
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
                "output_directory": {
                    "type": "string",
                    "description": (
                        "Directory path where the fax_a_friend.md file will be created.\n"
                        "Recommended: Use the user's current working directory for convenience.\n"
                        "Must be a valid, writable directory path.\n"
                        "Examples: '/tmp', '~/Documents', './output', '/Users/username/Desktop'"
                    ),
                },
            },
            "required": ["all_related_context", "task", "output_directory"],
        }

    async def run(self, **kwargs) -> dict[str, Any]:
        all_related_context = kwargs.get("all_related_context", "")
        file_list = kwargs.get("file_list", [])
        task = kwargs.get("task", "")
        output_directory = kwargs.get("output_directory", "")

        code_context = build_code_context(file_list)
        master_prompt = self._create_master_prompt(all_related_context, code_context, task)

        try:
            output_dir = self._prepare_output_directory(output_directory)

            file_path = os.path.join(output_dir, "fax_a_friend.md")

            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(master_prompt)

            abs_path = os.path.abspath(file_path)

            return {
                "status": "success",
                "file_path": abs_path,
                "file_name": "fax_a_friend.md",
                "output_directory": output_dir,
                "prompt_length": len(master_prompt),
                "context_length": len(master_prompt),
                "task": task,
                "instructions": self._get_manual_workflow_instructions(abs_path),
            }

        except Exception as e:
            return {"status": "failed", "error": str(e), "output_directory": output_directory, "context_length": len(master_prompt), "task": task}

    def _create_master_prompt(self, all_related_context: str, code_context: str, task: str) -> str:
        """Create a comprehensive prompt identical to PhoneAFriendTool's version."""

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

    def _prepare_output_directory(self, output_directory: str) -> str:
        """Validate and prepare the output directory."""
        if not output_directory:
            raise ValueError("output_directory parameter is required")

        expanded_path = os.path.expanduser(output_directory)
        resolved_path = os.path.abspath(expanded_path)

        try:
            os.makedirs(resolved_path, exist_ok=True)
        except OSError as e:
            raise ValueError(f"Cannot create directory '{resolved_path}': {e}")

        if not os.access(resolved_path, os.W_OK):
            raise ValueError(f"Directory '{resolved_path}' is not writable")

        return resolved_path

    def _get_manual_workflow_instructions(self, file_path: str) -> str:
        """Generate clear instructions for the manual workflow."""
        return f"""
🚨 MANUAL INTERVENTION REQUIRED 🚨

Your master prompt has been saved to: {file_path}

NEXT STEPS - Please follow these instructions:

1. 📂 Open the file: {file_path}
2. 📋 Copy the ENTIRE prompt content from the file
3. 🤖 Paste it into your preferred AI chat interface (ChatGPT, Claude, Gemini, etc.)
4. ⏳ Wait for the AI's response
5. 📝 Copy the AI's complete response
6. 🔄 Return to this conversation and provide the AI's response

The prompt is ready for any external AI service. Simply copy and paste the entire content.

💡 TIP: You can use the same prompt with multiple AI services to compare responses!
"""
