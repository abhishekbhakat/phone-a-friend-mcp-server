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

3. Configure API access (choose one method):

**Option A: Environment Variables**
```bash
export OPENROUTER_API_KEY="your-openrouter-key"
# OR
export OPENAI_API_KEY="your-openai-key"
# OR
export ANTHROPIC_API_KEY="your-anthropic-key"
# OR
export GOOGLE_API_KEY="your-google-key"
```

**Option B: CLI Arguments**
```bash
phone-a-friend-mcp-server --api-key "your-api-key" --provider openai
```

## Usage 💡

### Command Line Options
```bash

# Custom base URL (if needed)
phone-a-friend-mcp-server --base-url "https://custom-api.example.com"

# Temperature control (0.0 = deterministic, 2.0 = very creative)
phone-a-friend-mcp-server --temperature 0.4

# Combined example
phone-a-friend-mcp-server --api-key "sk-..." --provider openai --model "o3" -v
```

### Environment Variables (Optional)
```bash

# Optional model overrides
export PHONE_A_FRIEND_MODEL="your-preferred-model"
export PHONE_A_FRIEND_PROVIDER="your-preferred-provider"
export PHONE_A_FRIEND_BASE_URL="https://custom-api.example.com"

# Temperature control (0.0-2.0, where 0.0 = deterministic, 2.0 = very creative)
export PHONE_A_FRIEND_TEMPERATURE=0.4
```

## Model Selection 🤖

Default reasoning models to be selected:
- **OpenAI**: o3
- **Anthropic**: Claude 4 Opus
- **Google**: Gemini 2.5 Pro Preview 05-06 (automatically set temperature to 0.0)
- **OpenRouter**: For other models like Deepseek or Qwen

You can override the auto-selection by setting `PHONE_A_FRIEND_MODEL` environment variable or using the `--model` CLI option.

## Available Tools 🛠️

### phone_a_friend
📞 Consult external AI for critical thinking and complex reasoning. Makes API calls to get responses.

### fax_a_friend
📠 Generate master prompt file for manual AI consultation. Creates file for copy-paste workflow.

**Parameters (both tools):**
- `all_related_context` (required): All context related to the problem
- `any_additional_context` (optional): Additional helpful context
- `task` (required): Specific task or question for the AI


## Use Cases 🎯

1. In-depth Reasoning for Vibe Coding
2. For complex algorithms, data structures, or mathematical computations
3. Frontend Development with React, Vue, CSS, or modern frontend frameworks

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
        "--refresh",
        "phone-a-friend-mcp-server",
      ],
      "env": {
        "OPENROUTER_API_KEY": "your-openrouter-api-key",
        "PHONE_A_FRIEND_MODEL": "anthropic/claude-4-opus",
        "PHONE_A_FRIEND_TEMPERATURE": "0.4"
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
        "PHONE_A_FRIEND_MODEL": "anthropic/claude-4-opus",
        "PHONE_A_FRIEND_TEMPERATURE": "0.4"
      }
    }
  }
}
```

## License 📄

MIT License - see LICENSE file for details.
