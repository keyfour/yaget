"""
Base scanner interface for all scanner types
"""

from abc import ABC, abstractmethod
import os
from utils.console import console


class BaseScanner(ABC):
    """Base class for all scanners"""

    def __init__(self):
        """Initialize the scanner"""
        pass

    @abstractmethod
    def scan(self, directory):
        """
        Scan a directory for specific content

        Args:
            directory (str): The directory to scan

        Returns:
            dict: The scan results
        """
        pass

    @abstractmethod
    def process_with_model(self, scan_results, model):
        """
        Process scan results with a model

        Args:
            scan_results (dict): The results from the scan
            model (BaseModel): The model to use for processing

        Returns:
            dict: The processed results
        """
        pass

    @abstractmethod
    def display_results(self, processed_results):
        """
        Display the processed results

        Args:
            processed_results (dict): The processed results
        """
        pass

    def load_ignore_list(self, directory):
        """
        Load the list of files or directories to ignore from a .yagetignore file.

        Args:
            directory (str): The directory containing the .yagetignore file

        Returns:
            list: The list of patterns to ignore
        """
        ignore_list = []
        ignore_file_path = os.path.join(directory, ".yagetignore")
        if os.path.exists(ignore_file_path):
            with open(ignore_file_path, "r") as ignore_file:
                ignore_list = [
                    line.strip()
                    for line in ignore_file.readlines()
                    if line.strip() and not line.startswith("#")
                ]
            console.print(
                f"[bold green]✔[/bold green] Loaded ignore list from {ignore_file_path}"
            )
        return ignore_list

    def should_ignore(self, path, ignore_list, directory):
        """
        Determine if a given path should be ignored based on the ignore list.

        Args:
            path (str): The path to check
            ignore_list (list): The list of patterns to ignore
            directory (str): The base directory

        Returns:
            bool: True if the path should be ignored, False otherwise
        """
        rel_path = os.path.relpath(path, directory)
        for ignore_entry in ignore_list:
            if ignore_entry.endswith("/"):
                # Ignore directories and all files within them
                if rel_path.startswith(ignore_entry.rstrip("/")):
                    return True
            else:
                # Ignore specific files
                if rel_path == ignore_entry:
                    return True
        return False

    def list_files(self, directory, ignore_list, extensions=None):
        """
        List files in a directory with specific extensions

        Args:
            directory (str): The directory to scan
            ignore_list (list): The list of patterns to ignore
            extensions (list): The list of file extensions to include

        Returns:
            list: The list of file paths
        """
        if extensions is None:
            extensions = [".py", ".cpp", ".h", ".java", ".js", ".html", ".sh"]

        files = []
        for root, dirs, filenames in os.walk(directory):
            # Remove directories from the scan if they are in the ignore list
            dirs[:] = [
                d
                for d in dirs
                if not self.should_ignore(os.path.join(root, d), ignore_list, directory)
            ]
            for filename in filenames:
                file_path = os.path.join(root, filename)
                if any(
                    filename.endswith(ext) for ext in extensions
                ) and not self.should_ignore(file_path, ignore_list, directory):
                    files.append(file_path)
        return files
