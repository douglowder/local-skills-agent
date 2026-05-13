"""Main CLI interface for the skills agent."""

import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from .agent import Agent


def print_welcome(console: Console) -> None:
    """Print welcome message."""
    console.print("\n[bold cyan]╔═══════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║[/bold cyan]  [bold white]Local Skills Agent[/bold white]              [bold cyan]║[/bold cyan]")
    console.print("[bold cyan]║[/bold cyan]  Ollama-powered agentic loop      [bold cyan]║[/bold cyan]")
    console.print("[bold cyan]╚═══════════════════════════════════════╝[/bold cyan]\n")


def print_help(console: Console) -> None:
    """Print help message."""
    table = Table(title="Available Commands", show_header=True, header_style="bold magenta")
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="white")

    table.add_row("/help", "Show this help message")
    table.add_row("/reset", "Clear conversation history")
    table.add_row("/models", "List available Ollama models")
    table.add_row("/skills", "List available skills")
    table.add_row("/quit or /exit", "Exit the program")
    table.add_row("", "")
    table.add_row("[Any other text]", "Send message to the agent")

    console.print(table)


def list_models(agent: Agent, console: Console) -> None:
    """List available Ollama models."""
    models = agent.get_available_models()
    if models:
        console.print("\n[bold]Available Ollama models:[/bold]")
        for model in models:
            console.print(f"  • {model}")
    else:
        console.print("[yellow]No models found. Is Ollama running?[/yellow]")


def list_skills(agent: Agent, console: Console) -> None:
    """List available skills, grouped hierarchically by plugin."""
    loader = agent.skill_loader
    if not loader.skills:
        console.print(
            "[yellow]No skills found. Create SKILL.md files under "
            ".skills/plugins/<plugin>/skills/<slug>/ "
            "(or as flat .md files in .skills/).[/yellow]"
        )
        return

    console.print("\n[bold]Available skills:[/bold]")

    plugins_with_skills = [p for p in loader.plugins.values() if p.skills]
    standalone = [s for s in loader.skills.values() if s.plugin is None]

    for plugin in plugins_with_skills:
        header = f"[bold magenta]{plugin.name}[/bold magenta]"
        if plugin.version:
            header += f" [dim]v{plugin.version}[/dim]"
        if plugin.description:
            header += f"  {plugin.description}"
        console.print(f"\n{header}")
        for skill in plugin.skills:
            console.print(
                f"  • [cyan]{skill.name}[/cyan]: {skill.description}"
            )

    if standalone:
        if plugins_with_skills:
            console.print("\n[bold magenta](standalone)[/bold magenta]")
        for skill in standalone:
            console.print(
                f"  • [cyan]{skill.name}[/cyan]: {skill.description}"
            )


def interactive_mode(
    model: str,
    skills_dir: str,
    max_iterations: int = 20,
    require_confirmation: bool = True,
    workspace_root: Optional[Path] = None,
    allow_remote_ollama: bool = False,
) -> None:
    """Run the agent in interactive mode."""
    console = Console()
    print_welcome(console)

    try:
        agent = Agent(
            model=model,
            skills_dir=skills_dir,
            max_iterations=max_iterations,
            require_confirmation=require_confirmation,
            workspace_root=workspace_root,
            allow_remote_ollama=allow_remote_ollama,
        )
        console.print(f"[green]✓[/green] Using model: [bold]{model}[/bold]")
        console.print(f"[green]✓[/green] Skills directory: [bold]{skills_dir}[/bold]")
        console.print(
            f"[green]✓[/green] Workspace root: [bold]{agent.workspace_root}[/bold]"
        )
        host_marker = (
            "[bold red]REMOTE[/bold red]"
            if allow_remote_ollama
            else "[green]loopback[/green]"
        )
        console.print(
            f"[green]✓[/green] Ollama host: [bold]{agent.client.host}[/bold] "
            f"({host_marker})"
        )
        if require_confirmation:
            console.print(
                "[green]✓[/green] Confirmation prompts: [bold]on[/bold] "
                "(bash and write_file will ask before running)\n"
            )
        else:
            console.print(
                "[bold red]⚠ Confirmation prompts disabled[/bold red] "
                "— bash and write_file will run without asking\n"
            )

        skills_count = len(agent.skill_loader.skills)
        if skills_count > 0:
            console.print(f"[green]✓[/green] Loaded {skills_count} skill(s)\n")
        else:
            console.print("[yellow]⚠[/yellow] No skills found\n")

        console.print("Type [bold]/help[/bold] for available commands\n")

    except Exception as e:
        console.print(f"[bold red]Error initializing agent:[/bold red] {e}")
        console.print("\n[yellow]Make sure Ollama is running:[/yellow] ollama serve")
        sys.exit(1)

    while True:
        try:
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith("/"):
                command = user_input.lower()

                if command in ["/quit", "/exit"]:
                    console.print("\n[bold]Goodbye![/bold]\n")
                    break
                elif command == "/help":
                    print_help(console)
                elif command == "/reset":
                    agent.reset()
                elif command == "/models":
                    list_models(agent, console)
                elif command == "/skills":
                    list_skills(agent, console)
                else:
                    console.print(f"[red]Unknown command: {command}[/red]")
                    console.print("Type [bold]/help[/bold] for available commands")

                continue

            # Run agent with user message
            agent.run(user_input)

        except KeyboardInterrupt:
            console.print("\n\n[bold]Interrupted. Use /quit to exit.[/bold]")
            continue
        except EOFError:
            console.print("\n\n[bold]Goodbye![/bold]\n")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {e}\n")


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Local Skills Agent - Ollama-powered agentic loop"
    )
    parser.add_argument(
        "--model",
        "-m",
        default="gpt-oss:20b",
        help="Ollama model to use (default: gpt-oss:20b)",
    )
    parser.add_argument(
        "--skills-dir",
        "-s",
        default=".skills",
        help="Directory containing skill definitions (default: .skills)",
    )
    parser.add_argument(
        "--message",
        help="Single message to send (non-interactive mode)",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=20,
        help="Maximum number of agent loop iterations (default: 20)",
    )
    parser.add_argument(
        "--yes-i-trust-the-llm",
        action="store_true",
        help=(
            "Skip the y/N confirmation before bash and write_file run. "
            "DANGEROUS: the LLM can execute arbitrary commands and overwrite "
            "files without asking. Only use in fully sandboxed environments."
        ),
    )
    parser.add_argument(
        "--workspace-root",
        default=None,
        help=(
            "Confine read_file, write_file, and list_directory to this "
            "directory tree (default: current working directory). Paths "
            "that resolve outside the root are rejected."
        ),
    )
    parser.add_argument(
        "--allow-remote-ollama",
        action="store_true",
        help=(
            "Permit the agent to connect to a non-loopback Ollama endpoint "
            "(via OLLAMA_HOST). DANGEROUS: the entire conversation, including "
            "any local file content the agent reads, is sent to that host. "
            "By default the agent refuses to start if OLLAMA_HOST resolves "
            "to a remote address."
        ),
    )

    args = parser.parse_args()
    require_confirmation = not args.yes_i_trust_the_llm
    workspace_root = Path(args.workspace_root) if args.workspace_root else None

    if args.message:
        # Non-interactive mode
        console = Console()
        try:
            agent = Agent(
                model=args.model,
                skills_dir=args.skills_dir,
                max_iterations=args.max_iterations,
                require_confirmation=require_confirmation,
                workspace_root=workspace_root,
                allow_remote_ollama=args.allow_remote_ollama,
            )
            console.print(
                f"[green]✓[/green] Ollama host: [bold]{agent.client.host}[/bold]"
            )
            agent.run(args.message)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            sys.exit(1)
    else:
        # Interactive mode
        interactive_mode(
            args.model,
            args.skills_dir,
            args.max_iterations,
            require_confirmation=require_confirmation,
            workspace_root=workspace_root,
            allow_remote_ollama=args.allow_remote_ollama,
        )


if __name__ == "__main__":
    main()
