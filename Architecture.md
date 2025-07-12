# PythonClaudeCli - Detailed Project Overview

## 📁 Project Structure

```
PythonClaudeCli/
├── LICENSE                    # MIT License
├── Readme.md                  # Project documentation
├── __init__.py               # Package initialization
├── ai/                       # Main package directory
│   ├── __init__.py          
│   ├── __main__.py          # Module entry point
│   ├── api/                 # API client components
│   │   ├── __init__.py
│   │   └── client.py        # Claude API wrapper
│   ├── cli.py               # Main CLI handling logic
│   ├── constants.py         # Configuration constants
│   ├── models.py            # Data models (Interaction class)
│   ├── modes/               # CLI modes
│   │   ├── __init__.py
│   │   └── interactive.py   # Interactive mode implementation
│   └── utils/               # Utility modules
│       ├── __init__.py
│       ├── colors.py        # ANSI color codes
│       ├── interactive.py   # Interactive utilities
│       ├── io.py           # File I/O operations
│       └── spinner.py      # Progress spinner animation
├── create.py                # Helper script for creating zip files
├── main.py                  # Main entry point
├── requirements.txt         # Python dependencies
├── resources/               # Project resources
│   ├── Demo.gif            # Demo animation
│   └── Image.jpg           # Image resource
└── setup.py                # Installation script
```

## 🎯 Project Purpose

**PythonClaudeCli** is a command-line interface tool for interacting with Anthropic's Claude AI models. It provides both interactive and command-line modes for seamless AI conversations in the terminal.

## 🔧 Core Components

### 1. **Entry Points**
- `main.py`: Primary entry point that imports and runs the CLI
- `ai/__main__.py`: Module entry point for running as `python -m ai`

### 2. **CLI Handler** (`ai/cli.py`)
- Processes command-line arguments
- Routes between interactive and command-line modes
- Handles special commands (help, clear, history)
- Manages application lifecycle

### 3. **API Client** (`ai/api/client.py`)
- Wraps the Anthropic Python SDK
- Manages API authentication
- Handles both text and image uploads
- Maintains conversation history
- Implements retry logic for API calls

### 4. **Interactive Mode** (`ai/modes/interactive.py`)
- Built with `prompt_toolkit` for rich terminal UI
- Implements vim-style key bindings
- Handles multi-line input
- Manages file uploads and special commands
- Maintains session state

### 5. **Data Models** (`ai/models.py`)
- **`Interaction`**: Structured class representing a user-AI interaction
  - Stores query, response, and timestamp
  - Provides serialization methods for JSON persistence
  - Ensures consistent data structure across the application

### 6. **Utilities**
- **`io.py`**: File operations, token management, conversation persistence, markdown logging
- **`colors.py`**: ANSI color codes for terminal formatting
- **`spinner.py`**: Animated progress indicator during API calls
- **`interactive.py`**: Helper functions for interactive mode

## 📊 Data Flow

```
User Input
    ↓
CLI Handler (cli.py)
    ↓
┌─────────────────┬──────────────────┐
│ Interactive Mode│ Command-Line Mode │
│ (interactive.py)│                   │
└─────────┬───────┴───────┬───────────┘
          ↓               ↓
      API Client (client.py)
          ↓
    Claude API
          ↓
    Response Processing
          ↓
    Terminal Output
```

## 📦 Dependencies

### Python Packages (requirements.txt)
- `anthropic>=0.44.0` - Official Anthropic Python SDK
- `prompt_toolkit>=3.0.39` - Interactive terminal applications
- `pyperclip>=1.8.2` - Cross-platform clipboard support

### System Requirements
- Python 3.8 or higher
- Anthropic API key
- Terminal with ANSI color support

## ⚙️ Configuration

### User Configuration Files
Located in home directory:
- `~/.ask_token` - Primary API key storage
- `~/.ask_history` - Command history
- `~/.ask_conversation_state.json` - Conversation persistence (JSON format)
- `~/.ask_conversation.md` - Human-readable conversation log (Markdown format)
- `~/.ask_uploads/` - Temporary cache for uploaded files

### Legacy Support
For backward compatibility:
- `~/.claude_token`
- `~/.claude_history`
- `~/.claude_conversation_state.json`

### API Configuration (constants.py)
- Default model: `claude-3-5-sonnet-20241022`
- Default max tokens: 1024
- Default system prompt: "You are a helpful assistant."

## 🚀 Workflows

### Installation Workflow (setup.py)
1. **Environment Check**: Verifies Python 3.8+ and pip availability
2. **Directory Setup**: Creates installation directory
3. **Virtual Environment**: Sets up isolated Python environment
4. **Package Installation**: Installs all required dependencies
5. **File Setup**: Copies project files to installation directory
6. **Shell Integration**: Adds `ai` command to system PATH
7. **API Configuration**: Prompts for API token if not present

### Usage Workflows

#### Interactive Mode
```bash
ai  # Launch interactive prompt
```

**Available Commands:**
- `help`, `?` - Display help information
- `h [N]` - Show last N command history entries
- `c [N]` - Show last N conversation entries
- `clear` - Clear current conversation
- `upload <files>` - Upload files to include in conversation
- `exit`, `quit` - Exit the program

#### Command-Line Mode
```bash
# Quick query
ai "What is the capital of France?"

# Show help
ai --help
ai -h

# Clear conversation
ai clear

# Upload files
ai upload document.md image.png

# Recursive directory upload
ai upload --recursive ./docs/
```

## 🌟 Special Features

### File Upload Capabilities
- Multiple file upload support
- Text files included in message body
- Images sent as attachments
- Recursive directory upload with `-r` flag
- Intelligent file type detection
- Caching mechanism for uploaded files

### Conversation Management
- Persistent conversation history across sessions
- Dual persistence format:
  - JSON-based state persistence for programmatic access
  - Markdown-based log for human-readable history
- Structured message history using `Interaction` class
- History viewing and navigation
- Clear command for fresh starts

### Terminal Experience
- Color-coded output (user input, AI responses, system messages)
- Animated spinner during API calls
- Vim-style key bindings in interactive mode
- Multi-line input support
- Unix pipe compatibility

### Error Handling
- Graceful API error handling
- Retry logic for transient failures
- Clear error messages
- Token validation

## 🔐 Security Considerations
- API tokens stored in user home directory with appropriate permissions
- No hardcoded credentials
- Secure communication with Claude API via HTTPS
- Local file caching with user-only access

## 🛠️ Development Tools
- `create.py`: Utility script for creating distribution zip files
- Git integration for version control
- MIT License for open-source distribution

The project demonstrates clean architecture with separation of concerns, robust error handling, and a user-friendly interface for AI interactions through the terminal.

## 📝 Recent Updates

### Structured Message History (Latest)
- Introduced `Interaction` class in `models.py` for structured conversation data
- Refactored conversation history to use consistent data structures
- Improved serialization and deserialization of conversation state

### Markdown Conversation Logging
- Added automatic markdown logging of all conversations to `~/.ask_conversation.md`
- Provides human-readable conversation history with timestamps
- Complements the JSON state file for dual-format persistence

### Enhanced CLI Flags
- Added `--help` and `-h` flags for command-line help access
- Improved help message formatting and accessibility