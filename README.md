# YAGET - Yet Another Generator for Enhancing Tasks

YAGET is a powerful, modular tool designed to analyze, understand, and enhance your codebase and documentation using modern LLM technologies. YAGET provides comprehensive project insights through semantic understanding of your code and documentation.

**🚧 Disclaimer:** YAGET is a **personal project** that has evolved from a prototype into a more comprehensive tool. While significantly enhanced, it's still under active development. Features may be subject to change as the project continues to evolve. Feedback and suggestions are welcome!

## Key Features

### Intelligent Scanning

- **Multiple Scanner Types**:
  - **TODO Scanner**: Find and process TODO comments in code files
  - **Code Scanner**: Analyze code structure, metrics, and patterns
  - **PDF Scanner**: Extract and semantically understand PDF content
  - **Text Scanner**: Process markdown, configuration files, and other text documents

### Semantic Understanding

- **Embeddings-Based Analysis**: Generate vector embeddings for documentation
- **Context-Aware Responses**: Retrieve relevant project information during interactions
- **Intelligent Caching**: Store scan results with automatic change detection

### Interactive Capabilities

- **Chat Mode**: Have conversations about your project with LLM assistance
- **Implementation Suggestions**: Get code suggestions for TODOs and other improvements
- **Project Documentation Insights**: Ask questions about your project's documentation

### Flexible Architecture

- **Multiple LLM Providers**: Support for both OpenAI and Ollama
- **Modular Design**: Easily extendable with new scanners and features
- **Configurable Behavior**: Fine-tune how scans are performed and results processed

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

### Step 4: Configure Environment

Create a `.env` file in the project root directory:

```
# For OpenAI
PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key
MODEL=gpt-4

# For Ollama (uncomment to use)
# PROVIDER=ollama
# OLLAMA_SERVER=http://localhost:11434
# MODEL=llama3
```

## Usage

### Scanning Your Project

Scan for TODOs, analyze code structure, and extract content from documents:

```bash
# Scan for TODOs and generate implementation suggestions
python main.py scan --scan_todo /path/to/your/project --process

# Comprehensive project analysis with embeddings
python main.py scan --scan_todo --scan_code --scan_pdf --scan_text --use_embeddings /path/to/your/project
```

### Chat About Your Project

Interact with your project using natural language:

```bash
# Start chat mode with project context
python main.py chat /path/to/your/project
```

In chat mode, you can ask questions about your codebase, documentation, and TODOs. The system uses the scanned data to provide informed responses.

### Advanced Usage

Configure scans with additional options:

```bash
# Custom file extensions for code scanning
python main.py scan --scan_code --extensions .py .js .ts /path/to/your/project

# Custom context lines for TODOs
python main.py scan --scan_todo --before_lines 5 --max_lines_after 15 /path/to/your/project
```

### Chat Mode Commands

When using chat mode, the following commands are available:

- `exit` or `quit`: End the chat session
- `save`: Save the chat history to a file
- `help`: Show help text
- `scan todo`, `scan code`, `scan pdf`, or `scan text`: Run a scan operation from within chat
- `scan text extensions=.txt,.md,.json`: Scan with custom extensions

## Project Structure

YAGET follows a modular architecture:

```
yaget/
├── models/              # LLM integration modules
├── scanners/            # Scanner implementations
├── utils/               # Utility functions
├── chat/                # Chat mode implementation
├── main.py              # Main entry point
├── cli.py               # Command-line interface
└── README.md            # This readme file
```

## Planned Features

Future development will focus on:

- **Document Editing**: Direct modification of files based on suggestions
- **Refactoring Tools**: Automated code improvement capabilities
- **Project Health Metrics**: Overall codebase quality assessment
- **Multiple Language Support**: Enhanced understanding of various programming languages
- **Integration with Development Tools**: IDE plugins and CI/CD support

## Contributions

Contributions are welcome! Please submit a pull request or open an issue with any suggestions or changes.

To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- **LangChain**: For providing the framework to integrate language models
- **FAISS**: For efficient vector search capabilities
- **PyPDF2**: For PDF content extraction
- **Rich**: For beautiful terminal output

---

For more information or support, please open an issue on the GitHub repository.
