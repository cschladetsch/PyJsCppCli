"""
Command-line interface handling for AI CLI

This module provides the main command-line interface for the AI CLI,
handling both interactive and non-interactive modes.
"""

import os
import sys
import random
import json
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

def handle_command_line_query(query: str, no_spinner: bool = False, json_output: bool = False, model: Optional[str] = None) -> int:
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
        
    # Configure client with model if specified
    if model:
        client.model = model
    
    spinner = Spinner()
    try:
        if not no_spinner:
            spinner.start()
        reply, updated_interactions = client.generate_response(query, interactions=interactions)
        if not no_spinner:
            spinner.stop()
        
        if json_output:
            import json
            output = {
                "query": query,
                "response": reply,
                "model": getattr(client, 'model', 'default')
            }
            print(json.dumps(output, indent=2))
        else:
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
    import argparse
    
    # Create parser but don't parse yet - we need to handle some cases manually
    parser = argparse.ArgumentParser(
        prog='ask',
        description='Command Line Interface for Claude AI',
        add_help=False,  # We'll handle help manually
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Check for --help or -h anywhere in arguments
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Ask CLI - Command Line Interface for Claude AI")
        try:
            from .build_info import BUILD_DATE
            print(f"Version: Built {BUILD_DATE}")
        except ImportError:
            pass
        print("\nUsage:")
        print("  ask [options] [query]")
        print("  ask                          - Enter interactive mode")
        print("  ask -                        - Read query from stdin")
        print("  ask '''multiline query'''    - Start multiline query with triple quotes")
        print("\nOptions:")
        print("  --help, -h                   - Show this help")
        print("  --version, -v                - Show version information")
        print("  --reset                      - Reset configuration to defaults")
        print("  --init-config                - Create default config files in ~/.config/claude/")
        print("  --music                      - Toggle startup music on/off")
        print("  --music-history              - Show music play history")
        print("  --volume [LEVEL]             - Set/show music volume (0.0-1.0)")
        print("  --model MODEL                - Specify Claude model to use")
        print("  --no-spinner                 - Disable loading spinner")
        print("  --json                       - Output response in JSON format")
        print("  --config PATH                - Specify config file path")
        print("\nCommands (in interactive mode or as query):")
        print("  help, ?                      - Show help")
        print("  clear                        - Clear conversation history")
        print("  c, conversation              - Show conversation history")
        print("  upload <file1> [file2] ...   - Upload files for analysis")
        print("    Options:")
        print("      --recursive, -r          - Include all files in directories")
        print("\nMultiline queries:")
        print("  - Use triple quotes (''' or \"\"\") to start a multiline query")
        print("  - Read from stdin: echo \"query\" | ask -")
        print("  - Pipe from file: cat query.txt | ask -")
        print("\nExamples:")
        print("  ask \"What is 2+2?\"")
        print("  ask --model claude-3-opus \"Explain quantum computing\"")
        print("  echo \"Analyze this text\" | ask -")
        print("  ask --no-spinner --json \"Return a JSON array of prime numbers under 10\"")
        return 0
    
    # Check for --version flag
    if "--version" in sys.argv or "-v" in sys.argv:
        print("Ask CLI - Command Line Interface for Claude AI")
        try:
            from .build_info import BUILD_DATE
            print(f"Built: {BUILD_DATE}")
        except ImportError:
            print("Version: Development")
        return 0
    
    # Check for --init-config flag
    if "--init-config" in sys.argv:
        from .utils.config_loader import ConfigLoader
        ConfigLoader.create_default_configs()
        print_success(f"Created default configuration files in {ConfigLoader.CONFIG_DIR}")
        print("\nConfiguration files created:")
        print(f"  - {ConfigLoader.CONFIG_DIR}/system          - Custom system prompt")
        print(f"  - {ConfigLoader.CONFIG_DIR}/aliases.json    - Command aliases")
        print(f"  - {ConfigLoader.CONFIG_DIR}/models.json     - Model preferences")
        print(f"  - {ConfigLoader.CONFIG_DIR}/templates.json  - Response templates")
        return 0
    
    # Check for --music-history flag
    if "--music-history" in sys.argv:
        from .utils.music import MusicPlayer
        history = MusicPlayer.get_history()
        if history:
            print("Music History (last 10 plays):")
            for entry in history[-10:]:
                print(f"  {entry['timestamp']}: {entry['progression']} ({entry.get('method', 'unknown')})")
        else:
            print("No music history found.")
        return 0
    
    # Check for --music flag to toggle music
    if "--music" in sys.argv:
        from .utils.config_loader import ConfigLoader
        from pathlib import Path
        models_file = Path.home() / ".config" / "claude" / "models.json"
        if models_file.exists():
            model_prefs = ConfigLoader.get_model_preferences()
            current_state = model_prefs.get('startup_music', True)
            model_prefs['startup_music'] = not current_state
            models_file.write_text(json.dumps(model_prefs, indent=2))
            state_text = "enabled" if model_prefs['startup_music'] else "disabled"
            print_success(f"Startup music {state_text}")
        else:
            print_error("Configuration file not found. Run with --init-config first.")
        return 0
    
    # Check for --volume flag
    if "--volume" in sys.argv:
        try:
            idx = sys.argv.index("--volume")
            if idx + 1 < len(sys.argv):
                volume = float(sys.argv[idx + 1])
                if 0.0 <= volume <= 1.0:
                    from .utils.config_loader import ConfigLoader
                    from pathlib import Path
                    models_file = Path.home() / ".config" / "claude" / "models.json"
                    if models_file.exists():
                        model_prefs = ConfigLoader.get_model_preferences()
                        model_prefs['music_volume'] = volume
                        models_file.write_text(json.dumps(model_prefs, indent=2))
                        print_success(f"Music volume set to {volume:.1f}")
                    else:
                        print_error("Configuration file not found. Run with --init-config first.")
                else:
                    print_error("Volume must be between 0.0 and 1.0")
            else:
                # Show current volume
                from .utils.music import MusicPlayer
                current_volume = MusicPlayer.get_volume()
                print(f"Current music volume: {current_volume:.1f}")
        except ValueError:
            print_error("Invalid volume value. Must be a number between 0.0 and 1.0")
        return 0
    
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
    
    # Parse command line arguments
    no_spinner = False
    json_output = False
    model = None
    config_path = None
    
    # Extract options from argv
    filtered_args = []
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--no-spinner":
            no_spinner = True
        elif arg == "--json":
            json_output = True
        elif arg == "--model" and i + 1 < len(sys.argv):
            model = sys.argv[i + 1]
            i += 1  # Skip the model value
        elif arg == "--config" and i + 1 < len(sys.argv):
            config_path = sys.argv[i + 1]
            i += 1  # Skip the config path
        elif arg == "--volume":
            # Skip --volume and its optional value (handled earlier)
            if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith('-'):
                i += 1  # Skip the volume value
        else:
            filtered_args.append(arg)
        i += 1
    
    # Set config path if specified
    if config_path:
        os.environ['ASK_CONFIG_PATH'] = config_path
    
    # Check for command line arguments
    if filtered_args:
        query = " ".join(filtered_args)
        
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
        
        return handle_command_line_query(query, no_spinner=no_spinner, json_output=json_output, model=model)
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
