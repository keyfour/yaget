"""
File utilities for working with files and directories
"""

import os
import shutil
import tempfile
from .console import console


def ensure_directory_exists(directory):
    """
    Ensure a directory exists, creating it if necessary

    Args:
        directory (str): The directory to check
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        console.print(f"[bold green]✔[/bold green] Created directory {directory}")


def get_file_extension(file_path):
    """
    Get the extension of a file

    Args:
        file_path (str): The path to the file

    Returns:
        str: The file extension
    """
    return os.path.splitext(file_path)[1].lower()


def count_files(directory, extensions=None):
    """
    Count the number of files in a directory with specific extensions

    Args:
        directory (str): The directory to count files in
        extensions (list): List of file extensions to count

    Returns:
        int: The number of files
    """
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if extensions is None or get_file_extension(file) in extensions:
                count += 1
    return count


def safe_write_file(file_path, content):
    """
    Safely write content to a file, using a temporary file first

    Args:
        file_path (str): The path to write to
        content (str): The content to write
    """
    # Create directory if it doesn't exist
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # Write to a temporary file first
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write(content)

    # Replace the original file with the temporary file
    shutil.move(temp_file.name, file_path)


def read_file_safely(file_path, encoding="utf-8"):
    """
    Safely read a file with fallback encodings

    Args:
        file_path (str): The path to read from
        encoding (str): The encoding to use

    Returns:
        str: The file contents
    """
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with a different encoding
        try:
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()
        except Exception as e:
            console.print(
                f"[bold red]Error:[/bold red] Failed to read file {file_path}: {e}"
            )
            return None
    except Exception as e:
        console.print(
            f"[bold red]Error:[/bold red] Failed to read file {file_path}: {e}"
        )
        return None
