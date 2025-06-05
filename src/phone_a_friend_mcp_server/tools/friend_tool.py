import json
from typing import Any, Dict

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

    This tool sends your problem to a highly capable external AI model via OpenRouter for deep analysis.
    The external AI is very smart but has NO MEMORY of previous conversations, so you must provide
    ALL relevant context in your request.

    IMPORTANT: The quality of the external AI's response depends ENTIRELY on the quality and
    completeness of the context you provide. Include everything the AI needs to understand
    and solve your problem effectively.

    Use this tool when you need:
    - Deep critical thinking beyond your immediate capabilities
    - Long context reasoning with extensive information
    - Multi-step analysis requiring external perspective
    - Complex problem solving that benefits from a fresh viewpoint

    The external AI is intelligent but not knowledgeable about current events, specific
    documentation, or domain-specific information unless you provide it.
    """

    @property
    def name(self) -> str:
        return "phone_a_friend"

    @property
    def description(self) -> str:
        return """🚨 ONLY USE WHEN EXPLICITLY REQUESTED: This tool should ONLY be used when the user specifically asks you to "phone a friend" or requests external AI consultation. Do NOT use this tool automatically or suggest using it unless the user explicitly requests it.

Phone-a-Friend: Consult an external AI for critical thinking and complex reasoning.

This tool sends your problem to a highly capable external AI model for deep analysis.
The external AI is very smart but has NO MEMORY of previous conversations, so you must provide
ALL relevant context in your request.

IMPORTANT: The quality of the external AI's response depends ENTIRELY on the quality and
completeness of the context you provide. Include everything the AI needs to understand
and solve your problem effectively.

Use this tool when you need:
- Deep critical thinking beyond your immediate capabilities
- Long context reasoning with extensive information
- Multi-step analysis requiring external perspective
- Complex problem solving that benefits from a fresh viewpoint

The external AI is intelligent but not knowledgeable about current events, specific
documentation, or domain-specific information unless you provide it."""

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

        # Create master prompt for external AI
        master_prompt = self._create_master_prompt(
            all_related_context,
            any_additional_context,
            task
        )

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
                "task": task
            }

        except Exception as e:
            return {
                "error": str(e),
                "status": "failed",
                "provider": self.config.provider,
                "model": self.config.model,
                "context_length": len(all_related_context + any_additional_context),
                "task": task,
                "master_prompt": master_prompt  # Include for debugging
            }

    def _create_agent(self) -> Agent:
        """Create Pydantic-AI agent with appropriate provider."""
        if self.config.provider == "openrouter":
            # OpenRouter has its own dedicated provider
            provider = OpenRouterProvider(api_key=self.config.api_key)
            model = OpenAIModel(self.config.model, provider=provider)
        elif self.config.provider == "anthropic":
            # Use Anthropic directly
            provider = AnthropicProvider(api_key=self.config.api_key)
            model = AnthropicModel(self.config.model, provider=provider)
        elif self.config.provider == "google":
            # Use Google/Gemini directly
            provider = GoogleProvider(api_key=self.config.api_key)
            model = GoogleModel(self.config.model, provider=provider)
        else:
            # Default to OpenAI
            provider = OpenAIProvider(api_key=self.config.api_key)
            model = OpenAIModel(self.config.model, provider=provider)

        return Agent(model)

    def _create_master_prompt(self, all_related_context: str, any_additional_context: str, task: str) -> str:
        """Create a comprehensive prompt for the external AI."""

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
