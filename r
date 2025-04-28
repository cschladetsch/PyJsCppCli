#!/bin/bash
# Script to set up PythonClaudeCli

# Text colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Setup directory
INSTALL_DIR="$HOME/local/PythonClaudeCli"
VENV_DIR="$INSTALL_DIR/.venv"

echo -e "${GREEN}Setting up PythonClaudeCli at $INSTALL_DIR${NC}\n"

# Check Python version
echo -e "${CYAN}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1)
if [[ $? -ne 0 ]]; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi
echo -e "${GREEN}û Found $PYTHON_VERSION${NC}"

# Create directory if it doesn't exist
echo -e "${CYAN}Setting up directory structure...${NC}"
mkdir -p "$INSTALL_DIR"
if [[ $? -ne 0 ]]; then
    echo -e "${RED}Failed to create directory: $INSTALL_DIR${NC}"
    exit 1
fi
echo -e "${GREEN}û Directory created${NC}"

# Create virtual environment
echo -e "${CYAN}Creating virtual environment...${NC}"
if [[ -d "$VENV_DIR" ]]; then
    echo -e "${BLUE}i Virtual environment already exists${NC}"
else
    python3 -m venv "$VENV_DIR"
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}Failed to create virtual environment. Install the venv module and try again.${NC}"
        exit 1
    fi
    echo -e "${GREEN}û Virtual environment created${NC}"
fi

# Activate virtual environment and install packages
echo -e "${CYAN}Installing required packages...${NC}"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install anthropic>=0.44.0 prompt_toolkit>=3.0.39 pyperclip>=1.8.2
if [[ $? -ne 0 ]]; then
    echo -e "${RED}Failed to install required packages.${NC}"
    deactivate
    exit 1
fi
echo -e "${GREEN}û Packages installed${NC}"
deactivate

# Create main.py if it doesn't exist
echo -e "${CYAN}Creating main script...${NC}"
MAIN_SCRIPT="$INSTALL_DIR/main.py"
if [[ -f "$MAIN_SCRIPT" ]]; then
    echo -e "${BLUE}i main.py already exists${NC}"
else
    cat > "$MAIN_SCRIPT" << 'EOF'
#!/usr/bin/env python3
"""
Main entry point for the AI CLI
"""

import sys
from ai.cli import main

if __name__ == "__main__":
    sys.exit(main())
EOF
    chmod +x "$MAIN_SCRIPT"
    echo -e "${GREEN}û Created main.py${NC}"
fi

# Create shell integration
echo -e "${CYAN}Setting up shell integration...${NC}"
SHELL_SCRIPT="$HOME/.ai_shell_integration"
cat > "$SHELL_SCRIPT" << EOF
#!/bin/bash

ai () {
    if [[ -d "$INSTALL_DIR/.venv" ]]
    then
        source "$INSTALL_DIR/.venv/bin/activate"
        python "$INSTALL_DIR/main.py" "\$@"
        deactivate
    else
        echo "Virtual environment not found. Please set up PythonClaudeCli first."
    fi
}
EOF

# Determine shell configuration file
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_CONFIG="$HOME/.bashrc"
else
    SHELL_CONFIG="$HOME/.bashrc"
    echo -e "${BLUE}i Could not determine shell type, using .bashrc${NC}"
fi

# Check if integration is already added
if grep -q "source $SHELL_SCRIPT" "$SHELL_CONFIG"; then
    echo -e "${BLUE}i Shell integration already exists in $SHELL_CONFIG${NC}"
else
    # Add shell integration to config
    echo -e "\n# AI CLI integration\nsource $SHELL_SCRIPT" >> "$SHELL_CONFIG"
    echo -e "${GREEN}û Added shell integration to $SHELL_CONFIG${NC}"
fi

# Ask for API token
echo -e "${CYAN}Setting up API token...${NC}"
TOKEN_FILE="$HOME/.ai_token"
if [[ -f "$TOKEN_FILE" ]]; then
    echo -e "${BLUE}i API token file already exists${NC}"
else
    echo -e "${CYAN}Enter your Anthropic API key (or press Enter to skip):${NC} "
    read -r API_KEY
    if [[ -n "$API_KEY" ]]; then
        echo "$API_KEY" > "$TOKEN_FILE"
        chmod 600 "$TOKEN_FILE"
        echo -e "${GREEN}û API token saved${NC}"
    else
        echo -e "${BLUE}i API token setup skipped${NC}"
    fi
fi

# Create project structure if needed
echo -e "${CYAN}Setting up project structure...${NC}"
mkdir -p "$INSTALL_DIR/ai/utils" "$INSTALL_DIR/ai/api"

# Check if project files already exist
if [[ -f "$INSTALL_DIR/ai/cli.py" ]]; then
    echo -e "${BLUE}i Project files already exist${NC}"
else
    # Create basic files
    cat > "$INSTALL_DIR/ai/__init__.py" << 'EOF'
"""
AI CLI - A command-line interface for Claude AI
"""

__version__ = "0.2.0"
EOF

    cat > "$INSTALL_DIR/ai/__main__.py" << 'EOF'
"""
Entry point for running as a module
"""

from .cli import main

if __name__ == "__main__":
    main()
EOF

    cat > "$INSTALL_DIR/ai/constants.py" << 'EOF'
"""
Constants and configuration for AI CLI
"""

import os

# File paths
HISTORY_FILE = os.path.expanduser("~/.ai_history")
CONVERSATION_STATE_FILE = os.path.expanduser("~/.ai_conversation_state.json")
UPLOAD_CACHE_DIR = os.path.expanduser("~/.ai_uploads")
TOKEN_FILE = os.path.expanduser("~/.ai_token")

# API configuration
DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
DEFAULT_MAX_TOKENS = 1024
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."

# UI Configuration
SPINNER_FRAMES = ["?", "?", "?", "?", "?", "?", "?", "?", "?", "?"]
SPINNER_MESSAGES = [
    "Thinking", "Processing", "Contemplating",
    "Analyzing", "Computing", "Pondering"
]
EOF

    cat > "$INSTALL_DIR/ai/utils/__init__.py" << 'EOF'
"""AI CLI utilities"""
EOF

    cat > "$INSTALL_DIR/ai/api/__init__.py" << 'EOF'
"""AI API client"""
EOF

    # Create minimal cli.py
    cat > "$INSTALL_DIR/ai/cli.py" << 'EOF'
"""
Command-line interface for AI CLI
"""

import sys

def main():
    """Main entry point for the CLI"""
    print("AI CLI is set up, but functionality needs to be implemented.")
    print("Please copy your project files into the correct locations.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
EOF

    echo -e "${GREEN}û Created basic project structure${NC}"
    echo -e "${BLUE}i This is a minimal setup. You'll need to add full functionality.${NC}"
fi

# Final instructions
echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "To use the AI CLI, restart your terminal or run:"
echo -e "  source $SHELL_CONFIG"
echo -e "Then you can run 'ai' from anywhere."
echo -e "\n${BLUE}Note: You'll need to copy your actual project files into $INSTALL_DIR/ai/ to get full functionality.${NC}"
