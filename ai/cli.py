"""
Command-line interface handling for AI CLI

This module provides the main command-line interface for the AI CLI,
handling both interactive and non-interactive modes.
"""

import os
import sys
import random
from typing import List, Optional, Union
from .utils.colors import Colors
from .utils.spinner import Spinner
from .utils.output_formatter import (
    OutputFormatter, print_error, print_warning, 
    print_success, print_info, print_response
)
from .utils.io import load_conversation_state, save_conversation_state, append_to_conversation_log
from .modes.interactive import InteractiveMode
from .api.client import ClaudeClient
from .constants import HISTORY_FILE, RESPONSE_INTROS
from .models import Interaction

def handle_command_line_query(query: str) -> int:
    """Handle a command line query without entering interactive mode.
    
    Args:
        query: The user's query string
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    client = ClaudeClient()
    
    # Add command to history
    with open(os.path.expanduser(HISTORY_FILE), 'a') as f:
        f.write(query + '\n')
    
    # Load existing conversation state
    interactions = load_conversation_state()
    
    # Check for special commands
    if query.lower() == "clear":
        interactions = []
        save_conversation_state(interactions)
        print("Conversation history cleared.")
        return 0
    elif query.lower() == "c" or query.lower() == "conversation":
        if not interactions:
            print("No conversation history found.")
            return 0
            
        for i, interaction in enumerate(interactions, 1):
            user_short = interaction.query[:50] + "..." if len(interaction.query) > 50 else interaction.query
            print(f"{i}. User: {user_short}")
            assistant_short = interaction.response[:50] + "..." if len(interaction.response) > 50 else interaction.response
            print(f"   Claude: {assistant_short}")
            print()
        return 0
        
    # Handle the upload command
    if query.lower().startswith("upload "):
        args = query.split()[1:]
        interactive = InteractiveMode()
        interactive.handle_upload_command(args)
        return 0
    
    # Handle help command
    if query.lower() in ["help", "?"]:
        print("Ask CLI - Command Line Interface for Claude AI")
        print("\nUsage:")
        print("  ask [command or query]")
        print("  ask --help, -h                - Show this help")
        print("  ask --reset                  - Reset configuration to defaults")
        print("  ask -                        - Read query from stdin")
        print("  ask '''multiline query'''    - Start multiline query with triple quotes")
        print("\nAvailable commands:")
        print("  help, ?                      - Show this help")
        print("  clear                        - Clear conversation history")
        print("  c, conversation              - Show conversation history")
        print("  upload <file1> [file2] ...   - Upload files for analysis")
        print("    Options:")
        print("      --recursive, -r          - Include all files in directories")
        print("\nMultiline queries:")
        print("  - Use triple quotes (''' or \"\"\") to start a multiline query")
        print("  - Read from stdin: echo \"query\" | ask -")
        print("  - Pipe from file: cat query.txt | ask -")
        print("\nWith no arguments, Ask CLI enters interactive mode.")
        return 0
        
    spinner = Spinner()
    try:
        spinner.start()
        reply, updated_interactions = client.generate_response(query, interactions=interactions)
        spinner.stop()
        intro = random.choice(RESPONSE_INTROS)
        print_response(intro, reply)
        
        # Save updated conversation state
        save_conversation_state(updated_interactions)
        # Log the latest interaction to markdown file
        if updated_interactions:
            append_to_conversation_log(updated_interactions[-1])
        return 0
        
    except (KeyboardInterrupt, EOFError):
        spinner.stop()
        print("\nOperation canceled.")
        return 1
    except Exception as e:
        spinner.stop()
        print_error(f"An error occurred while processing your request: {str(e)}")
        return 1

def main():
    """Main entry point for the CLI"""
    # Check for --help flag
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        return handle_command_line_query("help")
    
    # Check for --reset flag
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        from pathlib import Path
        
        # Clear all default config paths
        config_paths = [
            Path.home() / '.ask' / 'config.yml',
            Path.home() / '.ask' / 'config.yaml',
            Path.home() / '.ask' / 'config.json',
            Path.cwd() / '.ask.yml',
            Path.cwd() / '.ask.yaml',
            Path.cwd() / '.ask.json',
        ]
        
        removed_files = []
        for path in config_paths:
            if path.exists():
                try:
                    path.unlink()
                    removed_files.append(str(path))
                except Exception as e:
                    print_error(f"Failed to remove {path}: {e}")
        
        if removed_files:
            print_success("Configuration reset successfully. Removed:")
            for file in removed_files:
                print(f"  - {file}")
        else:
            print_info("No configuration files found to remove.")
        
        return 0
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        
        # Check if query is "-" to read from stdin
        if query == "-":
            try:
                query = sys.stdin.read().strip()
                if not query:
                    print_error("No input received from stdin")
                    return 1
            except KeyboardInterrupt:
                print("\nOperation canceled.")
                return 1
        # Check if query starts with triple quotes for multiline
        elif query.startswith('"""') or query.startswith("'''"):
            quote_style = query[:3]
            # If the query ends with the same triple quotes, it's complete
            if len(query) > 6 and query.endswith(quote_style):
                query = query[3:-3].strip()
            else:
                # Otherwise, keep reading until we find the closing quotes
                lines = [query[3:]]
                print("Enter multiline query (end with " + quote_style + " on a new line):")
                try:
                    while True:
                        line = input()
                        if line.strip() == quote_style:
                            break
                        lines.append(line)
                    query = "\n".join(lines).strip()
                except (KeyboardInterrupt, EOFError):
                    print("\nOperation canceled.")
                    return 1
        
        return handle_command_line_query(query)
    else:
        # No arguments, enter interactive mode
        interactive = InteractiveMode()
        try:
            interactive.run()
            return 0
        except Exception as e:
            print(f"{Colors.RED}An error occurred: {str(e)}{Colors.RESET}")
            return 1

if __name__ == "__main__":
    sys.exit(main())
