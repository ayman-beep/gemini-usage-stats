# AI CLI Tools Information

This directory contains detailed information about the CLI tools supported by the AI CLI Usage Analytics dashboard.

## Supported CLI Tools

### 1. Gemini CLI (Google)

**Official Resources:**
- Documentation: https://ai.google.dev/gemini-api/docs
- Package: `@google/gemini-cli`

**Installation:**
```bash
npm install -g @google/gemini-cli
```

**Data Location:**
- Sessions: `~/.gemini/tmp/`
- Config: `~/.gemini/trustedFolders.json`

**Supported Models:**
| Model | Input | Output | Cached |
|-------|-------|--------|--------|
| gemini-3-pro | $2.00 | $12.00 | $0.20 |
| gemini-3-flash | $0.50 | $3.00 | $0.05 |
| gemini-2.5-pro | $1.25 | $10.00 | $0.125 |
| gemini-2.5-flash | $0.30 | $1.20 | $0.03 |
| gemini-2.5-flash-lite | $0.10 | $0.40 | $0.01 |

---

### 2. Codex CLI (OpenAI)

**Official Resources:**
- GitHub: https://github.com/openai/codex
- Documentation: https://developers.openai.com/codex/cli
- Package: `@openai/codex`

**Description:**
A lightweight, open-source coding agent that runs locally in your terminal. It can read, modify, and execute code on your machine.

**Installation:**
```bash
# npm
npm install -g @openai/codex

# Homebrew
brew install --cask codex

# Binary download from GitHub releases
```

**Authentication:**
```bash
# Sign in with ChatGPT
codex login

# Or use API key
codex login --token YOUR_API_KEY
```

**Data Location:**
- Sessions: `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`
- Config: `~/.codex/config.toml`

**Supported Models (Official Codex CLI Pricing):**

**GPT-5.2 Series:**
| Model | Input | Output | Cached | Primary Strength |
|-------|-------|--------|--------|------------------|
| gpt-5.2 / gpt-5.2-instant | $1.75 | $14.00 | $0.175 | General agentic tasks & fast planning |
| gpt-5.2-thinking | $1.75 | $14.00 | $0.175 | Balanced reasoning for complex logic |
| gpt-5.2-pro | $21.00 | $168.00 | $2.10 | High-stakes architecture & zero-error logic |
| gpt-5.2-codex | $1.75 | $14.00 | $0.175 | Deep codebase migrations & refactoring |

**GPT-5.1 Series:**
| Model | Input | Output | Cached |
|-------|-------|--------|--------|
| gpt-5.1 / gpt-5.1-codex-max | $1.25 | $10.00 | $0.125 |
| gpt-5.1-codex-mini | $0.25 | $2.00 | $0.025 |
| gpt-5-nano | $0.05 | $0.40 | $0.005 |

**Legacy Codex Models:**
| Model | Input | Output | Cached |
|-------|-------|--------|--------|
| gpt-5-codex | $0.50 | $1.50 | $0.025 |
| gpt-5.3-codex | $0.30 | $1.20 | $0.025 |
| gpt-4-codex | $2.00 | $6.00 | $0.50 |

**Other OpenAI Models:**
| Model | Input | Output | Cached |
|-------|-------|--------|--------|
| o3-mini | $1.10 | $4.40 | $0.55 |
| o1 | $15.00 | $60.00 | $7.50 |
| gpt-4o | $2.50 | $10.00 | $1.25 |

**Key Features:**
- Local execution for privacy
- Interactive TUI (Terminal User Interface)
- Non-interactive mode (`codex exec`)
- Session persistence
- Configurable sandbox policies
- MCP (Model Context Protocol) support

**Common Commands:**
```bash
codex                              # Launch interactive TUI
codex "your prompt here"          # Run with initial prompt
codex exec "task description"     # Non-interactive mode
codex resume                       # Resume last session
codex --full-auto "task"          # Fully automated execution
```

---

### 3. Opencode CLI (Anomaly)

**Official Resources:**
- Website: https://opencode.ai
- GitHub: https://github.com/anomalyco/opencode
- Documentation: https://opencode.ai/docs

**Description:**
An open source AI coding agent that provides a terminal-based interface, desktop app, or IDE extension for AI-assisted coding. Multi-provider support (Anthropic, OpenAI, Google, etc.).

**Installation:**
```bash
# Install script (recommended)
curl -fsSL https://opencode.ai/install | bash

# npm
npm install -g opencode-ai

# Homebrew
brew install anomalyco/tap/opencode

# Scoop (Windows)
scoop install opencode
```

**Data Location:**
- Sessions: `~/.local/share/opencode/storage/session/`
- Messages: `~/.local/share/opencode/storage/message/`
- Config: `~/.config/opencode/opencode.json`

**Supported Models (Opencode Zen Pricing):**

**Anthropic Claude Models:**
| Model | Input | Output | Cached |
|-------|-------|--------|--------|
| claude-opus-4-6 / claude-opus-4-5 | $5.00 | $25.00 | $0.50 |
| claude-sonnet-4-5 / claude-sonnet-4 | $3.00 | $15.00 | $0.30 |
| claude-haiku-4-5 | $1.00 | $5.00 | $0.10 |
| claude-opus-4-1 (Legacy) | $15.00 | $75.00 | $1.50 |
| claude-3-7-sonnet | $3.00 | $15.00 | $0.30 |
| claude-3-5-sonnet | $3.00 | $15.00 | $0.30 |
| claude-3-opus | $15.00 | $75.00 | $1.50 |

**Opencode Zen Exclusive Models:**
| Model | Input | Output | Cached |
|-------|-------|--------|--------|
| kimi-k2-5 / kimi-k2 | $0.60 | $3.00 | $0.15 |
| glm-4-7 / glm-4-6 | $0.60 | $2.20 | $0.11 |
| minimax-m2-5 / minimax-m2-1 | $0.30 | $1.20 | $0.03 |

**Key Features:**
- Multi-provider LLM support (not locked to single provider)
- Dual agent modes (Build/Plan)
- LSP (Language Server Protocol) integration
- MCP (Model Context Protocol) support
- Session management with undo/redo
- Desktop app and IDE extensions available

**Common Commands:**
```bash
opencode                           # Start TUI
opencode run "your question"      # Non-interactive
opencode stats                     # Show usage statistics
/init                              # Initialize project (in TUI)
/undo                              # Undo last changes
/connect                           # Configure provider API keys
```

**Environment Variables:**
- `ANTHROPIC_API_KEY` - For Claude models
- `OPENAI_API_KEY` - For OpenAI models
- `GOOGLE_API_KEY` - For Gemini models
- `OPENCODE_CONFIG` - Custom config file path

---

## Pricing Notes

All pricing is shown in USD per 1 million tokens as of January 2026.

- **Input tokens**: Tokens sent to the API (your prompts + context)
- **Output tokens**: Tokens generated by the model (responses)
- **Cached tokens**: Tokens that were cached from previous requests (discounted rate)

## Data Privacy

All CLI tools store session data locally on your machine:
- Gemini: `~/.gemini/`
- Codex: `~/.codex/`
- Opencode: `~/.local/share/opencode/`

This dashboard only reads these local files and does not send any data to external servers.
