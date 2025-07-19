# Utils Module

Comprehensive utility functions and helpers for AI CLI, providing core functionality including the advanced variable system, UI components, and system integration.

## Files

### Core Utilities
- `__init__.py` - Module initialization and exports
- `config.py` - Main configuration management system
- `config_loader.py` - YAML/JSON configuration file loading
- `exceptions.py` - Custom exception classes for error handling
- `validation.py` - Input validation and security checks
- `io.py` - File I/O operations, token management, and file uploads

### User Interface Components
- `colors.py` - Terminal color utilities with ANSI escape codes
- `spinner.py` - Animated loading spinner for long operations
- `output_formatter.py` - Response formatting and display
- `markdown_renderer.py` - Rich markdown rendering in terminal
- `theme_config.py` - Customizable color themes for output
- `interactive.py` - Interactive mode helpers and prompt management

### Music and Audio
- `music.py` - Musical sequence generation and playback
- `midi_music.py` - MIDI file generation from text input

### API and Networking
- `connection_pool.py` - HTTP connection pooling for efficiency
- `streaming.py` - Async stream processing for real-time responses
- `logging.py` - Structured logging configuration

### Variable System
- **`variables.py`** - **Persistent variable storage and interpolation system with 80+ tests**

## Key Components

### Variable System (`variables.py`)
The crown jewel of the utils module - a comprehensive variable management system:

- **Simple Assignment**: `name=John` syntax for setting variables
- **Direct Usage**: Use `name` directly in text (no $ prefix needed)
- **JSON Parsing**: Automatic parsing of arrays, objects, booleans, null values
- **Persistence**: Variables stored in `~/.config/ai-cli/variables.json`
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
- **80+ comprehensive tests** covering all edge cases
- **C++ API integration** for cross-language access
- **Error handling** for corrupted files and edge cases
- **Unicode support** for international characters
- **JSON validation** with fallback to string storage
- **Thread-safe operations** for concurrent access
- **Performance optimized** for large variable sets

### Configuration System
- **Hierarchical config loading**: System → User → Local
- **YAML and JSON support**: Flexible configuration formats
- **Environment variable override**: `AI_CONFIG_PATH`
- **Default templates**: Auto-generated on first run

### UI Components
- **Themes**: Multiple color themes (default, monokai, solarized, dracula)
- **Spinner**: Smooth animation with fallback for non-TTY
- **Markdown**: Tables, code blocks, lists, emphasis
- **Progress indicators**: Real-time status updates

### Security Features
- **Input validation**: Sanitize user inputs
- **Path traversal protection**: Safe file operations
- **API key security**: Never logged or exposed
- **Command injection prevention**: Safe subprocess execution

## Usage Examples

### Variable System
```python
from ai.utils.variables import process_input

# Set and use variables
result, was_assignment = process_input("name=Alice")
result, _ = process_input("Hello name!")  # → "Hello Alice!"
```

### Theme System
```python
from ai.utils.theme_config import apply_theme, THEMES

# Apply a theme
theme = THEMES["monokai"]
apply_theme(theme)
```

### Configuration
```python
from ai.utils.config import get_config

# Load user configuration
config = get_config()
model = config.get("default_model", "gpt-4")
```

## Description

This module provides the foundation for AI CLI's functionality, offering robust utilities for configuration management, user interface, file operations, and the innovative variable system that enables persistent context across CLI sessions. All components are designed with security, performance, and user experience in mind.