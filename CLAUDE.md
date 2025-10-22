# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project is a reimplementation of "Claude Skills" designed to work with local models via Ollama instead of Claude's API. It implements an agentic loop where an LLM is called iteratively with context and tool access.

**Core Concept - The Agentic Loop:**
- An LLM called in a loop
- Maintaining a history of actions in the session (the "context")
- With access to tool calls (read files, write files, bash, etc.)

**Skills Architecture:**
1. Skills are files containing instructions for the LLM
2. On startup, search for available skills and load their descriptions into context
3. Provide the LLM with a mechanism to invoke skills (typically via bash/file reading)
4. When the LLM wants to use a skill, it reads the skill files and executes the instructions

This project uses local models through Ollama. The specific model selection is TBD.

## Development Setup

This project requires Python 3.11+ and Ollama running locally. It uses `uv` for package management.

1. Install dependencies:
   ```bash
   uv pip install -e .
   ```

2. Make sure Ollama is running:
   ```bash
   ollama serve
   ```

3. Pull a model (if needed):
   ```bash
   ollama pull llama3.2
   ```

## Running the Code

Interactive mode:
```bash
skills
# or with specific model
skills --model llama3.2
```

Single message:
```bash
skills --message "your message here"
```

Direct Python execution:
```bash
python -m skills.main
```

## Project Structure

```
skills/
├── __init__.py          # Package initialization
├── agent.py             # Main agent loop orchestration
├── ollama_client.py     # Ollama API integration
├── skill_loader.py      # Skills discovery and loading
├── tools.py             # Tool implementations (file I/O, bash, etc.)
└── main.py              # CLI interface

.skills/                 # Skills directory (auto-discovered)
├── write_hello_world.md
├── analyze_code.md
└── list_python_files.md
```

## Architecture

### Agent Loop (`agent.py`)
The `Agent` class orchestrates the agentic loop:
1. Maintains message history (context)
2. Sends messages + available tools to Ollama
3. Processes LLM responses and tool calls
4. Executes tools and adds results back to context
5. Continues loop until task completion or max iterations

### Tools (`tools.py`)
Available tools that the LLM can invoke:
- `ReadFileTool` - Read file contents
- `WriteFileTool` - Write content to files
- `BashTool` - Execute bash commands (30s timeout)
- `ListDirectoryTool` - List directory contents

Tools are defined with JSON Schema parameters and execute via the `execute_tool()` function.

### Skills System (`skill_loader.py`)
- Skills are Markdown files in `.skills/` directory
- `SkillLoader` discovers skills on startup
- Skill descriptions added to system prompt
- LLM uses `read_file` tool to read skill instructions
- LLM follows instructions in the skill file

### Ollama Integration (`ollama_client.py`)
- Wraps the `ollama` Python client
- Supports chat mode with tool calls
- Model configurable at runtime (default: llama3.2)

### Context Management
Context maintained as a list of messages in the `Agent.messages` attribute:
- System message with tools and skills info
- User messages
- Assistant responses
- Tool call results

## Development Notes

- This project uses `uv` for package management
- The agent loop has a max iteration limit (default: 10) to prevent infinite loops
- Tool execution errors are caught and returned as strings to the LLM
- The CLI uses `rich` for formatted output (panels, markdown, colors)
- Skills are auto-discovered on agent initialization
