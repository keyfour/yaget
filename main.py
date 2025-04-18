#!/usr/bin/env python3
"""
YAGET - Yet Another Generator for Enhancing Tasks
Main entry point for the application
"""

import os
import sys
from dotenv import load_dotenv
from cli import parse_args
from utils.console import console
from utils.cache import check_cache, save_cache
from models import get_model_provider
from scanners import get_scanner


def main():
    """Main entry point for the application"""
    # Parse command-line arguments
    args = parse_args()

    # Load environment variables
    load_environment(args.dotenv_path)

    # Get the model provider
    model = get_model_provider(args)

    # Handle subcommands
    if args.command == "scan":
        handle_scan_command(args, model)
    elif args.command == "chat":
        handle_chat_command(args, model)
    else:
        console.print("[bold red]Error:[/bold red] Unknown command")
        sys.exit(1)


def load_environment(dotenv_path=None):
    """Load environment variables from a .env file if provided."""
    if dotenv_path:
        load_dotenv(dotenv_path)
    else:
        load_dotenv(
            ".env"
        )  # Default to loading from the .env file in the current directory

    # Check for required environment variables based on provider
    provider = os.getenv("PROVIDER", "openai").lower()
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            console.print(
                "[bold red]Error:[/bold red] OPENAI_API_KEY is not set in the .env file or environment."
            )
            raise ValueError(
                "OPENAI_API_KEY is not set in the .env file or environment."
            )
    elif provider == "ollama":
        # Verify Ollama server can be accessed
        try:
            import requests

            server_url = os.getenv("OLLAMA_SERVER", "http://localhost:11434")
            response = requests.get(f"{server_url}/api/version")
            if response.status_code != 200:
                console.print(
                    f"[bold yellow]Warning:[/bold yellow] Ollama server returned status code {response.status_code}"
                )
        except Exception as e:
            console.print(
                f"[bold yellow]Warning:[/bold yellow] Could not connect to Ollama server: {e}"
            )

    console.print(
        "[bold green]✔[/bold green] Environment variables loaded successfully."
    )


def handle_scan_command(args, model):
    """Handle the scan subcommand"""
    # Check if we should use cached data
    cached_data = None
    if not args.force_scan:
        cached_data = check_cache(args.directory)

    # If no cached data or force scan is enabled, perform a new scan
    if cached_data is None or args.force_scan:
        console.print(
            f"🔍 Scanning directory [bold]{args.directory}[/bold]...", style="bold cyan"
        )

        # Get the requested scanners
        scanners = []
        if args.scan_todo:
            scanners.append(get_scanner("todo", args))
        if args.scan_code:
            scanners.append(get_scanner("code", args))
        if args.scan_pdf:
            scanners.append(get_scanner("pdf", args))
        if args.scan_text:
            scanners.append(get_scanner("text", args))

        # If no scanners were specified, use all of them
        if not scanners:
            console.print("No scanner specified, using all scanners.")
            scanners.append(get_scanner("todo", args))
            scanners.append(get_scanner("code", args))
            scanners.append(get_scanner("pdf", args))
            scanners.append(get_scanner("text", args))

        # Run each scanner
        results = {}
        for scanner in scanners:
            scanner_name = scanner.__class__.__name__
            console.print(f"Running [bold]{scanner_name}[/bold]...")
            results[scanner_name] = scanner.scan(args.directory)

        # Save results to cache if not disabled
        if not args.no_cache:
            save_cache(args.directory, results)

        # Process results with the model
        if args.process:
            for scanner_name, scanner_results in results.items():
                console.print(f"Processing results from [bold]{scanner_name}[/bold]...")
                scanner = next(
                    (s for s in scanners if s.__class__.__name__ == scanner_name), None
                )
                if scanner:
                    processed_results = scanner.process_with_model(
                        scanner_results, model
                    )
                    scanner.display_results(processed_results)
    else:
        console.print("[bold green]✔[/bold green] Using cached data.")
        # Process cached results with the model if needed
        if args.process:
            console.print("Processing cached results...")
            for scanner_name, scanner_results in cached_data.items():
                if scanner_name.endswith("Scanner"):
                    scanner_type = scanner_name.lower().replace("scanner", "").strip()
                    try:
                        scanner = get_scanner(scanner_type, args)
                        console.print(
                            f"Processing results from [bold]{scanner_name}[/bold]..."
                        )
                        processed_results = scanner.process_with_model(
                            scanner_results, model
                        )
                        scanner.display_results(processed_results)
                    except ValueError:
                        console.print(
                            f"[bold yellow]Warning:[/bold yellow] Could not process results from {scanner_name}"
                        )


def handle_chat_command(args, model):
    """Handle the chat subcommand"""
    from chat.session import ChatSession

    # Create a new chat session
    session = ChatSession(model, args.directory, args.max_context_size)

    # Start the interactive chat
    session.start()


if __name__ == "__main__":
    main()
