"""
OpenAI model provider implementation
"""

import os
from langchain_openai import ChatOpenAI
from .base import BaseModel
from utils.console import console


class OpenAIModel(BaseModel):
    """OpenAI model provider implementation"""

    def __init__(self, model_name="gpt-3.5-turbo"):
        """
        Initialize the OpenAI model provider

        Args:
            model_name (str): The name of the model to use
        """
        super().__init__(model_name)
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set in the environment")

        self.llm = ChatOpenAI(openai_api_key=self.api_key, model_name=model_name)

    def generate(self, prompt, **kwargs):
        """
        Generate text from a prompt using OpenAI

        Args:
            prompt (str): The prompt to generate text from
            **kwargs: Additional OpenAI-specific arguments

        Returns:
            str: The generated text
        """
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] Failed to generate text: {e}")
            raise

    def chat(self, messages, **kwargs):
        """
        Generate a response in a chat conversation using OpenAI

        Args:
            messages (list): List of message dictionaries (role, content)
            **kwargs: Additional OpenAI-specific arguments

        Returns:
            str: The generated response
        """
        try:
            # LangChain's ChatOpenAI expects a specific format
            # Convert the messages to the expected format if needed
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] Failed to chat: {e}")
            raise
