"""Tests for the agent module."""

import pytest

from skills.agent import Agent
from skills.tools import ReadFileTool


class TestAgent:
    """Test the Agent class."""

    def test_agent_initialization(self, sample_skill_dir):
        """Test Agent initialization."""
        agent = Agent(
            model="llama3.2",
            skills_dir=str(sample_skill_dir),
            max_iterations=5,
        )

        assert agent.client.model == "llama3.2"
        assert agent.max_iterations == 5
        assert len(agent.messages) == 0
        assert len(agent.tools) == 4  # Default tools
        assert len(agent.skill_loader.skills) == 2  # Sample skills

    def test_agent_default_parameters(self):
        """Test Agent with default parameters."""
        agent = Agent()

        assert agent.client.model == "llama3.2"
        assert agent.max_iterations == 10

    def test_initialize_system_prompt(self, sample_skill_dir):
        """Test system prompt initialization."""
        agent = Agent(skills_dir=str(sample_skill_dir))

        system_prompt = agent._initialize_system_prompt()

        assert "helpful AI assistant" in system_prompt
        assert "read_file" in system_prompt
        assert "write_file" in system_prompt
        assert "bash" in system_prompt
        assert "Available skills:" in system_prompt
        assert "test_skill" in system_prompt

    def test_initialize_system_prompt_no_skills(self, temp_dir):
        """Test system prompt when no skills are available."""
        agent = Agent(skills_dir=str(temp_dir / "nonexistent"))

        system_prompt = agent._initialize_system_prompt()

        assert "helpful AI assistant" in system_prompt
        assert "No skills available" in system_prompt

    def test_run_simple_response(self, mocker, sample_skill_dir):
        """Test running agent with a simple response (no tools)."""
        agent = Agent(skills_dir=str(sample_skill_dir))

        # Mock the Ollama client response
        mock_response = {
            "message": {
                "role": "assistant",
                "content": "Hello! I can help you with that.",
                "tool_calls": [],
            }
        }
        mocker.patch.object(agent.client, "chat", return_value=mock_response)

        # Mock console output to avoid cluttering test output
        mocker.patch.object(agent.console, "print")

        agent.run("Hello")

        # Should have system prompt and user message
        assert len(agent.messages) >= 2
        assert agent.messages[0]["role"] == "system"
        assert agent.messages[1]["role"] == "user"
        assert agent.messages[1]["content"] == "Hello"
        assert agent.messages[-1]["role"] == "assistant"

    def test_run_with_tool_call(self, mocker, sample_skill_dir, temp_dir):
        """Test running agent with a tool call."""
        agent = Agent(skills_dir=str(sample_skill_dir))

        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test content")

        # Mock responses: first with tool call, then final response
        mock_responses = [
            {
                "message": {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "read_file",
                                "arguments": {"path": str(test_file)},
                            }
                        }
                    ],
                }
            },
            {
                "message": {
                    "role": "assistant",
                    "content": "The file contains: Test content",
                    "tool_calls": [],
                }
            },
        ]

        mock_chat = mocker.patch.object(agent.client, "chat")
        mock_chat.side_effect = mock_responses

        mocker.patch.object(agent.console, "print")

        agent.run("Read the test file")

        # Should have multiple messages including tool result
        assert any(msg.get("role") == "tool" for msg in agent.messages)
        mock_chat.call_count == 2

    def test_run_with_unknown_tool(self, mocker, sample_skill_dir):
        """Test running agent with an unknown tool call."""
        agent = Agent(skills_dir=str(sample_skill_dir))

        mock_response = {
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "function": {
                            "name": "unknown_tool",
                            "arguments": {},
                        }
                    }
                ],
            }
        }

        mocker.patch.object(agent.client, "chat", return_value=mock_response)
        mocker.patch.object(agent.console, "print")

        agent.run("Use an unknown tool")

        # Should have an error message in the tool response
        tool_messages = [msg for msg in agent.messages if msg.get("role") == "tool"]
        assert len(tool_messages) > 0
        assert "Unknown tool" in tool_messages[-1]["content"]

    def test_run_max_iterations(self, mocker, sample_skill_dir):
        """Test that agent stops after max iterations."""
        agent = Agent(skills_dir=str(sample_skill_dir), max_iterations=3)

        # Mock response that always requests a tool (infinite loop scenario)
        mock_response = {
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "function": {
                            "name": "bash",
                            "arguments": {"command": "echo test"},
                        }
                    }
                ],
            }
        }

        mocker.patch.object(agent.client, "chat", return_value=mock_response)
        mocker.patch.object(agent.console, "print")

        agent.run("Keep using tools")

        # Should stop after max_iterations
        # Count tool messages to verify it stopped
        tool_calls = [msg for msg in agent.messages if msg.get("role") == "tool"]
        assert len(tool_calls) <= 3

    def test_reset(self, sample_skill_dir, mocker):
        """Test resetting the agent."""
        agent = Agent(skills_dir=str(sample_skill_dir))

        mocker.patch.object(agent.console, "print")

        # Add some messages
        agent.messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]

        agent.reset()

        assert len(agent.messages) == 0

    def test_get_available_models(self, mocker):
        """Test getting available models."""
        agent = Agent()

        mock_models = ["llama3.2", "qwen3:30b", "mistral"]
        mocker.patch.object(agent.client, "list_models", return_value=mock_models)

        models = agent.get_available_models()

        assert models == mock_models

    def test_tools_registration(self):
        """Test that all default tools are registered."""
        agent = Agent()

        assert "read_file" in agent.tools
        assert "write_file" in agent.tools
        assert "bash" in agent.tools
        assert "list_directory" in agent.tools

    def test_run_preserves_message_history(self, mocker, sample_skill_dir):
        """Test that message history is preserved across runs."""
        agent = Agent(skills_dir=str(sample_skill_dir))

        mock_response = {
            "message": {
                "role": "assistant",
                "content": "Response",
                "tool_calls": [],
            }
        }
        mocker.patch.object(agent.client, "chat", return_value=mock_response)
        mocker.patch.object(agent.console, "print")

        agent.run("First message")
        first_msg_count = len(agent.messages)

        agent.run("Second message")
        second_msg_count = len(agent.messages)

        # Should have more messages after second run
        assert second_msg_count > first_msg_count
        # Should contain both user messages
        user_messages = [msg for msg in agent.messages if msg.get("role") == "user"]
        assert len(user_messages) == 2

    def test_run_with_multiple_tool_calls(self, mocker, sample_skill_dir, temp_dir):
        """Test running agent with multiple tool calls in one response."""
        agent = Agent(skills_dir=str(sample_skill_dir))

        test_file = temp_dir / "test.txt"
        test_file.write_text("Content")

        mock_responses = [
            {
                "message": {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "read_file",
                                "arguments": {"path": str(test_file)},
                            }
                        },
                        {
                            "function": {
                                "name": "bash",
                                "arguments": {"command": "echo 'test'"},
                            }
                        },
                    ],
                }
            },
            {
                "message": {
                    "role": "assistant",
                    "content": "Done with both tools",
                    "tool_calls": [],
                }
            },
        ]

        mock_chat = mocker.patch.object(agent.client, "chat")
        mock_chat.side_effect = mock_responses
        mocker.patch.object(agent.console, "print")

        agent.run("Use multiple tools")

        # Should have tool results for both calls
        tool_messages = [msg for msg in agent.messages if msg.get("role") == "tool"]
        assert len(tool_messages) >= 2

    def test_run_with_content_and_tool_calls(self, mocker, sample_skill_dir):
        """Test response with both content and tool calls."""
        agent = Agent(skills_dir=str(sample_skill_dir))

        mock_response = {
            "message": {
                "role": "assistant",
                "content": "Let me check that file for you.",
                "tool_calls": [
                    {
                        "function": {
                            "name": "bash",
                            "arguments": {"command": "ls"},
                        }
                    }
                ],
            }
        }

        mocker.patch.object(agent.client, "chat", return_value=mock_response)
        mocker.patch.object(agent.console, "print")

        agent.run("List files")

        # Should have both the content message and tool execution
        assert any(
            msg.get("content") == "Let me check that file for you."
            for msg in agent.messages
        )
        assert any(msg.get("role") == "tool" for msg in agent.messages)
