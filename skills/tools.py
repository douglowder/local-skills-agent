"""Tool implementations for the agent."""

import json
import subprocess
from pathlib import Path
from typing import Any, Callable, Optional

ConfirmCallback = Callable[[str, dict[str, Any]], bool]

# Path components / names / suffixes that look like secrets we should never
# read or write through the agent's tools, even if they are inside the
# workspace root. Defense in depth against an LLM that has been redirected by
# indirect prompt injection.
SECRET_DIR_NAMES = frozenset({".ssh", ".aws", ".gnupg", ".gcloud"})
SECRET_FILE_NAMES = frozenset(
    {
        ".env",
        "id_rsa",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
        "credentials",
        "credentials.json",
    }
)
SECRET_NAME_PREFIXES: tuple[str, ...] = (".env.",)
SECRET_NAME_SUFFIXES: tuple[str, ...] = (".pem", ".key")


def _is_secret_path(path: Path) -> bool:
    """Return True if `path` looks like a credentials or secrets path."""
    for part in path.parts:
        if part in SECRET_DIR_NAMES:
            return True
    name = path.name
    if name in SECRET_FILE_NAMES:
        return True
    if name.startswith(SECRET_NAME_PREFIXES):
        return True
    if name.endswith(SECRET_NAME_SUFFIXES):
        return True
    return False


def _resolve_in_root(path: str, root: Optional[Path]) -> tuple[Optional[Path], Optional[str]]:
    """Resolve `path` (expanding ~) and verify confinement.

    Returns (resolved_path, error_message). On success, error_message is None.
    On failure, resolved_path is None and error_message is a user-facing string.
    """
    try:
        target = Path(path).expanduser()
    except (RuntimeError, ValueError) as e:
        return None, f"Error: Invalid path: {e}"

    if root is not None:
        if not target.is_absolute():
            target = root / target
        try:
            target = target.resolve()
            resolved_root = root.resolve()
            target.relative_to(resolved_root)
        except (OSError, ValueError):
            return None, (
                f"Error: Path is outside the workspace root "
                f"({root}): {path}"
            )
    else:
        try:
            target = target.resolve()
        except OSError as e:
            return None, f"Error: Cannot resolve path: {e}"

    if _is_secret_path(target):
        return None, f"Error: Refusing to access secret-looking path: {path}"

    return target, None


class Tool:
    """Base class for agent tools."""

    def __init__(self, name: str, description: str, parameters: dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters

    def execute(self, **kwargs) -> str:
        """Execute the tool with given parameters."""
        raise NotImplementedError

    def to_dict(self) -> dict[str, Any]:
        """Convert tool to dictionary format for LLM."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ReadFileTool(Tool):
    """Tool to read file contents."""

    def __init__(self, root: Optional[Path] = None):
        super().__init__(
            name="read_file",
            description="Read the contents of a file",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read",
                    }
                },
                "required": ["path"],
            },
        )
        self.root = root

    def execute(self, path: str) -> str:
        """Read and return file contents."""
        file_path, err = _resolve_in_root(path, self.root)
        if err:
            return err
        try:
            if not file_path.exists():
                return f"Error: File not found: {path}"
            return file_path.read_text()
        except Exception as e:
            return f"Error reading file: {e}"


class WriteFileTool(Tool):
    """Tool to write content to a file."""

    def __init__(
        self,
        confirm: Optional[ConfirmCallback] = None,
        root: Optional[Path] = None,
    ):
        super().__init__(
            name="write_file",
            description="Write content to a file",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to write",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file",
                    },
                },
                "required": ["path", "content"],
            },
        )
        self.confirm = confirm
        self.root = root

    def execute(self, path: str, content: str) -> str:
        """Write content to file."""
        file_path, err = _resolve_in_root(path, self.root)
        if err:
            return err
        if self.confirm and not self.confirm(
            "write_file", {"path": str(file_path), "bytes": len(content)}
        ):
            return "Error: Write declined by user"
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing file: {e}"


class BashTool(Tool):
    """Tool to execute bash commands."""

    def __init__(self, confirm: Optional[ConfirmCallback] = None):
        super().__init__(
            name="bash",
            description="Execute a bash command",
            parameters={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute",
                    }
                },
                "required": ["command"],
            },
        )
        self.confirm = confirm

    def execute(self, command: str) -> str:
        """Execute bash command and return output."""
        if self.confirm and not self.confirm("bash", {"command": command}):
            return "Error: Command execution declined by user"
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR: {result.stderr}"
            if result.returncode != 0:
                output += f"\nReturn code: {result.returncode}"
            return output or "Command executed successfully (no output)"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds"
        except Exception as e:
            return f"Error executing command: {e}"


class ListDirectoryTool(Tool):
    """Tool to list directory contents."""

    def __init__(self, root: Optional[Path] = None):
        super().__init__(
            name="list_directory",
            description="List contents of a directory",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the directory to list (defaults to current directory)",
                    }
                },
                "required": [],
            },
        )
        self.root = root

    def execute(self, path: str = ".") -> str:
        """List directory contents."""
        dir_path, err = _resolve_in_root(path, self.root)
        if err:
            return err
        try:
            if not dir_path.exists():
                return f"Error: Directory not found: {path}"
            if not dir_path.is_dir():
                return f"Error: Not a directory: {path}"

            items = []
            for item in sorted(dir_path.iterdir()):
                item_type = "DIR" if item.is_dir() else "FILE"
                items.append(f"{item_type}: {item.name}")

            return "\n".join(items) if items else "Directory is empty"
        except Exception as e:
            return f"Error listing directory: {e}"


def get_default_tools(
    confirm: Optional[ConfirmCallback] = None,
    workspace_root: Optional[Path] = None,
) -> list[Tool]:
    """Return the default set of tools.

    `confirm`, if provided, is invoked before any side-effectful tool
    (bash, write_file) runs. Returning False cancels the operation.

    `workspace_root` constrains read_file, write_file and list_directory
    to a directory tree. If None, defaults to the current working
    directory. Pass an explicit Path to set a different root.
    """
    if workspace_root is None:
        workspace_root = Path.cwd()
    return [
        ReadFileTool(root=workspace_root),
        WriteFileTool(confirm=confirm, root=workspace_root),
        BashTool(confirm=confirm),
        ListDirectoryTool(root=workspace_root),
    ]


def execute_tool(tool: Tool, arguments: dict[str, Any]) -> str:
    """Execute a tool with the given arguments."""
    try:
        return tool.execute(**arguments)
    except TypeError as e:
        return f"Error: Invalid arguments for tool {tool.name}: {e}"
    except Exception as e:
        return f"Error executing tool {tool.name}: {e}"
