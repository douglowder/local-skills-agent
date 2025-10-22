"""Integration tests using actual Ollama models.

These tests require Ollama to be running with the qwen3:30b model available.
Run with: uv run pytest tests/test_integration.py -v
"""

import pytest

from skills.agent import Agent
from skills.ollama_client import OllamaClient


@pytest.fixture
def ollama_model():
    """Return the model to use for integration tests."""
    return "qwen3:30b"


@pytest.fixture
def check_ollama_available(ollama_model):
    """Check if Ollama is available and has the required model."""
    try:
        client = OllamaClient(model=ollama_model)
        models = client.list_models()
        if ollama_model not in models:
            pytest.skip(f"Model {ollama_model} not available in Ollama")
    except Exception as e:
        pytest.skip(f"Ollama not available: {e}")


class TestOllamaIntegration:
    """Integration tests with actual Ollama."""

    def test_list_models(self, check_ollama_available, ollama_model):
        """Test listing available models."""
        client = OllamaClient(model=ollama_model)
        models = client.list_models()

        assert len(models) > 0
        assert ollama_model in models
        print(f"\nAvailable models: {models}")

    def test_simple_chat(self, check_ollama_available, ollama_model):
        """Test a simple chat interaction."""
        client = OllamaClient(model=ollama_model)

        messages = [
            {"role": "user", "content": "Say 'Hello, World!' and nothing else."}
        ]

        response = client.chat(messages=messages)

        assert "message" in response
        assert response["message"]["role"] == "assistant"
        assert "content" in response["message"]
        print(f"\nResponse: {response['message']['content']}")

    def test_chat_with_tools_simple(self, check_ollama_available, ollama_model):
        """Test chat with tool calling capability."""
        client = OllamaClient(model=ollama_model)

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the weather for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city name",
                            }
                        },
                        "required": ["location"],
                    },
                },
            }
        ]

        messages = [
            {
                "role": "user",
                "content": "What's the weather in San Francisco? Use the get_weather tool.",
            }
        ]

        response = client.chat(messages=messages, tools=tools)

        assert "message" in response
        print(f"\nResponse: {response['message']}")

        # The model may or may not use tools depending on its capabilities
        # Just verify we get a valid response
        assert response["message"]["role"] == "assistant"


class TestAgentIntegration:
    """Integration tests for the Agent with actual Ollama."""

    def test_agent_initialization(self, check_ollama_available, ollama_model, temp_dir):
        """Test agent can initialize with qwen3:30b."""
        agent = Agent(model=ollama_model, skills_dir=str(temp_dir / ".skills"))

        assert agent.client.model == ollama_model
        assert len(agent.tools) > 0

    def test_agent_simple_interaction(
        self, check_ollama_available, ollama_model, temp_dir, capsys
    ):
        """Test agent can handle a simple interaction."""
        agent = Agent(
            model=ollama_model, skills_dir=str(temp_dir / ".skills"), max_iterations=3
        )

        agent.run("Please respond with just the word 'SUCCESS' and nothing else.")

        # Check that we got some response
        assert len(agent.messages) > 0

        # Find assistant messages
        assistant_msgs = [
            msg for msg in agent.messages if msg.get("role") == "assistant"
        ]
        assert len(assistant_msgs) > 0

        print("\n--- Agent Messages ---")
        for msg in agent.messages:
            print(f"{msg.get('role', 'unknown')}: {msg.get('content', 'N/A')[:100]}")

    def test_agent_with_tool_use(
        self, check_ollama_available, ollama_model, temp_dir, capsys
    ):
        """Test agent can use tools."""
        agent = Agent(
            model=ollama_model, skills_dir=str(temp_dir / ".skills"), max_iterations=5
        )

        # Create a test file for the agent to read
        test_file = temp_dir / "test_data.txt"
        test_file.write_text("Integration test content")

        agent.run(
            f"Read the file at {test_file} using the read_file tool and tell me what it contains."
        )

        # Check if any tool was called
        tool_msgs = [msg for msg in agent.messages if msg.get("role") == "tool"]

        print("\n--- Tool Calls ---")
        for msg in tool_msgs:
            print(f"Tool result: {msg.get('content', 'N/A')[:200]}")

        # The agent should have attempted to use the tool
        # (though tool support varies by model)
        assert len(agent.messages) > 0

    def test_agent_with_bash_tool(
        self, check_ollama_available, ollama_model, temp_dir
    ):
        """Test agent can use bash tool."""
        agent = Agent(
            model=ollama_model, skills_dir=str(temp_dir / ".skills"), max_iterations=5
        )

        agent.run("Use the bash tool to execute 'echo Testing123' and show me the result.")

        # Check that we got responses
        assert len(agent.messages) > 0

        print("\n--- Bash Tool Test Messages ---")
        for msg in agent.messages:
            role = msg.get("role", "unknown")
            content = str(msg.get("content", "N/A"))[:200]
            print(f"{role}: {content}")

    def test_agent_with_skill(
        self, check_ollama_available, ollama_model, sample_skill_dir
    ):
        """Test agent can discover and potentially use skills."""
        agent = Agent(
            model=ollama_model,
            skills_dir=str(sample_skill_dir),
            max_iterations=5,
        )

        # Verify skills were loaded
        assert len(agent.skill_loader.skills) > 0
        print(f"\nLoaded skills: {agent.skill_loader.get_skill_names()}")

        # Try to get the agent to use a skill
        agent.run("What skills are available? List them for me.")

        # Check for responses
        assert len(agent.messages) > 0

        print("\n--- Skill Interaction Messages ---")
        for msg in agent.messages[-3:]:  # Last 3 messages
            print(f"{msg.get('role', 'unknown')}: {msg.get('content', 'N/A')[:200]}")

    def test_agent_conversation_context(
        self, check_ollama_available, ollama_model, temp_dir
    ):
        """Test agent maintains context across multiple interactions."""
        agent = Agent(
            model=ollama_model, skills_dir=str(temp_dir / ".skills"), max_iterations=3
        )

        # First interaction
        agent.run("Remember this number: 42")

        # Second interaction - should remember
        agent.run("What number did I just tell you to remember?")

        # Check we have multiple user messages
        user_msgs = [msg for msg in agent.messages if msg.get("role") == "user"]
        assert len(user_msgs) >= 2

        print("\n--- Context Test Messages ---")
        for msg in agent.messages[-5:]:  # Last 5 messages
            print(f"{msg.get('role', 'unknown')}: {msg.get('content', 'N/A')[:150]}")


class TestModelCapabilities:
    """Test specific capabilities of the qwen3:30b model."""

    def test_model_response_quality(self, check_ollama_available, ollama_model):
        """Test the model can provide coherent responses."""
        client = OllamaClient(model=ollama_model)

        messages = [
            {
                "role": "user",
                "content": "Explain what an agentic loop is in one sentence.",
            }
        ]

        response = client.chat(messages=messages)

        content = response["message"]["content"]
        assert len(content) > 10  # Should be a meaningful response
        assert any(
            word in content.lower() for word in ["agent", "loop", "llm", "model"]
        )

        print(f"\nModel explanation: {content}")

    def test_model_json_understanding(self, check_ollama_available, ollama_model):
        """Test the model understands structured data."""
        client = OllamaClient(model=ollama_model)

        messages = [
            {
                "role": "user",
                "content": 'Given this JSON: {"name": "Alice", "age": 30}, what is the name? Reply with just the name.',
            }
        ]

        response = client.chat(messages=messages)

        content = response["message"]["content"]
        print(f"\nJSON test response: {content}")

        # Should mention Alice
        assert "alice" in content.lower()

    def test_model_follows_instructions(self, check_ollama_available, ollama_model):
        """Test the model can follow specific instructions."""
        client = OllamaClient(model=ollama_model)

        messages = [
            {
                "role": "user",
                "content": "Count from 1 to 3, with each number on a new line. Only output the numbers, nothing else.",
            }
        ]

        response = client.chat(messages=messages)

        content = response["message"]["content"]
        print(f"\nInstruction following test: {content}")

        # Should contain numbers 1, 2, 3
        assert "1" in content
        assert "2" in content
        assert "3" in content
