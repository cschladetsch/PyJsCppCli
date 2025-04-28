# Project Name

A Python utility for processing and analyzing data with built-in AI capabilities.

## Installation

### Setting up PythonClaudeCli

1. Clone the repository:
```bash
git clone https://github.com/username/PythonClaudeCli.git ~/local/PythonClaudeCli
```

2. Create and activate a virtual environment:
```bash
cd ~/local/PythonClaudeCli
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Add the `ai` function to your shell configuration:
Add the following to your `.bashrc` or `.zshrc` file:
```bash
ai() {
    if [[ -d "/home/xian/local/PythonClaudeCli/.venv" ]]
    then
        source "/home/xian/local/PythonClaudeCli/.venv/bin/activate"
        python "/home/xian/local/PythonClaudeCli/main.py" "$@"
        deactivate
    else
        echo "Virtual environment not found. Please set up PythonClaudeCli first."
    fi
}
```

5. Update your shell:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

*Note: Adjust the paths in the function to match your installation location.*

## Usage

The project can be used as a command-line utility or imported as a library in your Python code.

### As a library

```python
from project import ai

# Using the AI function for text analysis
result = ai.analyze("Your text to analyze")
print(result)

# Using the AI function for data processing
processed_data = ai.process(your_data)
```

### Command line

```bash
# Basic usage
python -m project analyze "Text to analyze"

# Processing a file
python -m project process --input data.csv --output results.json
```

## Bash Functions

### `ai` Bash Function

The project includes a bash function called `ai` that provides quick access to AI capabilities directly from your terminal.

#### Usage:

```bash
ai [your question or prompt]
```

#### Examples:

```bash
# Get factual information
$ ai what is capital of india
 New Delhi is the capital city of India. It has been the capital of India since 1911...

# Explanations
$ ai explain quantum computing

# Calculations
$ ai what is the square root of 144?

# Code generation
$ ai write a python function to calculate fibonacci numbers

# Translation
$ ai translate "hello world" to Spanish
```

#### Installation:

Add the following to your `.bashrc` or `.zshrc` file:

```bash
ai() {
    if [[ -d "/home/xian/local/PythonClaudeCli/.venv" ]]
    then
        source "/home/xian/local/PythonClaudeCli/.venv/bin/activate"
        python "/home/xian/local/PythonClaudeCli/main.py" "$@"
        deactivate
    else
        echo "Virtual environment not found. Please set up PythonClaudeCli first."
    fi
}
```

This function checks if the virtual environment for PythonClaudeCli exists, activates it, runs the main Python script with all provided arguments, and then deactivates the virtual environment when done.

You'll need to adjust the paths to match your installation location.

## API Reference

### `ai` Module

The `ai` module provides intelligent processing features.

#### `ai.analyze(text, mode="default")`

Analyzes the given text using AI techniques and returns structured insights.

**Parameters:**
- `text` (str): The text to analyze
- `mode` (str, optional): Analysis mode. Options: "default", "comprehensive", "summary". Defaults to "default"

**Returns:**
