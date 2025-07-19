# API Module

Handles communication with Claude API with integrated variable system support.

## Files

- `__init__.py` - Module initialization
- `async_client.py` - Asynchronous API client implementation
- `client.py` - Synchronous API client implementation

## Usage

The API module provides both synchronous and asynchronous clients for interacting with Claude's API endpoints. All API interactions support the persistent variable system for enhanced conversation continuity.

## Variable System Integration

### Client Features
Both API clients can process messages containing variables before sending to Claude:
- **Variable Interpolation**: Replace variable references in prompts
- **Session Continuity**: Maintain context across API calls
- **Persistent State**: Variables survive client restarts

### Implementation
```python
from ..utils.variables import process_input as process_variables

# Before sending to API
processed_prompt, was_assignment = process_variables(user_input)
if not was_assignment:
    # Send processed_prompt to Claude API
    response = client.send_message(processed_prompt)
```

### Benefits
- **Enhanced Context**: Variables provide persistent context across API calls
- **Dynamic Content**: Messages can reference stored variables
- **Conversation State**: Maintain user preferences and data between sessions