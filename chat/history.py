"""
Chat history management module
"""

import json
import os


class ChatHistory:
    """Manages chat history and context window for chat sessions"""

    def __init__(self, max_size=10):
        """
        Initialize chat history

        Args:
            max_size (int): Maximum number of messages to keep in context
        """
        self.max_size = max_size
        self.messages = []

    def add_message(self, role, content):
        """
        Add a message to the history

        Args:
            role (str): The role of the message sender ('system', 'user', or 'assistant')
            content (str): The message content
        """
        self.messages.append({"role": role, "content": content})

        # Trim history if it exceeds the maximum size
        # Keep the system message and the most recent messages
        if len(self.messages) > self.max_size + 1:
            # If the first message is a system message, preserve it
            if self.messages[0]["role"] == "system":
                self.messages = [self.messages[0]] + self.messages[-(self.max_size) :]
            else:
                self.messages = self.messages[-self.max_size :]

    def get_messages(self):
        """
        Get all messages in the history

        Returns:
            list: List of message dictionaries
        """
        return self.messages

    def clear(self):
        """Clear all messages except system messages"""
        self.messages = [msg for msg in self.messages if msg["role"] == "system"]

    def save_to_file(self, file_path):
        """
        Save the chat history to a file

        Args:
            file_path (str): Path to save the history to
        """
        with open(file_path, "w") as f:
            json.dump(self.messages, f, indent=2)

    def load_from_file(self, file_path):
        """
        Load chat history from a file

        Args:
            file_path (str): Path to load the history from
        """
        if not os.path.exists(file_path):
            return

        with open(file_path, "r") as f:
            self.messages = json.load(f)
