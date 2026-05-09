"""Agent loop implementation."""

import json
from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm

from .ollama_client import OllamaClient
from .skill_loader import SkillLoader
from .tools import Tool, execute_tool, get_default_tools


class Agent:
    """The main agent that orchestrates the agentic loop."""

    def __init__(
        self,
        model: str = "gpt-oss:20b",
        skills_dir: str = ".skills",
        max_iterations: int = 20,
        require_confirmation: bool = True,
    ):
        self.client = OllamaClient(model=model)
        self.skill_loader = SkillLoader(skills_dir=skills_dir)
        self.console = Console()
        self.require_confirmation = require_confirmation
        confirmer = self._make_confirmer() if require_confirmation else None
        self.tools = {
            tool.name: tool for tool in get_default_tools(confirm=confirmer)
        }
        self.max_iterations = max_iterations

        # Message history (context)
        self.messages: list[dict[str, Any]] = []

        # Load skills
        self.skill_loader.discover_skills()

    def _make_confirmer(self):
        """Build a confirmation callback bound to this agent's console."""

        def confirmer(action: str, details: dict) -> bool:
            try:
                return Confirm.ask(
                    f"[bold red]⚠ Allow {action}?[/bold red]",
                    default=False,
                    console=self.console,
                )
            except (EOFError, KeyboardInterrupt):
                return False

        return confirmer

    def _initialize_system_prompt(self) -> str:
        """Create the system prompt with available tools and skills."""
        system_prompt = """You are a helpful AI assistant with access to tools and skills.

# CRITICAL: Tool Calling Behavior

DO NOT THINK OUT LOUD. DO NOT EXPLAIN YOUR REASONING.
When you need information or to perform an action: MAKE THE TOOL CALL IMMEDIATELY.
NO explanations between tool calls. NO planning text. Just make the tool call.
ONLY provide text to the user when you have the final complete answer.

If you catch yourself writing "I should..." or "Next step is..." - STOP and make the tool call instead.

# Tools

You have these tools available:
- read_file: Read the contents of a file
- write_file: Write content to a file
- bash: Execute bash commands
- list_directory: List directory contents

# Skills

Skills are specialized capabilities stored in .skills/ directory. When a user request matches a skill's purpose, you MUST automatically use that skill.

"""
        # Add skills information
        skills_summary = self.skill_loader.get_skills_summary()
        system_prompt += f"{skills_summary}\n"

        system_prompt += """
# How to Use Skills

**IMPORTANT: Automatic Skill Discovery**
When a user asks you to do something, FIRST check if any available skill matches their request. Then use that skill WITHOUT being explicitly told.

**To use a skill:**
1. Read the skill file from .skills/ using read_file (e.g., `.skills/code_quality_analyzer.md`)
2. Follow the instructions in that skill file
3. The skill may reference supporting files (scripts, benchmarks, templates) - read those as needed
4. Skills can invoke other skills (composability)

**Examples:**
- User: "Analyze this code" → Automatically use code_quality_analyzer skill
- User: "Document this project" → Automatically use technical_documentation_generator skill
- User: "Make a hello world" → Automatically use write_hello_world skill

**Key Principles:**
- Match user intent to skills automatically
- Always read the skill file first to get detailed instructions
- Skills contain step-by-step guidance - follow them precisely
- Skills may have supporting resources (scripts/, benchmarks/, templates/) - use them
- Never make up analysis - use the skill's methods and data

When you're done with a task, provide a clear response. Always be helpful and precise."""

        return system_prompt

    def run(self, user_message: str) -> None:
        """Run the agent loop with a user message."""
        # Initialize with system prompt if this is the first message
        if not self.messages:
            system_prompt = self._initialize_system_prompt()
            self.messages.append({"role": "system", "content": system_prompt})

        # Add user message
        self.messages.append({"role": "user", "content": user_message})

        # Display user message
        self.console.print(Panel(user_message, title="[bold blue]User[/bold blue]", border_style="blue"))

        # Agent loop
        for iteration in range(self.max_iterations):
            # Get response from LLM
            response = self.client.chat(
                messages=self.messages,
                tools=[tool.to_dict() for tool in self.tools.values()],
            )

            message = response.get("message", {})
            role = message.get("role", "assistant")
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])

            # Add assistant message to history
            self.messages.append(message)

            # If there's content, display it
            if content:
                self.console.print(Panel(
                    Markdown(content),
                    title="[bold green]Assistant[/bold green]",
                    border_style="green"
                ))

            # If no tool calls, we're done
            if not tool_calls:
                break

            # Execute tool calls
            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                tool_name = function.get("name", "")
                arguments = function.get("arguments", {})

                # Display tool call
                self.console.print(f"\n[bold yellow]Tool Call:[/bold yellow] {tool_name}")
                self.console.print(f"[yellow]Arguments:[/yellow] {json.dumps(arguments, indent=2)}")

                # Execute the tool
                if tool_name in self.tools:
                    tool = self.tools[tool_name]
                    result = execute_tool(tool, arguments)

                    # Display tool result
                    self.console.print(Panel(
                        result[:500] + ("..." if len(result) > 500 else ""),
                        title=f"[bold cyan]Tool Result: {tool_name}[/bold cyan]",
                        border_style="cyan"
                    ))

                    # Add tool result to messages
                    self.messages.append({
                        "role": "tool",
                        "content": result,
                    })
                else:
                    error_msg = f"Error: Unknown tool '{tool_name}'"
                    self.console.print(f"[bold red]{error_msg}[/bold red]")
                    self.messages.append({
                        "role": "tool",
                        "content": error_msg,
                    })

        if iteration >= self.max_iterations - 1:
            self.console.print("\n[bold red]Warning: Reached maximum iterations[/bold red]")

    def reset(self) -> None:
        """Reset the agent's conversation history."""
        self.messages = []
        self.console.print("[bold yellow]Conversation history cleared[/bold yellow]")

    def get_available_models(self) -> list[str]:
        """Get list of available Ollama models."""
        return self.client.list_models()
