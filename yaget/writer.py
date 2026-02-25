"""
Code writing utilities for yaget.

This module handles writing generated code to the filesystem.
"""

import os
import logging
from pathlib import Path


def write_code_to_file(file_path: str, code: str) -> None:
    """
    Write generated code to a file.
    
    Args:
        file_path: Relative path where code should be written
        code: The code to write
    """
    try:
        # Create directory if it doesn't exist
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        # Write the code to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
            f.write('\n')  # Ensure file ends with newline
        
        logging.info(f"Successfully wrote code to: {file_path}")
        
    except Exception as e:
        logging.error(f"Error writing code to {file_path}: {e}")
        raise


def validate_code_syntax(file_path: str) -> bool:
    """
    Perform basic syntax validation on generated code.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        True if syntax is valid, False otherwise
    """
    try:
        # Try to compile Python code (if it's a .py file)
        if file_path.endswith('.py'):
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            compile(code, file_path, 'exec')
            return True
        
        return True  # Assume valid for non-Python files
        
    except SyntaxError as e:
        logging.warning(f"Syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        logging.error(f"Error validating syntax in {file_path}: {e}")
        return False