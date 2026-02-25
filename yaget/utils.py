"""
Utility functions for yaget.

This module contains shared helper functions.
"""

import logging
import os
from typing import Any, Dict


def setup_logging() -> None:
    """Set up basic logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def get_environment_variable(name: str, default: Any = None) -> Any:
    """Get an environment variable with a default value."""
    return os.getenv(name, default)


def validate_file_path(file_path: str) -> bool:
    """Validate that a file path is safe and relative."""
    # Ensure the path is relative and doesn't contain dangerous patterns
    if os.path.isabs(file_path):
        logging.warning(f"Absolute path detected: {file_path}")
        return False
    
    if '..' in file_path:
        logging.warning(f"Parent directory reference detected: {file_path}")
        return False
    
    return True


def dict_to_env_vars(config: Dict[str, Any]) -> Dict[str, str]:
    """Convert a dictionary to environment variable format."""
    return {f"YAGET_{k.upper()}": str(v) for k, v in config.items()}