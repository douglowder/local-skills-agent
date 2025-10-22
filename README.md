# Local Skills Agent

A local, Ollama-based reimplementation of Claude Skills. This implements an agentic loop where an LLM is called iteratively with context and tool access.

## Core Concept - The Agentic Loop

- An LLM called in a loop
- Maintaining a history of actions in the session (the "context")
- With access to tool calls (read files, write files, bash, etc.)

## Installation

1. Make sure [Ollama](https://ollama.ai/) is installed and running:
   ```bash
   ollama serve
   ```

2. Pull a model (e.g., llama3.2):
   ```bash
   ollama pull llama3.2
   ```

3. Install this package (using uv):
   ```bash
   uv pip install -e .
   ```

## Usage

### Interactive Mode

```bash
skills
```

Or with a specific model:
```bash
skills --model llama3.2
```

### Single Message Mode

```bash
skills --message "List all Python files in this directory"
```

### Commands

In interactive mode, you can use these commands:

- `/help` - Show available commands
- `/reset` - Clear conversation history
- `/models` - List available Ollama models
- `/skills` - List available skills
- `/quit` or `/exit` - Exit the program

## Skills

Skills are markdown files stored in the `.skills/` directory. Each skill contains instructions for the LLM.

### Creating a Skill

Create a `.md` file in the `.skills/` directory:

```markdown
# My Custom Skill

Brief description of what this skill does.

## Instructions

Detailed instructions for the LLM to follow when this skill is invoked.

1. Step one
2. Step two
3. etc.
```

The agent will automatically discover and make skills available to the LLM.

## Architecture

- **Agent Loop** (`skills/agent.py`): Core loop that calls the LLM iteratively
- **Tools** (`skills/tools.py`): File I/O, bash execution, directory listing
- **Skills System** (`skills/skill_loader.py`): Discovery and loading of skill definitions
- **Ollama Client** (`skills/ollama_client.py`): Interface to local Ollama models
- **Context Management**: Built into the agent loop via message history

## Example

```bash
$ skills
Using model: llama3.2
Loaded 3 skill(s)

You: Use the write_hello_world skill to create a hello world program

[Agent uses the read_file tool to read the skill]
[Agent uses the write_file tool to create hello_world.py]
[Agent confirms the file was created]
```

## Development

The project uses Python 3.11+ and requires:
- `ollama` - Python client for Ollama
- `rich` - Terminal formatting and output
