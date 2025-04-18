"""
Scanners package for scanning different file types and content
"""

from .base import BaseScanner
from .todo_scanner import TodoScanner
from .code_scanner import CodeScanner
from .pdf_scanner import PdfScanner
from .text_scanner import TextScanner


def get_scanner(scanner_type, args):
    """
    Factory function to get the appropriate scanner

    Args:
        scanner_type (str): The type of scanner to get
        args: Command-line arguments

    Returns:
        BaseScanner: An instance of the requested scanner
    """
    if scanner_type == "todo":
        return TodoScanner(
            before_lines=args.before_lines,
            max_lines_after=args.max_lines_after,
            extensions=args.extensions,
        )
    elif scanner_type == "code":
        return CodeScanner(extensions=args.extensions)
    elif scanner_type == "pdf":
        return PdfScanner()
    elif scanner_type == "text":
        return TextScanner(extensions=getattr(args, "text_extensions", None))
    else:
        raise ValueError(f"Unknown scanner type: {scanner_type}")
