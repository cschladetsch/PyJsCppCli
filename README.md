# AI CLI

![CLI Demo2](Demo3.gif)

![CLI Demo](Resources/Demo.gif)

Command-line interface for interacting with AI models.

**Version:** 0.3.0 | **Python:** 3.8+ | **License:** MIT

## Overview

This CLI app provides a seamless, terminal-based interface to interact with various AI models. It combines the power of advanced AI reasoning capabilities with the efficiency of a command-line workflow, perfect for developers, researchers, and power users.

## Features

- **Interactive Mode**: Engage in continuous conversations with AI through a responsive terminal interface
- **Command-Line Mode**: Quick queries without entering the interactive environment
- **Variable System**: Persistent variables with simple assignment and interpolation (`name=John`, then use `name`)
- **Vim-Style Key Bindings**: Familiar navigation and editing for power users
- **Conversation Management**: Save, view, and clear conversation history
- **File Upload Support**: Share files with AI for analysis, with intelligent handling of both text and image files
- **Rich Terminal UI**: Color-coded output and animated progress indicators
- **Context Preservation**: Maintain conversation context for more coherent exchanges
- **C++ API**: Cross-language variable access for integration
- **Async Support**: Asynchronous API client for improved performance
- **Plugin Architecture**: Extensible plugin system for custom functionality
- **Theme Support**: Customizable color themes for terminal output
- **MIDI Music Generation**: Generate and play MIDI music from text
- **Connection Pooling**: Efficient HTTP connection management

## Installation

### Prerequisites

- Python 3.8+
- AI API key (supports multiple providers)
- sox (optional, for startup music)
  - macOS: `brew install sox`
  - Ubuntu/Debian: `sudo apt-get install sox`
  - Fedora: `sudo dnf install sox`
  - Arch: `sudo pacman -S sox`

### Quick Install

```bash
# Clone the repository
# You have already done this

# Set up your API key:
echo "your-api-key" > ~/.ai_token
# Or set environment variable: export AI_API_KEY="your-api-key"
# Or for specific providers: export ANTHROPIC_API_KEY="your-anthropic-key"

# Build and test everything
./b    # Builds C++ components and runs all tests

# Run the CLI (dependencies will be auto-installed on first run)
python3 main.py "Hello AI!"
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
| `--init-config` | Create default config files in ~/.config/ai-cli/ |
| `--model MODEL` | Specify AI model to use |
| `--no-spinner` | Disable loading spinner animation |
| `--json` | Output response in JSON format |
| `--config PATH` | Specify custom config file path |
| `--music` | Toggle startup music on/off |
| `--music-history` | Show music play history |
| `--volume [LEVEL]` | Set/show music volume (0.0-1.0) |
| `--playsong` | Play the entire accumulated MIDI song |
| `--playsong --loop` | Play MIDI song on loop (Ctrl+C to stop) |
| `--gen-midi [TEXT]` | Generate MIDI file from text input |
| `--clear-music` | Delete the accumulated MIDI file |

### Interactive Mode

Launch the interactive mode by running the command without arguments:

```bash
ask
```

This opens a prompt where you can chat with AI continuously. The prompt is displayed as a magenta lambda symbol (λ).

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
| `vars` | Show all stored variables |
| `name=value` | Set a variable (e.g., `user=Alice`) |
| `exit`, `quit` | Exit the program |

#### Variable System

Set and use variables for persistent storage across conversations:

```bash
# Set variables
name=John
age=25
data=["item1", "item2", "item3"]

# Use variables (simple word substitution)
Hello name, you are age years old
# → "Hello John, you are 25 years old"

# Variables persist across sessions
vars  # List all variables
```

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
ask --model gpt-4 "Explain quantum computing"

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

The CLI intelligently handles different file types:

- **Text Files** (markdown, code, txt, etc.): Content is extracted and included directly in the message to AI
- **Image Files** (jpeg, png, gif, webp): Sent as attachments via the AI API
- **Unsupported Files**: Warning message is displayed, and file is skipped

## Configuration

### API Key

You can provide your AI API key in either of two ways:

1. **Environment Variable**:
   ```bash
   export AI_API_KEY="your-api-key-here"
   # Or for specific providers:
   export ANTHROPIC_API_KEY="your-anthropic-key"
   export OPENAI_API_KEY="your-openai-key"
   ```

2. **Token File**:
   ```bash
   echo "your-api-key-here" > ~/.ai_token
   ```

### Configuration Directory

The CLI uses `~/.config/ai-cli/` for user customization. To create default configuration files:

```bash
ask --init-config
```

This creates the following files:

| File | Purpose |
|------|---------|
| `~/.config/ai-cli/system` | Custom system prompt |
| `~/.config/ai-cli/conversations.json` | Conversation history (auto-managed) |
| `~/.config/ai-cli/variables.json` | Persistent variables |
| `~/.config/ai-cli/aliases.json` | Command aliases |
| `~/.config/ai-cli/models.json` | Model preferences and settings |
| `~/.config/ai-cli/templates.json` | Response templates |

#### Custom System Prompt

Edit `~/.config/ai-cli/system` to customize AI's behavior:

```bash
echo "You are a helpful coding assistant specializing in Python" > ~/.config/ai-cli/system
```

#### Model Preferences

Edit `~/.config/ai-cli/models.json` to configure:
- Default model
- Conversation load timeout (default: 3.0 seconds)
- Temperature and max tokens

Example:
```json
{
  "default": "gpt-4",
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
- Via config: Set `"startup_music": false` in `~/.config/ai-cli/models.json`

Music history is stored in `~/.config/ai-cli/music.json` (trimmed to 3KB).
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
| `~/.ai_token` | API token (if not using environment variable) |
| `~/.ask_history` | Command history |
| `~/.ask_uploads` | Temporary cache for uploaded files |
| `~/.config/ai-cli/` | User configuration directory |
| `~/.config/ai-cli/conversations.json` | Conversation state |
| `~/.config/ai-cli/system` | Custom system prompt |
| `~/.config/ai-cli/aliases.json` | Command aliases |
| `~/.config/ai-cli/models.json` | Model preferences |
| `~/.config/ai-cli/templates.json` | Response templates |
| `~/.config/ai-cli/music.json` | Music play history |

Note: The `~/.ask_*` files are in the home directory for easy access, while configuration files are organized under `~/.config/ai-cli/` following XDG standards.

## Development & Testing

### Build System

The project includes a modern CMake-based build system with C++23 support:

```bash
./b    # Build everything and run all tests
./r    # Run console (builds if needed)
./t    # Run comprehensive test suite
```

#### Available Build Commands

| Script | Purpose |
|--------|---------|
| `./b` | Build C++ components and run all Python tests |
| `./r` | Smart run script - builds if needed, then starts console |
| `./t` | Comprehensive test suite with 40+ tests |

#### Test Options

```bash
./t --quick       # Quick functionality test (30 seconds)
./t --unit        # Run 80+ unit tests
./t --integration # Integration tests
./t --cpp         # C++ API tests
./t --build       # Build system tests
./t --help        # Show all options
```

The test suite includes:
- **80+ Unit Tests**: Comprehensive coverage of variable system
- **Integration Tests**: Full conversation flow testing
- **C++ API Tests**: Cross-language binding verification
- **Build System Tests**: CMake and compilation verification

### C++ Integration

The variable system includes a C++ API for cross-language integration:

```cpp
#include "ai/bindings/variable_api.cpp"

VariableManager vm;
vm.SetVariable("test", "value");
std::string result = vm.GetVariable("test");
```

Build C++ components:
```bash
mkdir build && cd build
cmake .. -DCMAKE_CXX_COMPILER=clang++
make
```

## Advanced Usage

### Using with Unix Pipes

AI CLI works well with Unix pipes, allowing integration into complex workflows:

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
- **API Layer**: AI provider API integration with connection pooling
- **Plugin System**: Extensible architecture for custom functionality
- **Utilities**: Configuration, validation, logging, and streaming support

## Project Structure

```
ai/                          # AI integration
│   ├── bindings/             # C++ API bindings
│   │   ├── variable_api.cpp  # C++ variable interface
│   │   └── CMakeLists.txt    # C++ build configuration
│   ├── plugins/              # Plugin system
│   │   ├── base.py           # Base plugin classes
│   │   ├── decorators.py     # Plugin decorators
│   │   └── plugin_manager.py # Plugin management
│   └── utils/                # Utilities
│       ├── config.py         # Configuration management
│       ├── config_loader.py  # Configuration file loading
│       ├── variables.py      # Variable system
│       ├── validation.py     # Input validation
│       ├── exceptions.py     # Error handling
│       ├── logging.py        # Logging system
│       ├── streaming.py      # Streaming support
│       ├── connection_pool.py # Connection pooling
│       ├── io.py            # File I/O operations
│       ├── colors.py        # Terminal colors
│       ├── spinner.py       # Progress animation
│       ├── output_formatter.py # Output formatting
│       ├── interactive.py    # Interactive mode helpers
│       ├── markdown_renderer.py # Markdown rendering
│       ├── music.py         # Music player functionality
│       ├── midi_music.py    # MIDI music generation
│       └── theme_config.py  # Theme configuration
├── b                        # Build script
├── r                        # Run script  
├── t                        # Test script
├── CMakeLists.txt          # CMake configuration
├── Doxyfile                # Documentation generation
├── docs/                     # Documentation
├── tests/                    # Test suite
│   ├── unit/                # Unit tests (40+ tests)
│   ├── integration/         # Integration tests
│   └── cpp/                 # C++ API tests
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

If you see "Token file not found and API key environment variable is not set":

1. Create a token file: `echo "your-api-key" > ~/.ai_token`
2. Or set the environment variable: `export AI_API_KEY="your-api-key"`

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

- The Python community for excellent libraries like prompt\_toolkit

