# AI Module

Core module for the PyClaudeCli application with variable system and C++ integration.

## Structure

- `__init__.py` - Module initialization
- `__main__.py` - Entry point for running the module
- `build_info.py` - Build information and versioning
- `cli.py` - Command-line interface implementation
- `constants.py` - Application constants
- `models.py` - Data models and structures

## Subdirectories

- `api/` - API client implementations
- `bindings/` - **C++ API bindings for cross-language integration**
- `modes/` - Different interaction modes (interactive, async)
- `plugins/` - Plugin system and extensions
- `utils/` - Utility functions and helpers

## Key Features

### Variable System
- **Simple syntax**: `name=John`, then use `name` directly
- **Persistent storage**: Variables saved to `~/.config/claude/variables.json`
- **JSON support**: Arrays, objects, booleans, null values automatically parsed
- **Cross-session**: Variables persist between CLI restarts

### C++ Integration
- **Cross-language API**: Access variables from C++ using `GetVariable("name")`
- **CMake build system**: Modern C++23 support with Clang as default
- **Conditional compilation**: Shared code between library and tests

### Interactive Integration
- **Seamless integration**: Variable commands work in interactive mode
- **Command support**: `vars` command to list all stored variables
- **Auto-interpolation**: Variables automatically replaced in conversations

## Quick Start

```bash
./r                  # Start console with variable system
./b                  # Build C++ components and run tests
./t --quick          # Test variable functionality
```