"""
Interactive command mode for Claude CLI with improved text file handling
"""

import os
import sys
import random
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.history import FileHistory

from ..utils.colors import Colors
from ..utils.spinner import Spinner
from ..utils.output_formatter import (
    OutputFormatter, print_error, print_warning, 
    print_success, print_info, print_response
)
from ..utils.io import (
    load_conversation_state, 
    save_conversation_state, 
    prepare_files_for_upload, 
    resolve_file_paths,
    append_to_conversation_log
)
from ..constants import RESPONSE_INTROS
from ..api.client import ClaudeClient
from ..constants import HISTORY_FILE, DEFAULT_SYSTEM_PROMPT, UPLOAD_CACHE_DIR
from ..models import Interaction

def setup_key_bindings():
    """Set up vim-style key bindings"""
    from prompt_toolkit.key_binding.bindings.vi import load_vi_bindings
    kb = KeyBindings()
    kb.add_binding('escape', 'i')(load_vi_bindings())
    return kb

def get_prompt_message():
    """Return simple prompt"""
    return ANSI(OutputFormatter.format_prompt('> '))

class InteractiveMode:
    """Interactive command mode for Claude AI"""
    
    def __init__(self):
        self.system_prompt = DEFAULT_SYSTEM_PROMPT
        self.client = ClaudeClient()
        self.interactions = load_conversation_state()
        self.session = PromptSession(
            history=FileHistory(HISTORY_FILE),
            key_bindings=setup_key_bindings(),
            editing_mode=EditingMode.VI,
            message=get_prompt_message
        )
        # Ensure upload cache dir exists
        os.makedirs(UPLOAD_CACHE_DIR, exist_ok=True)

    def show_history(self, n=None):
        """Display command history, optionally limited to last n entries"""
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = [line.strip() for line in f if line.strip()]
                if n is not None:
                    history = history[-n:]
                for i, cmd in enumerate(history, 1):
                    print(f"{i}. {cmd}")
        except FileNotFoundError:
            print("No history found.")

    def show_conversation(self, n=None):
        """Display conversation history, optionally limited to last n exchanges"""
        if not self.interactions:
            print("No conversation history found.")
            return
            
        interactions_to_show = self.interactions
        if n is not None:
            interactions_to_show = self.interactions[-n:]
            
        for i, interaction in enumerate(interactions_to_show, 1):
            user_short = interaction.query[:50] + "..." if len(interaction.query) > 50 else interaction.query
            print(f"{i}. User: {user_short}")
            assistant_short = interaction.response[:50] + "..." if len(interaction.response) > 50 else interaction.response
            print(f"   Claude: {assistant_short}")
            print()

    def clear_conversation(self):
        """Clear the conversation history"""
        self.interactions = []
        save_conversation_state(self.interactions)
        print("Conversation history cleared.")

    def handle_upload_command(self, args):
        """Process the upload command with arguments"""
        if not args:
            print_error("No files specified. Usage: upload <file1> [file2] ...")
            return True
            
        # Parse flags
        recursive = "--recursive" in args or "-r" in args
        if recursive:
            args = [arg for arg in args if arg not in ["--recursive", "-r"]]
        
        # Resolve all file paths
        file_paths = resolve_file_paths(args, allow_directories=recursive)
        
        if not file_paths:
            print(f"{Colors.RED}No files found matching the provided patterns.{Colors.RESET}")
            return True
        
        # Prepare files for upload
        print(f"{Colors.BLUE}Processing {len(file_paths)} files for upload...{Colors.RESET}")
        uploaded_files, text_files_content = prepare_files_for_upload(file_paths)
        
        # Display summary
        image_files_count = len(uploaded_files)
        if image_files_count > 0:
            total_size = sum(f["size"] for f in uploaded_files)
            print(f"{Colors.GREEN}Ready to send {image_files_count} image files ({total_size/1024:.1f} KB):{Colors.RESET}")
            for i, f in enumerate(uploaded_files, 1):
                print(f"  {i}. {f['file_name']} ({f['size']/1024:.1f} KB, {f['mime_type']})")
        
        has_text_content = bool(text_files_content.strip())
        if has_text_content:
            print_info("Text files will be included in your message.")
        
        if not image_files_count and not has_text_content:
            print_error("No supported files found to upload.")
            return True
        
        # Prompt for a message to send with the files
        print(f"\n{Colors.CYAN}Enter a message to send with these files (or press Enter to just upload):{Colors.RESET}")
        message = input("> ")
        
        # Generate response with the uploaded files
        spinner = Spinner()
        spinner.start()
        response, self.interactions = self.client.generate_response(
            message, 
            self.system_prompt,
            self.interactions,
            uploaded_files,
            text_files_content
        )
        spinner.stop()
        intro = random.choice(RESPONSE_INTROS)
        print_response(intro, response)
        save_conversation_state(self.interactions)
        # Log the latest interaction to markdown file
        if self.interactions:
            append_to_conversation_log(self.interactions[-1])
        return True

    def process_input(self, user_prompt):
        """Process user input and execute appropriate action"""
        if user_prompt.lower() in ["exit", "quit"]:
            save_conversation_state(self.interactions)
            return False
        elif user_prompt.lower() == "h":
            self.show_history()
            return True
        elif user_prompt.lower().startswith("h "):
            try:
                n = int(user_prompt.split()[1])
                self.show_history(n)
            except (IndexError, ValueError):
                print("Usage: h <number> - shows last N entries from history")
            return True
        elif user_prompt.lower() == "c":
            self.show_conversation()
            return True
        elif user_prompt.lower().startswith("c "):
            try:
                n = int(user_prompt.split()[1])
                self.show_conversation(n)
            except (IndexError, ValueError):
                print("Usage: c <number> - shows last N conversation exchanges")
            return True
        elif user_prompt.lower() == "clear":
            self.clear_conversation()
            return True
        elif user_prompt.lower().startswith("upload "):
            args = user_prompt.split()[1:]
            return self.handle_upload_command(args)
        elif user_prompt.lower() in ["help", "?"]:
            print("Available commands:")
            print("  help, ? - Show this help")
            print("  h      - Show full command history")
            print("  h N    - Show last N command history entries")
            print("  c      - Show full conversation history")
            print("  c N    - Show last N conversation exchanges")
            print("  clear  - Clear conversation history")
            print("  upload <file1> [file2] ... - Upload files to AI")
            print("    Options:")
            print("      --recursive, -r - Include all files in directories")
            print("  exit   - Exit the program")
            return True
        else:
            spinner = Spinner()
            spinner.start()
            response, self.interactions = self.client.generate_response(
                user_prompt, 
                self.system_prompt,
                self.interactions
            )
            spinner.stop()
            intro = random.choice(RESPONSE_INTROS)
            print_response(intro, response)
            save_conversation_state(self.interactions)
            # Log the latest interaction to markdown file
            if self.interactions:
                append_to_conversation_log(self.interactions[-1])
            return True

    def run(self):
        """Run the interactive mode main loop"""
        try:
            from ..build_info import BUILD_TIME
            header_text = f"Claude: Built {BUILD_TIME}"
        except ImportError:
            header_text = "Claude"
        print(OutputFormatter.format_header(header_text, level=1))
        #print(f"Type {Colors.CYAN}help{Colors.RESET} to see available commands")
        
        while True:
            try:
                user_input = self.session.prompt()
                if not self.process_input(user_input):
                    break
            except (KeyboardInterrupt, EOFError):
                save_conversation_state(self.interactions)
                print("\nExiting...")
                break
