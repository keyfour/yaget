"""
TODO scanner for finding and processing TODO comments in code
"""

import re
from rich.progress import track

"""
TODO scanner for finding and processing TODO comments in code
"""

import re
from rich.progress import track
from rich.syntax import Syntax
from .base import BaseScanner
from utils.console import console


class TodoScanner(BaseScanner):
    """Scanner for TODO comments in code files"""

    def __init__(self, before_lines=2, max_lines_after=10, extensions=None):
        """
        Initialize the TODO scanner

        Args:
            before_lines (int): Number of lines before TODO to include in the context
            max_lines_after (int): Maximum number of lines to follow after TODO
            extensions (list): List of file extensions to scan
        """
        super().__init__()
        self.before_lines = before_lines
        self.max_lines_after = max_lines_after
        self.extensions = extensions

    def scan(self, directory):
        """
        Scan a directory for TODO comments

        Args:
            directory (str): The directory to scan

        Returns:
            list: List of TODOs with context
        """
        console.print(
            f"🔍 Scanning files in [bold]{directory}[/bold] for TODOs...",
            style="bold cyan",
        )
        todos = []

        # Load ignore list
        ignore_list = self.load_ignore_list(directory)

        # List files to scan
        files = self.list_files(directory, ignore_list, self.extensions)

        # Scan files for TODOs
        for file_path in track(files, description="Scanning files for TODOs..."):
            content = self.read_file(file_path)
            file_todos = self.extract_todos(
                content, self.before_lines, self.max_lines_after
            )
            for todo, context in file_todos:
                todos.append({"todo": todo, "context": context, "file_path": file_path})

        console.print(
            f"[bold green]✔[/bold green] Found [bold]{len(todos)}[/bold] TODOs in the project."
        )
        return todos

    def process_with_model(self, scan_results, model):
        """
        Process TODO scan results with a model

        Args:
            scan_results (list): The results from the scan
            model (BaseModel): The model to use for processing

        Returns:
            list: The processed results
        """
        console.print("⚙️ [bold cyan]Generating suggestions for TODOs...[/bold cyan]")
        processed_results = []

        for index, todo_info in enumerate(
            track(scan_results, description="Processing TODOs...")
        ):
            todo = todo_info["todo"]
            context = todo_info["context"]
            file_path = todo_info["file_path"]

            context_snippet = "".join(context)

            # Inform the user about the current invocation
            console.print(
                f"[bold blue]Processing TODO {index + 1}/{len(scan_results)}:[/bold blue] '{todo}' in file [bold]{file_path}[/bold]"
            )

            # Create the prompt
            prompt = (
                f"For the TODO: '{todo}' in file {file_path}, considering the context:\n{context_snippet}\n"
                f"Generate an implementation suggestion. Please remove #TODO and #ENDTODO comments."
            )

            # Get the completion from the model
            generated_text = model.generate(prompt)

            # Add the results to the list
            processed_results.append(
                {
                    "file": file_path,
                    "todo": todo,
                    "context": context_snippet.strip(),
                    "generated_snippet": generated_text.strip(),
                }
            )

        console.print("[bold green]✔[/bold green] Generation of suggestions completed.")
        return processed_results

    def display_results(self, processed_results):
        """
        Display the processed results

        Args:
            processed_results (list): The processed results
        """
        console.print("[bold yellow]Printing the results:[/bold yellow]")
        for result in processed_results:
            console.print(f"[bold]File:[/bold] {result['file']}")
            console.print(f"[bold]TODO:[/bold] {result['todo']}")
            console.print(f"[bold]Context:[/bold]\n{result['context']}")
            console.print("[bold]Generated Snippet:[/bold]", style="cyan")

            # Use rich's Syntax for VSCode-like highlighting
            syntax = Syntax(
                result["generated_snippet"],
                "python",  # Attempt to infer language from file extension
                theme="monokai",
                line_numbers=False,
            )
            console.print(syntax)
            console.print("------")

    def read_file(self, file_path):
        """
        Read a file and return its contents as a list of lines

        Args:
            file_path (str): Path to the file

        Returns:
            list: List of lines in the file
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.readlines()
        except UnicodeDecodeError:
            # Try with a different encoding
            try:
                with open(file_path, "r", encoding="latin-1") as file:
                    return file.readlines()
            except Exception as e:
                console.print(
                    f"[bold red]Error:[/bold red] Could not read file {file_path}: {e}"
                )
                return []
        except Exception as e:
            console.print(
                f"[bold red]Error:[/bold red] Could not read file {file_path}: {e}"
            )
            return []

    def is_todo_comment(self, line):
        """
        Check if a line contains a TODO comment.
        Supports various comment styles.
        """
        # Match lines that start with common comment symbols and contain 'TODO', excluding 'ENDTODO'
        return re.search(r"^\s*(#|//|/\*|<!--)\s*TODO(?!.*ENDTODO)", line) is not None

    def is_endtodo_comment(self, line):
        """
        Check if a line contains an ENDTODO comment.
        Supports various comment styles.
        """
        # Match lines that start with common comment symbols and contain 'ENDTODO'
        return re.search(r"^\s*(#|//|/\*|<!--)\s*ENDTODO", line) is not None

    def extract_todos(self, file_content, before_lines=2, max_lines_after=10):
        """
        Extract TODOs from file content

        Args:
            file_content (list): Lines of the file
            before_lines (int): Number of lines before TODO to include in the context
            max_lines_after (int): Maximum number of lines to follow after TODO

        Returns:
            list: List of (todo, context) tuples
        """
        todos = []
        for i, line in enumerate(file_content):
            if self.is_todo_comment(line):
                context = self.capture_context(
                    file_content, i, before_lines, max_lines_after
                )
                todos.append((line.strip(), context))
        return todos

    def capture_context(self, content, line_index, before_lines, max_lines_after):
        """
        Capture the context around a TODO comment.

        Args:
            content (list): Lines of the file
            line_index (int): Index of the TODO line
            before_lines (int): Number of lines before TODO to include in the context
            max_lines_after (int): Maximum number of lines to follow after TODO

        Returns:
            list: Lines of context
        """
        start_index = max(line_index - before_lines, 0)
        context = content[start_index : line_index + 1]  # Include the TODO line itself

        # Add lines after the TODO until we hit an ENDTODO or reach the limit
        for j in range(
            line_index + 1, min(line_index + 1 + max_lines_after, len(content))
        ):
            if self.is_endtodo_comment(content[j]):
                context.append(content[j])
                break
            context.append(content[j])

        return context
