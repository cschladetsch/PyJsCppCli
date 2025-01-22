# Python Cluade Interactive Console

## Overview
This project provides an interactive command-line interface (CLI) to communicate with an AI assistant powered by Anthropic's Claude. Users can input prompts, receive responses, and leverage helpful tools like command history and vim-style editing. 

The script includes a loading spinner for a smooth user experience and customizable settings for improved usability.

---

## Features
- **Interactive Mode**: Chat with the AI in real-time.
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

---

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/interactive-ai-cli.git
   cd interactive-ai-cli
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your API token:
   - Save your Anthropic API key to the `~/.claude_token` file or set it in the `CLAUDE_API_KEY` environment variable.

---

## Usage
### Interactive Mode
Run the script without arguments to enter the interactive mode:
```bash
python main.py
```

### Direct Query Mode
Run the script with a query to get an immediate response:
```bash
python main.py "Your query here"
```

### Key Commands
- **General**:
  - `help` or `?`: Display available commands.
  - `exit` or `quit`: Exit the program.
- **History**:
  - `h`: Show complete command history.
  - `h N`: Show the last N entries from history.

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

