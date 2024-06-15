
# Yaget (Yet-another-GenAI-tool)

Yaget is a Python-based tool designed to enhance your codebase by scanning for `TODO` comments, capturing relevant context, and generating code suggestions using the LangChain library integrated with OpenAI’s powerful language models. This tool simplifies managing `TODO` items and provides valuable suggestions for code improvements.


**🚧 Disclaimer:** Yaget is a **personal project** currently in an **early prototype** stage. It is developed for learning, experimentation, and personal use. As such, features may be incomplete, and functionality might be limited or subject to change. Please use it with this understanding. Feedback and suggestions are welcome as the project continues to evolve.

## Features

...
- **Project File Scanning**: Traverse through your project directory to locate files containing `TODO` comments.
- **Context Capture**: Dynamically capture the context around `TODO` comments until an `ENDTODO` marker is reached.
- **Prompt Generation**: Utilize LangChain to create detailed prompts based on the captured context.
- **AI-Powered Code Suggestions**: Generate actionable code snippets using OpenAI's language models.
- **Flexible Configuration**: Customize the number of lines captured before `TODO` comments and specify file types for scanning.

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/keyfour/yaget.git
cd yaget
```

### Step 2: Set Up a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure API Key

Create a `.env` file in the project root directory and add your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key
```

## Usage

### Command Line Interface

Run the script with the project directory and optional parameters for context lines:

```bash
python yaget.py /path/to/your/project --before_lines 3
```

### Arguments

- `project_directory`: The path to the directory containing your project files.
- `--before_lines`: (Optional) Number of lines before the `TODO` to include in the context. Default is 2 lines.

### Example

To scan a project at `/home/user/project` and include 3 lines before each `TODO`:

```bash
python yaget.py /home/user/project --before_lines 3
```

### Output

Yaget generates detailed prompts and suggestions for each `TODO` found. Example output:

```
Prompt:
 For the TODO: 'TODO: Refactor this function' in file /home/user/project/main.py, considering the context:
def process_data(data):
    # Initial processing steps
    pass
# ENDTODO
Generate an implementation suggestion.

Generated Snippet:
 Suggested implementation for TODO: 'TODO: Refactor this function':
def process_data(data):
    # Optimized processing steps
    # TODO: Implement efficient sorting algorithm
    pass
```

## Project Structure

- **yaget.py**: Main script to run the tool.
- **requirements.txt**: List of dependencies.
- **README.md**: This readme file.
- **.env**: Environment file for storing API keys (not included in the repository).

## Development

### Setup

1. **Fork and Clone** the repository:
   ```bash
   git clone https://github.com/yourusername/yaget.git
   cd yaget
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create and Activate** a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

### Running Tests

Add tests to ensure functionality using frameworks like `unittest` or `pytest`.

## Contributions

We welcome contributions! Please submit a pull request or open an issue with any suggestions or changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- **LangChain**: For providing the framework to integrate language models.
- **OpenAI**: For the API enabling advanced AI-powered code suggestions.

---

For further details, visit the [LangChain Documentation](https://python.langchain.com/docs/) and [OpenAI Documentation](https://beta.openai.com/docs/).

Feel free to [contact us](mailto:your.email@example.com) for support or inquiries.
