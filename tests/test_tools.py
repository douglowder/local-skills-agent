"""Tests for the tools module."""

import subprocess
from pathlib import Path

import pytest

from skills.tools import (
    BashTool,
    ListDirectoryTool,
    ReadFileTool,
    Tool,
    WriteFileTool,
    execute_tool,
    get_default_tools,
)


class TestTool:
    """Test the base Tool class."""

    def test_tool_initialization(self):
        """Test Tool initialization."""
        tool = Tool(
            name="test_tool",
            description="A test tool",
            parameters={"type": "object", "properties": {}},
        )
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert tool.parameters["type"] == "object"

    def test_tool_to_dict(self):
        """Test Tool.to_dict() method."""
        tool = Tool(
            name="test_tool",
            description="A test tool",
            parameters={"type": "object", "properties": {}},
        )
        tool_dict = tool.to_dict()

        assert tool_dict["type"] == "function"
        assert tool_dict["function"]["name"] == "test_tool"
        assert tool_dict["function"]["description"] == "A test tool"
        assert tool_dict["function"]["parameters"]["type"] == "object"

    def test_tool_execute_not_implemented(self):
        """Test that Tool.execute raises NotImplementedError."""
        tool = Tool(
            name="test_tool",
            description="A test tool",
            parameters={"type": "object", "properties": {}},
        )
        with pytest.raises(NotImplementedError):
            tool.execute()


class TestReadFileTool:
    """Test the ReadFileTool class."""

    def test_read_file_success(self, sample_file):
        """Test reading a file successfully."""
        tool = ReadFileTool()
        result = tool.execute(path=str(sample_file))
        assert result == "Hello, World!"

    def test_read_file_not_found(self, temp_dir):
        """Test reading a non-existent file."""
        tool = ReadFileTool()
        result = tool.execute(path=str(temp_dir / "nonexistent.txt"))
        assert "Error: File not found" in result

    def test_read_file_permission_error(self, temp_dir, monkeypatch):
        """Test handling permission errors."""
        tool = ReadFileTool()
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        # Mock read_text to raise PermissionError
        def mock_read_text():
            raise PermissionError("Permission denied")

        monkeypatch.setattr(Path, "read_text", lambda self: mock_read_text())

        result = tool.execute(path=str(test_file))
        assert "Error reading file" in result


class TestWriteFileTool:
    """Test the WriteFileTool class."""

    def test_write_file_success(self, temp_dir):
        """Test writing to a file successfully."""
        tool = WriteFileTool()
        file_path = temp_dir / "output.txt"

        result = tool.execute(path=str(file_path), content="Test content")

        assert "Successfully wrote to" in result
        assert file_path.read_text() == "Test content"

    def test_write_file_creates_parent_dirs(self, temp_dir):
        """Test that parent directories are created."""
        tool = WriteFileTool()
        file_path = temp_dir / "subdir" / "nested" / "file.txt"

        result = tool.execute(path=str(file_path), content="Nested content")

        assert "Successfully wrote to" in result
        assert file_path.read_text() == "Nested content"

    def test_write_file_error(self, temp_dir, monkeypatch):
        """Test handling write errors."""
        tool = WriteFileTool()

        # Mock write_text to raise an error
        def mock_write_text(self, content):
            raise IOError("Write failed")

        monkeypatch.setattr(Path, "write_text", mock_write_text)

        result = tool.execute(path=str(temp_dir / "test.txt"), content="content")
        assert "Error writing file" in result

    def test_write_file_confirm_declined_blocks_write(self, temp_dir):
        """If the confirm callback returns False, the file is not written."""
        target = temp_dir / "should_not_exist.txt"
        tool = WriteFileTool(confirm=lambda action, details: False)
        result = tool.execute(path=str(target), content="nope")
        assert "declined by user" in result
        assert not target.exists()


class TestBashTool:
    """Test the BashTool class."""

    def test_bash_simple_command(self):
        """Test executing a simple bash command."""
        tool = BashTool()
        result = tool.execute(command="echo 'Hello, Bash!'")
        assert "Hello, Bash!" in result

    def test_bash_command_with_stderr(self):
        """Test command that produces stderr output."""
        tool = BashTool()
        result = tool.execute(command="echo 'error' >&2")
        assert "STDERR" in result or "error" in result

    def test_bash_command_failure(self):
        """Test command that fails."""
        tool = BashTool()
        result = tool.execute(command="exit 1")
        assert "Return code: 1" in result

    def test_bash_command_timeout(self, monkeypatch):
        """Test command timeout."""
        tool = BashTool()

        # Mock subprocess.run to raise TimeoutExpired
        def mock_run(*args, **kwargs):
            raise subprocess.TimeoutExpired("cmd", 30)

        monkeypatch.setattr(subprocess, "run", mock_run)

        result = tool.execute(command="sleep 100")
        assert "timed out" in result.lower()

    def test_bash_command_exception(self, monkeypatch):
        """Test handling of exceptions during command execution."""
        tool = BashTool()

        # Mock subprocess.run to raise an exception
        def mock_run(*args, **kwargs):
            raise RuntimeError("Command failed")

        monkeypatch.setattr(subprocess, "run", mock_run)

        result = tool.execute(command="test")
        assert "Error executing command" in result

    def test_bash_confirm_declined_blocks_execution(self, monkeypatch):
        """If the confirm callback returns False, the command is not run."""
        ran = {"value": False}

        def mock_run(*args, **kwargs):
            ran["value"] = True
            raise AssertionError("subprocess.run should not have been called")

        monkeypatch.setattr(subprocess, "run", mock_run)

        tool = BashTool(confirm=lambda action, details: False)
        result = tool.execute(command="rm -rf /")
        assert "declined by user" in result
        assert ran["value"] is False

    def test_bash_confirm_approved_runs_command(self):
        """If the confirm callback returns True, the command runs normally."""
        seen = []
        tool = BashTool(confirm=lambda action, details: seen.append((action, details)) or True)
        result = tool.execute(command="echo confirmed")
        assert "confirmed" in result
        assert seen == [("bash", {"command": "echo confirmed"})]


class TestListDirectoryTool:
    """Test the ListDirectoryTool class."""

    def test_list_directory_success(self, temp_dir):
        """Test listing a directory successfully."""
        # Create some test files
        (temp_dir / "file1.txt").write_text("content")
        (temp_dir / "file2.py").write_text("code")
        (temp_dir / "subdir").mkdir()

        tool = ListDirectoryTool()
        result = tool.execute(path=str(temp_dir))

        assert "FILE: file1.txt" in result
        assert "FILE: file2.py" in result
        assert "DIR: subdir" in result

    def test_list_directory_empty(self, temp_dir):
        """Test listing an empty directory."""
        tool = ListDirectoryTool()
        result = tool.execute(path=str(temp_dir))
        assert "Directory is empty" in result

    def test_list_directory_not_found(self, temp_dir):
        """Test listing a non-existent directory."""
        tool = ListDirectoryTool()
        result = tool.execute(path=str(temp_dir / "nonexistent"))
        assert "Error: Directory not found" in result

    def test_list_directory_not_a_directory(self, sample_file):
        """Test listing when path is not a directory."""
        tool = ListDirectoryTool()
        result = tool.execute(path=str(sample_file))
        assert "Error: Not a directory" in result

    def test_list_directory_default_path(self, monkeypatch, temp_dir):
        """Test listing current directory when no path provided."""
        tool = ListDirectoryTool()
        monkeypatch.chdir(temp_dir)
        (temp_dir / "test.txt").write_text("content")

        result = tool.execute()
        assert "FILE: test.txt" in result


class TestGetDefaultTools:
    """Test the get_default_tools function."""

    def test_get_default_tools(self):
        """Test that get_default_tools returns all expected tools."""
        tools = get_default_tools()

        assert len(tools) == 4
        assert any(isinstance(tool, ReadFileTool) for tool in tools)
        assert any(isinstance(tool, WriteFileTool) for tool in tools)
        assert any(isinstance(tool, BashTool) for tool in tools)
        assert any(isinstance(tool, ListDirectoryTool) for tool in tools)


class TestExecuteTool:
    """Test the execute_tool function."""

    def test_execute_tool_success(self, sample_file):
        """Test executing a tool successfully."""
        tool = ReadFileTool()
        result = execute_tool(tool, {"path": str(sample_file)})
        assert result == "Hello, World!"

    def test_execute_tool_invalid_arguments(self):
        """Test executing a tool with invalid arguments."""
        tool = ReadFileTool()
        result = execute_tool(tool, {"invalid_arg": "value"})
        assert "Error: Invalid arguments" in result

    def test_execute_tool_exception(self, monkeypatch):
        """Test handling exceptions during tool execution."""
        tool = ReadFileTool()

        # Mock execute to raise an exception
        def mock_execute(**kwargs):
            raise RuntimeError("Tool failed")

        monkeypatch.setattr(tool, "execute", mock_execute)

        result = execute_tool(tool, {"path": "/tmp/test.txt"})
        assert "Error executing tool" in result
