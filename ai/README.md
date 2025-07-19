# AI Module

Core module for the PyClaudeCli application providing a command-line interface to Claude AI with advanced features including variable system, plugin architecture, and C++ integration.

## Structure

- `__init__.py` - Module initialization and version info
- `__main__.py` - Entry point for running the module
- `cli.py` - Command-line interface implementation with argument parsing
- `constants.py` - Application constants and default configurations
- `models.py` - Data models for interactions and responses

## Subdirectories

- `api/` - Claude API client implementations (sync and async)
- `bindings/` - **C++ API bindings for cross-language integration**
- `modes/` - Different interaction modes (interactive, async interactive)
- `plugins/` - Extensible plugin system with decorators
- `utils/` - Comprehensive utility functions including:
  - Configuration management
  - Variable system with persistence
  - Input validation and security
  - Terminal UI components (spinner, colors, themes)
  - Music generation and playback
  - Connection pooling for API efficiency

## Key Features

### Variable System
- **Simple syntax**: `name=John`, then use `name` directly in text
- **Persistent storage**: Variables saved to `~/.config/claude/variables.json`
- **JSON support**: Arrays, objects, booleans, null values automatically parsed
- **Cross-session**: Variables persist between CLI restarts
- **80+ test coverage**: Comprehensive test suite for reliability

### C++ Integration
- **Cross-language API**: Access variables from C++ using `GetVariable("name")`
- **CMake build system**: Modern C++23 support with Clang as default
- **Conditional compilation**: Shared code between library and tests
- **Python bindings**: Seamless integration with Python variable system

### Interactive Mode Features
- **Conversation history**: View with `c` or `conversation` command
- **File uploads**: `upload file1.txt file2.py --recursive dir/`
- **Variable management**: `vars` command to list all stored variables
- **Auto-interpolation**: Variables automatically replaced in conversations
- **Vim keybindings**: Efficient text navigation and editing

### API Features
- **Async support**: Non-blocking API calls for better performance
- **Connection pooling**: Reuse HTTP connections efficiently
- **Streaming responses**: Real-time response display
- **Error handling**: Comprehensive error messages and recovery

### Plugin System
- **Decorator-based**: Simple `@plugin` decorator for extensions
- **Hot reload**: Plugins can be loaded dynamically
- **Event hooks**: Subscribe to application events
- **Custom commands**: Add new commands to interactive mode

## Quick Start

```bash
./r                  # Start console with variable system
./b                  # Build C++ components and run tests
./t --quick          # Test variable functionality
```