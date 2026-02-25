# yaget/config.py

Manages configuration from environment variables and defaults.

**Configuration Parameters** (all stored in a dataclass)  
```python
from dataclasses import dataclass

@dataclass
class Config:
    model: str = "codellama:7b"
    context_size: int = 2048
    temperature: float = 0.2
    ollama_url: str = "http://localhost:11434"
```

**Loading Order**  
1. Default values (hard‑coded).  
2. Environment variables prefixed with `YAGET_` (e.g., `YAGET_MODEL`, `YAGET_CONTEXT_SIZE`).  
3. Optional `.env` file (loaded via `python-dotenv`).  

**Functions**  
- `load_config(env_file: Optional[str] = None) -> Config` – loads from environment and/or `.env`.  
- `merge_with_cli(config: Config, cli_args: dict) -> Config` – creates a new Config instance with CLI overrides applied.

**Dependencies**  
- `os`  
- `python-dotenv` (optional, for `.env` support)  
- `dataclasses` (Python 3.7+)
