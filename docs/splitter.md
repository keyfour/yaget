# yaget/splitter.py

Splits long content into smaller prompts that fit the LLM's context window.

**Function**  
`split_content(content: str, context_size: int) -> List[str]`  

- **Input**:  
  - `content`: requirement text for one file.  
  - `context_size`: maximum tokens the LLM can handle.  
- **Output**: List of prompt strings, each estimated to be under the token limit.

**Token Estimation**  
- Simple approximation: `len(text) / 4` (rough average for English).  
- For v1, this is sufficient; future versions may use a proper tokenizer.

**Splitting Strategy**  
1. If estimated tokens ≤ `context_size`, return `[content]`.  
2. Otherwise, split by paragraphs (`\n\n`).  
3. Re‑combine paragraphs until adding another would exceed the limit, then start a new prompt.  
4. Detect code blocks (triple backticks) and treat them as atomic – do not split inside a code block.  
5. Each prompt should be coherent (complete paragraphs, bullet lists, code blocks).

**Example**  
```python
prompts = split_content(long_text, 2048)
for prompt in prompts:
    print(f"Prompt length: {len(prompt)}")
```

**Dependencies**  
- `logging` (for warnings)  
- Internal: `utils.estimate_tokens` (if extracted)
