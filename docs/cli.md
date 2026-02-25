# yaget/cli.py

Defines the command‑line interface and orchestrates the entire pipeline.

**Functions**  

- `parse_args() -> argparse.Namespace`  
  Uses `argparse` to parse command‑line arguments.  
  - Required positional argument: `requirements_file` (path to the Markdown file).  
  - Optional flags:  
    - `--model` (override LLM model)  
    - `--context-size` (override context window)  
    - `--temperature` (override temperature)  
    - `--ollama-url` (override Ollama base URL)  

- `main() -> None`  
  Entry point for the CLI.  
  1. Load configuration via `config.load_config()`.  
  2. Merge with CLI overrides.  
  3. Parse requirements with `parser.parse_requirements()`.  
  4. For each section `(file_path, content)`:  
     - Split content into prompts using `splitter.split_content(content, config.context_size)`.  
     - For each prompt, call `llm_client.generate(prompt)` and collect results.  
     - Concatenate generated code for the same file.  
     - Write final code using `writer.write_code(file_path, code)`.  
  5. Handle exceptions gracefully, print user‑friendly messages, and exit with appropriate codes (0 on success, non‑zero on failure).

**Error Handling**  
- Log errors and warnings.  
- If a section fails, continue with the next (optional).  
- Exit code 1 on critical failure.

**Dependencies**  
- `argparse` (standard library)  
- `sys`, `logging`  
- Internal modules: `config`, `parser`, `splitter`, `llm_client`, `writer`
