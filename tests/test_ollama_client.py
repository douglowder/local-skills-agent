"""Tests for the ollama_client module."""

import pytest

from skills.ollama_client import OllamaClient, _is_loopback, _normalize_host


class TestOllamaClient:
    """Test the OllamaClient class."""

    def test_ollama_client_initialization(self):
        """Test OllamaClient initialization."""
        client = OllamaClient(model="llama3.2")
        assert client.model == "llama3.2"
        assert client.client is not None

    def test_ollama_client_default_model(self):
        """Test OllamaClient with default model."""
        client = OllamaClient()
        assert client.model == "llama3.2"

    def test_list_models_success(self, mocker):
        """Test listing models successfully."""
        client = OllamaClient()

        # Create mock model objects
        class MockModel:
            def __init__(self, name):
                self.model = name

        class MockListResponse:
            def __init__(self, model_names):
                self.models = [MockModel(name) for name in model_names]

        # Mock the list method
        mock_list = mocker.patch.object(client.client, "list")
        mock_list.return_value = MockListResponse(
            ["llama3.2", "qwen3:30b", "mistral"]
        )

        models = client.list_models()

        assert len(models) == 3
        assert "llama3.2" in models
        assert "qwen3:30b" in models
        assert "mistral" in models
        mock_list.assert_called_once()

    def test_list_models_empty(self, mocker):
        """Test listing models when none are available."""
        client = OllamaClient()

        class MockListResponse:
            models = []

        mock_list = mocker.patch.object(client.client, "list")
        mock_list.return_value = MockListResponse()

        models = client.list_models()
        assert len(models) == 0

    def test_list_models_error(self, mocker, capsys):
        """Test handling errors when listing models."""
        client = OllamaClient()

        mock_list = mocker.patch.object(client.client, "list")
        mock_list.side_effect = Exception("Connection error")

        models = client.list_models()

        assert len(models) == 0
        captured = capsys.readouterr()
        assert "Error listing models" in captured.out

    def test_chat_success(self, mocker):
        """Test chat method successfully."""
        client = OllamaClient()

        mock_chat = mocker.patch.object(client.client, "chat")
        mock_response = {
            "message": {
                "role": "assistant",
                "content": "Hello! How can I help you?",
            }
        }
        mock_chat.return_value = mock_response

        messages = [{"role": "user", "content": "Hello"}]
        response = client.chat(messages=messages)

        assert response == mock_response
        mock_chat.assert_called_once_with(
            model="llama3.2",
            messages=messages,
            stream=False,
        )

    def test_chat_with_tools(self, mocker):
        """Test chat method with tools."""
        client = OllamaClient()

        mock_chat = mocker.patch.object(client.client, "chat")
        mock_response = {
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [{"function": {"name": "test_tool"}}],
            }
        }
        mock_chat.return_value = mock_response

        messages = [{"role": "user", "content": "Use a tool"}]
        tools = [{"type": "function", "function": {"name": "test_tool"}}]

        response = client.chat(messages=messages, tools=tools)

        assert response == mock_response
        mock_chat.assert_called_once_with(
            model="llama3.2",
            messages=messages,
            tools=tools,
            stream=False,
        )

    def test_chat_with_streaming(self, mocker):
        """Test chat method with streaming enabled."""
        client = OllamaClient()

        mock_chat = mocker.patch.object(client.client, "chat")
        mock_response = iter([{"message": {"role": "assistant", "content": "chunk"}}])
        mock_chat.return_value = mock_response

        messages = [{"role": "user", "content": "Hello"}]
        response = client.chat(messages=messages, stream=True)

        # Response should be an iterator
        assert hasattr(response, "__iter__")
        mock_chat.assert_called_once_with(
            model="llama3.2",
            messages=messages,
            stream=True,
        )

    def test_chat_error(self, mocker, capsys):
        """Test handling errors during chat."""
        client = OllamaClient()

        mock_chat = mocker.patch.object(client.client, "chat")
        mock_chat.side_effect = Exception("Connection error")

        messages = [{"role": "user", "content": "Hello"}]
        response = client.chat(messages=messages)

        assert "message" in response
        assert "Error communicating with Ollama" in response["message"]["content"]
        captured = capsys.readouterr()
        assert "Error communicating with Ollama" in captured.out

    def test_generate_success(self, mocker):
        """Test generate method successfully."""
        client = OllamaClient()

        mock_generate = mocker.patch.object(client.client, "generate")
        mock_response = {"response": "Generated text here"}
        mock_generate.return_value = mock_response

        response = client.generate(prompt="Test prompt")

        assert response == mock_response
        mock_generate.assert_called_once_with(
            model="llama3.2",
            prompt="Test prompt",
            stream=False,
        )

    def test_generate_with_streaming(self, mocker):
        """Test generate method with streaming."""
        client = OllamaClient()

        mock_generate = mocker.patch.object(client.client, "generate")
        mock_response = iter([{"response": "chunk"}])
        mock_generate.return_value = mock_response

        response = client.generate(prompt="Test prompt", stream=True)

        assert hasattr(response, "__iter__")
        mock_generate.assert_called_once_with(
            model="llama3.2",
            prompt="Test prompt",
            stream=True,
        )

    def test_generate_error(self, mocker, capsys):
        """Test handling errors during generate."""
        client = OllamaClient()

        mock_generate = mocker.patch.object(client.client, "generate")
        mock_generate.side_effect = Exception("Model error")

        response = client.generate(prompt="Test prompt")

        assert "response" in response
        assert "Error communicating with Ollama" in response["response"]
        captured = capsys.readouterr()
        assert "Error communicating with Ollama" in captured.out

    def test_custom_model(self, mocker):
        """Test using a custom model."""
        client = OllamaClient(model="qwen3:30b")

        mock_chat = mocker.patch.object(client.client, "chat")
        mock_chat.return_value = {"message": {"role": "assistant", "content": "Hi"}}

        client.chat(messages=[{"role": "user", "content": "Hi"}])

        # Verify the custom model was used
        call_args = mock_chat.call_args
        assert call_args[1]["model"] == "qwen3:30b"


class TestHostValidation:
    """Tests for OLLAMA_HOST resolution and loopback validation."""

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("127.0.0.1:11434", "http://127.0.0.1:11434"),
            ("localhost:11434", "http://localhost:11434"),
            ("http://127.0.0.1:11434", "http://127.0.0.1:11434"),
            ("https://example.com", "https://example.com"),
        ],
    )
    def test_normalize_host(self, raw, expected):
        assert _normalize_host(raw) == expected

    @pytest.mark.parametrize(
        "url",
        [
            "http://127.0.0.1:11434",
            "http://localhost:11434",
            "http://[::1]:11434",
            "http://127.0.0.255",
        ],
    )
    def test_loopback_urls_match(self, url):
        assert _is_loopback(url) is True

    @pytest.mark.parametrize(
        "url",
        [
            "http://10.0.0.1:11434",
            "http://192.168.1.5:11434",
            "https://ollama.example.com",
            "http://8.8.8.8:11434",
        ],
    )
    def test_non_loopback_urls_do_not_match(self, url):
        assert _is_loopback(url) is False

    def test_default_host_is_loopback(self, monkeypatch):
        monkeypatch.delenv("OLLAMA_HOST", raising=False)
        client = OllamaClient()
        assert client.host == "http://127.0.0.1:11434"

    def test_remote_host_refused_by_default(self, monkeypatch):
        monkeypatch.setenv("OLLAMA_HOST", "http://ollama.example.com:11434")
        with pytest.raises(ValueError, match="non-loopback"):
            OllamaClient()

    def test_remote_host_allowed_with_flag(self, monkeypatch):
        monkeypatch.setenv("OLLAMA_HOST", "http://ollama.example.com:11434")
        client = OllamaClient(allow_remote=True)
        assert client.host == "http://ollama.example.com:11434"

    def test_bare_host_port_normalized_and_validated(self, monkeypatch):
        monkeypatch.setenv("OLLAMA_HOST", "127.0.0.1:11434")
        client = OllamaClient()
        assert client.host == "http://127.0.0.1:11434"
