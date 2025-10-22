"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_skill_dir(temp_dir):
    """Create a sample skills directory with test skills."""
    skills_dir = temp_dir / ".skills"
    skills_dir.mkdir()

    # Create a sample skill
    skill1 = skills_dir / "test_skill.md"
    skill1.write_text("""# Test Skill

This is a test skill for unit testing.

## Instructions

1. Do something
2. Do something else
""")

    skill2 = skills_dir / "another_skill.md"
    skill2.write_text("""# Another Skill

Another test skill.

## Instructions

Follow these steps.
""")

    return skills_dir


@pytest.fixture
def sample_file(temp_dir):
    """Create a sample file for testing."""
    file_path = temp_dir / "test.txt"
    file_path.write_text("Hello, World!")
    return file_path


@pytest.fixture
def mock_ollama_response():
    """Mock Ollama response."""
    return {
        "message": {
            "role": "assistant",
            "content": "This is a test response",
        }
    }


@pytest.fixture
def mock_ollama_response_with_tool_call():
    """Mock Ollama response with tool call."""
    return {
        "message": {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "function": {
                        "name": "read_file",
                        "arguments": {"path": "/tmp/test.txt"},
                    }
                }
            ],
        }
    }
