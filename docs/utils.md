# yaget/utils.py

Shared helper functions used across modules.

**Suggested Utilities**  

- `setup_logging(level=logging.INFO)` – configure logging format and output.  
- `estimate_tokens(text: str) -> int` – simple length/4 estimation (used by splitter).  
- `ensure_directory(path: str)` – create parent directories if needed (used by writer).  
- `syntax_check(code: str, language: str) -> bool` – basic compile/parse check for Python (others ignored).  
- `read_file_safe(path: str) -> str` – read a file with error handling.  
- `write_file_safe(path: str, content: str)` – write a file with error handling (used by writer).  

**Example**  
```python
if not syntax_check(code, "python"):
    logging.warning("Generated Python code has syntax errors.")
```

**Dependencies**  
- `logging`, `os`, `sys`
