"""
Command-line interface handling for AI CLI
"""

import os
import sys
from .utils.colors import Colors
from .utils.spinner import Spinner
from .utils.io import load_conversation_state, save_conversation_state
from .modes.interactive import InteractiveMode
from .api.client import ClaudeClient
from .constants import HISTORY_FILE

def handle_command_line_query(query):
    """Handle a command line query without entering interactive mode"""
    client = ClaudeClient()
    
    # Add command to history
    with open(os.path.expanduser(HISTORY_FILE), 'a') as f:
        f.write(query + '\n')
    
    # Load existing conversation state
    message_history = load_conversation_state()
    
    # Check for special commands
    if query.lower() == "clear":
        message_history = []
        save_conversation_state(message_history)
        print("Conversation history cleared.")
        return 0
    elif query.lower() == "c" or query.lower() == "conversation":
        if not message_history:
            print("No conversation history found.")
            return 0
            
        exchanges = []
        for i in range(0, len(message_history), 2):
            if i+1 < len(message_history):
                exchanges.append((message_history[i]["content"], message_history[i+1]["content"]))
                
        for i, (user, assistant) in enumerate(exchanges, 1):
            user_short = user[:50] + "..." if len(user) > 50 else user
            print(f"{i}. User: {user_short}")
            assistant_short = assistant[:50] + "..." if len(assistant) > 50 else assistant
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
        reply, updated_history = client.generate_response(query)
        spinner.stop()
        print(f"{Colors.BLUE}<{Colors.RESET} {Colors.CYAN}{reply}{Colors.RESET}")
        
        # Save updated conversation state
        save_conversation_state(updated_history)
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
