# yaget/ollama.py

from __future__ import annotations

import logging
import typing as t
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import Any, Callable, Dict, Iterator, List, Optional


@dataclass(frozen=True)
class ConnectionParams:
    """Encapsulates connection details for Ollama API."""

    api_endpoint: str = "https://ollama.com"
    auth_token: Optional[str] = None
    timeout_seconds: float = 30.0


@dataclass(frozen=True)
class RequestContext:
    """Contains request-specific parameters for an Ollama conversation."""

    model_name: str
    system_prompt: str
    conversation_history: List[Dict]
    stream_enabled: bool = False
    think_level: Optional[t.Literal["low", "medium", "high"]] = None


def init_session(api_endpoint: str, auth_token: Optional[str] = None) -> Dict:
    """
    Establishes connection to the Ollama API.

    Args:
        api_endpoint (str): Base URL for the Ollama API
        auth_token (Optional[str]): Authentication token if required

    Returns:
        Dict: Session parameters containing connection details
    """
    return {
        "api_endpoint": api_endpoint,
        "auth_token": auth_token,
        "session_created_at": str(datetime.now()),
    }


def close_session(session_params: Dict) -> None:
    """Closes an existing Ollama session."""
    # In a real implementation, this would handle cleanup
    pass


def get_models(
    ollama_list_fn: Callable[[], List[str]], session_params: Dict
) -> List[str]:
    """
    Retrieves available models from the platform.

    Args:
        ollama_list_fn (Callable): Function to list available models
        session_params (Dict): Connection parameters

    Returns:
        List[str]: Available model names
    """
    return ollama_list_fn()


def pull_model(
    ollama_pull_fn: Callable[[str, Dict], bool], model_name: str, session_params: Dict
) -> bool:
    """
    Downloads and caches a specific model.

    Args:
        ollama_pull_fn (Callable): Function to pull models
        model_name (str): Name of the model to download
        session_params (Dict): Connection parameters

    Returns:
        bool: Success status
    """
    return ollama_pull_fn(model_name, session_params)


def chat(
    ollama_chat_fn: Callable,
    message: Dict[str, str],
    context: RequestContext,
    history: List[Dict],
) -> Dict[str, Any]:
    """
    Initiates a conversation with the specified model.

    Args:
        message (Dict): User message to send
        context (RequestContext): Request context including system prompt
        history (List[Dict]): Conversation history
        session_params (Dict): Connection parameters

    Returns:
        Dict[str, Any]: Response from the model
    """
    try:
        _validate_message(message)
        response = ollama_chat_fn(
            model=context.model_name,
            messages=[
                {"role": "system", "content": context.system_prompt},
                *[{"role": m["role"], "content": m["content"]} for m in history],
                {"role": message["role"], "content": message["content"]},
            ],
            tools=None,  # Placeholder for future tool integration
            stream=context.stream_enabled,
            think=context.think_level,
        )

        if isinstance(response, Iterator):
            return next(response)
        elif not response:
            raise ValueError("Empty or invalid response received")
        else:
            return response

    except Exception as e:
        logging.error(f"Failed to chat: {str(e)}")
        return {}


def request(ollama_chat_fn: Callable, message_text: str, context_params: Dict) -> str:
    """
    Sends a single message without maintaining conversation state.

    Args:
        ollama_chat_fn (Callable): Ollama chat function
        message_text (str): User input
        context_params (Dict): Request context

    Returns:
        str: Model's response
    """
    return chat(
        ollama_chat_fn,
        {"role": "user", "content": message_text},
        RequestContext(**context_params),
        history=[],
    )["message"]["content"]


@lru_cache(maxsize=128)
def get_cached_models(ollama_list_fn, session_params: Dict) -> List[str]:
    return get_models(ollama_list_fn, session_params)


def _validate_message(message: Dict[str, str]) -> None:
    required_fields = {"role", "content"}
    if not all(k in message for k in required_fields):
        raise ValueError("Message must contain 'role' and 'content' fields")
