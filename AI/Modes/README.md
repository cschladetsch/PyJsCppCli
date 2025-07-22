# Modes Module

Different interaction modes for the CLI with integrated variable system support.

## Files

- `__init__.py` - Module initialization
- `interactive.py` - **Synchronous interactive mode with variable integration**
- `async_interactive.py` - **Asynchronous interactive mode with variable integration**

## Description

This module provides different ways to interact with AI models through the CLI, supporting both synchronous and asynchronous conversation modes. Both modes include full integration with the persistent variable system.

## Variable System Integration

### Interactive Mode (`interactive.py`)
The synchronous interactive mode includes comprehensive variable support:

#### Variable Commands
- `name=value` - Set a variable (e.g., `user=Alice`)
- `vars` - List all stored variables
- Variable interpolation in all input text

#### Features
- **Automatic Processing**: All user input processed for variable assignments and interpolation
- **Persistent Storage**: Variables saved to `~/.config/ai-cli/variables.json`
- **Real-time Updates**: Variables immediately available after assignment
- **Help Integration**: Variable commands included in help system

#### Usage Flow
```bash
λ name=Alice
Variable 'name' set to: Alice

λ age=25
Variable 'age' set to: 25

λ Hello name, you are age years old
Hello Alice, you are 25 years old

λ vars
Stored variables:
  name = Alice
  age = 25
```

### Async Interactive Mode (`async_interactive.py`)
The asynchronous mode also supports the variable system with the same functionality as the synchronous mode, enabling:
- **Non-blocking Operations**: Variable access doesn't block async operations
- **Concurrent Safety**: Thread-safe variable access
- **Performance**: Efficient variable processing in async context

## Implementation Details

### Variable Processing Pipeline
1. **Input Capture**: User input received by interactive mode
2. **Variable Processing**: `process_variables()` called from `ai.utils.variables`
3. **Assignment Detection**: Check for `var=value` patterns
4. **Interpolation**: Replace variable names with values in text
5. **Command Routing**: Route to appropriate handler (variables, help, AI model, etc.)

### Integration Points
- **Process Input**: Variable processing integrated into main input handler
- **Help System**: Variable commands automatically included in help
- **Error Handling**: Graceful handling of variable system errors
- **State Management**: Variables persist across mode restarts

### Technical Implementation
```python
# In both interactive modes:
from ..Utils.variables import process_input as process_variables

def process_input(self, user_prompt):
    # Process variables first
    processed_prompt, was_assignment = process_variables(user_prompt)
    
    if was_assignment:
        print(processed_prompt)  # Show assignment result
        return True
    
    # Continue with normal processing using interpolated text
    user_prompt = processed_prompt
    # ... rest of interactive logic
```

## Benefits

- **Seamless Integration**: Variables work transparently in all interactive modes
- **Consistent Experience**: Same variable syntax across sync/async modes  
- **Persistent State**: Variables survive mode switches and CLI restarts
- **Enhanced Productivity**: Persistent data across conversation sessions
- **Cross-Mode Compatibility**: Variables set in one mode available in all others