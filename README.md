# ask - Claude CLI

![CLI Demo](Resources/Demo.gif)

A Python CLI for interacting with Claude AI, with persistent conversation history, file uploads, variable interpolation, and MIDI music generation. Also includes a C++ variable API and a multi-provider HTTP client framework.

**Version:** 0.3.0 | **Python:** 3.8+ | **License:** MIT

## Installation

```bash
git clone https://github.com/cschladetsch/PyClaudeCli
cd PyClaudeCli
pip install -e .
```

Set your API key:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# or
export CLAUDE_API_KEY="sk-ant-..."
# or write it to ~/.claude_token
```

## Usage

```bash
ask                                  # Enter interactive mode
ask "What is 2+2?"                   # One-shot query
ask -                                # Read query from stdin
echo "explain this" | ask -          # Pipe input
ask --model claude-3-opus "..."      # Use a specific model
ask --json "Return prime numbers"    # JSON output
ask --no-spinner "Quick question"    # Disable spinner
```

### Interactive mode commands

| Command | Description |
|---------|-------------|
| `help`, `?` | Show help |
| `clear` | Clear conversation history |
| `c`, `conversation` | Show conversation history |
| `h [N]` | Show last N history entries |
| `upload <file> ...` | Upload files for analysis |
| `name=value` | Set a variable |
| `vars` | List all variables |
| `exit`, `quit` | Exit |

### Multiline queries

```bash
ask '''
Explain the difference between
TCP and UDP in simple terms
'''
```

### File uploads

```bash
ask upload image.png diagram.jpg     # Upload images
ask upload -r ./src                  # Upload directory recursively
```

### Variables

Variables persist across sessions in `~/.config/claude/variables.json`.

```
λ name=Alice
λ Ask a question as if you were $name
```

## Options

| Flag | Description |
|------|-------------|
| `--help`, `-h` | Show help |
| `--version`, `-v` | Show version |
| `--model MODEL` | Specify Claude model |
| `--no-spinner` | Disable loading spinner |
| `--json` | Output response as JSON |
| `--config PATH` | Specify config file |
| `--init-config` | Create default config files |
| `--reset` | Reset configuration to defaults |
| `--music` | Toggle startup music |
| `--music-history` | Show music play history |
| `--volume [LEVEL]` | Set/show music volume (0.0-1.0) |
| `--playsong [--loop]` | Play accumulated MIDI song |
| `--gen-midi [TEXT]` | Generate MIDI file from text |
| `--clear-music` | Delete accumulated MIDI file |

## Configuration

Run `ask --init-config` to create default config files in `~/.config/claude/`:

| File | Purpose |
|------|---------|
| `system` | Custom system prompt |
| `aliases.json` | Command aliases |
| `models.json` | Model preferences and music settings |
| `templates.json` | Response templates |

## Project Structure

```
ask/                    # Python CLI package
├── api/                # Anthropic API client
├── modes/              # Interactive and async modes
├── plugins/            # Plugin system
└── utils/              # Colors, config, IO, variables, MIDI

ask/bindings/           # C++ variable API (bridges to Python via popen)
src/                    # C++ multi-provider HTTP framework (Anthropic, OpenAI, Gemini, Cohere)
Tests/                  # Python unit/integration tests and C++ tests
```

## Building C++ components

```bash
./b                     # Build and run all tests
```

Requires: CMake 3.10+, GCC 13+ or Clang 15+, libcurl, nlohmann-json.

```bash
# Ubuntu/Debian
sudo apt install build-essential cmake libcurl4-openssl-dev nlohmann-json3-dev
```

## License

MIT
