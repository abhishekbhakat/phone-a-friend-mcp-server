import os
from typing import Any, Dict

import aiofiles

from phone_a_friend_mcp_server.tools.base_tools import BaseTool


class FaxAFriendTool(BaseTool):
    """
    Fax-a-Friend: Generate a master prompt file for manual AI consultation.

    ⚠️  ONLY USE WHEN EXPLICITLY REQUESTED BY USER ⚠️

    This tool creates a comprehensive master prompt and saves it to a file for manual
    copy-paste into external AI interfaces. It uses the same prompt structure as the
    phone_a_friend tool but requires manual intervention to get the AI response.

    Use this tool when:
    - The automated phone_a_friend tool is unavailable
    - You want to manually control which AI service to use
    - You need to consult multiple AI services with the same prompt
    - API access is limited or unavailable

    The tool generates a file that you can manually copy and paste into any AI interface.
    """

    @property
    def name(self) -> str:
        return "fax_a_friend"

    @property
    def description(self) -> str:
        return """🚨 ONLY USE WHEN EXPLICITLY REQUESTED: This tool should ONLY be used when the user specifically asks you to "fax a friend" or requests manual AI consultation. Do NOT use this tool automatically or suggest using it unless the user explicitly requests it.

Fax-a-Friend: Generate a master prompt file for manual AI consultation.

This tool creates a comprehensive master prompt and saves it to 'fax_a_friend.md' for manual
copy-paste into external AI interfaces. It uses the same prompt structure as the
phone_a_friend tool but requires manual intervention to get the AI response.

Use this tool when:
- The automated phone_a_friend tool is unavailable
- You want to manually control which AI service to use
- You need to consult multiple AI services with the same prompt
- API access is limited or unavailable

After running this tool, you'll need to manually copy the generated prompt and paste it
into your preferred AI interface."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "all_related_context": {
                    "type": "string",
                    "description": """ALL context directly related to the problem. Include:
- Background information and history
- Previous attempts and their outcomes
- Stakeholders and their perspectives
- Constraints, requirements, and limitations
- Current situation and circumstances
- Any relevant data, metrics, or examples
- Timeline and deadlines
- Success criteria and goals

Be comprehensive - the external AI has no memory and needs complete context."""
                },
                "any_additional_context": {
                    "type": "string",
                    "description": """ANY additional context that might be helpful. Include:
- Relevant documentation, specifications, or guidelines
- Industry standards or best practices
- Similar cases or precedents
- Technical details or domain knowledge
- Regulatory or compliance requirements
- Tools, resources, or technologies available
- Budget or resource constraints
- Organizational context or culture

The external AI is smart but not knowledgeable - provide all relevant information."""
                },
                "task": {
                    "type": "string",
                    "description": """The specific task or question for the external AI. Be clear and specific about:
- What exactly you need help with
- What type of analysis or reasoning you want
- What format you prefer for the response
- What decisions need to be made
- What problems need to be solved

Examples:
- "Analyze this situation and recommend the best approach"
- "Help me think through the pros and cons of each option"
- "Design a step-by-step plan to solve this problem"
- "Identify potential risks and mitigation strategies"
- "Provide a critical analysis of this proposal"""
                }
            },
            "required": ["all_related_context", "task"]
        }

    async def run(self, **kwargs) -> Dict[str, Any]:
        all_related_context = kwargs.get("all_related_context", "")
        any_additional_context = kwargs.get("any_additional_context", "")
        task = kwargs.get("task", "")

        # Create master prompt using the same logic as phone_a_friend
        master_prompt = self._create_master_prompt(
            all_related_context,
            any_additional_context,
            task
        )

        try:
            # Write to fax_a_friend.md in current working directory
            file_path = "fax_a_friend.md"
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(master_prompt)

            # Get absolute path for user reference
            abs_path = os.path.abspath(file_path)

            return {
                "status": "success",
                "file_path": abs_path,
                "file_name": "fax_a_friend.md",
                "prompt_length": len(master_prompt),
                "context_length": len(all_related_context + any_additional_context),
                "task": task,
                "instructions": self._get_manual_workflow_instructions(abs_path)
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "file_path": "fax_a_friend.md",
                "context_length": len(all_related_context + any_additional_context),
                "task": task
            }

    def _create_master_prompt(self, all_related_context: str, any_additional_context: str, task: str) -> str:
        """Create a comprehensive prompt for the external AI (same logic as phone_a_friend)."""

        prompt_parts = [
            "You are a highly capable AI assistant being consulted for critical thinking and complex reasoning.",
            "You have no memory of previous conversations, so all necessary context is provided below.",
            "",
            "=== TASK ===",
            task,
            "",
            "=== ALL RELATED CONTEXT ===",
            all_related_context,
        ]

        if any_additional_context.strip():
            prompt_parts.extend([
                "",
                "=== ADDITIONAL CONTEXT ===",
                any_additional_context,
            ])

        prompt_parts.extend([
            "",
            "=== INSTRUCTIONS ===",
            "- Analyze the situation thoroughly using the provided context",
            "- Think step-by-step and show your reasoning process",
            "- Consider multiple perspectives and potential solutions",
            "- Identify key insights, risks, and opportunities",
            "- Provide actionable recommendations based on your analysis",
            "- Be specific and practical in your response",
            "",
            "Please provide your analysis and recommendations:"
        ])

        return "\n".join(prompt_parts)

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
