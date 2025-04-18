"""
Enhanced chat session module with PDF and text embeddings for better context
"""

import os
import json
import datetime
from rich.markdown import Markdown
from utils.console import console
from utils.file_utils import ensure_directory_exists
from utils.cache import check_cache
from .history import ChatHistory


class ChatSession:
    """Interactive chat session with a model using enhanced context"""

    def __init__(self, model, context_directory, max_context_size=10):
        """
        Initialize a chat session

        Args:
            model: The model to use for chat
            context_directory (str): Directory to use as context
            max_context_size (int): Maximum number of messages to keep in context
        """
        self.model = model
        self.context_directory = context_directory
        self.max_context_size = max_context_size
        self.history = ChatHistory(max_size=max_context_size)

        # Load cached scan data if available
        self.cached_data = None
        cached_data = check_cache(context_directory)
        if cached_data:
            self.cached_data = cached_data
            console.print(
                "[bold green]✔[/bold green] Loaded cached scan data for context"
            )

        # Initialize embeddings containers
        self.pdf_embeddings = None
        self.text_embeddings = None

        # Load embeddings from cache if available
        if self.cached_data:
            # Check if there's PDF data with embeddings
            for key, data in self.cached_data.items():
                # Load PDF embeddings
                if (
                    key.endswith("Scanner")
                    and "pdf_files" in data
                    and "embeddings" in data
                ):
                    self.pdf_embeddings = data["embeddings"]
                    console.print(
                        "[bold green]✔[/bold green] Loaded PDF embeddings for semantic search"
                    )

                # Load text embeddings
                if (
                    key.endswith("Scanner")
                    and "text_files" in data
                    and "embeddings" in data
                ):
                    self.text_embeddings = data["embeddings"]
                    console.print(
                        "[bold green]✔[/bold green] Loaded text embeddings for semantic search"
                    )

        # Add a system message to initialize the chat
        system_message = self._create_system_message()
        self.history.add_message("system", system_message)

    def _create_system_message(self):
        """
        Create a system message to initialize the chat

        Returns:
            str: The system message
        """
        system_msg = (
            f"You are an AI assistant that helps with development tasks. "
            f"You have access to code and content in the directory: {self.context_directory}. "
            f"Use this context to provide helpful answers and suggestions. "
        )

        # Add information about available scan data
        if self.cached_data:
            system_msg += "You have access to the following scan data:\n"

            for key, data in self.cached_data.items():
                if key.endswith("Scanner") and "todo" in key.lower():
                    todo_count = len(data) if isinstance(data, list) else 0
                    system_msg += f"- TODO comments: {todo_count} items\n"

                if key.endswith("Scanner") and "code" in key.lower():
                    if isinstance(data, dict) and "stats" in data:
                        files = data["stats"].get("total_files", 0)
                        system_msg += f"- Code structure: {files} files analyzed\n"

                if key.endswith("Scanner") and "pdf" in key.lower():
                    if isinstance(data, dict) and "stats" in data:
                        pdfs = data["stats"].get("total_pdfs", 0)
                        system_msg += f"- PDF documents: {pdfs} files analyzed\n"

                if key.endswith("Scanner") and "text_files" in data:
                    if isinstance(data, dict) and "stats" in data:
                        text_files = data["stats"].get("total_files", 0)
                        system_msg += f"- Text files: {text_files} files analyzed\n"

        # Add information about available embeddings
        if self.pdf_embeddings and self.pdf_embeddings.get("status") == "success":
            system_msg += "- PDF content is available for semantic search\n"

        if self.text_embeddings and self.text_embeddings.get("status") == "success":
            system_msg += "- Text content is available for semantic search\n"

        system_msg += f"\nCurrent date and time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return system_msg

    def start(self):
        """Start the interactive chat session"""
        console.print("[bold cyan]Starting chat mode...[/bold cyan]")
        console.print(
            "Type [bold yellow]'exit'[/bold yellow] or [bold yellow]'quit'[/bold yellow] to end the session."
        )
        console.print(
            "Type [bold yellow]'save'[/bold yellow] to save the chat history."
        )
        console.print("Type [bold yellow]'help'[/bold yellow] for more commands.")
        console.print()

        # Display the initial assistant message
        self._send_message(
            "Hello! I'm your AI assistant for development tasks. How can I help you today?"
        )

        while True:
            # Get user input
            user_input = console.input("[bold green]You:[/bold green] ")

            # Check for special commands
            if user_input.lower() in ["exit", "quit"]:
                console.print("[bold cyan]Ending chat session.[/bold cyan]")
                break
            elif user_input.lower() == "save":
                self._save_history()
                continue
            elif user_input.lower() == "help":
                self._show_help()
                continue
            elif user_input.lower().startswith("scan "):
                self._handle_scan_command(user_input)
                continue

            # Check if we should enhance the context with document content
            context_additions = []

            # Get PDF context if available
            pdf_context = self._get_relevant_pdf_content(user_input)
            if pdf_context:
                context_additions.append(pdf_context)

            # Get text context if available
            text_context = self._get_relevant_text_content(user_input)
            if text_context:
                context_additions.append(text_context)

            # Add user message to history
            self.history.add_message("user", user_input)

            # Prepare messages with enhanced context if available
            messages = self.history.get_messages()

            # If we have context additions, add them as system messages
            if context_additions:
                # Combine all context additions into a single context message
                combined_context = "\n\n".join(context_additions)
                context_message = {
                    "role": "system",
                    "content": f"Here's relevant information from the project documents that may help answer the query:\n\n{combined_context}",
                }

                # Insert the context message after the initial system message
                messages_with_context = messages.copy()
                # Insert after the first message (which should be the system message)
                messages_with_context.insert(1, context_message)

                # Use the enhanced messages
                response = self.model.chat(messages_with_context)
            else:
                # Use the standard messages
                response = self.model.chat(messages)

            # Add response to history
            self.history.add_message("assistant", response)

            # Display the response
            self._send_message(response)

    def _get_relevant_pdf_content(self, query):
        """
        Get relevant PDF content for a query using embeddings

        Args:
            query (str): The user query

        Returns:
            str: Relevant PDF content or None
        """


"""
Enhanced chat session module with PDF and text embeddings for better context
"""

import os
import json
import datetime
from rich.markdown import Markdown
from utils.console import console
from utils.file_utils import ensure_directory_exists
from utils.cache import check_cache
from .history import ChatHistory


class ChatSession:
    """Interactive chat session with a model using enhanced context"""

    def __init__(self, model, context_directory, max_context_size=10):
        """
        Initialize a chat session

        Args:
            model: The model to use for chat
            context_directory (str): Directory to use as context
            max_context_size (int): Maximum number of messages to keep in context
        """
        self.model = model
        self.context_directory = context_directory
        self.max_context_size = max_context_size
        self.history = ChatHistory(max_size=max_context_size)

        # Load cached scan data if available
        self.cached_data = None
        cached_data = check_cache(context_directory)
        if cached_data:
            self.cached_data = cached_data
            console.print(
                "[bold green]✔[/bold green] Loaded cached scan data for context"
            )

        # Initialize embeddings containers
        self.pdf_embeddings = None
        self.text_embeddings = None

        # Load embeddings from cache if available
        if self.cached_data:
            # Check if there's PDF data with embeddings
            for key, data in self.cached_data.items():
                # Load PDF embeddings
                if (
                    key.endswith("Scanner")
                    and "pdf_files" in data
                    and "embeddings" in data
                ):
                    self.pdf_embeddings = data["embeddings"]
                    console.print(
                        "[bold green]✔[/bold green] Loaded PDF embeddings for semantic search"
                    )

                # Load text embeddings
                if (
                    key.endswith("Scanner")
                    and "text_files" in data
                    and "embeddings" in data
                ):
                    self.text_embeddings = data["embeddings"]
                    console.print(
                        "[bold green]✔[/bold green] Loaded text embeddings for semantic search"
                    )

        # Add a system message to initialize the chat
        system_message = self._create_system_message()
        self.history.add_message("system", system_message)

    def _create_system_message(self):
        """
        Create a system message to initialize the chat

        Returns:
            str: The system message
        """
        system_msg = (
            f"You are an AI assistant that helps with development tasks. "
            f"You have access to code and content in the directory: {self.context_directory}. "
            f"Use this context to provide helpful answers and suggestions. "
        )

        # Add information about available scan data
        if self.cached_data:
            system_msg += "You have access to the following scan data:\n"

            for key, data in self.cached_data.items():
                if key.endswith("Scanner") and "todo" in key.lower():
                    todo_count = len(data) if isinstance(data, list) else 0
                    system_msg += f"- TODO comments: {todo_count} items\n"

                if key.endswith("Scanner") and "code" in key.lower():
                    if isinstance(data, dict) and "stats" in data:
                        files = data["stats"].get("total_files", 0)
                        system_msg += f"- Code structure: {files} files analyzed\n"

                if key.endswith("Scanner") and "pdf" in key.lower():
                    if isinstance(data, dict) and "stats" in data:
                        pdfs = data["stats"].get("total_pdfs", 0)
                        system_msg += f"- PDF documents: {pdfs} files analyzed\n"

                if key.endswith("Scanner") and "text_files" in data:
                    if isinstance(data, dict) and "stats" in data:
                        text_files = data["stats"].get("total_files", 0)
                        system_msg += f"- Text files: {text_files} files analyzed\n"

        # Add information about available embeddings
        if self.pdf_embeddings and self.pdf_embeddings.get("status") == "success":
            system_msg += "- PDF content is available for semantic search\n"

        if self.text_embeddings and self.text_embeddings.get("status") == "success":
            system_msg += "- Text content is available for semantic search\n"

        system_msg += f"\nCurrent date and time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return system_msg

    def start(self):
        """Start the interactive chat session"""
        console.print("[bold cyan]Starting chat mode...[/bold cyan]")
        console.print(
            "Type [bold yellow]'exit'[/bold yellow] or [bold yellow]'quit'[/bold yellow] to end the session."
        )
        console.print(
            "Type [bold yellow]'save'[/bold yellow] to save the chat history."
        )
        console.print("Type [bold yellow]'help'[/bold yellow] for more commands.")
        console.print()

        # Display the initial assistant message
        self._send_message(
            "Hello! I'm your AI assistant for development tasks. How can I help you today?"
        )

        while True:
            # Get user input
            user_input = console.input("[bold green]You:[/bold green] ")

            # Check for special commands
            if user_input.lower() in ["exit", "quit"]:
                console.print("[bold cyan]Ending chat session.[/bold cyan]")
                break
            elif user_input.lower() == "save":
                self._save_history()
                continue
            elif user_input.lower() == "help":
                self._show_help()
                continue
            elif user_input.lower().startswith("scan "):
                self._handle_scan_command(user_input)
                continue

            # Check if we should enhance the context with document content
            context_additions = []

            # Get PDF context if available
            pdf_context = self._get_relevant_pdf_content(user_input)
            if pdf_context:
                context_additions.append(pdf_context)

            # Get text context if available
            text_context = self._get_relevant_text_content(user_input)
            if text_context:
                context_additions.append(text_context)

            # Add user message to history
            self.history.add_message("user", user_input)

            # Prepare messages with enhanced context if available
            messages = self.history.get_messages()

            # If we have context additions, add them as system messages
            if context_additions:
                # Combine all context additions into a single context message
                combined_context = "\n\n".join(context_additions)
                context_message = {
                    "role": "system",
                    "content": f"Here's relevant information from the project documents that may help answer the query:\n\n{combined_context}",
                }

                # Insert the context message after the initial system message
                messages_with_context = messages.copy()
                # Insert after the first message (which should be the system message)
                messages_with_context.insert(1, context_message)

                # Use the enhanced messages
                response = self.model.chat(messages_with_context)
            else:
                # Use the standard messages
                response = self.model.chat(messages)

            # Add response to history
            self.history.add_message("assistant", response)

            # Display the response
            self._send_message(response)

    def _get_relevant_pdf_content(self, query):
        """
        Get relevant PDF content for a query using embeddings

        Args:
            query (str): The user query

        Returns:
            str: Relevant PDF content or None
        """
        if not self.pdf_embeddings or self.pdf_embeddings.get("status") != "success":
            return None

        try:
            # Import the PDF scanner class to use its query method
            from scanners.pdf_scanner import PdfScanner

            scanner = PdfScanner()

            # Query the embeddings
            results = scanner.query_pdf_content(query, self.pdf_embeddings, top_k=3)

            if not results:
                return None

            # Format the results
            context = "PDF Document Context:\n\n"
            for result in results:
                metadata = result.get("metadata", {})
                filename = metadata.get("filename", "Unknown document")
                context += f"From {filename}:\n{result['content']}\n\n"

            return context

        except Exception as e:
            console.print(
                f"[bold yellow]Warning:[/bold yellow] Could not retrieve PDF context: {e}"
            )
            return None

    def _get_relevant_text_content(self, query):
        """
        Get relevant text file content for a query using embeddings

        Args:
            query (str): The user query

        Returns:
            str: Relevant text content or None
        """
        if not self.text_embeddings or self.text_embeddings.get("status") != "success":
            return None

        try:
            # Import the Text scanner class to use its query method
            from scanners.text_scanner import TextScanner

            scanner = TextScanner()

            # Query the embeddings
            results = scanner.query_text_content(query, self.text_embeddings, top_k=3)

            if not results:
                return None

            # Format the results
            context = "Text File Context:\n\n"
            for result in results:
                metadata = result.get("metadata", {})
                filename = metadata.get("filename", "Unknown file")
                file_type = metadata.get("type", "")
                context += f"From {filename} ({file_type}):\n{result['content']}\n\n"

            return context

        except Exception as e:
            console.print(
                f"[bold yellow]Warning:[/bold yellow] Could not retrieve text context: {e}"
            )
            return None

    def _send_message(self, message):
        """
        Display a message from the assistant

        Args:
            message (str): The message to display
        """
        console.print("[bold blue]Assistant:[/bold blue]")

        # Check if message contains markdown
        if "```" in message or "#" in message or "*" in message:
            # Render as markdown
            md = Markdown(message)
            console.print(md)
        else:
            # Render as plain text
            console.print(message)

        console.print()

    def _save_history(self):
        """Save the chat history to a file"""
        # Create the chat directory if it doesn't exist
        chat_dir = os.path.join(self.context_directory, ".yaget_chats")
        ensure_directory_exists(chat_dir)

        # Create a filename with the current date and time
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_{timestamp}.json"
        file_path = os.path.join(chat_dir, filename)

        # Save the history
        with open(file_path, "w") as f:
            json.dump(self.history.get_messages(), f, indent=2)

        console.print(f"[bold green]✔[/bold green] Chat history saved to {file_path}")

    def _show_help(self):
        """Show help text for chat commands"""
        console.print("[bold yellow]Available Commands:[/bold yellow]")
        console.print("- [bold]exit[/bold] or [bold]quit[/bold]: End the chat session")
        console.print("- [bold]save[/bold]: Save the chat history to a file")
        console.print("- [bold]help[/bold]: Show this help text")
        console.print("- [bold]scan <type>[/bold]: Run a scan operation")
        console.print("  - [bold]scan todo[/bold]: Scan for TODOs")
        console.print("  - [bold]scan code[/bold]: Scan code structure")
        console.print("  - [bold]scan pdf[/bold]: Scan PDF files")
        console.print("  - [bold]scan text[/bold]: Scan text files")
        console.print()

    def _handle_scan_command(self, command):
        """
        Handle a scan command in chat mode

        Args:
            command (str): The scan command
        """
        parts = command.split()
        if len(parts) < 2:
            console.print(
                "[bold red]Error:[/bold red] Missing scan type. Use 'scan todo', 'scan code', 'scan pdf', or 'scan text'."
            )
            return

        scan_type = parts[1].lower()

        if scan_type not in ["todo", "code", "pdf", "text"]:
            console.print(f"[bold red]Error:[/bold red] Unknown scan type: {scan_type}")
            return

        # Import the scanner here to avoid circular imports
        from scanners import get_scanner

        # Create a mock args object with default values
        class MockArgs:
            def __init__(self, directory, scan_type):
                self.directory = directory
                self.before_lines = 2
                self.max_lines_after = 10
                self.extensions = [".py", ".cpp", ".h", ".java", ".js", ".html", ".sh"]
                self.text_extensions = [
                    ".txt",
                    ".md",
                    ".rst",
                    ".json",
                    ".yaml",
                    ".yml",
                    ".ini",
                    ".conf",
                    ".config",
                ]
                self.use_embeddings = True

        args = MockArgs(self.context_directory, scan_type)

        # Get the scanner
        scanner = get_scanner(scan_type, args)

        # Run the scan
        console.print(f"[bold cyan]Running {scan_type} scan...[/bold cyan]")
        results = scanner.scan(self.context_directory)

        # Process with model and display results
        processed_results = scanner.process_with_model(results, self.model)
        scanner.display_results(processed_results)

        # Update cached data
        if not self.cached_data:
            self.cached_data = {}
        self.cached_data[scanner.__class__.__name__] = results

        # Update embeddings if this was a PDF or text scan
        if scan_type == "pdf" and "embeddings" in results:
            self.pdf_embeddings = results["embeddings"]
        elif scan_type == "text" and "embeddings" in results:
            self.text_embeddings = results["embeddings"]

        # Add a summary to the chat history
        if scan_type == "todo":
            summary = f"Found {len(results)} TODOs in the project."
        elif scan_type == "code":
            summary = f"Analyzed {results['stats']['total_files']} files with {results['stats']['total_lines']} lines of code."
        elif scan_type == "pdf":
            if "error" in results:
                summary = f"Error scanning PDFs: {results['error']}"
            else:
                summary = f"Analyzed {results['stats']['total_pdfs']} PDFs with {results['stats']['total_pages']} pages."
        elif scan_type == "text":
            if "error" in results:
                summary = f"Error scanning text files: {results['error']}"
            else:
                summary = f"Analyzed {results['stats']['total_files']} text files with {results['stats']['total_chunks']} content chunks."

        user_message = f"I just ran a {scan_type} scan on the project."
        assistant_message = f"I've completed the {scan_type} scan. {summary}"

        self.history.add_message("user", user_message)
        self.history.add_message("assistant", assistant_message)


"""
Enhanced chat session module with PDF embeddings for better context
"""

import os
import json
import datetime
from rich.markdown import Markdown
from utils.console import console
from utils.file_utils import ensure_directory_exists
from utils.cache import check_cache
from .history import ChatHistory


class ChatSession:
    """Interactive chat session with a model using enhanced context"""

    def __init__(self, model, context_directory, max_context_size=10):
        """
        Initialize a chat session

        Args:
            model: The model to use for chat
            context_directory (str): Directory to use as context
            max_context_size (int): Maximum number of messages to keep in context
        """
        self.model = model
        self.context_directory = context_directory
        self.max_context_size = max_context_size
        self.history = ChatHistory(max_size=max_context_size)

        # Load cached scan data if available
        self.cached_data = None
        cached_data = check_cache(context_directory)
        if cached_data:
            self.cached_data = cached_data
            console.print(
                "[bold green]✔[/bold green] Loaded cached scan data for context"
            )

        # Initialize pdf_embeddings
        self.pdf_embeddings = None
        if self.cached_data:
            # Check if there's PDF data with embeddings
            pdf_data = None
            for key, data in self.cached_data.items():
                if key.endswith("Scanner") and "pdf_files" in data:
                    pdf_data = data
                    break

            if pdf_data and "embeddings" in pdf_data:
                self.pdf_embeddings = pdf_data["embeddings"]
                console.print(
                    "[bold green]✔[/bold green] Loaded PDF embeddings for semantic search"
                )

        # Add a system message to initialize the chat
        system_message = self._create_system_message()
        self.history.add_message("system", system_message)

    def _create_system_message(self):
        """
        Create a system message to initialize the chat

        Returns:
            str: The system message
        """
        system_msg = (
            f"You are an AI assistant that helps with development tasks. "
            f"You have access to code and content in the directory: {self.context_directory}. "
            f"Use this context to provide helpful answers and suggestions. "
        )

        # Add information about available scan data
        if self.cached_data:
            system_msg += "You have access to the following scan data:\n"

            for key, data in self.cached_data.items():
                if key.endswith("Scanner") and "todo" in key.lower():
                    todo_count = len(data) if isinstance(data, list) else 0
                    system_msg += f"- TODO comments: {todo_count} items\n"

                if key.endswith("Scanner") and "code" in key.lower():
                    if isinstance(data, dict) and "stats" in data:
                        files = data["stats"].get("total_files", 0)
                        system_msg += f"- Code structure: {files} files analyzed\n"

                if key.endswith("Scanner") and "pdf" in key.lower():
                    if isinstance(data, dict) and "stats" in data:
                        pdfs = data["stats"].get("total_pdfs", 0)
                        system_msg += f"- PDF documents: {pdfs} files analyzed\n"

        system_msg += f"\nCurrent date and time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return system_msg

    def start(self):
        """Start the interactive chat session"""
        console.print("[bold cyan]Starting chat mode...[/bold cyan]")
        console.print(
            "Type [bold yellow]'exit'[/bold yellow] or [bold yellow]'quit'[/bold yellow] to end the session."
        )
        console.print(
            "Type [bold yellow]'save'[/bold yellow] to save the chat history."
        )
        console.print("Type [bold yellow]'help'[/bold yellow] for more commands.")
        console.print()

        # Display the initial assistant message
        self._send_message(
            "Hello! I'm your AI assistant for development tasks. How can I help you today?"
        )

        while True:
            # Get user input
            user_input = console.input("[bold green]You:[/bold green] ")

            # Check for special commands
            if user_input.lower() in ["exit", "quit"]:
                console.print("[bold cyan]Ending chat session.[/bold cyan]")
                break
            elif user_input.lower() == "save":
                self._save_history()
                continue
            elif user_input.lower() == "help":
                self._show_help()
                continue
            elif user_input.lower().startswith("scan "):
                self._handle_scan_command(user_input)
                continue

            # Check if we should enhance the context with PDF content
            pdf_context = self._get_relevant_pdf_content(user_input)

            # Add user message to history
            self.history.add_message("user", user_input)

            # Prepare messages with enhanced context if available
            messages = self.history.get_messages()

            # Insert PDF context as an additional system message if available
            if pdf_context:
                # Find the position to insert the context (after system message, before user query)
                context_position = (
                    1  # Default to position after the first system message
                )
                context_message = {
                    "role": "system",
                    "content": f"Here's relevant information from the PDF documents that may help answer the query:\n\n{pdf_context}",
                }

                # Insert the context message
                messages_with_context = messages.copy()
                messages_with_context.insert(context_position, context_message)

                # Use the enhanced messages
                response = self.model.chat(messages_with_context)
            else:
                # Use the standard messages
                response = self.model.chat(messages)

            # Add response to history
            self.history.add_message("assistant", response)

            # Display the response
            self._send_message(response)

    def _get_relevant_pdf_content(self, query):
        """
        Get relevant PDF content for a query using embeddings

        Args:
            query (str): The user query

        Returns:
            str: Relevant PDF content or None
        """
        if not self.pdf_embeddings or not self.cached_data:
            return None

        # Find the PDF scanner in cached data
        pdf_scanner = None
        for key, data in self.cached_data.items():
            if key.endswith("Scanner") and "pdf_files" in data:
                pdf_scanner = data
                break

        if not pdf_scanner:
            return None

        try:
            # Import the PDF scanner class to use its query method
            from scanners.pdf_scanner import PdfScanner

            scanner = PdfScanner()

            # Query the embeddings
            results = scanner.query_pdf_content(query, self.pdf_embeddings, top_k=3)

            if not results:
                return None

            # Format the results
            context = "PDF Document Context:\n\n"
            for result in results:
                metadata = result.get("metadata", {})
                filename = metadata.get("filename", "Unknown document")
                context += f"From {filename}:\n{result['content']}\n\n"

            return context

        except Exception as e:
            console.print(
                f"[bold yellow]Warning:[/bold yellow] Could not retrieve PDF context: {e}"
            )
            return None

    def _send_message(self, message):
        """
        Display a message from the assistant

        Args:
            message (str): The message to display
        """
        console.print("[bold blue]Assistant:[/bold blue]")

        # Check if message contains markdown
        if "```" in message or "#" in message or "*" in message:
            # Render as markdown
            md = Markdown(message)
            console.print(md)
        else:
            # Render as plain text
            console.print(message)

        console.print()

    def _save_history(self):
        """Save the chat history to a file"""
        # Create the chat directory if it doesn't exist
        chat_dir = os.path.join(self.context_directory, ".yaget_chats")
        ensure_directory_exists(chat_dir)

        # Create a filename with the current date and time
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_{timestamp}.json"
        file_path = os.path.join(chat_dir, filename)

        # Save the history
        with open(file_path, "w") as f:
            json.dump(self.history.get_messages(), f, indent=2)

        console.print(f"[bold green]✔[/bold green] Chat history saved to {file_path}")

    def _show_help(self):
        """Show help text for chat commands"""
        console.print("[bold yellow]Available Commands:[/bold yellow]")
        console.print("- [bold]exit[/bold] or [bold]quit[/bold]: End the chat session")
        console.print("- [bold]save[/bold]: Save the chat history to a file")
        console.print("- [bold]help[/bold]: Show this help text")
        console.print("- [bold]scan <type>[/bold]: Run a scan operation")
        console.print("  - [bold]scan todo[/bold]: Scan for TODOs")
        console.print("  - [bold]scan code[/bold]: Scan code structure")
        console.print("  - [bold]scan pdf[/bold]: Scan PDF files")
        console.print()

    def _handle_scan_command(self, command):
        """
        Handle a scan command in chat mode

        Args:
            command (str): The scan command
        """
        parts = command.split()
        if len(parts) < 2:
            console.print(
                "[bold red]Error:[/bold red] Missing scan type. Use 'scan todo', 'scan code', or 'scan pdf'."
            )
            return

        scan_type = parts[1].lower()

        if scan_type not in ["todo", "code", "pdf"]:
            console.print(f"[bold red]Error:[/bold red] Unknown scan type: {scan_type}")
            return

        # Import the scanner here to avoid circular imports
        from scanners import get_scanner

        # Create a mock args object with default values
        class MockArgs:
            def __init__(self, directory, scan_type):
                self.directory = directory
                self.before_lines = 2
                self.max_lines_after = 10
                self.extensions = [".py", ".cpp", ".h", ".java", ".js", ".html", ".sh"]

        args = MockArgs(self.context_directory, scan_type)

        # Get the scanner
        scanner = get_scanner(scan_type, args)

        # Run the scan
        console.print(f"[bold cyan]Running {scan_type} scan...[/bold cyan]")
        results = scanner.scan(self.context_directory)

        # Process with model and display results
        processed_results = scanner.process_with_model(results, self.model)
        scanner.display_results(processed_results)

        # Update cached data
        if not self.cached_data:
            self.cached_data = {}
        self.cached_data[scanner.__class__.__name__] = results

        # Update PDF embeddings if this was a PDF scan
        if scan_type == "pdf" and "embeddings" in results:
            self.pdf_embeddings = results["embeddings"]

        # Add a summary to the chat history
        if scan_type == "todo":
            summary = f"Found {len(results)} TODOs in the project."
        elif scan_type == "code":
            summary = f"Analyzed {results['stats']['total_files']} files with {results['stats']['total_lines']} lines of code."
        elif scan_type == "pdf":
            if "error" in results:
                summary = f"Error scanning PDFs: {results['error']}"
            else:
                summary = f"Analyzed {results['stats']['total_pdfs']} PDFs with {results['stats']['total_pages']} pages."

        user_message = f"I just ran a {scan_type} scan on the project."
        assistant_message = f"I've completed the {scan_type} scan. {summary}"

        self.history.add_message("user", user_message)
        self.history.add_message("assistant", assistant_message)
