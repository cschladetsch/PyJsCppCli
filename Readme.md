# Python Claude Interactive Console

## Demo

[Demo](resources/Demo.gif)

## Overview
This project provides an interactive command-line interface (CLI) to communicate with an AI assistant powered by Anthropic's Claude. Users can input prompts, receive responses, and leverage helpful tools like command history and vim-style editing. 

The script includes a loading spinner for a smooth user experience and customizable settings for improved usability.

Also provided is a script called 'ask' that provides a `bash` function to make it easier to use.

---

## Features
- **Interactive Mode**: Chat with the AI in real-time.
- **Conversation Memory**: The CLI remembers conversation context between command invocations.
- **Command History**: Access past commands and responses.
- **ANSI Colors**: User-friendly and visually appealing interface.
- **Vim Key Bindings**: Navigate and edit prompts using vim-style shortcuts.
- **Spinner Animation**: Smooth loading animations during AI processing.
- **Customizable System Prompt**: Define the AI's behavior with a pre-set system prompt.
- **Batch Query Support**: Run a query directly via command-line arguments.

---

## Requirements
- Python 3.7+
- Required Libraries: Install dependencies using pip.

```bash
pip install anthropic prompt_toolkit
```

---

## File Structure
- **main.py**: The primary script for running the interactive CLI.
- **`~/.claude_token`**: File to store the Anthropic API token.
- **`~/.claude_history`**: File to store the history of user commands.
- **`~/.claude_conversation_state.json`**: File to store conversation context between invocations.

---

## Installation
1. Clone the repository:
   ```bash
   $ git clone https://github.com/cschladetsch/PythonClaudeCli
   $ cd PythonClaudeCli
   ```

2. Install required dependencies:
   ```bash
   $ pip install -r requirements.txt
   ```

3. Set up your API token:
   - Save your Anthropic API key to the `~/.claude_token` file or set it in the `CLAUDE_API_KEY` environment variable.

---

## Usage

### Interactive Mode

Run the script without arguments to enter the interactive mode:
```bash
$ python main.py
$ # or, just:
$ ask
```

### Direct Query Mode
Run the script with a query to get an immediate response:
```bash
$ python main.py "Your query here"
$ # or:
$ ask "Your query here"
```

### Memory Management
The CLI now maintains conversation memory between invocations:
```bash
$ ask "What is the capital of France?"
< Paris is the capital of France.

$ ask "What is its population?"
< The population of Paris is approximately 2.1 million people in the city proper.
```

### Key Commands
- **General**:
  - `help` or `?`: Display available commands.
  - `exit` or `quit`: Exit the program.
- **History**:
  - `h`: Show complete command history.
  - `h N`: Show the last N entries from history.
- **Conversation**:
  - `c` or `conversation`: Show conversation history.
  - `c N`: Show the last N conversation exchanges.
  - `clear`: Clear the conversation memory.

---

## Spinner Animation
The script includes a smooth and visually engaging spinner animation. It cycles through various frames while displaying loading messages like:
- "Thinking..."
- "Processing..."
- "Contemplating..."

---

## Key Bindings
- **Vim Mode**: Enable vim-style navigation and editing using the `vi_mode` filter from `prompt_toolkit`.
- **Escape Key**: Switch between insert and command modes.

---

## Error Handling
The script includes robust error handling for:
- Missing API token file or environment variable.
- Failed API requests.
- KeyboardInterrupt or EOFError events for clean exits.

---

## Customization
### System Prompt
You can customize the assistant's behavior by modifying the `self.system_prompt` string in the `InteractiveMode` class.

### Spinner Messages
Edit the `self.loading_messages` list in the `Spinner` class to include personalized messages.

---

## Troubleshooting
- **Error: Token file not found**: Ensure the `~/.claude_token` file exists or set the `CLAUDE_API_KEY` environment variable.
- **Missing Dependencies**: Reinstall required libraries using:
  ```bash
  pip install -r requirements.txt
  ```

---

## License
This project is licensed under the [MIT License](LICENSE).
