"""Ollama client integration."""

import ipaddress
import os
import urllib.parse
from typing import Any, Iterator

import ollama

DEFAULT_HOST = "http://127.0.0.1:11434"


def _normalize_host(host: str) -> str:
    """Add http:// to bare host:port forms; the ollama client accepts either."""
    if not host.startswith(("http://", "https://")):
        host = f"http://{host}"
    return host


def _is_loopback(host_url: str) -> bool:
    """Return True if `host_url` points at a loopback address."""
    try:
        parsed = urllib.parse.urlparse(host_url)
    except ValueError:
        return False
    hostname = parsed.hostname
    if hostname is None:
        return False
    if hostname.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        return False


class OllamaClient:
    """Client for interacting with Ollama models."""

    def __init__(self, model: str = "llama3.2", allow_remote: bool = False):
        self.model = model
        raw_host = os.environ.get("OLLAMA_HOST", DEFAULT_HOST)
        self.host = _normalize_host(raw_host)
        if not allow_remote and not _is_loopback(self.host):
            raise ValueError(
                f"Refusing to connect to non-loopback Ollama host: {self.host}\n"
                f"OLLAMA_HOST resolves to a remote endpoint, which means the "
                f"entire conversation (including any local file content the "
                f"agent reads) would be sent there. Pass --allow-remote-ollama "
                f"to permit this explicitly."
            )
        self.client = ollama.Client(host=self.host)

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
