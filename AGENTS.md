# AGENTS.md - Yaget Project Guide

## Project Overview

Yaget (Yet-another-GenAI-tool) is a Python-based tool that scans codebases for `TODO` comments, captures relevant context, and generates AI-powered code suggestions using LangChain and OpenAI's language models.

**Status**: Early prototype stage - features may be incomplete and functionality is subject to change.

## Project Structure

```
yaget/
├── yaget/                 # Core documentation and modules
│   ├── bootstrap.md       # (Empty - possibly for future use)
│   ├── ollama.md          # Ollama integration specifications
│   ├── ollama.py          # Ollama client implementation
│   └── prompts.md         # (Empty - possibly for future use)
├── examples/
│   ├── run_example.sh     # Example usage script
│   └── simple_project/    # Example project for testing
├── tests/                 # Test directory (currently empty)
├── yaget.py              # Main script
├── requirements.txt      # Dependencies
├── .gitignore            # Standard Python .gitignore
├── .yagetignore          # Files/directories for Yaget to ignore
└── README.md            # Project documentation
```

## Essential Commands

### Setup and Installation

```bash
# Clone repository
git clone https://github.com/keyfour/yaget.git
cd yaget

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
echo "OPENAI_API_KEY=your_openai_api_key" > .env
```

### Running the Tool

```bash
# Basic usage
python yaget.py /path/to/project

# With custom context lines
python yaget.py /path/to/project --before_lines 3

# With custom max lines after TODO
python yaget.py /path/to/project --max_lines_after 15

# With custom .env file
python yaget.py /path/to/project --dotenv_path /path/to/custom.env

# Run example
./examples/run_example.sh
```

### Testing

```bash
# No test framework currently implemented
# Tests directory exists but is empty
# Add tests using unittest, pytest, or other frameworks
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Required for OpenAI API access
- Can be set in `.env` file or environment variables

### Ignore Files

- `.yagetignore`: Contains patterns for files/directories to ignore
  - Default ignores: `.venv/`, `.git/`
  - Supports both file patterns and directory patterns (ending with `/`)

### File Extensions Scanned

Default extensions: `.py`, `.cpp`, `.h`, `.java`, `.js`, `.html`, `.sh`

## Code Organization and Patterns

### Main Script (`yaget.py`)

**Structure:**
- Environment loading and API key validation
- File scanning with ignore pattern support
- TODO comment extraction with context capture
- AI-powered suggestion generation using LangChain
- Rich console output for formatted results

**Key Functions:**
- `load_environment()`: Load and validate API keys
- `load_ignore_list()`: Load patterns from `.yagetignore`
- `list_project_files()`: Scan directory for supported files
- `extract_todos()`: Extract TODO comments with context
- `generate_prompts_and_snippets()`: Generate AI suggestions

### Ollama Module (`yaget/ollama.py`)

**Architecture:**
- Functional programming style (prefers over OOP)
- Dependency injection throughout
- Dataclasses for configuration
- Type hints and comprehensive documentation

**Key Components:**
- `ConnectionParams`: API connection configuration
- `RequestContext`: Request-specific parameters
- Session management functions
- Model management (list, pull operations)
- Chat functionality with error handling

### Code Style

**Current Issues (from diagnostics):**
- Multiple line length violations (E501 - lines > 79 chars)
- Unexpected spaces around keyword equals (E251)
- Long lines across multiple functions

**Imports:**
- Type hints imported as `typing as t`
- Comprehensive imports for LangChain, OpenAI, Rich
- Forward compatibility with newer imports

### TODO Format

Supported comment styles:
- Python: `# TODO: description`
- C/C++: `// TODO: description`
- HTML: `<!-- TODO: description -->`

TODO context capture:
- Default: 2 lines before TODO
- Max lines after: 10 (configurable)
- Context stops at `ENDTODO` marker

## Dependencies

### Core Requirements

- **LangChain**: 0.2.3 (framework for AI integration)
- **OpenAI**: 1.34.0 (API client)
- **Rich**: 13.7.1 (terminal formatting)
- **python-dotenv**: 1.0.1 (environment loading)
- **Pygments**: 2.18.0 (syntax highlighting)

### Development Dependencies

- **yapf**: 0.40.2 (formatter - available but not configured)
- **mypy**: (cache exists in .gitignore but not actively used)

## Important Gotchas

### API Key Requirements

- **Required**: OpenAI API key must be set in `.env` file
- **Error**: Tool will exit with error if key is missing
- **Format**: `OPENAI_API_KEY=your_key_here`

### TODO Comment Limitations

- **Context Capture**: Only captures until `ENDTODO` marker
- **Max Lines**: Configurable but limited to prevent excessive context
- **Comment Styles**: Only supports common comment syntax patterns

### File Scanning

- **Default Extensions**: Limited to specific file types
- **Ignore Patterns**: Respects `.yagetignore` and standard `.gitignore`
- **Directory Traversal**: Skips ignored directories entirely

### Error Handling

- **Network Issues**: Limited error handling for API failures
- **File Reading**: Basic file reading without encoding handling
- **Validation**: Basic TODO comment validation

### Performance Considerations

- **Sequential Processing**: Processes files sequentially (no parallelization)
- **Memory Usage**: Loads entire files into memory
- **Rate Limits**: No built-in rate limiting for API calls

## Development Guidelines

### Adding New AI Providers

- Follow the pattern established in `yaget/ollama.py`
- Use dependency injection for API clients
- Implement proper error handling and logging
- Add comprehensive type hints and documentation

### Extending File Support

- Update `list_project_files()` extensions list
- Consider adding file type-specific comment parsing
- Test with various comment styles and file formats

### Testing Strategy

- No current test framework - consider adding pytest
- Example project in `examples/simple_project/` can be used for testing
- Should test TODO extraction, context capture, and AI integration

### Code Quality

- Address existing style warnings (line length, spacing)
- Consider adding pre-commit hooks for formatting
- Implement type checking (mypy available)

## Future Considerations

Based on existing documentation files:

- **Ollama Integration**: `ollama.py` provides foundation for local model support
- **Modular Design**: Separation between core functionality and AI providers
- **Functional Programming**: Preference for functional over OOP style
- **Type Safety**: Strong emphasis on type hints and dataclasses

## Troubleshooting

### Common Issues

1. **Missing API Key**: Ensure `.env` file exists with valid key
2. **File Not Found**: Check project directory path and permissions
3. **Import Errors**: Verify all dependencies are installed
4. **TODO Not Found**: Check comment syntax and ensure proper extension

### Debug Mode

No built-in debug mode - consider adding verbose logging option for development.

## Contributing

### Current State

- Early prototype - features may be incomplete
- No formal contribution guidelines established
- Testing framework needs implementation
- Code quality issues should be addressed

### Development Workflow

1. Fork repository
2. Create feature branch
3. Implement changes
4. Add tests (when framework is established)
5. Submit pull request

---

*This document was automatically generated based on analysis of the current codebase. Review and update as the project evolves.*