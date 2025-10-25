# Local Skills Agent

> **A self-extending AI agent system that runs entirely on local infrastructure with zero API costs**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-80%20passing-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Local Skills Agent** is an agentic AI system powered by [Ollama](https://ollama.ai/) that can autonomously create and extend its own capabilities. Built as a local-first reimplementation of Claude Skills, it runs entirely on your hardware with no external API dependencies.

## ✨ What Makes This Special

### 🎯 Self-Extending Architecture
The **crown jewel** is the `skill_creator` meta-skill that enables the agent to create new skills from natural language descriptions. The agent literally writes code that extends itself.

```bash
# Ask the agent to create a new capability
$ skills --message "Create a skill that generates git commit messages"

# The agent creates .skills/git_commit_generator.md
# Now use it immediately - no restart needed
$ skills --message "Generate a commit message for my staged changes"
```

### 🔒 100% Local & Private
- **Zero API costs** - runs on your hardware forever
- **Complete data privacy** - nothing leaves your machine
- **No vendor lock-in** - open source, works with any Ollama model
- **Offline capable** - works without internet connection

### 🧩 Composable Skills System
Skills automatically discover and invoke each other to complete complex workflows:

```bash
# One request triggers multiple skills working together
$ skills --message "Analyze demo_code.py and generate tests for it"

# Agent automatically:
# 1. Uses code_quality_analyzer (reads industry benchmarks)
# 2. Finds code quality issues
# 3. Uses test_generator
# 4. Creates comprehensive test suite
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Ollama** - [Install](https://ollama.ai/)
- **uv** (recommended) or pip

### Installation (2 minutes)

```bash
# 1. Clone the repository
git clone https://github.com/ArneJanning/local-skills-agent.git
cd local-skills-agent

# 2. Start Ollama (in a separate terminal)
ollama serve

# 3. Pull recommended model
ollama pull gpt-oss:20b

# 4. Install the package
uv pip install -e .
# or: pip install -e .

# 5. Run it!
skills
```

### Your First Interaction

```bash
$ skills

You: What can you do?
Agent: [Lists 8 available skills including skill_creator]

You: Create a skill that checks if Python imports are properly sorted
Agent: [Creates .skills/import_checker.md]

You: Check the imports in my main.py file
Agent: [Uses the newly created skill immediately]
```

**That's it!** You now have a self-extending AI agent running locally.

---

## 📚 Table of Contents

- [Core Concepts](#-core-concepts)
- [Built-in Skills](#-built-in-skills)
- [Usage Guide](#-usage-guide)
- [Model Recommendations](#-model-recommendations)
- [Architecture](#-architecture)
- [Creating Skills](#-creating-skills)
- [API Reference](#-api-reference)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)
- [Contributing](#-contributing)

---

## 💡 Core Concepts

### The Agentic Loop

At its core, this is an **agentic loop** - an LLM called iteratively with:
- **Context** - Full conversation history maintained
- **Tools** - File I/O, bash execution, directory operations
- **Skills** - Reusable instruction sets the LLM can discover and follow

```
┌─────────────────────────────────────┐
│  User Request                       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Agent Loop                         │
│  • Maintains conversation context   │
│  • Calls LLM with tools + skills    │
│  • Executes tool calls              │
│  • Continues until task complete    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Tools Execute                      │
│  • read_file                        │
│  • write_file                       │
│  • bash (30s timeout)               │
│  • list_directory                   │
└─────────────────────────────────────┘
```

### Skills System

**Skills are markdown files** in `.skills/` that contain step-by-step instructions:

```markdown
# My Custom Skill

## Purpose
What this skill does and when to use it

## Instructions
1. Use read_file to load the target
2. Process the data
3. Use write_file to save results
```

The agent:
1. **Auto-discovers** all `.md` files in `.skills/` at startup
2. **Pattern-matches** user requests to skill descriptions
3. **Reads the full skill** for detailed instructions
4. **Executes the workflow** using available tools

### Progressive Disclosure

Complex skills can have supporting resources:

```
.skills/
├── code_quality_analyzer.md          # Main skill
└── code_quality_analyzer/            # Supporting files
    ├── benchmarks/
    │   └── industry_standards.json   # Real data
    ├── scripts/
    │   └── analyzer.py               # Helper scripts
    └── templates/
        └── report_template.md        # Output formats
```

The agent reads these **only when needed**, keeping the initial context small.

### The Meta-Programming Loop

The `skill_creator` skill creates new skills:

```
User: "Create a skill for X"
  ↓
Agent reads skill_creator.md
  ↓
Agent writes .skills/new_skill.md
  ↓
Skill auto-discovered immediately
  ↓
Agent can now use it!
  ↓
System extended 🎉
```

---

## 🎯 Built-in Skills

The system ships with 8 foundational skills:

| Skill | Description | Type |
|-------|-------------|------|
| **skill_creator** 👑 | Creates new skills from natural language | Meta-skill |
| **code_quality_analyzer** | Comprehensive analysis with industry benchmarks | Multi-file |
| **readme_generator** | Generates professional README.md files | Generator |
| **test_generator** | Creates pytest test stubs for functions | Generator |
| **technical_documentation_generator** | Creates comprehensive technical docs | Generator |
| **write_hello_world** | Simple hello world program creator | Example |
| **analyze_code** | Quick analysis (delegates to quality analyzer) | Delegator |
| **list_python_files** | Finds all Python files in directory | Utility |

### Skill Highlights

#### 🌟 skill_creator (The Crown Jewel)

Creates properly formatted skills with templates, best practices, and immediate availability.

**Example:**
```bash
You: Create a skill that analyzes SQL queries for performance issues
Agent: [Creates .skills/sql_analyzer.md with proper structure]
You: Analyze this query: SELECT * FROM users WHERE email LIKE '%@%'
Agent: [Uses the newly created skill to analyze the query]
```

#### 📊 code_quality_analyzer (Multi-file Skill)

Analyzes Python code against real industry standards (SEI/IEEE benchmarks).

**Features:**
- Cyclomatic complexity analysis
- Maintainability index calculation
- Actual benchmark data from `.skills/code_quality_analyzer/benchmarks/`
- Formatted reports with recommendations

**Example:**
```bash
You: Analyze my_module.py for code quality
Agent: [Reads industry_standards.json, analyzes code, generates detailed report]
```

#### 🧪 test_generator

Generates pytest test stubs by analyzing function signatures.

**Example:**
```bash
You: Generate tests for utils.py
Agent: [Creates tests/test_utils.py with test stubs for all public functions]
```

---

## 📖 Usage Guide

### Interactive Mode

The primary way to use the agent:

```bash
$ skills

╔═══════════════════════════════════════╗
║  Local Skills Agent                   ║
║  Ollama-powered agentic loop          ║
╚═══════════════════════════════════════╝

✓ Using model: gpt-oss:20b
✓ Skills directory: .skills
✓ Loaded 8 skill(s)

You: _
```

**Available Commands:**
- `/help` - Show available commands
- `/reset` - Clear conversation history
- `/models` - List available Ollama models
- `/skills` - Show all loaded skills
- `/quit` or `/exit` - Exit the program

### Single Message Mode

For one-off tasks or scripting:

```bash
# Quick task
skills --message "List all Python files in this directory"

# Create a skill
skills --message "Create a skill that validates JSON files"

# Complex workflow
skills --message "Analyze all .py files and generate a quality report"
```

### Advanced Options

```bash
# Specify model
skills --model llama3.1:8b-instruct-q4_K_M

# Adjust max iterations for complex tasks
skills --max-iterations 30 --message "Complex multi-step workflow"

# Use custom skills directory
skills --skills-dir ./my-custom-skills

# Combine options
skills --model gpt-oss:20b --max-iterations 25 --skills-dir ./project-skills
```

### Workflow Examples

#### Example 1: Complete Code Quality Pipeline

```bash
You: Analyze all Python files in src/, generate a quality report,
     and create tests for any functions with complexity > 10

# Agent automatically:
# 1. Uses list_python_files to find all .py files
# 2. Uses code_quality_analyzer on each file
# 3. Identifies high-complexity functions
# 4. Uses test_generator to create test stubs
# 5. Generates comprehensive report
```

#### Example 2: Self-Extension for New Domain

```bash
You: Create a skill that analyzes Dockerfile best practices

# Agent creates the skill

You: Analyze my Dockerfile

# Agent uses the newly created skill immediately
```

#### Example 3: Documentation Pipeline

```bash
You: Generate README, technical docs, and API documentation for this project

# Agent:
# 1. Uses readme_generator
# 2. Uses technical_documentation_generator
# 3. Analyzes code structure for API docs
# 4. Creates all three documents
```

---

## 🎯 Model Recommendations

### ✅ Recommended Models

Models that excel at tool calling and complete tasks reliably:

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **gpt-oss:20b** ⭐ | 20B | Medium | Excellent | Production use, best overall |
| **llama3.1:8b-instruct-q4_K_M** | 8B | Fast | Very Good | Development, quick tasks |
| **qwen2.5-coder:32b** | 32B | Slow | Excellent | Complex coding tasks |
| **mistral-small:24b** | 24B | Medium | Very Good | Balanced performance |
| **llama3.2:3b** | 3B | Very Fast | Good | Simple tasks, testing |

**Installation:**
```bash
# Recommended for production
ollama pull gpt-oss:20b

# Good for development
ollama pull llama3.1:8b-instruct-q4_K_M
```

### ❌ Not Recommended

**Reasoning models** that produce excessive verbose output:

- ❌ `qwen3:30b` - Produces 100+ lines of reasoning per action
- ❌ `deepseek-r1:*` - Fails to complete agentic workflows
- ❌ `qwq:latest` - Too verbose for tool calling

**Why they fail:** Reasoning models are designed to show extensive chain-of-thought thinking. This causes them to "think themselves into a corner" and stop making tool calls, preventing task completion.

### Model Selection Guide

```bash
# Quick tasks, development
skills --model llama3.2:3b

# Production workflows
skills --model gpt-oss:20b

# Complex coding tasks
skills --model qwen2.5-coder:32b

# Need more iterations for complex tasks
skills --model gpt-oss:20b --max-iterations 30
```

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────┐
│              User Interface (CLI)               │
│              skills/main.py                     │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│           Agent Loop (agent.py)                 │
│  • Context Management (message history)         │
│  • LLM orchestration                            │
│  • Tool call processing                         │
│  • Max iterations: 20 (configurable)            │
└──────────┬──────────────────────────────────────┘
           │
           ├──────────────┐
           │              │
           ▼              ▼
┌──────────────────┐  ┌──────────────────────┐
│ Ollama Client    │  │ Skills Loader        │
│ (ollama_client)  │  │ (skill_loader.py)    │
│                  │  │                      │
│ • Model mgmt     │  │ • Auto-discovery     │
│ • Chat API       │  │ • Progressive load   │
│ • Tool calling   │  │ • Skill cache        │
└──────────────────┘  └──────────────────────┘
           │                      │
           │                      │
           ▼                      ▼
┌─────────────────────────────────────────────────┐
│              Tool Execution (tools.py)          │
│  ┌───────────────────────────────────────────┐  │
│  │ • read_file    • write_file              │  │
│  │ • bash (30s timeout) • list_directory    │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### Component Details

#### Agent (`skills/agent.py`)

The core orchestrator:

```python
class Agent:
    def __init__(self, model="gpt-oss:20b", skills_dir=".skills", max_iterations=20):
        # Initialize Ollama client
        # Load skills
        # Set up tools

    def run(self, user_message: str):
        # Add message to context
        # Loop: Call LLM → Execute tools → Add results to context
        # Continue until complete or max_iterations
```

**Key Features:**
- Maintains full conversation context
- Handles tool call execution
- Provides progress feedback via Rich UI
- Configurable iteration limits

#### Skills Loader (`skills/skill_loader.py`)

Auto-discovers and manages skills:

```python
class SkillLoader:
    def discover_skills(self):
        # Find all .md files in skills_dir
        # Parse name and description
        # Build skill index

    def get_skills_summary(self) -> str:
        # Return formatted skill list for system prompt
```

**Features:**
- Automatic discovery on startup
- Lazy loading of skill content
- Caching for performance
- Support for multi-file skills

#### Ollama Client (`skills/ollama_client.py`)

Interfaces with local Ollama:

```python
class OllamaClient:
    def chat(self, messages, tools):
        # Call Ollama chat API
        # Handle tool calling format
        # Return response with tool calls
```

#### Tools (`skills/tools.py`)

Available tools for the agent:

```python
class ReadFileTool:
    name = "read_file"
    description = "Read the contents of a file"
    parameters = {"path": "str"}

class WriteFileTool:
    name = "write_file"
    description = "Write content to a file"
    parameters = {"path": "str", "content": "str"}

class BashTool:
    name = "bash"
    description = "Execute bash commands (30s timeout)"
    parameters = {"command": "str"}

class ListDirectoryTool:
    name = "list_directory"
    description = "List directory contents"
    parameters = {"path": "str"}
```

### Data Flow

```
1. User Input
   ↓
2. Added to messages context
   ↓
3. Send to LLM (with tools + skill descriptions)
   ↓
4. LLM returns response (potentially with tool calls)
   ↓
5. Execute tool calls
   ↓
6. Add tool results to context
   ↓
7. Loop back to step 3 until:
   - Task complete (no more tool calls)
   - Max iterations reached
   - Error occurs
   ↓
8. Return final response to user
```

---

## 🛠️ Creating Skills

### Quick Start

Create a file in `.skills/` with a `.md` extension:

```bash
# Create a new skill
cat > .skills/my_skill.md << 'EOF'
# My Custom Skill

**Brief one-line description**

## Purpose

This skill does X when the user wants Y.

## Instructions

### 1. First Step
Use tool_name to accomplish...

### 2. Second Step
Process the results...

### 3. Final Step
Generate output...

## Tools Used

- read_file: For reading files
- write_file: For creating output
EOF

# The skill is immediately available!
skills --message "/skills"
```

### Skill Template

```markdown
# Skill Name

**One-line description of what this skill does**

## Purpose

Detailed explanation of:
- What this skill accomplishes
- When it should be used
- What makes it different from other skills

## Instructions

Step-by-step instructions for the LLM to follow:

### 1. Preparation
- Gather required information
- Validate inputs
- Set up any needed context

### 2. Main Processing
- Detailed steps
- Specific tool calls
- Error handling

### 3. Output Generation
- Format results
- Save or display
- Confirm completion

## Tools Used

- tool_name: Explanation of how it's used
- tool_name: Explanation of how it's used

## Example Usage

**User:** "Example user request"
**Agent:** [What the agent does]
**Result:** [Expected outcome]

## Notes

- Special considerations
- Edge cases
- Limitations
```

### Multi-File Skills

For complex skills with supporting resources:

```bash
.skills/
├── my_complex_skill.md           # Main skill file
└── my_complex_skill/             # Supporting resources
    ├── scripts/
    │   └── processor.py          # Helper scripts
    ├── data/
    │   └── reference_data.json   # Data files
    └── templates/
        └── output_template.md    # Output formats
```

**Important:** The main skill file must instruct the agent to read supporting files:

```markdown
## Instructions

### 1. Load Reference Data (REQUIRED FIRST STEP)

**IMPORTANT:** Before proceeding, read the reference data:
```
read_file(".skills/my_complex_skill/data/reference_data.json")
```

This ensures the data is loaded early in the skill execution.
```

### Skill Best Practices

#### ✅ DO:

- **Be explicit** about which tools to use and when
- **Number your steps** for clarity
- **Include examples** of expected inputs/outputs
- **Handle edge cases** in your instructions
- **Use clear purpose statements** so the agent knows when to invoke the skill
- **Test with gpt-oss:20b** before committing

#### ❌ DON'T:

- Assume the agent has context it doesn't have
- Use vague instructions like "process the data"
- Forget to specify file paths explicitly
- Make skills too generic (be specific about the use case)
- Skip error handling guidance

### Example: Creating a Real Skill

Let's create a skill that validates JSON files:

```markdown
# JSON Validator

**Validate JSON files for syntax errors and schema compliance**

## Purpose

This skill validates JSON files when the user needs to check JSON syntax,
format, or compliance with expected schemas.

## Instructions

### 1. Identify Target File

Ask the user which JSON file to validate, or use context from their request.
The file path should be relative to the current directory.

### 2. Read the JSON File

Use read_file to load the file contents:
```
read_file("path/to/file.json")
```

### 3. Validate Syntax

Attempt to parse the JSON. If parsing fails, report the specific error:
- Line number where error occurred
- Type of error (unclosed bracket, invalid syntax, etc.)
- Suggested fix if possible

### 4. Check Structure (if valid)

If syntax is valid, analyze structure:
- Count of top-level keys
- Data types present
- Nesting depth
- Array lengths

### 5. Report Results

Provide a clear report:

**If invalid:**
```
❌ JSON Validation Failed
File: path/to/file.json
Error: Unexpected token at line 15
Issue: Missing closing bracket
```

**If valid:**
```
✅ JSON Valid
File: path/to/file.json
Structure:
- 12 top-level keys
- Maximum nesting depth: 3 levels
- Contains: objects, arrays, strings, numbers
```

## Tools Used

- read_file: Load the JSON file contents
- bash: (optional) Use `jq` for advanced validation if available

## Example Usage

**User:** "Validate config.json"
**Agent:** Reads config.json, parses it, reports results

**User:** "Is my data.json file valid?"
**Agent:** Validates and provides detailed structural analysis
```

Save this to `.skills/json_validator.md` and it's immediately available!

---

## 📚 API Reference

### Command Line Interface

```bash
usage: skills [-h] [--model MODEL] [--skills-dir SKILLS_DIR]
              [--message MESSAGE] [--max-iterations MAX_ITERATIONS]

Local Skills Agent - Ollama-powered agentic loop

options:
  -h, --help            Show help message and exit

  --model MODEL, -m MODEL
                        Ollama model to use (default: gpt-oss:20b)

  --skills-dir SKILLS_DIR, -s SKILLS_DIR
                        Directory containing skill definitions (default: .skills)

  --message MESSAGE     Single message to send (non-interactive mode)

  --max-iterations MAX_ITERATIONS
                        Maximum number of agent loop iterations (default: 20)
```

### Python API

```python
from skills.agent import Agent

# Create agent
agent = Agent(
    model="gpt-oss:20b",
    skills_dir=".skills",
    max_iterations=20
)

# Run a task
agent.run("Analyze demo.py for code quality issues")

# Reset conversation
agent.reset()

# Get available models
models = agent.get_available_models()
```

### Tool Specifications

#### read_file

```json
{
  "name": "read_file",
  "description": "Read the contents of a file",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Path to the file to read"
      }
    },
    "required": ["path"]
  }
}
```

#### write_file

```json
{
  "name": "write_file",
  "description": "Write content to a file",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Path where file should be written"
      },
      "content": {
        "type": "string",
        "description": "Content to write to the file"
      }
    },
    "required": ["path", "content"]
  }
}
```

#### bash

```json
{
  "name": "bash",
  "description": "Execute bash commands (30 second timeout)",
  "parameters": {
    "type": "object",
    "properties": {
      "command": {
        "type": "string",
        "description": "The bash command to execute"
      }
    },
    "required": ["command"]
  }
}
```

#### list_directory

```json
{
  "name": "list_directory",
  "description": "List contents of a directory",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Path to directory to list"
      }
    },
    "required": ["path"]
  }
}
```

---

## 🔧 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/ArneJanning/local-skills-agent.git
cd local-skills-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
uv pip install -e ".[dev]"
# or: pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=skills --cov-report=html

# Run specific test file
pytest tests/test_agent.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_agent.py::TestAgent::test_initialization
```

**Test Coverage:** 80 tests covering:
- Agent loop functionality
- Skill loading and discovery
- Tool execution
- Ollama client integration
- Multi-file skill workflows

### Project Structure

```
local-skills-agent/
├── skills/                      # Main package
│   ├── __init__.py
│   ├── agent.py                # Agent loop orchestration
│   ├── ollama_client.py        # Ollama API integration
│   ├── skill_loader.py         # Skills discovery and loading
│   ├── tools.py                # Tool implementations
│   └── main.py                 # CLI interface
│
├── .skills/                    # Skills directory
│   ├── skill_creator.md       # Meta-skill (creates skills)
│   ├── code_quality_analyzer.md
│   ├── readme_generator.md
│   └── ...
│
├── tests/                      # Test suite
│   ├── conftest.py            # Pytest configuration
│   ├── test_agent.py
│   ├── test_skill_loader.py
│   └── ...
│
├── DEMO.md                     # Demo scripts
├── ACHIEVEMENT.md             # Technical summary
├── pyproject.toml             # Package configuration
└── README.md                  # This file
```

### Code Style

We follow PEP 8 with these specifics:

```python
# Import order
import standard_library
import third_party
from local_package import module

# Type hints
def function_name(param: str, optional: int = 0) -> bool:
    """Docstring following Google style."""
    pass

# Class structure
class ClassName:
    """Class docstring."""

    def __init__(self, param: str):
        self.param = param

    def public_method(self) -> str:
        """Public method docstring."""
        return self._private_method()

    def _private_method(self) -> str:
        """Private method docstring."""
        return "value"
```

### Adding a New Tool

1. **Define the tool in `skills/tools.py`:**

```python
class MyNewTool:
    name = "my_tool"
    description = "What this tool does"
    parameters = {
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param"]
    }

    @staticmethod
    def execute(param: str) -> str:
        """Execute the tool."""
        # Implementation
        return "result"
```

2. **Add to tool registry in `get_default_tools()`:**

```python
def get_default_tools() -> list[Tool]:
    return [
        ReadFileTool(),
        WriteFileTool(),
        BashTool(),
        ListDirectoryTool(),
        MyNewTool(),  # Add your tool
    ]
```

3. **Write tests in `tests/test_tools.py`:**

```python
def test_my_new_tool():
    tool = MyNewTool()
    result = tool.execute("test_param")
    assert result == "expected"
```

4. **Update documentation** in this README

### Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Run full test suite: `pytest`
4. Commit changes: `git commit -am "Release v0.X.0"`
5. Tag release: `git tag -a v0.X.0 -m "Release v0.X.0"`
6. Push: `git push origin main --tags`

---

## 🐛 Troubleshooting

### Ollama Connection Issues

**Problem:** `Error: Could not connect to Ollama`

**Solutions:**
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama
ollama serve

# Check Ollama version
ollama --version

# Test Ollama directly
ollama list
```

### Model Not Found

**Problem:** `Error: Model 'gpt-oss:20b' not found`

**Solution:**
```bash
# Pull the model
ollama pull gpt-oss:20b

# List available models
ollama list

# Try with a different model
skills --model llama3.2:3b
```

### Max Iterations Reached

**Problem:** `Warning: Reached maximum iterations`

**Cause:** Task too complex or model too verbose

**Solutions:**
```bash
# Increase max iterations
skills --max-iterations 30

# Use a less verbose model
skills --model llama3.1:8b-instruct-q4_K_M

# Break task into smaller steps
# Instead of: "Do A, B, C, and D"
# Try: "Do A and B", then "Do C and D"
```

### Skills Not Loading

**Problem:** `No skills found`

**Solutions:**
```bash
# Check skills directory exists
ls -la .skills/

# Verify .md files are present
ls .skills/*.md

# Use custom skills directory
skills --skills-dir /path/to/skills

# Check file permissions
chmod 644 .skills/*.md
```

### Tool Execution Failures

**Problem:** `Error executing bash command`

**Solutions:**
```bash
# Check bash timeout (30s default)
# For long-running commands, consider:
# 1. Breaking into smaller steps
# 2. Using background execution
# 3. Modifying timeout in tools.py (development)

# Verify file paths are correct
# Paths are relative to current working directory
pwd  # Check where you're running from
```

### Model Produces Verbose Output

**Problem:** Model outputs extensive reasoning but doesn't complete tasks

**Cause:** Using a reasoning model (qwen3:30b, deepseek-r1, qwq)

**Solution:**
```bash
# Switch to a recommended model
skills --model gpt-oss:20b

# Or use llama3.1 for faster execution
skills --model llama3.1:8b-instruct-q4_K_M
```

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'skills'`

**Solutions:**
```bash
# Reinstall in development mode
uv pip install -e .

# Check virtual environment is activated
which python  # Should point to .venv/bin/python

# Verify installation
python -c "import skills; print(skills.__file__)"
```

---

## ❓ FAQ

### General Questions

**Q: Is this really free forever?**
A: Yes! It runs entirely on local Ollama. Download a model once, run it forever. Zero API costs, zero subscriptions.

**Q: How does this compare to ChatGPT or Claude?**
A: Different use cases. ChatGPT/Claude are general purpose. This is specialized for agentic workflows with tool calling. Benefits: 100% local, $0 cost, self-extending, no rate limits. Tradeoff: Requires local GPU/CPU resources.

**Q: Can I use this commercially?**
A: Yes! MIT license. Use it however you want.

**Q: Does it work offline?**
A: Yes, completely. Once you have Ollama and a model downloaded, no internet needed.

### Technical Questions

**Q: Which model should I use?**
A: For best results: `gpt-oss:20b`. For development: `llama3.1:8b-instruct-q4_K_M`. See [Model Recommendations](#-model-recommendations).

**Q: Can I add custom tools?**
A: Yes! See [Development → Adding a New Tool](#adding-a-new-tool).

**Q: How do I create skills programmatically?**
A: Just write a `.md` file to `.skills/`. The agent auto-discovers it on next startup. Or ask the agent to create one using `skill_creator`!

**Q: Can skills invoke other skills?**
A: Yes! Skills can use `read_file` to read other skill files, enabling composition. Example: `analyze_code` delegates to `code_quality_analyzer`.

**Q: What's the maximum number of iterations?**
A: Default is 20. Configurable via `--max-iterations`. If you hit the limit, increase it or break the task into smaller parts.

**Q: How much disk space do I need?**
A: Models vary: `llama3.2:3b` = 2GB, `gpt-oss:20b` = 13GB, `qwen2.5-coder:32b` = 19GB. Plan for ~15-20GB for a good model.

**Q: How much RAM do I need?**
A: Depends on model size. Rule of thumb: 2x model size. So `gpt-oss:20b` (13GB) needs ~26GB RAM. Use smaller models on limited hardware.

### Skills Questions

**Q: Can I modify existing skills?**
A: Yes! They're just markdown files. Edit them like any code.

**Q: Do I need to restart after creating a skill?**
A: No! In interactive mode, new skills are available immediately. In single-message mode, they're loaded at startup.

**Q: Can skills have state?**
A: No, skills are stateless instructions. The agent's context (conversation history) provides continuity.

**Q: How do I debug a skill?**
A: Run with a single message and watch the tool calls. Add explicit "report progress" instructions to the skill.

### Performance Questions

**Q: Why is it slow?**
A: Could be: large model, CPU vs GPU inference, or verbose model. Try a smaller/faster model like `llama3.2:3b`.

**Q: Can I run this on CPU only?**
A: Yes, but slower. Models like `llama3.2:3b` work reasonably on CPU. Larger models benefit significantly from GPU.

**Q: How do I make it faster?**
A: 1) Use smaller models, 2) Use GPU acceleration, 3) Reduce max_iterations, 4) Simplify skills.

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Ways to Contribute

- 🐛 **Report bugs** - Open an issue with reproduction steps
- ✨ **Suggest features** - Open an issue with your idea
- 📝 **Improve documentation** - Submit PRs for docs improvements
- 🎯 **Create skills** - Share useful skills via PRs
- 🔧 **Fix issues** - Pick an issue and submit a PR
- 🧪 **Add tests** - Improve test coverage

### Contribution Process

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/local-skills-agent.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Add tests for new functionality
   - Update documentation
   - Follow code style guidelines

4. **Run tests**
   ```bash
   pytest
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**
   - Describe what you changed and why
   - Link any related issues
   - Wait for review

### Skill Contributions

Have a useful skill? Share it!

1. Create your skill in `.skills/`
2. Test it thoroughly
3. Document it well (purpose, instructions, examples)
4. Submit a PR

**Great skill characteristics:**
- Solves a real problem
- Well documented
- Tested with multiple models
- Handles edge cases
- Includes examples

### Code Review Guidelines

We review for:
- ✅ Tests pass
- ✅ Code follows style guide
- ✅ Documentation updated
- ✅ No breaking changes (or properly documented)
- ✅ Commit messages are clear

### Community

- 💬 **Discussions** - For questions and ideas
- 🐛 **Issues** - For bugs and feature requests
- 📧 **Email** - For private inquiries

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

This means you can:
- ✅ Use commercially
- ✅ Modify
- ✅ Distribute
- ✅ Use privately

Just include the original license and copyright.

---

## 🙏 Acknowledgments

- **Ollama Team** - For making local LLM inference accessible
- **Anthropic** - For the Claude Skills concept that inspired this
- **Open Source Community** - For the models and tools this builds upon

---

## 📚 Additional Resources

### Documentation
- [ACHIEVEMENT.md](ACHIEVEMENT.md) - Complete technical summary
- [SKILL_CREATOR_DEMO.md](SKILL_CREATOR_DEMO.md) - Meta-programming demonstration
- [DEMO.md](DEMO.md) - Live demo script

### External Links
- [Ollama Documentation](https://github.com/ollama/ollama)
- [gpt-oss Model Info](https://ollama.ai/library/gpt-oss)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

---

## 🚀 What's Next?

Once you're comfortable with the basics:

1. **Create your first custom skill**
   ```bash
   skills --message "Create a skill that does [something you need]"
   ```

2. **Explore multi-file skills**
   - Add supporting scripts
   - Include reference data
   - Use templates for output

3. **Build complex workflows**
   - Chain multiple skills together
   - Create domain-specific skill sets
   - Share your skills with the community

4. **Contribute back**
   - Share useful skills
   - Report bugs
   - Suggest improvements

---

**Ready to extend your AI?** 🎯

```bash
skills --message "What should we build today?"
```

---

<p align="center">
  <strong>Built with ❤️ using local AI</strong><br>
  <sub>No clouds were harmed in the making of this software</sub>
</p>
