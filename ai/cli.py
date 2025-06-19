"""
Command-line interface handling for AI CLI
"""

import os
import sys
import random
from .utils.colors import Colors
from .utils.spinner import Spinner
from .utils.io import load_conversation_state, save_conversation_state, append_to_conversation_log
from .modes.interactive import InteractiveMode
from .api.client import ClaudeClient
from .constants import HISTORY_FILE, RESPONSE_INTROS
from .models import Interaction

def handle_command_line_query(query):
    """Handle a command line query without entering interactive mode"""
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
        print("AI CLI - Command Line Interface for Claude AI")
        print("\nUsage:")
        print("  ai [command or query]")
        print("  ai --help, -h                - Show this help")
        print("\nAvailable commands:")
        print("  help, ?                      - Show this help")
        print("  clear                        - Clear conversation history")
        print("  c, conversation              - Show conversation history")
        print("  upload <file1> [file2] ...   - Upload files to AI")
        print("    Options:")
        print("      --recursive, -r          - Include all files in directories")
        print("\nWith no arguments, AI CLI enters interactive mode.")
        return 0
        
    spinner = Spinner()
    try:
        spinner.start()
        reply, updated_interactions = client.generate_response(query, interactions=interactions)
        spinner.stop()
        intro = random.choice(RESPONSE_INTROS)
        print(f"{Colors.BLUE}<{Colors.RESET} {Colors.CYAN}{intro}\n\n{reply}{Colors.RESET}")
        
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
        print(f"{Colors.RED}An error occurred while processing your request: {str(e)}{Colors.RESET}")
        return 1

def main():
    """Main entry point for the CLI"""
    # Check for --help flag
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        return handle_command_line_query("help")
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
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
