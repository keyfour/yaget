"""
Command-line interface module for the YAGET application
"""

import argparse
import os


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="YAGET - Yet Another Generator for Enhancing Tasks"
    )

    # Common arguments
    parser.add_argument("--dotenv_path", help="Path to the .env file")

    # Model provider configuration
    parser.add_argument(
        "--provider",
        choices=["openai", "ollama"],
        default=os.getenv("PROVIDER", "openai"),
        help="LLM provider to use (default: openai)",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("MODEL", "gpt-3.5-turbo"),
        help="Model name to use (default: gpt-3.5-turbo)",
    )
    parser.add_argument(
        "--ollama_server",
        default=os.getenv("OLLAMA_SERVER", "http://localhost:11434"),
        help="Ollama server URL (default: http://localhost:11434)",
    )

    # Embedding model configuration
    parser.add_argument(
        "--embedding_provider",
        choices=["openai", "ollama"],
        default=os.getenv("EMBEDDING_PROVIDER", None),
        help="Provider to use for embeddings (defaults to --provider if not specified)",
    )
    parser.add_argument(
        "--embedding_model",
        default=os.getenv("EMBEDDING_MODEL", None),
        help="Model to use for embeddings (defaults to appropriate model for provider)",
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Scan command
    scan_parser = subparsers.add_parser(
        "scan", help="Scan files and generate suggestions"
    )
    scan_parser.add_argument("directory", help="Path to the directory to scan")
    scan_parser.add_argument(
        "--scan_todo", action="store_true", help="Scan for TODO comments"
    )
    scan_parser.add_argument(
        "--scan_code", action="store_true", help="Scan and analyze code structure"
    )
    scan_parser.add_argument(
        "--scan_pdf", action="store_true", help="Scan for PDF files and extract content"
    )
    scan_parser.add_argument(
        "--scan_text",
        action="store_true",
        help="Scan for text files (md, txt, etc.) and extract content",
    )
    scan_parser.add_argument(
        "--force_scan",
        action="store_true",
        help="Force a new scan even if cached data exists",
    )
    scan_parser.add_argument(
        "--no_cache", action="store_true", help="Don't cache scan results"
    )
    scan_parser.add_argument(
        "--process", action="store_true", help="Process scan results with the LLM"
    )
    scan_parser.add_argument(
        "--before_lines",
        type=int,
        default=2,
        help="Number of lines before TODO to include in the context",
    )
    scan_parser.add_argument(
        "--max_lines_after",
        type=int,
        default=10,
        help="Maximum number of lines to follow after TODO in search of ENDTODO",
    )
    scan_parser.add_argument(
        "--extensions",
        nargs="+",
        default=[".py", ".cpp", ".h", ".java", ".js", ".html", ".sh"],
        help="File extensions to scan for code/TODOs",
    )
    scan_parser.add_argument(
        "--text_extensions",
        nargs="+",
        default=[
            ".txt",
            ".md",
            ".rst",
            ".json",
            ".yaml",
            ".yml",
            ".ini",
            ".conf",
            ".config",
        ],
        help="File extensions to scan for text content",
    )
    scan_parser.add_argument(
        "--use_embeddings",
        action="store_true",
        help="Generate embeddings for PDF and text content",
    )

    # Chat command
    chat_parser = subparsers.add_parser(
        "chat", help="Start an interactive chat session"
    )
    chat_parser.add_argument(
        "directory", help="Path to the directory to use as context"
    )
    chat_parser.add_argument(
        "--max_context_size",
        type=int,
        default=10,
        help="Maximum number of messages to keep in context",
    )
    chat_parser.add_argument(
        "--load_session", help="Path to a previous chat session to load"
    )
    chat_parser.add_argument("--save_session", help="Path to save the chat session")
    chat_parser.add_argument(
        "--use_embeddings",
        action="store_true",
        help="Use embeddings for semantic search during chat",
    )

    args = parser.parse_args()

    # If no subcommand is provided, show help
    if args.command is None:
        parser.print_help()
        exit(1)

    return args
