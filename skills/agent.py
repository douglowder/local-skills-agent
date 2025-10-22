"""Agent loop implementation."""

import json
from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .ollama_client import OllamaClient
from .skill_loader import SkillLoader
from .tools import Tool, execute_tool, get_default_tools


class Agent:
    """The main agent that orchestrates the agentic loop."""

    def __init__(
        self,
        model: str = "llama3.2",
        skills_dir: str = ".skills",
        max_iterations: int = 10,
    ):
        self.client = OllamaClient(model=model)
        self.skill_loader = SkillLoader(skills_dir=skills_dir)
        self.tools = {tool.name: tool for tool in get_default_tools()}
        self.max_iterations = max_iterations
        self.console = Console()

        # Message history (context)
        self.messages: list[dict[str, Any]] = []

        # Load skills
        self.skill_loader.discover_skills()

    def _initialize_system_prompt(self) -> str:
        """Create the system prompt with available tools and skills."""
        system_prompt = """You are a helpful AI assistant with access to tools and skills.

You can use the following tools to accomplish tasks:
- read_file: Read the contents of a file
- write_file: Write content to a file
- bash: Execute bash commands
- list_directory: List directory contents

"""
        # Add skills information
        skills_summary = self.skill_loader.get_skills_summary()
        system_prompt += f"\n{skills_summary}\n"

        system_prompt += """
When you need to use a tool, respond with a tool call. When you're done with the task or want to respond to the user, provide your response.

Always be helpful, clear, and concise in your responses."""

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
