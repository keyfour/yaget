# yaget/llm_client.py

Abstracts communication with a local LLM backend.

**Abstract Base Class**  
```python
from abc import ABC, abstractmethod

class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Send a prompt to the LLM and return the generated text."""
        pass
```

**Concrete Implementation: OllamaClient**  

- Constructor: `OllamaClient(model: str, temperature: float = 0.2, base_url: str = "http://localhost:11434", timeout: int = 60)`  
- `generate(prompt)` sends a POST request to `/api/generate` with JSON:  
  ```json
  {
    "model": model,
    "prompt": prompt,
    "stream": false,
    "options": {"temperature": temperature}
  }
  ```  
- Returns the `response` field from the API.  
- Handles HTTP errors, retries (configurable), and malformed responses. Logs warnings and raises exceptions on failure.

**Future Backends**  
- Structure the client to allow adding new backends (e.g., llama.cpp, transformers) without changing other modules.

**Dependencies**  
- `requests`  
- `logging`, `time` (for retries)
