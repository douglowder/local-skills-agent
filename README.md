# Local Skills Agent

A local, Ollama-based reimplementation of Claude Skills. This implements an agentic loop where an LLM is called iteratively with context and tool access.

## Core Concept - The Agentic Loop

- An LLM called in a loop
- Maintaining a history of actions in the session (the "context")
- With access to tool calls (read files, write files, bash, etc.)

## Model Recommendations

**✅ Recommended Models** (good at tool calling, complete tasks reliably):
- `gpt-oss:20b` - **Excellent choice!** Clean output, reliable tool calling, follows instructions precisely
- `llama3.1:8b-instruct-q4_K_M` - Fast, reliable, excellent tool calling
- `llama3.2:3b` - Lightweight, good for simple tasks
- `qwen2.5-coder:32b` - Strong coding abilities
- `mistral-small:24b` - Excellent reasoning with good tool calling

**❌ Not Recommended** (reasoning models that produce excessive verbose output):
- `qwen3:30b` - Reasoning model, produces 100+ lines of thought per action
- `deepseek-r1:*` - Reasoning model, fails to complete agentic workflows
- `qwq:latest` - Reasoning model, too verbose for tool calling

**Why reasoning models fail:** They're designed to show extensive chain-of-thought reasoning, which causes them to "think themselves into a corner" and fail to make tool calls, preventing task completion.

## Installation

1. Make sure [Ollama](https://ollama.ai/) is installed and running:
   ```bash
   ollama serve
   ```

2. Pull a recommended model:
   ```bash
   ollama pull gpt-oss:20b
   # Or: ollama pull llama3.1:8b-instruct-q4_K_M
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

### Advanced Options

```bash
# Specify model
skills --model llama3.1:8b-instruct-q4_K_M

# Adjust max iterations (default: 20)
skills --max-iterations 30 --message "Complex multi-step task"

# Use custom skills directory
skills --skills-dir ./my-skills
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

### Built-in Skills

The system includes several built-in skills:

- **`write_hello_world`** - Creates a simple Hello World program
- **`analyze_code`** - Quick code analysis (delegates to code_quality_analyzer)
- **`code_quality_analyzer`** - Comprehensive code quality analysis with industry benchmarks
- **`technical_documentation_generator`** - Generates technical documentation
- **`readme_generator`** - Generates professional README.md files
- **`skill_creator`** - 🌟 **The crown jewel** - Creates new skills! Makes the system self-extending

### Using the Skill Creator

The most powerful feature: the agent can create new skills for itself!

```bash
skills --message "Create a skill that checks for security vulnerabilities in Python code"
```

The agent will:
1. Read the `skill_creator.md` instructions
2. Create a new skill file with proper structure
3. Make it immediately available for use

### Creating Skills Manually

Create a `.md` file in the `.skills/` directory:

```markdown
# My Custom Skill

Brief description of what this skill does.

## Purpose

Explain when this skill should be used and what it does.

## Instructions

Detailed step-by-step instructions for the LLM to follow:

### 1. First Step
Use specific tool calls...

### 2. Second Step
Process the data...

### 3. Final Step
Generate output...

## Tools Used

- read_file: What it's used for
- write_file: What it's used for
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
