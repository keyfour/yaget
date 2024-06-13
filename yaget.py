import os
import re
import argparse
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI  # Updated import for chat models
from rich.console import Console
from rich.progress import track
from rich.syntax import Syntax

# Create a console object for rich printing
console = Console()


def load_environment(dotenv_path=None):
    """
    Load environment variables from a .env file if provided.
    """
    if dotenv_path:
        load_dotenv(dotenv_path)
    else:
        load_dotenv(
        )  # Default to loading from the .env file in the current directory

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        console.print(
            "[bold red]Error:[/bold red] OPENAI_API_KEY is not set in the .env file or environment."
        )
        raise ValueError(
            "OPENAI_API_KEY is not set in the .env file or environment.")

    console.print(
        "[bold green]✔[/bold green] Environment variables loaded successfully."
    )
    return api_key


def list_project_files(project_directory, extensions=None):
    if extensions is None:
        extensions = ['.py', '.cpp', '.h', '.java', '.js', '.html',
                      '.sh']  # Default extensions
    files = []
    for root, dirs, filenames in os.walk(project_directory):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    return files


def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()


def is_todo_comment(line):
    """
    Check if a line contains a TODO comment.
    Supports various comment styles.
    """
    # Match lines that start with common comment symbols and contain 'TODO', excluding 'ENDTODO'
    return re.match(r'^\s*(#|//|<!--)\s*TODO(?!.*ENDTODO)', line)


def is_endtodo_comment(line):
    """
    Check if a line contains an ENDTODO comment.
    Supports various comment styles.
    """
    # Match lines that start with common comment symbols and contain 'ENDTODO'
    return re.match(r'^\s*(#|//|<!--)\s*ENDTODO', line)


def extract_todos(file_content, before_lines=2):
    todos = []
    for i, line in enumerate(file_content):
        if is_todo_comment(line):
            context = capture_context(file_content, i, before_lines)
            todos.append((line.strip(), context))
    return todos


def capture_context(content, line_index, before_lines):
    start_index = max(line_index - before_lines, 0)
    context = content[start_index:line_index +
                      1]  # Include the TODO line itself
    for j in range(line_index + 1, len(content)):
        if is_endtodo_comment(content[j]):
            break
        context.append(content[j])
    return context


def scan_files_for_todos(project_directory, before_lines=2):
    console.print(
        f"🔍 Scanning files in [bold]{project_directory}[/bold] for TODOs...",
        style="bold cyan")
    todos = []
    files = list_project_files(project_directory)
    for file_path in track(files, description="Scanning files..."):
        content = read_file(file_path)
        file_todos = extract_todos(content, before_lines)
        for todo, context in file_todos:
            todos.append((todo, context, file_path))
    console.print(
        f"[bold green]✔[/bold green] Found [bold]{len(todos)}[/bold] TODOs in the project."
    )
    return todos


def generate_prompts_and_snippets(todos, api_key):
    console.print(
        "⚙️ [bold cyan]Generating prompts and code snippets from TODOs...[/bold cyan]"
    )
    prompts_and_snippets = []

    # Initialize LangChain's ChatOpenAI model
    llm = ChatOpenAI(
        openai_api_key=api_key,
        model_name='gpt-3.5-turbo')  # Correct usage for chat models
    prompt_template = PromptTemplate(
        template=
        "For the TODO: '{todo}' in file {file_path}, considering the context:\n{context}\n"
        "Generate an implementation suggestion. Please remove #TODO and #ENDTODO comments.",
        input_variables=["todo", "context", "file_path"])

    # Create a sequence combining the prompt and LLM using the pipe operator
    sequence = prompt_template | llm

    for index, (todo, context, file_path) in enumerate(
            track(todos, description="Processing TODOs...")):
        context_snippet = ''.join(context)

        # Inform the user about the current invocation
        console.print(
            f"[bold blue]Processing TODO {index + 1}/{len(todos)}:[/bold blue] '{todo}' in file [bold]{file_path}[/bold]"
        )

        # Execute the sequence to get the completion
        response = sequence.invoke({
            "todo": todo,
            "context": context_snippet,
            "file_path": file_path
        })

        # Directly access attributes of the AIMessage object
        generated_text = response.content if response else "No suggestion generated."
        model_name = response.response_metadata.get(
            'model_name', 'Unknown model') if hasattr(
                response, 'response_metadata') else 'Unknown model'
        token_usage = response.response_metadata.get(
            'token_usage', {}) if hasattr(response,
                                          'response_metadata') else {}

        # Summarize metadata
        metadata_summary = f"Model: {model_name}, Tokens Used: {token_usage.get('total_tokens', 'N/A')}"

        # Add useful metadata
        snippet_info = {
            "file": file_path,
            "todo": todo,
            "context": context_snippet.strip(),
            "generated_snippet": generated_text.strip(),
            "metadata_summary": metadata_summary
        }

        prompts_and_snippets.append(snippet_info)

    console.print(
        "[bold green]✔[/bold green] Generation of prompts and snippets completed."
    )
    return prompts_and_snippets


def main():
    parser = argparse.ArgumentParser(
        description=
        "Scan project files for TODOs and generate code suggestions.")
    parser.add_argument("project_directory",
                        help="Path to the project directory")
    parser.add_argument(
        "--before_lines",
        type=int,
        default=2,
        help="Number of lines before TODO to include in the context")
    parser.add_argument("--dotenv_path", help="Path to the .env file")
    args = parser.parse_args()

    # Load environment variables from the specified .env file
    api_key = load_environment(args.dotenv_path)

    # Scan files for TODOs and generate prompts and snippets
    todos = scan_files_for_todos(args.project_directory,
                                 before_lines=args.before_lines)
    prompts_and_snippets = generate_prompts_and_snippets(todos, api_key)

    # Print the results in a structured format
    console.print("[bold yellow]Printing the results:[/bold yellow]")
    for snippet_info in prompts_and_snippets:
        console.print(f"[bold]File:[/bold] {snippet_info['file']}")
        console.print(f"[bold]TODO:[/bold] {snippet_info['todo']}")
        console.print(f"[bold]Context:[/bold]\n{snippet_info['context']}")
        console.print("[bold]Generated Snippet:[/bold]", style="cyan")
        # Use rich's Syntax for VSCode-like highlighting, without line numbers
        syntax = Syntax(snippet_info['generated_snippet'],
                        "python",
                        theme="monokai",
                        line_numbers=False)
        console.print(syntax)
        console.print(
            f"[bold]Metadata:[/bold] {snippet_info['metadata_summary']}")
        console.print("------")


if __name__ == "__main__":
    main()
