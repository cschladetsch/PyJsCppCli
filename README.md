# Claude CLI

![Claude CLI Demo](Resources/Demo.gif)

Command-line interface for interacting with Claude AI models.

**Version:** 0.2.1 | **Python:** 3.8+ | **License:** MIT

## Overview

Claude CLI provides a seamless, terminal-based interface to interact with Anthropic's Claude AI models. It combines the power of Claude's advanced reasoning capabilities with the efficiency of a command-line workflow, perfect for developers, researchers, and power users.

## Features

- **Interactive Mode**: Engage in continuous conversations with Claude through a responsive terminal interface
- **Command-Line Mode**: Quick queries without entering the interactive environment
- **Vim-Style Key Bindings**: Familiar navigation and editing for power users
- **Conversation Management**: Save, view, and clear conversation history
- **File Upload Support**: Share files with Claude for analysis, with intelligent handling of both text and image files
- **Rich Terminal UI**: Color-coded output and animated progress indicators
- **Context Preservation**: Maintain conversation context for more coherent exchanges

## Installation

### Prerequisites

- Python 3.8+
- Anthropic API key
- sox (optional, for startup music)
  - macOS: `brew install sox`
  - Ubuntu/Debian: `sudo apt-get install sox`
  - Fedora: `sudo dnf install sox`
  - Arch: `sudo pacman -S sox`

### Quick Install

```bash
# Clone the repository
git clone https://github.com/cschladetsch/PyClaudeCli.git
cd PyClaudeCli

# Set up your API key
echo "your-anthropic-api-key" > ~/.claude_token
# Or set environment variable: export CLAUDE_API_KEY="your-anthropic-api-key"

# Run the CLI (dependencies will be auto-installed on first run)
python3 main.py "Hello Claude!"
```

The application will automatically install required dependencies on first run if they're not already present.

### Setting Up the "ask" Command

To use the `ask` command from anywhere in your terminal, add an alias to your shell configuration:

#### For Zsh (`.zshrc`)

```bash
echo "alias ask=~/local/repos/PyClaudeCli/main.py" >> ~/.zshrc
source ~/.zshrc
```

#### For Bash (`.bashrc`)

```bash
echo "alias ask=~/local/repos/PyClaudeCli/main.py" >> ~/.bashrc
source ~/.bashrc
```

Note: Adjust the path to match where you cloned the repository. The example above assumes the repository is in `~/local/repos/PyClaudeCli/`.

After setting up the alias, you can use the `ask` command from any directory.

## Usage

### Command-Line Options

```bash
ask [options] [query]
```

#### Options

| Option | Description |
|--------|-------------|
| `--help`, `-h` | Show help message and exit |
| `--version`, `-v` | Show version information |
| `--reset` | Reset configuration to defaults |
| `--model MODEL` | Specify Claude model to use (e.g., claude-3-opus) |
| `--no-spinner` | Disable loading spinner animation |
| `--json` | Output response in JSON format |
| `--config PATH` | Specify custom config file path |
| `--music` | Toggle startup music on/off |
| `--music-history` | Show music play history |
| `--volume [LEVEL]` | Set/show music volume (0.0-1.0) |

### Interactive Mode

Launch the interactive mode by running the command without arguments:

```bash
ask
```

This opens a prompt where you can chat with Claude continuously. The prompt is displayed as a magenta lambda symbol (λ).

#### Available Commands in Interactive Mode

| Command | Description |
|---------|-------------|
| `help`, `?` | Show available commands |
| `h` | Show command history |
| `h N` | Show last N commands from history |
| `c` | Show conversation history |
| `c N` | Show last N exchanges from conversation |
| `clear` | Clear conversation history |
| `upload <file1> [file2] ...` | Upload files to analyze |
| `exit`, `quit` | Exit the program |

#### Upload Command Options

```bash
# Upload a single file
upload document.md

# Upload multiple files
upload document.md image.png code.py

# Upload all files in a directory (recursive)
upload --recursive ./project/

# Or use the short form
upload -r ./project/
```

### Command-Line Mode

For quick, one-off queries without entering interactive mode:

```bash
# Ask a question
ask "What is the capital of France?"

# Use a specific model
ask --model claude-3-opus "Explain quantum computing"

# Get JSON output
ask --json "List 5 prime numbers"

# Disable the spinner for cleaner output
ask --no-spinner "What is 2+2?"

# Pipe input from stdin
echo "Analyze this text" | ask -

# Multiline queries with triple quotes
ask '''
This is a multiline query.
It can span multiple lines.
'''

# Clear conversation history
ask clear

# Show conversation history
ask c
# or
ask conversation

# Upload files for analysis
ask upload document.md image.png

# Show version
ask --version

# Show help
ask --help
```

## File Handling

Claude CLI intelligently handles different file types:

- **Text Files** (markdown, code, txt, etc.): Content is extracted and included directly in the message to Claude
- **Image Files** (jpeg, png, gif, webp): Sent as attachments via the Claude API
- **Unsupported Files**: Warning message is displayed, and file is skipped

## Configuration

### API Key

You can provide your Claude API key in either of two ways:

1. **Environment Variable**:
   ```bash
   export CLAUDE_API_KEY="your-api-key-here"
   ```

2. **Token File**:
   ```bash
   echo "your-api-key-here" > ~/.claude_token
   ```

### Configuration Directory

Claude CLI uses `~/.config/claude/` for user customization. To create default configuration files:

```bash
ask --init-config
```

This creates the following files:

| File | Purpose |
|------|---------|
| `~/.config/claude/system` | Custom system prompt |
| `~/.config/claude/conversations.json` | Conversation history (auto-managed) |
| `~/.config/claude/aliases.json` | Command aliases |
| `~/.config/claude/models.json` | Model preferences and settings |
| `~/.config/claude/templates.json` | Response templates |

#### Custom System Prompt

Edit `~/.config/claude/system` to customize Claude's behavior:

```bash
echo "You are a helpful coding assistant specializing in Python" > ~/.config/claude/system
```

#### Model Preferences

Edit `~/.config/claude/models.json` to configure:
- Default model
- Conversation load timeout (default: 3.0 seconds)
- Temperature and max tokens

Example:
```json
{
  "default": "claude-3-sonnet-20240229",
  "conversation_load_timeout": 5.0,
  "startup_music": true,
  "preferences": {
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

#### Startup Music

The CLI plays a full 4/4 bar musical phrase on startup. This can be toggled:
- Via command line: `ask --music`
- Via config: Set `"startup_music": false` in `~/.config/claude/models.json`

Music history is stored in `~/.config/claude/music.json` (trimmed to 3KB).
Patterns include arpeggios, scales, and rhythmic variations in various keys.

**Note for WSL2 users:** The CLI will attempt to play audio through Windows PowerShell. If you don't hear sound:
1. Check Windows Terminal settings - ensure "Bell notification style" is not set to "None"
2. Check Windows sound settings - ensure system sounds are not muted
3. The CLI tries two methods:
   - Windows audio synthesis (higher quality)
   - PowerShell console beeps (fallback)

### Data Storage

The CLI maintains several files:

| File | Purpose |
|------|---------|
| `~/.ask_history` | Command history |
| `~/.config/claude/conversations.json` | Conversation state |
| `~/.ask_uploads` | Temporary cache for uploaded files |
| `~/.ask_token` | API token (if not using environment variable) |

Legacy paths are supported for backward compatibility.

## Advanced Usage

### Using with Unix Pipes

Claude CLI works well with Unix pipes, allowing integration into complex workflows:

```bash
# Analyze the output of a command
ls -lh | ask "Analyze this directory listing and identify large files"

# Analyze a file's content
cat complex_code.py | ask "Explain what this code does"
```

### Shell Function Integration

You can create shell functions for common operations:

```bash
# Add to your .bashrc or .zshrc
function explain() {
  cat "$1" | ask "Explain this code step by step"
}

# Then use like:
explain complex_algorithm.py
```

## Architecture

![Architecture Diagram](docs/architecture.png)

The Ask CLI follows a layered architecture with clear separation of concerns:

- **Entry Points**: Multiple ways to launch the application
- **CLI Layer**: Command parsing and routing
- **Interaction Modes**: Interactive, async, and command-line modes
- **API Layer**: Claude API integration with connection pooling
- **Plugin System**: Extensible architecture for custom functionality
- **Utilities**: Configuration, validation, logging, and streaming support

## Project Structure

```
PyClaudeCli/
├── main.py                    # Primary entry point
├── ai/                        # Main package
│   ├── __main__.py           # Module entry point
│   ├── cli.py                # CLI handling logic
│   ├── constants.py          # Configuration constants
│   ├── models.py             # Data models
│   ├── api/                  # API clients
│   │   ├── client.py         # Sync Claude API client
│   │   └── async_client.py   # Async Claude API client
│   ├── modes/                # Interaction modes
│   │   ├── interactive.py    # Interactive mode
│   │   └── async_interactive.py # Async interactive mode
│   ├── plugins/              # Plugin system
│   │   ├── base.py           # Base plugin classes
│   │   ├── decorators.py     # Plugin decorators
│   │   └── plugin_manager.py # Plugin management
│   └── utils/                # Utilities
│       ├── config.py         # Configuration management
│       ├── validation.py     # Input validation
│       ├── exceptions.py     # Error handling
│       ├── logging.py        # Logging system
│       ├── streaming.py      # Streaming support
│       ├── connection_pool.py # Connection pooling
│       ├── io.py            # File I/O operations
│       ├── colors.py        # Terminal colors
│       ├── spinner.py       # Progress animation
│       └── output_formatter.py # Output formatting
├── docs/                     # Documentation
├── tests/                    # Test suite
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── requirements.txt         # Dependencies
├── requirements-dev.txt     # Development dependencies
├── pyproject.toml          # Modern Python packaging
└── .github/workflows/      # CI/CD pipeline
```

## Version Management

The project uses semantic versioning (MAJOR.MINOR.PATCH) and includes an automatic version bumping system:

- **Automatic Version Bumping**: A git pre-commit hook automatically increments the patch version on each commit
- **Version Display**: The current version is shown when starting the interactive mode
- **Version Files**: Version is maintained in both `__init__.py` and `ai/__init__.py`

To disable automatic version bumping for a specific commit:
```bash
git commit --no-verify -m "Your commit message"
```

## Troubleshooting

### API Key Not Found

If you see "Token file not found and 'CLAUDE_API_KEY' environment variable is not set":

1. Create a token file: `echo "your-api-key" > ~/.claude_token`
2. Or set the environment variable: `export CLAUDE_API_KEY="your-api-key"`

### File Upload Issues

For "File type not supported" errors with text files, ensure you have the latest version with proper text file handling.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Anthropic](https://www.anthropic.com/) for creating Claude
- The Python community for excellent libraries like prompt_toolkit

---

*Made with ❤️ for the Claude community*
