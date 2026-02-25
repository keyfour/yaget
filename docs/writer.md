# yaget/writer.py

Writes generated code to the filesystem.

**Function**  
`write_code(file_path: str, code: str) -> None`  

- **Input**:  
  - `file_path`: relative path where the code should be written.  
  - `code`: string containing the generated code.  
- **Behavior**:  
  - Ensure the directory of `file_path` exists (`os.makedirs(..., exist_ok=True)`).  
  - Write `code` to the file (UTF‑8 encoding).  
  - If the file already exists, **overwrite** it (log a warning).  
- **Optional syntax check**:  
  - For `.py` files: try `compile(code, file_path, 'exec')` and log a warning if it fails.  
  - Other extensions can be ignored initially.  
- **Error handling**: catch `IOError`/`OSError`, log the error, and re‑raise a custom exception (e.g., `WriteError`).

**Example**  
```python
write_code("src/main.py", "print('Hello, world!')")
```

**Dependencies**  
- `os`, `logging`  
- Internal: `utils.syntax_check` (optional)
