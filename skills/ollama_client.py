"""Ollama client integration."""

import json
from typing import Any, Iterator

import ollama


class OllamaClient:
    """Client for interacting with Ollama models."""

    def __init__(self, model: str = "llama3.2"):
        self.model = model
        self.client = ollama.Client()

    def list_models(self) -> list[str]:
        """List available models."""
        try:
            response = self.client.list()
            return [model.model for model in response.models]
        except Exception as e:
            print(f"Error listing models: {e}")
            return []

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        stream: bool = False,
    ) -> dict[str, Any] | Iterator[dict[str, Any]]:
        """Send a chat request to Ollama."""
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "stream": stream,
            }

            if tools:
                kwargs["tools"] = tools

            response = self.client.chat(**kwargs)
            return response
        except Exception as e:
            error_msg = f"Error communicating with Ollama: {e}"
            print(error_msg)
            return {
                "message": {
                    "role": "assistant",
                    "content": error_msg,
                }
            }

    def generate(
        self,
        prompt: str,
        stream: bool = False,
    ) -> dict[str, Any] | Iterator[dict[str, Any]]:
        """Generate a response from Ollama."""
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=stream,
            )
            return response
        except Exception as e:
            error_msg = f"Error communicating with Ollama: {e}"
            print(error_msg)
            return {"response": error_msg}
