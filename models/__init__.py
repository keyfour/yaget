"""
LLM provider models package
"""

from .base import BaseModel
from .ollama import OllamaModel
from .openai import OpenAIModel


def get_model_provider(args):
    """
    Factory function to get the appropriate model provider
    """
    provider = args.provider.lower()

    if provider == "openai":
        return OpenAIModel(args.model)
    elif provider == "ollama":
        return OllamaModel(args.model, args.ollama_server)
    else:
        raise ValueError(f"Unknown provider: {provider}")
