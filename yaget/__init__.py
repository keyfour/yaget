__init__.py

# Package initialization for yaget

from .cli import main
from .parser import parse_requirements_file
from .splitter import split_content
from .llm_client import get_llm_client, generate_code
from .writer import write_code_to_file
from .config import load_config, get_model_name, get_context_size, get_temperature
from .utils import setup_logging, get_environment_variable, validate_file_path

__version__ = "0.1.0"
__all__ = [
    "main",
    "parse_requirements_file",
    "split_content",
    "get_llm_client",
    "generate_code",
    "write_code_to_file",
    "load_config",
    "get_model_name",
    "get_context_size",
    "get_temperature",
    "setup_logging",
    "get_environment_variable",
    "validate_file_path",
    "__version__",
]