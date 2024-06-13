import os
import argparse
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI  # Updated import for chat models

def load_environment(dotenv_path=None):
    """
    Load environment variables from a .env file if provided.
    """
    if dotenv_path:
        load_dotenv(dotenv_path)
    else:
        load_dotenv()  # Default to loading from the .env file in the current directory

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in the .env file or environment.")
    return api_key

def list_project_files(project_directory, extensions=None):
    if extensions is None:
        extensions = ['.py', '.cpp', '.h', '.java']  # Default extensions
    files = []
    for root, dirs, filenames in os.walk(project_directory):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    return files

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

def extract_todos(file_content, before_lines=2):
    todos = []
    for i, line in enumerate(file_content):
        if 'TODO' in line:
            context = capture_context(file_content, i, before_lines)
            todos.append((line.strip(), context))
    return todos

def capture_context(content, line_index, before_lines):
    start_index = max(line_index - before_lines, 0)
    context = content[start_index:line_index + 1]  # Include the TODO line itself
    for j in range(line_index + 1, len(content)):
        context.append(content[j])
        if 'ENDTODO' in content[j]:
            break
    return context

def scan_files_for_todos(project_directory, before_lines=2):
    todos = []
    files = list_project_files(project_directory)
    for file_path in files:
        content = read_file(file_path)
        file_todos = extract_todos(content, before_lines)
        for todo, context in file_todos:
            todos.append((todo, context, file_path))
    return todos

def generate_prompts_and_snippets(todos, api_key):
    prompts_and_snippets = []

    # Initialize LangChain's ChatOpenAI model
    llm = ChatOpenAI(openai_api_key=api_key, model_name='gpt-3.5-turbo')  # Correct usage for chat models
    prompt_template = PromptTemplate(
        template="For the TODO: '{todo}' in file {file_path}, considering the context:\n{context}\n"
                 "Generate an implementation suggestion. Please remove #TODO and #ENDTODO comments.",
        input_variables=["todo", "context", "file_path"]
    )

    # Create a sequence combining the prompt and LLM using the pipe operator
    sequence = prompt_template | llm

    for todo, context, file_path in todos:
        context_snippet = ''.join(context)

        # Execute the sequence to get the completion
        response = sequence.invoke({
            "todo": todo,
            "context": context_snippet,
            "file_path": file_path
        })

        # Directly access attributes of the AIMessage object
        generated_text = response.content if response else "No suggestion generated."
        model_name = response.response_metadata.get('model_name', 'Unknown model') if hasattr(response, 'response_metadata') else 'Unknown model'
        token_usage = response.response_metadata.get('token_usage', {}) if hasattr(response, 'response_metadata') else {}

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

    return prompts_and_snippets

def main():
    parser = argparse.ArgumentParser(description="Scan project files for TODOs and generate code suggestions.")
    parser.add_argument("project_directory", help="Path to the project directory")
    parser.add_argument("--before_lines", type=int, default=2, help="Number of lines before TODO to include in the context")
    parser.add_argument("--dotenv_path", help="Path to the .env file")
    args = parser.parse_args()

    # Load environment variables from the specified .env file
    api_key = load_environment(args.dotenv_path)

    # Scan files for TODOs and generate prompts and snippets
    todos = scan_files_for_todos(args.project_directory, before_lines=args.before_lines)
    prompts_and_snippets = generate_prompts_and_snippets(todos, api_key)

    # Print the results in a structured format
    for snippet_info in prompts_and_snippets:
        print(f"File: {snippet_info['file']}")
        print(f"TODO: {snippet_info['todo']}")
        print(f"Context:\n{snippet_info['context']}")
        print("Generated Snippet:\n", snippet_info['generated_snippet'])
        print(f"Metadata: {snippet_info['metadata_summary']}")
        print("------\n")

if __name__ == "__main__":
    main()
