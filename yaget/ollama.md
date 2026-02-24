---
filename: yaget/ollama.py
---

# Module requirements

## Overall requirements

- **IMPORTANT**: preffer pure functional coding style over object-oriented
- avoid hard coupling and use Dependency injection everywhere its possible

## Dependencies

- Ollama Python library

```python
from ollama import chat
from ollama import ChatResponse
```

### ollama.chat

Main method to access ollama API via ollama package

**Functionality Summary:**
A method that initiates a chat request with an AI model, supporting both synchronous and streaming responses. It handles message processing and tool integration for conversational interactions.

**Interface Details:**

1. `chat` method:
   - **Signatures:**

     ```python
     def chat(
       self,
       model: str = '',
       messages: Optional[Sequence[Union[Mapping[str, Any], Message]]] = None,
       tools: Optional[Sequence[...]] = None,
       stream: bool = False,
       think: Optional[Union[bool, Literal['low', 'medium', 'high']]] = None,
       logprobs: Optional[bool] = None,
       top_logprobs: Optional[int] = None,
       format: Optional[Literal['', 'json']] = None,
       options: Optional[Union[Mapping[str, Any], Options]] = None,
       keep_alive: Optional[Union[float, str]] = None
     ) -> Union[ChatResponse, Iterator[ChatResponse]]
     ```

   - **Arguments:**
     - `model`: The AI model to use for the chat.
     - `messages`: Input messages in specified format.
     - `tools`: Tools (functions or JSON schemas) available during chat.
     - `stream`: Boolean indicating if response should be streamed.
     - `think`: Controls internal reasoning level ('low', 'medium', 'high' or False).
     - `logprobs`: Indicates whether to include log probabilities in output.
     - `top_logprobs`: Number of top tokens with highest log probabilities.
     - `format`: Output format (empty string or 'json').
     - `options`: Additional settings as dictionary or Options object.
     - `keep_alive`: Keeps connection alive for specified duration.

   - **Return:**
     - `ChatResponse` if streaming is disabled (`stream=False`)
     - `Iterator[ChatResponse]` if streaming is enabled (`stream=True`)

2. **Raises:**
   - `RequestError`: If no model is provided.
   - `ResponseError`: If the request cannot be fulfilled.

The function uses overloading to handle different stream modes, making it versatile for both batch and real-time chat interactions.

## Data structures

### Connection Parameters

A dataclass to encapsulate connection details:

- API endpoint URL
- Authentication credentials
- Timeout settings
- Stream options

### Request Context

Context object should be a dataclass containing request-specific parameters:

- model name
- system prompt
- conversation history
- streaming preference

## Functions

- use context object to access ollama

### Init session

Start session with ollama API. Argument session,

```python
def init_session(
    api_endpoint: str = "https://ollama.com",
    auth_token: Optional[str] = None,
) -> Dict:
    """
    Establishes a connection to the Ollama API.

    Args:
        api_endpoint: Base URL for the Ollama API
        auth_token: Authentication token if required

    Returns:
        Session parameters object
    """
```

### Close session

Clear session context

### Init context

Should check availability of the model via `get_models`
May optionally pull the model

### Chat

Send message within a connection. Arguments session, context, message, history

```python
def chat(
    ollama_chat: Callable, #specify parameters for Callable
    message: Dict[str, str],
    context: Dict,
    history: List[Dict],
    session_params
) -> Dict[str, Any]:
    """
    Initiates a conversation with the specified model.

    Args:
        message: User message to send
        context: Request context including system prompt
        history: Conversation history
        session_params: Connection parameters

    Returns:
        Response from the model
    """
```

### Request

Send a single message without a history

```python
def request(ollama_chat: Callable, message: str, context: Dict) -> str:
    """
    Sends a single message without maintaining conversation state.

    Args:
        message: User input
        context: Request context

    Returns:
        Model's response
    """
```

### Get list of models

**name**: `get_models`

```python
def get_models(ollama_list_fn: Callable, session_params) -> List[str]:
    """
    Retrieves available models from the platform.

    Args:
        session_params: Connection parameters

    Returns:
        List of model names
    """
```

List models

```python
ollama.list()
```

### Pull the model

Get model via ollama interface. Argument - session object

```python
def pull_model(ollama_pull_fn: Callable, model_name: str, session_params) -> bool:
    """
    Downloads and caches a specific model.

    Args:
        model_name: Name of the model to download
        session_params: Connection parameters

    Returns:
        Success status
    """
```

Pull a model

```python
ollama.pull('gemma3')
```

### General Ollama examples

```python
from ollama import chat
from ollama import ChatResponse

response: ChatResponse = chat(model='gemma3', messages=[
  {
    'role': 'user',
    'content': 'Why is the sky blue?',
  },
])
print(response['message']['content'])
# or access fields directly from the response object
print(response.message.content)
```

Possible errors

```python
model = 'does-not-yet-exist'

try:
  ollama.chat(model)
except ollama.ResponseError as e:
  print('Error:', e.error)
  if e.status_code == 404:
    ollama.pull(model)
```
