# Utils Module

Utility functions and helpers for PyClaudeCli, including the comprehensive variable system.

## Files

- `__init__.py` - Module initialization
- `colors.py` - Terminal color utilities
- `config.py` - Configuration management
- `config_loader.py` - Configuration file loading
- `connection_pool.py` - Connection pooling utilities
- `exceptions.py` - Custom exception classes
- `interactive.py` - Interactive mode utilities
- `io.py` - Input/output utilities
- `logging.py` - Logging configuration
- `markdown_renderer.py` - Markdown rendering utilities
- `midi_music.py` - MIDI music generation utilities
- `music.py` - Music generation utilities
- `output_formatter.py` - Output formatting utilities
- `spinner.py` - Loading spinner implementation
- `streaming.py` - Stream processing utilities
- `theme_config.py` - Theme configuration management
- `validation.py` - Input validation utilities
- **`variables.py`** - **Persistent variable storage and interpolation system**

## Key Components

### Variable System (`variables.py`)
The crown jewel of the utils module - a comprehensive variable management system:

- **Simple Assignment**: `name=John` syntax for setting variables
- **Direct Usage**: Use `name` directly in text (no $ prefix needed)
- **JSON Parsing**: Automatic parsing of arrays, objects, booleans, null values
- **Persistence**: Variables stored in `~/.config/claude/variables.json`
- **Cross-Session**: Variables persist between CLI restarts
- **Interactive Integration**: Seamless integration with interactive mode

#### Usage Examples
```python
from ai.utils.variables import VariableManager

vm = VariableManager()

# Set variables
vm.process_input("name=Alice")
vm.process_input("age=25") 
vm.process_input('hobbies=["reading", "coding"]')

# Use variables (interpolation)
result, _ = vm.process_input("Hello name, you are age years old")
# → "Hello Alice, you are 25 years old"

# List all variables
variables = vm.list_variables()
```

#### Features
- **40+ comprehensive tests** covering all functionality
- **C++ API integration** for cross-language access
- **Error handling** for corrupted files and edge cases
- **Unicode support** for international characters
- **JSON validation** with fallback to string storage

## Description

This module contains various utility functions that support the core functionality of PyClaudeCli, including configuration management, I/O operations, formatting, user interface elements, and the powerful variable system that enables persistent data storage across CLI sessions.