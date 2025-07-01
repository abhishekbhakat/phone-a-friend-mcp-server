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
Primary AI → Phone-a-Friend MCP → OpenRouter → External AI (O3, Claude, etc.) → Processed Response → Primary AI
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

## Quick Start ⚡

Configure your MCP client (e.g., Claude Desktop) using the JSON block below—no cloning or manual installation required.
The `uv` runner will automatically download and execute the server package if it isn't present.

Add the following JSON configuration to your MCP client and replace `<YOUR_API_KEY>` with your key:

```json
{
  "mcpServers": {
    "phone-a-friend": {
      "command": "uvx",
      "args": [
        "phone-a-friend-mcp-server",
        "--provider", "openai",
        "--api-key", "<YOUR_API_KEY>"
      ]
    }
  }
}
```
> That's it! You can now use the `phone_a_friend` tool in any compatible client. For more options, see the Advanced Configuration section.

## Available Tools 🛠️

### phone_a_friend
📞 Consult external AI for critical thinking and complex reasoning. Makes API calls to get responses.

### fax_a_friend
📠 Generate master prompt file for manual AI consultation. Creates file for copy-paste workflow.

**Parameters**

*phone_a_friend*

- `all_related_context` (required): General, non-code context such as constraints, tracebacks, or high-level requirements.
- `file_list` (required): Array of file paths or glob patterns. **Just pass the paths** – the server automatically reads those files (skips anything in `.gitignore` or non-text/binary) and builds the full code context for the external AI.
- `task` (required): A clear, specific description of what you want the external AI to do.

*fax_a_friend*

- `all_related_context` (required): Same as above.
- `file_list` (required): Same as above.
- `task` (required): Same as above.
- `output_directory` (required): Directory where the generated `fax_a_friend.md` master prompt file will be saved.

## Advanced Configuration 🔧

This section covers all configuration options, including environment variables, CLI flags, and model selection.

### Providers and API Keys

The server can be configured via CLI flags or environment variables.

| Provider | CLI Flag | Environment Variable |
| :--- | :--- | :--- |
| OpenAI | `--provider openai` | `OPENAI_API_KEY` |
| OpenRouter | `--provider openrouter` | `OPENROUTER_API_KEY` |
| Anthropic | `--provider anthropic` | `ANTHROPIC_API_KEY` |
| Google | `--provider google` | `GOOGLE_API_KEY` |

**CLI Example:**
```bash
phone-a-friend-mcp-server --provider openai --api-key "sk-..."
```

**Environment Variable Example:**
```bash
export OPENAI_API_KEY="sk-..."
phone-a-friend-mcp-server
```

### Model Selection

You can override the default model for each provider.

| Provider | Default Model |
| :--- | :--- |
| **OpenAI** | `o3` |
| **Anthropic** | `Claude 4 Opus` |
| **Google** | `Gemini 2.5 Pro Preview 05-06` |
| **OpenRouter**| `anthropic/claude-4-opus` |

**Override with CLI:**
```bash
phone-a-friend-mcp-server --model "o3"
```

**Override with Environment Variable:**
```bash
export PHONE_A_FRIEND_MODEL="o3"
```

### Additional Options

| Feature | CLI Flag | Environment Variable | Default |
| :--- | :--- | :--- | :--- |
| **Temperature** | `--temperature 0.5` | `PHONE_A_FRIEND_TEMPERATURE` | `0.4` |
| **Base URL** | `--base-url ...` | `PHONE_A_FRIEND_BASE_URL` | Provider default |

## Use Cases 🎯

1. In-depth Reasoning for Vibe Coding
2. For complex algorithms, data structures, or mathematical computations
3. Frontend Development with React, Vue, CSS, or modern frontend frameworks

## License 📄

MIT License - see LICENSE file for details.
