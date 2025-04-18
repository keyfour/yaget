"""
Base model interface for LLM providers
"""

from abc import ABC, abstractmethod


class BaseModel(ABC):
    """Base class for all model providers"""

    def __init__(self, model_name):
        """Initialize the model provider"""
        self.model_name = model_name

    @abstractmethod
    def generate(self, prompt, **kwargs):
        """
        Generate text from a prompt

        Args:
            prompt (str): The prompt to generate text from
            **kwargs: Additional provider-specific arguments

        Returns:
            str: The generated text
        """
        pass

    @abstractmethod
    def chat(self, messages, **kwargs):
        """
        Generate a response in a chat conversation

        Args:
            messages (list): List of message dictionaries (role, content)
            **kwargs: Additional provider-specific arguments

        Returns:
            str: The generated response
        """
        pass
