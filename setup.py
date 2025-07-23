#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup script for PythonClaudeCli
This script will:
1. Create the necessary directory structure
2. Set up a virtual environment
3. Install required packages
4. Copy or create the required files
5. Make the 'ask' command available in your shell
"""

import os
import sys
import shutil
import subprocess
import platform
import argparse
from pathlib import Path
from datetime import datetime

# Colors for terminal output
class Colors:
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    CYAN = '\033[36m'
    RED = '\033[31m'
    ORANGE = '\033[38;5;208m'
    RESET = '\033[0m'

def print_step(message):
    """Print a step in the installation process"""
    print(f"{Colors.CYAN}==>{Colors.RESET} {message}")

def print_success(message):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message):
    """Print an error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message):
    """Print an info message"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")

def run_command(command, cwd=None, env=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command,
            check=True,
            text=True,
            capture_output=True,
            cwd=cwd,
            env=env
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {' '.join(command)}")
        print(e.stderr)
        return None

def check_python_version():
    """Check if Python version is at least 3.8"""
    print_step("Checking Python version...")
    
    if sys.version_info < (3, 8):
        print_error("Python 3.8 or higher is required")
        print_info(f"Current version: {sys.version}")
        return False
    
    print_success(f"Python {sys.version.split()[0]} detected")
    return True

def check_pip():
    """Check if pip is installed"""
    print_step("Checking for pip...")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            check=True,
            capture_output=True,
            text=True
        )
        print_success("pip is installed")
        return True
    except subprocess.CalledProcessError:
        print_error("pip is not installed")
        print_info("Please install pip before continuing")
        return False

def setup_directory(install_dir):
    """Create and set up the installation directory"""
    print_step(f"Setting up directory: {install_dir}")
    
    # Create the directory if it doesn't exist
    os.makedirs(install_dir, exist_ok=True)
    
    # Check if we can write to it
    if not os.access(install_dir, os.W_OK):
        print_error(f"Cannot write to {install_dir}")
        return False
    
    print_success(f"Directory ready: {install_dir}")
    return True

def setup_virtual_env(install_dir):
    """Set up a virtual environment"""
    venv_dir = os.path.join(install_dir, ".venv")
    print_step(f"Creating virtual environment at {venv_dir}")
    
    # Check if venv already exists
    if os.path.exists(venv_dir):
        print_info("Virtual environment already exists")
        return True
    
    # Create virtual environment
    result = run_command([sys.executable, "-m", "venv", venv_dir])
    if result is None:
        print_error("Failed to create virtual environment")
        return False
    
    print_success("Virtual environment created")
    return True

def install_requirements(install_dir):
    """Install required packages in the virtual environment"""
    print_step("Installing required packages...")
    
    # Determine the path to pip in the virtual environment
    if platform.system() == "Windows":
        pip_path = os.path.join(install_dir, ".venv", "Scripts", "pip")
    else:
        pip_path = os.path.join(install_dir, ".venv", "bin", "pip")
    
    # Install required packages
    packages = ["anthropic>=0.44.0", "prompt_toolkit>=3.0.39", "pyperclip>=1.8.2", 
                "pygame>=2.5.0", "pyyaml>=6.0", "aiohttp>=3.8.0", "aiofiles>=23.0.0"]
    for package in packages:
        print_info(f"Installing {package}...")
        result = run_command([pip_path, "install", package])
        if result is None:
            print_error(f"Failed to install {package}")
            return False
    
    print_success("All packages installed")
    return True

def create_main_script(install_dir):
    """Create main.py script"""
    print_step("Creating main.py script...")
    
    main_script = os.path.join(install_dir, "main.py")
    with open(main_script, "w") as f:
        f.write('''#!/usr/bin/env python3
"""
Main entry point for the Ask CLI
"""

import sys
from ask.cli import main

if __name__ == "__main__":
    sys.exit(main())
''')
    
    # Make executable on Unix-like systems
    if platform.system() != "Windows":
        os.chmod(main_script, 0o755)
    
    print_success("Created main.py")
    return True

def check_if_files_exist(install_dir):
    """Check if the Python package files already exist"""
    structure = [
        "ask/__init__.py",
        "ask/cli.py",
        "ask/__main__.py",
        "ask/constants.py",
        "ask/utils/__init__.py",
        "ask/utils/colors.py",
        "ask/utils/spinner.py",
        "ask/utils/io.py",
        "ask/utils/interactive.py",
        "ask/api/__init__.py",
        "ask/api/client.py"
    ]
    
    exists = True
    for file_path in structure:
        full_path = os.path.join(install_dir, file_path)
        if not os.path.exists(full_path):
            exists = False
            break
    
    return exists

def copy_project_files(install_dir, source_dir=None):
    """Copy project files to installation directory"""
    print_step("Setting up project files...")
    
    # Create directories if they don't exist
    for directory in ["ask", "ask/utils", "ask/api"]:
        os.makedirs(os.path.join(install_dir, directory), exist_ok=True)
    
    # If source directory is provided and exists, copy from there
    if source_dir and os.path.exists(source_dir):
        print_info(f"Copying files from {source_dir}")
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith(".py"):
                    src_path = os.path.join(root, file)
                    # Determine relative path from source_dir
                    rel_path = os.path.relpath(src_path, source_dir)
                    dest_path = os.path.join(install_dir, rel_path)
                    
                    # Create directories if needed
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    
                    # Copy the file
                    shutil.copy2(src_path, dest_path)
        print_success("Files copied from source directory")
        return True
    
    # Check if files already exist
    if check_if_files_exist(install_dir):
        print_info("Project files already exist")
        return True
    
    # Otherwise, create minimal structure with placeholder files
    files = {
        "ask/__init__.py": '''"""
Ask CLI - A command-line interface for Claude AI
"""

__version__ = "0.2.0"
''',
        "ask/__main__.py": '''"""
Entry point for running as a module
"""

from .cli import main

if __name__ == "__main__":
    main()
''',
        "ask/constants.py": '''"""
Constants and configuration for Ask CLI
"""

import os

# File paths
HISTORY_FILE = os.path.expanduser("~/.ask_history")
CONVERSATION_STATE_FILE = os.path.expanduser("~/.ask_conversation_state.json")
UPLOAD_CACHE_DIR = os.path.expanduser("~/.ask_uploads")
TOKEN_FILE = os.path.expanduser("~/.ask_token")

# API configuration
##DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
DEFAULT_MODEL = "claude-opus-4-20250514"
DEFAULT_MAX_TOKENS = 1024
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."

# UI Configuration
SPINNER_FRAMES = ["?", "?", "?", "?", "?", "?", "?", "?", "?", "?"]
SPINNER_MESSAGES = [
    "Thinking", "Processing", "Contemplating",
    "Analyzing", "Computing", "Pondering"
]
''',
        "ask/utils/__init__.py": '''"""Ask CLI utilities"""
''',
        "ask/api/__init__.py": '''"""Ask API client"""
''',
    }
    
    # Create minimal files
    for file_path, content in files.items():
        full_path = os.path.join(install_dir, file_path)
        with open(full_path, "w") as f:
            f.write(content)
    
    print_info("Created basic project structure")
    print_info("Note: This is a minimal setup. You'll need to add functionality.")
    return True

def setup_shell_integration(install_dir):
    """Set up shell integration for the Ask CLI"""
    print_step("Setting up shell integration...")
    
    home_dir = str(Path.home())
    shell_script_path = os.path.join(home_dir, ".ask_shell_integration")
    
    # Create the shell integration script
    with open(shell_script_path, "w") as f:
        f.write(f'''#!/bin/bash

ask () {{
    if [[ -d "{install_dir}/.venv" ]]
    then
        source "{install_dir}/.venv/bin/activate"
        python "{install_dir}/main.py" "$@"
        deactivate
    else
        echo "Virtual environment not found. Please set up PythonClaudeCli first."
    fi
}}
''')
    
    # Identify which shell config file to update
    shell = os.environ.get("SHELL", "")
    shell_config = None
    
    if "bash" in shell:
        shell_config = os.path.join(home_dir, ".bashrc")
    elif "zsh" in shell:
        shell_config = os.path.join(home_dir, ".zshrc")
    else:
        print_info("Could not determine your shell, using default .bashrc")
        shell_config = os.path.join(home_dir, ".bashrc")
    
    # Check if integration is already in the shell config
    if os.path.exists(shell_config):
        with open(shell_config, "r") as f:
            content = f.read()
            if "source ~/.ask_shell_integration" in content:
                print_info("Shell integration already set up")
                return True
    
    # Add source command to shell config
    try:
        with open(shell_config, "a") as f:
            f.write(f'\n# Ask CLI integration\nsource {shell_script_path}\n')
        print_success(f"Added Ask CLI integration to {shell_config}")
        print_info("To use, restart your terminal or run 'source " + shell_config + "'")
        return True
    except Exception as e:
        print_error(f"Failed to update shell config: {e}")
        print_info(f"Manually add 'source {shell_script_path}' to your shell config")
        return False

def setup_api_token():
    """Set up the API token"""
    print_step("Setting up API token...")
    
    # Check if CLAUDE_API_KEY environment variable is set
    if "CLAUDE_API_KEY" in os.environ:
        print_info("Using CLAUDE_API_KEY from environment variable")
        return True
    
    token_file = os.path.expanduser("~/.ask_token")
    
    # Check if token file already exists
    if os.path.exists(token_file):
        print_info("API token already exists")
        return True
    
    # Check if legacy token file exists
    legacy_token_file = os.path.expanduser("~/.claude_token")
    if os.path.exists(legacy_token_file):
        print_info("Legacy API token found at ~/.claude_token")
        return True
    
    # Ask for the API token
    api_key = input(f"{Colors.CYAN}Enter your Anthropic API key: {Colors.RESET}")
    if not api_key:
        print_error("No API key provided")
        return False
    
    # Save the token
    try:
        with open(token_file, "w") as f:
            f.write(api_key)
        os.chmod(token_file, 0o600)  # Set permissions to user read/write only
        print_success("API token saved")
        return True
    except Exception as e:
        print_error(f"Failed to save API token: {e}")
        return False


def main():
    """Main entry point for the setup script"""
    parser = argparse.ArgumentParser(description="Set up PythonClaudeCli")
    parser.add_argument("--dir", default=os.path.expanduser("~/local/PythonClaudeCli"),
                        help="Installation directory (default: ~/local/PythonClaudeCli)")
    parser.add_argument("--source", help="Source directory with existing files")
    parser.add_argument("--skip-token", action="store_true", help="Skip API token setup")
    parser.add_argument("--skip-shell", action="store_true", help="Skip shell integration")
    
    args = parser.parse_args()
    
    print(f"{Colors.GREEN}PythonClaudeCli Setup{Colors.RESET}")
    print()
    
    # Run all setup steps
    if not check_python_version():
        return 1
    
    if not check_pip():
        return 1
    
    if not setup_directory(args.dir):
        return 1
    
    if not setup_virtual_env(args.dir):
        return 1
    
    if not install_requirements(args.dir):
        return 1
    
    if not create_main_script(args.dir):
        return 1
    
    if not copy_project_files(args.dir, args.source):
        return 1
    
    if not args.skip_shell and not setup_shell_integration(args.dir):
        print_info("Shell integration skipped, but setup can continue")
    
    if not args.skip_token and not setup_api_token():
        print_info("API token setup skipped, but you'll need to add it later")
    
    
    print()
    print(f"{Colors.GREEN}Setup complete!{Colors.RESET}")
    print("To use the Ask CLI, restart your terminal or run:")
    shell = os.environ.get("SHELL", "").split("/")[-1]
    if shell in ["bash", "zsh"]:
        print(f"  source ~/.{shell}rc")
    else:
        print("  source your shell configuration file")
    print("Then you can run 'ask' from anywhere.")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
