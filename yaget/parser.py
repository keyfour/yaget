"""
Markdown parsing and section extraction for yaget.

This module extracts sections from Markdown files where each top-level heading (#) specifies a relative file path.
"""

import re
from typing import List, Tuple


def parse_requirements_file(file_path: str) -> List[Tuple[str, str]]:
    """
    Parse a Markdown requirements file and extract sections.
    
    Args:
        file_path: Path to the Markdown file
        
    Returns:
        List of tuples containing (file_path, content) for each section
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Requirements file not found: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Error reading requirements file: {e}")

    # Find all top-level headings and their content
    pattern = r'^#\s+(.*?)\n((?:^.*\n?)*?)(?=^#|$)'
    matches = re.findall(pattern, content, re.MULTILINE)

    sections = []
    for heading, section_content in matches:
        # Clean up the heading and section content
        file_path = heading.strip()
        content = section_content.strip()
        
        if file_path and content:
            sections.append((file_path, content))

    return sections