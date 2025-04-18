"""
Ollama model provider implementation
"""

import json
import requests
from .base import BaseModel
from utils.console import console


class OllamaModel(BaseModel):
    """Ollama model provider implementation"""

    def __init__(self, model_name, server_url="http://localhost:11434"):
        """
        Initialize the Ollama model provider

        Args:
            model_name (str): The name of the model to use
            server_url (str): The URL of the Ollama server
        """
        super().__init__(model_name)
        self.server_url = server_url.rstrip("/")
        self._check_connection()

    def _check_connection(self):
        """Check the connection to the Ollama server"""
        try:
            response = requests.get(f"{self.server_url}/api/version")
            if response.status_code == 200:
                version_info = response.json()
                console.print(
                    f"[bold green]✔[/bold green] Connected to Ollama server (version {version_info.get('version', 'unknown')})"
                )
            else:
                console.print(
                    f"[bold yellow]⚠[/bold yellow] Connected to Ollama server but received unexpected status code: {response.status_code}"
                )
        except requests.RequestException as e:
            console.print(
                f"[bold red]✖[/bold red] Failed to connect to Ollama server at {self.server_url}: {e}"
            )
            raise ConnectionError(
                f"Failed to connect to Ollama server at {self.server_url}: {e}"
            )

    def generate(self, prompt, **kwargs):
        """
        Generate text from a prompt using Ollama

        Args:
            prompt (str): The prompt to generate text from
            **kwargs: Additional Ollama-specific arguments

        Returns:
            str: The generated text
        """
        payload = {"model": self.model_name, "prompt": prompt, **kwargs}

        try:
            response = requests.post(f"{self.server_url}/api/generate", json=payload)
            response.raise_for_status()

            # Ollama returns a stream of JSON objects, one per line
            # The last line has the full response
            lines = response.text.strip().split("\n")
            last_response = json.loads(lines[-1])

            return last_response.get("response", "")
        except requests.RequestException as e:
            console.print(f"[bold red]Error:[/bold red] Failed to generate text: {e}")
            raise

    def chat(self, messages, **kwargs):
        # Ensure we're using 'user' as the default role for any unrecognized roles
        ollama_messages = []
        for message in messages:
            role = message.get("role", "user")  # Default to user if no role specified
            content = message.get("content")

            if not (role and content):
                continue

            ollama_messages.append({"role": role, "content": content})

        payload = {
            "model": self.model_name,  # Make sure this matches the Ollama model name
            "messages": ollama_messages,
            "stream": False,
        }

        try:

            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"{self.server_url}/api/chat", json=payload, headers=headers
            )
            response.raise_for_status()

            response_data = response.json()
            return response_data.get("message", {}).get("content", "")
        except requests.RequestException as e:
            console.print(f"[bold red]Error:[/bold red] Failed to chat: {e}")
            raise
