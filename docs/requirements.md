"""
yaget - Development Guide

This document describes the architecture, components, and development guidelines for **yaget**, a tool that converts requirements documents written in Markdown into programming code using locally installed small Large Language Models (LLMs).

## Overview

yaget reads a Markdown file containing structured requirements, splits it into manageable prompts, and sends each prompt to a local LLM to generate corresponding source code. The generated code is then written to the file system according to paths specified in the requirements document.

Key features:

- Parses Markdown requirement files with embedded file paths.
- Uses locally hosted small LLMs (e.g., via Ollama, llama.cpp) for privacy and offline capability.
- Automatically splits large requirement sections into smaller prompts respecting the LLM's context window.
- Writes generated code to the appropriate relative paths.

## How It Works

1. **Input**: A Markdown file following the expected format (see below).
2. **Parsing**: The file is parsed into sections, each starting with a level‑1 heading that contains the target file path.
3. **Prompting**: For each section, the content is passed (possibly after splitting) to the LLM as a prompt. The LLM is instructed to generate code that implements the described requirements.
4. **Code Generation**: The LLM returns code, which is then cleaned and validated (basic syntax checks).
5. **Writing**: The code is written to the file path derived from the section heading. Any missing directories are created.

If a section is too long for the LLM's context, it is split into smaller logical chunks (e.g., paragraphs, bullet points) and multiple prompts are sent. The final output for that file is the concatenation of the generated chunks.

## Requirement Document Format

The input Markdown file **must** follow this structure:

- Each **top‑level heading** (`#`) specifies a relative file path (e.g., `# src/main.py`).
- The content below that heading contains the requirements for that file, written in natural language, bullet points, or any Markdown.
- Multiple such sections can exist in one document.
- The document may contain other Markdown elements (e.g., explanatory text) **outside** top-level headings – those are ignored.

Example:

```markdown
# src/main.py

This module is the entry point. It should:

- Parse command line arguments.
- Call the core logic.

# src/core.py

Implement a function `process(data)` that...
```

## Project Structure

All code resides under the `yaget/` directory in the project root. The intended layout:

```
yaget/
├── __init__.py
├── cli.py              # Command-line interface
├── parser.py           # Markdown parsing and section extraction
├── splitter.py         # Splits long sections into prompts
├── llm_client.py       # Interface with local LLM (abstracted)
├── writer.py           # Writes generated code to files
├── config.py           # Configuration (model, context size, etc.)
└── utils.py            # Helper functions
```

- `cli.py` defines the entry point (e.g., `yaget requirements.md`).
- `parser.py` extracts sections: for each `# path` heading, returns `(file_path, content)`.
- `splitter.py` takes a long content string and splits it into a list of prompt strings based on the configured context size.
- `llm_client.py` abstracts the LLM backend. It should support a simple `generate(prompt)` method.
- `writer.py` writes the final code to the filesystem, creating directories if needed.
- `config.py` loads settings from environment variables or a config file (e.g., model, context window, temperature).
- `utils.py` contains shared helpers (e.g., logging, file operations).

## Component Descriptions

### CLI (`cli.py`)

- Uses `argparse` to accept one argument: the path to the requirement Markdown file.
- Optionally accepts flags for configuration overrides (e.g., `--model`, `--context-size`).
- Orchestrates the pipeline: parse → split → generate → write.

### Parser (`parser.py`)

- Reads the Markdown file.
- Uses a simple regex or a Markdown parser (like `mistune` or `markdown`) to identify level‑1 headings.
- Returns a list of tuples: `[(file_path, content), ...]`.

### Splitter (`splitter.py`)

- Receives a content string and the configured context window size (in tokens).
- Estimates token count (simple approximation: `len(text) / 4`).
- If content fits, returns `[content]`.
- Otherwise, splits by paragraphs, then recombines until the token limit is approached, creating multiple prompts.
- Handles code blocks to avoid breaking them mid-chunk (optional for v1).

### LLM Client (`llm_client.py`)

- Abstract base class with concrete implementations for different backends (Ollama, llama.cpp, etc.).
- For v1, implement an Ollama client (most straightforward).
- Method: `generate(prompt) -> str` that returns the generated code.
- Handles errors and retries.

### Writer (`writer.py`)

- For each generated code string and its corresponding file path:
  - Ensure the directory exists (`os.makedirs`).
  - Write the code to the file.
  - Optionally run a basic syntax check (e.g., `compile()` for Python) and log warnings.

### Config (`config.py`)

- Reads `YAGET_MODEL`, `YAGET_CONTEXT_SIZE`, `YAGET_TEMPERATURE` from environment variables or a `.env` file.
- Provides defaults (e.g., model: "codellama:7b", context: 2048, temperature: 0.2).

## Development Setup

1. **Clone the repository** and create a virtual environment.
2. **Install dependencies**:
   - `pip install -r requirements.txt` (include `mistune`, `requests`, `python-dotenv`, etc.)
3. **Set up a local LLM**:
   - Install Ollama and pull a small model, e.g., `ollama pull codellama:7b`.
   - Ensure the Ollama server is running.
4. **Run tests** (once written) with `pytest`.
5. **Lint** with `flake8` and format with `black`.

## Usage (for development testing)

```bash
python -m yaget.cli path/to/requirements.md
```

To override defaults:

```bash
YAGET_MODEL="llama3.2:1b" python -m yaget.cli requirements.md
```

## Contributing Guidelines

- Follow PEP 8 style and use `black` for formatting.
- Write unit tests for all non-trivial functions.
- Keep modules focused; avoid circular imports.
- Document public functions with docstrings.
- Before committing, run the test suite and ensure no linting errors.

---

This guide is intended for developers working on yaget. Future usage documentation will be created separately.

## Current Implementation Status

### Completed Components
- `cli.py` - Command-line interface with argument parsing
- `parser.py` - Markdown parsing and section extraction
- `splitter.py` - Content splitting based on context window
- `llm_client.py` - LLM client interface with Ollama implementation
- `writer.py` - Code writing utilities
- `config.py` - Configuration management
- `utils.py` - Shared utility functions

### Current Architecture

The codebase now follows the specified architecture:

```
yaget/
├── __init__.py
├── cli.py              # Command-line interface
├── parser.py           # Markdown parsing and section extraction
├── splitter.py         # Splits long sections into prompts
├── llm_client.py       # Interface with local LLM (abstracted)
├── writer.py           # Writes generated code to files
├── config.py           # Configuration (model, context size, etc.)
└── utils.py            # Helper functions
```

### Next Steps

1. **Add tests**: Write unit tests for all components
2. **Add requirements.txt**: Define project dependencies
3. **Add .env.example**: Provide environment variable template
4. **Add usage documentation**: Create user-facing documentation
5. **Add error handling**: Improve error handling and validation
6. **Add logging**: Enhance logging for better debugging
7. **Add code validation**: Implement syntax validation for generated code

### Testing the Implementation

To test the current implementation:

1. Install dependencies: `pip install ollama mistune`
2. Set up Ollama and pull a model: `ollama pull codellama:7b`
3. Create a requirements file (e.g., `test.md`):
   ```markdown
   # test.py
   
   Implement a function `hello()` that returns "Hello, World!"
   ```
4. Run the CLI: `python -m yaget.cli test.md`
5. Verify the generated `test.py` file