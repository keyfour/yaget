"""
Configuration management for yaget.

This module loads and manages configuration settings from environment variables.
"""

import os
from typing import Optional


# Default configuration values
DEFAULT_MODEL = "codellama:7b"
DEFAULT_CONTEXT_SIZE = 2048
DEFAULT_TEMPERATURE = 0.2


# Configuration settings
_model_name: Optional[str] = None
_context_size: Optional[int] = None
_temperature: Optional[float] = None


def load_config(
    model_name: Optional[str] = None,
    context_size: Optional[int] = None,
    temperature: Optional[float] = None,
) -> None:
    """
    Load configuration from environment variables or parameters.
    
    Args:
        model_name: Override model name (defaults to environment variable)
        context_size: Override context size (defaults to environment variable)
        temperature: Override temperature (defaults to environment variable)
    """
    global _model_name, _context_size, _temperature
    
    # Load from environment variables if not provided
    _model_name = model_name or os.getenv("YAGET_MODEL", DEFAULT_MODEL)
    _context_size = context_size or int(os.getenv("YAGET_CONTEXT_SIZE", str(DEFAULT_CONTEXT_SIZE)))
    _temperature = temperature or float(os.getenv("YAGET_TEMPERATURE", str(DEFAULT_TEMPERATURE)))


def get_model_name() -> str:
    """Get the configured model name."""
    return _model_name or DEFAULT_MODEL


def get_context_size() -> int:
    """Get the configured context size."""
    return _context_size or DEFAULT_CONTEXT_SIZE


def get_temperature() -> float:
    """Get the configured temperature."""
    return _temperature or DEFAULT_TEMPERATURE