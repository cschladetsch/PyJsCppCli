# API Module

Handles communication with AI model APIs through both synchronous and asynchronous clients, with integrated variable system support and advanced features.

## Files

- `__init__.py` - Module initialization and exports
- `async_client.py` - Asynchronous API client with streaming support
- `client.py` - Synchronous API client with Anthropic SDK integration

## Usage

The API module provides both synchronous and asynchronous clients for interacting with AI model API endpoints. All API interactions support the persistent variable system for enhanced conversation continuity.

### Synchronous Client (client.py)
- Uses AI provider SDKs (e.g., Anthropic Python SDK)
- Supports file uploads (text and images)
- Handles conversation history and context
- Automatic retry logic for API errors

### Asynchronous Client (async_client.py)
- Built with aiohttp for non-blocking operations
- Streaming response support for real-time display
- Connection pooling for efficiency
- Compatible with async/await patterns

## Features

### API Key Management
- Reads from environment variable `AI_API_KEY` or provider-specific keys
- Falls back to `~/.ai_token` file
- Secure token handling with validation

### Message Formatting
- Automatic conversation history formatting
- System prompt support
- Image attachment handling
- Token limit management

### Error Handling
- Comprehensive error messages
- Network error recovery
- API rate limit handling
- Invalid response detection

## Variable System Integration

### Client Features
Both API clients can process messages containing variables before sending to the AI model:
- **Variable Interpolation**: Replace variable references in prompts
- **Session Continuity**: Maintain context across API calls
- **Persistent State**: Variables survive client restarts

### Implementation Example
```python
from ai.api import AIClient

client = AIClient()
response, interactions = client.generate_response(
    query="Tell me about {topic}",  # Variables are interpolated
    interactions=conversation_history,
    system_prompt=custom_prompt
)
```

### Benefits
- **Enhanced Context**: Variables provide persistent context across API calls
- **Dynamic Content**: Messages can reference stored variables
- **Conversation State**: Maintain user preferences and data between sessions