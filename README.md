# Phone-a-Friend MCP Server 🧠📞

An AI-to-AI consultation system that enables one AI to "phone a friend" (another AI) for critical thinking, long context reasoning, and complex problem solving via OpenRouter.

## The Problem 🤔

Sometimes an AI encounters complex problems that require:
- **Deep critical thinking** beyond immediate capabilities
- **Long context reasoning** with extensive information
- **Multi-step analysis** that benefits from external perspective
- **Specialized expertise** from different AI models

## The Solution �

Phone-a-Friend MCP Server creates a **two-step consultation process**:

1. **Context + Reasoning**: Package all relevant context and send to external AI for deep analysis
2. **Extract Actionable Insights**: Process the reasoning response into usable format for the primary AI

This enables AI systems to leverage other AI models as "consultants" for complex reasoning tasks.

## Architecture 🏗️

```
Primary AI → Phone-a-Friend MCP → OpenRouter → External AI (GPT-4, Claude, etc.) → Processed Response → Primary AI
```

**Sequential Workflow:**
1. `analyze_context` - Gather and structure all relevant context
2. `get_critical_thinking` - Send context to external AI via OpenRouter for reasoning
3. `extract_actionable_insights` - Process response into actionable format

## When to Use 🎯

**Ideal for:**
- Complex multi-step problems requiring deep analysis
- Situations needing long context reasoning (>100k tokens)
- Cross-domain expertise consultation
- Critical decision-making with high stakes
- Problems requiring multiple perspectives

**Not needed for:**
- Simple factual questions
- Basic reasoning tasks
- Quick responses
- Well-defined procedural tasks

## Installation 🚀

1. Clone the repository:
```bash
git clone https://github.com/abhishekbhakat/phone-a-friend-mcp-server.git
cd phone-a-friend-mcp-server
```

2. Install dependencies:
```bash
uv pip install -e .
```

3. Configure your preferred AI provider:

**OpenRouter (recommended - access to multiple models):**
```bash
export OPENROUTER_API_KEY="your-openrouter-key"
# Model will auto-select based on provider
```

**OpenAI:**
```bash
export OPENAI_API_KEY="your-openai-key"
# Uses latest available model by default
```

**Anthropic:**
```bash
export ANTHROPIC_API_KEY="your-anthropic-key"
# Uses latest available model by default
```

**Google/Gemini:**
```bash
export GOOGLE_API_KEY="your-google-key"  # or GEMINI_API_KEY
# Uses latest available model by default
```

## Usage 💡

### Command Line
```bash
# Start the server
phone-a-friend-mcp-server

# With verbose logging
phone-a-friend-mcp-server -v

# With specific provider (uses optimal model automatically)
phone-a-friend-mcp-server --provider anthropic
phone-a-friend-mcp-server --provider google

# Override with custom model if needed
phone-a-friend-mcp-server --provider anthropic --model "your-preferred-model"
```

### Environment Variables
```bash
# Auto-detects provider based on available API keys
export OPENROUTER_API_KEY="your-openrouter-key"  # Preferred
export OPENAI_API_KEY="your-openai-key"          # Default fallback
export ANTHROPIC_API_KEY="your-anthropic-key"    # Direct Anthropic
export GOOGLE_API_KEY="your-google-key"          # Google/Gemini

# Optional overrides (only if you want to override auto-selection)
export PHONE_A_FRIEND_MODEL="your-preferred-model"
export PHONE_A_FRIEND_PROVIDER="your-preferred-provider"
```

## Model Selection 🤖

The system automatically selects the most capable model for each provider:
- **OpenAI**: Latest reasoning model
- **Anthropic**: Latest Claude model
- **Google**: Latest Gemini Pro model
- **OpenRouter**: Access to latest models from all providers

You can override the auto-selection by setting `PHONE_A_FRIEND_MODEL` environment variable or using the `--model` CLI option.

## Available Tools 🛠️

### phone_a_friend
Consult an external AI for critical thinking and complex reasoning via OpenRouter.

**IMPORTANT:** The external AI is very smart but has NO MEMORY of previous conversations.
The quality of the response depends ENTIRELY on the quality and completeness of the context you provide.

**Parameters:**
- `all_related_context` (required): ALL context directly related to the problem. Include:
  - Background information and history
  - Previous attempts and their outcomes
  - Stakeholders and their perspectives
  - Constraints, requirements, and limitations
  - Current situation and circumstances
  - Any relevant data, metrics, or examples
  - Timeline and deadlines
  - Success criteria and goals

- `any_additional_context` (optional): ANY additional context that might be helpful. Include:
  - Relevant documentation, specifications, or guidelines
  - Industry standards or best practices
  - Similar cases or precedents
  - Technical details or domain knowledge
  - Regulatory or compliance requirements
  - Tools, resources, or technologies available
  - Budget or resource constraints
  - Organizational context or culture

- `task` (required): The specific task or question for the external AI. Be clear about:
  - What exactly you need help with
  - What type of analysis or reasoning you want
  - What format you prefer for the response
  - What decisions need to be made
  - What problems need to be solved

**Example Usage:**
```
all_related_context: "We're a SaaS startup with 50 employees. Our customer churn rate increased from 5% to 12% over the last quarter. We recently changed our pricing model and added new features. Customer support tickets increased 40%. Our main competitors are offering similar features at lower prices."

any_additional_context: "Industry benchmark for SaaS churn is 6-8%. Our pricing increased by 30%. New features include AI analytics and advanced reporting. Customer feedback mentions complexity and cost concerns."

task: "Analyze the churn increase and provide a comprehensive action plan to reduce it back to 5% within 6 months. Include specific strategies, timeline, and success metrics."
```

The system will automatically route this to the most capable AI model available based on your configured provider.

## Claude Desktop Configuration 🖥️

To use Phone-a-Friend MCP server with Claude Desktop, add this configuration to your `claude_desktop_config.json` file:

### Configuration File Location
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Configuration

**Option 1: Using uv (Recommended)**
```json
{
  "mcpServers": {
    "phone-a-friend": {
      "command": "uvx",
      "args": [
        "run",
        "--refresh",
        "phone-a-friend-mcp-server",
      ],
      "env": {
        "OPENROUTER_API_KEY": "your-openrouter-api-key",
        "PHONE_A_FRIEND_MODEL": "anthropic/claude-4-opus"
      }
    }
  }
}
```

### Environment Variables in Configuration

You can configure different AI providers directly in the Claude Desktop config:

```json
{
  "mcpServers": {
    "phone-a-friend": {
      "command": "phone-a-friend-mcp-server",
      "env": {
        "OPENROUTER_API_KEY": "your-openrouter-api-key",
        "PHONE_A_FRIEND_MODEL": "anthropic/claude-4-opus"
      }
    }
  }
}
```

**Alternative Providers:**
```json
{
  "mcpServers": {
    "phone-a-friend-openai": {
      "command": "phone-a-friend-mcp-server",
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key"
      }
    },
    "phone-a-friend-anthropic": {
      "command": "phone-a-friend-mcp-server",
      "env": {
        "ANTHROPIC_API_KEY": "your-anthropic-api-key"
      }
    },
    "phone-a-friend-google": {
      "command": "phone-a-friend-mcp-server",
      "env": {
        "GOOGLE_API_KEY": "your-google-api-key"
      }
    }
  }
}
```

### Setup Steps

1. **Install Phone-a-Friend MCP Server** (see Installation section above)
2. **Open Claude Desktop Settings** → Developer → Edit Config
3. **Add the configuration** (choose one of the options above)
4. **Replace paths and API keys** with your actual values
5. **Restart Claude Desktop**
6. **Look for the 🔨 hammer icon** in the input box to confirm the server is connected

### Troubleshooting

If the server doesn't appear in Claude Desktop:

1. **Check logs**:
   - macOS: `~/Library/Logs/Claude/mcp*.log`
   - Windows: `%APPDATA%\Claude\logs\mcp*.log`

2. **Verify paths** are absolute and correct
3. **Test manually** in terminal:
   ```bash
   phone-a-friend-mcp-server -v
   ```
4. **Restart Claude Desktop** completely
5. **Check API keys** are valid and have sufficient credits

## Development 🔧

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
ruff format .
ruff check .
```

## License 📄

MIT License - see LICENSE file for details.
