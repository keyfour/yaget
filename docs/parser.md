# yaget/parser.py

Extracts sections from the input Markdown file.

**Function**  
`parse_requirements(file_path: str) -> List[Tuple[str, str]]`  

- **Input**: Path to a Markdown file.  
- **Output**: List of `(file_path, content)` tuples.  
  - `file_path`: relative filesystem path taken from the top‑level heading (e.g., `# src/main.py` → `src/main.py`).  
  - `content`: the Markdown text under that heading (excluding the heading line) until the next top‑level heading or end of file.

**Rules**  
- A top‑level heading is any line starting with `# ` (single `#` followed by space).  
- Leading/trailing whitespace in the file path is stripped.  
- Text before the first top‑level heading is ignored.  
- If a heading is not a valid filesystem path (e.g., contains invalid characters), log a warning and skip the section.  
- Use a robust Markdown parser (e.g., `mistune`) to avoid regex pitfalls.

**Example**  
```python
sections = parse_requirements("requirements.md")
for path, content in sections:
    print(path, content[:50])
```

**Dependencies**  
- `mistune` (or another Markdown parser)  
- `os`, `logging`
