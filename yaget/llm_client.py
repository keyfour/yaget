"""
LLM client interface for yaget.

This module provides an abstract interface for interacting with local LLMs.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate_code(self, prompt: str) -> Optional[str]:
        """
        Generate code from a prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            Generated code as a string, or None if generation failed
        """
        pass


class OllamaClient(LLMClient):
    """LLM client implementation for Ollama."""

    def __init__(self, model_name: str = "codellama:7b"):
        self.model_name = model_name
        self._import_ollama()

    def _import_ollama(self):
        """Import ollama library and handle import errors."""
        try:
            import ollama
            self.ollama = ollama
        except ImportError:
            logging.error("ollama library not found. Please install with: pip install ollama")
            raise
        except Exception as e:
            logging.error(f"Error importing ollama: {e}")
            raise

    def generate_code(self, prompt: str) -> Optional[str]:
        """Generate code from a prompt using Ollama."""
        try:
            response = self.ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a code generation assistant. Generate clean, working code based on the requirements."},
                    {"role": "user", "content": prompt}
                ],
                stream=False,
            )
            
            if response and "message" in response and "content" in response["message"]:
                return response["message"]["content"].strip()
            else:
                logging.warning("Empty or invalid response from LLM")
                return None
                
        except Exception as e:
            logging.error(f"Error generating code: {e}")
            return None


# Global LLM client instance
_llm_client = None

def get_llm_client(model_name: str = "codellama:7b") -> LLMClient:
    """Get the global LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = OllamaClient(model_name)
    return _llm_client

def generate_code(prompt: str) -> Optional[str]:
    """Generate code from a prompt using the global LLM client."""
    client = get_llm_client()
    return client.generate_code(prompt)