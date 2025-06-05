import os
from typing import Any

import aiofiles

from phone_a_friend_mcp_server.tools.base_tools import BaseTool


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

Hard restrictions:
  • Generated prompt includes *only* the two context blocks you send.
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
        any_additional_context = kwargs.get("any_additional_context", "")
        task = kwargs.get("task", "")
        output_directory = kwargs.get("output_directory", "")

        # Create master prompt using the same logic as phone_a_friend
        master_prompt = self._create_master_prompt(all_related_context, any_additional_context, task)

        try:
            # Validate and prepare output directory
            output_dir = self._prepare_output_directory(output_directory)

            # Create full file path
            file_path = os.path.join(output_dir, "fax_a_friend.md")

            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(master_prompt)

            # Get absolute path for user reference
            abs_path = os.path.abspath(file_path)

            return {
                "status": "success",
                "file_path": abs_path,
                "file_name": "fax_a_friend.md",
                "output_directory": output_dir,
                "prompt_length": len(master_prompt),
                "context_length": len(all_related_context + any_additional_context),
                "task": task,
                "instructions": self._get_manual_workflow_instructions(abs_path),
            }

        except Exception as e:
            return {"status": "failed", "error": str(e), "output_directory": output_directory, "context_length": len(all_related_context + any_additional_context), "task": task}

    def _create_master_prompt(self, all_related_context: str, any_additional_context: str, task: str) -> str:
        """Create a comprehensive prompt identical to PhoneAFriendTool's version."""

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

    def _prepare_output_directory(self, output_directory: str) -> str:
        """Validate and prepare the output directory."""
        if not output_directory:
            raise ValueError("output_directory parameter is required")

        # Expand user path (~) and resolve relative paths
        expanded_path = os.path.expanduser(output_directory)
        resolved_path = os.path.abspath(expanded_path)

        # Create directory if it doesn't exist
        try:
            os.makedirs(resolved_path, exist_ok=True)
        except OSError as e:
            raise ValueError(f"Cannot create directory '{resolved_path}': {e}")

        # Check if directory is writable
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
