# yaget/__init__.py

Makes the `yaget` directory a Python package.

**Responsibilities**  
- Optionally expose the main entry point for convenience (e.g., `from yaget.cli import main`).  
- Define the package version: `__version__ = "0.1.0"`.  
- Import key classes/functions if they are intended for external use (though not strictly required for a CLI tool).

**Example**
```python
__version__ = "0.1.0"
from .cli import main
```

**Notes**  
- Keep this file minimal; no business logic.
