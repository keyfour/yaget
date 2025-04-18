"""
Cache utilities for storing and retrieving scan results
"""

import os
import json
import hashlib
import time
from datetime import datetime
from .console import console

# Cache directory name
CACHE_DIR = ".yaget_cache"


def get_directory_hash(directory):
    """
    Generate a hash of the directory structure and modification times

    Args:
        directory (str): The directory to hash

    Returns:
        str: Hash of the directory
    """
    dir_hash = hashlib.md5()

    # Get all files recursively
    all_files = []
    for root, dirs, files in os.walk(directory):
        # Skip the cache directory
        if CACHE_DIR in root:
            continue

        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)

    # Sort files for consistent hashing
    all_files.sort()

    # Hash file paths and modification times
    for file_path in all_files:
        try:
            mtime = os.path.getmtime(file_path)
            dir_hash.update(f"{file_path}:{mtime}".encode())
        except Exception:
            # Skip files that can't be accessed
            pass

    return dir_hash.hexdigest()


def get_cache_path(directory):
    """
    Get the path to the cache file for a directory

    Args:
        directory (str): The directory to get the cache path for

    Returns:
        str: Path to the cache file
    """
    # Create cache directory if it doesn't exist
    cache_dir = os.path.join(directory, CACHE_DIR)
    os.makedirs(cache_dir, exist_ok=True)

    # Return path to the cache file
    return os.path.join(cache_dir, "scan_cache.json")


def check_cache(directory):
    """
    Check if there's a valid cache for a directory

    Args:
        directory (str): The directory to check

    Returns:
        dict: The cached data, or None if no valid cache exists
    """
    cache_path = get_cache_path(directory)

    # Check if cache file exists
    if not os.path.exists(cache_path):
        return None

    # Load cache file
    try:
        with open(cache_path, "r") as f:
            cache = json.load(f)
    except Exception as e:
        console.print(f"[bold yellow]Warning:[/bold yellow] Failed to load cache: {e}")
        return None

    # Check if hash matches
    current_hash = get_directory_hash(directory)
    cached_hash = cache.get("directory_hash")

    if current_hash != cached_hash:
        console.print(
            "[bold yellow]Cache is outdated.[/bold yellow] Directory structure has changed."
        )
        return None

    # Check if cache is too old (1 day)
    cache_time = cache.get("timestamp", 0)
    if time.time() - cache_time > 86400:  # 24 hours in seconds
        console.print("[bold yellow]Cache is older than 24 hours.[/bold yellow]")
        return None

    console.print(
        f"[bold green]✔[/bold green] Found valid cache from {datetime.fromtimestamp(cache_time).strftime('%Y-%m-%d %H:%M:%S')}"
    )
    return cache.get("data")


def save_cache(directory, data):
    """
    Save data to the cache

    Args:
        directory (str): The directory to save the cache for
        data (dict): The data to save
    """
    cache_path = get_cache_path(directory)

    # Create cache data
    cache = {
        "directory_hash": get_directory_hash(directory),
        "timestamp": time.time(),
        "data": data,
    }

    # Save cache to file
    try:
        with open(cache_path, "w") as f:
            json.dump(cache, f, indent=2)
        console.print(f"[bold green]✔[/bold green] Saved cache to {cache_path}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Failed to save cache: {e}")
