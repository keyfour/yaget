import os
import argparse
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain.chains import LLMChain

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

# Function to traverse the directory and list files
def list_project_files(project_directory, extensions=None):
    if extensions is None:
        extensions = ['.py', '.cpp', '.h', '.java']  # Default extensions
    files = []
    for root, dirs, filenames in os.walk(project_directory):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    return files

# Function to read the content of a file
def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

# Function to extract TODOs and their context from file content
def extract_todos(file_content, before_lines=2):
    todos = []
    for i, line in enumerate(file_content):
        if 'TODO' in line:
            context = capture_context(file_content, i, before_lines)
            todos.append((line.strip(), context))
    return todos

# Function to capture the context around a specific line, ending at ENDTODO
def capture_context(content, line_index, before_lines):
    start_index = max(line_index - before_lines, 0)
    context = content[start_index:line_index + 1]  # Include the TODO line itself
    for j in range(line_index + 1, len(content)):
        context.append(content[j])
        if 'ENDTODO' in content[j]:
            break
    return context

# Main function to scan project and collect TODOs with context
def scan_files_for_todos(project_directory, before_lines=2):
    todos = []
    files = list_project_files(project_directory)
    for file_path in files:
        content = read_file(file_path)
        file_todos = extract_todos(content, before_lines)
        for todo, context in file_todos:
            todos.append((todo, context, file_path))
    return todos

# Setting Up LangChain Components
def generate_prompts_and_snippets(todos, api_key):
    prompts_and_snippets = []
    
    # Initialize LangChain components with the API key
    llm = OpenAI(api_key=api_key, model_name='gpt-3.5-turbo-0125')  # Replace with appropriate model
    prompt_template = PromptTemplate(
        template="For the TODO: '{todo}' in file {file_path}, considering the context:\n{context}\nGenerate an implementation suggestion.",
        input_variables=["todo", "context", "file_path"]
    )
    chain = LLMChain(llm=llm, prompt=prompt_template)
    
    for todo, context, file_path in todos:
        context_snippet = ''.join(context)
        formatted_prompt = prompt_template.format(todo=todo, context=context_snippet, file_path=file_path)
        response = chain.run({
            "todo": todo,
            "context": context_snippet,
            "file_path": file_path
        })
        prompts_and_snippets.append((formatted_prompt, response))
    
    return prompts_and_snippets

# Main function with argument parsing
def main():
    parser = argparse.ArgumentParser(description="Scan project files for TODOs and generate code suggestions.")
    parser.add_argument("project_directory", help="Path to the project directory")
    parser.add_argument("--before_lines", type=int, default=2, help="Number of lines before TODO to include in the context")
    parser.add_argument("--dotenv_path", help="Path to the .env file")
    args = parser.parse_args()

    print(f".env path: {args.dotenv_path}")
    api_key = load_environment(args.dotenv_path)

    # Scan files for TODOs and generate prompts and snippets
    todos = scan_files_for_todos(args.project_directory, before_lines=args.before_lines)
    prompts_and_snippets = generate_prompts_and_snippets(todos, api_key)

    # Print the results
    for prompt, snippet in prompts_and_snippets:
        print("Prompt:\n", prompt)
        print("Generated Snippet:\n", snippet)
        print("------\n")

if __name__ == "__main__":
    main()

