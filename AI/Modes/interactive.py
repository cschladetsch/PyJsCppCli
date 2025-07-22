"""
Interactive command mode for Claude CLI with improved text file handling
"""

import os
import random

from prompt_toolkit import PromptSession
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings

from ..api.client import ClaudeClient
from ..constants import (
    DEFAULT_SYSTEM_PROMPT,
    HISTORY_FILE,
    RESPONSE_INTROS,
    UPLOAD_CACHE_DIR,
)
from ..utils.colors import Colors
from ..utils.config_loader import ConfigLoader
from ..utils.io import (
    append_to_conversation_log,
    load_conversation_state_with_timeout,
    prepare_files_for_upload,
    resolve_file_paths,
    save_conversation_state,
)
from ..utils.output_formatter import (
    print_error,
    print_info,
    print_response,
)
from ..utils.spinner import Spinner
from ..utils.theme_config import theme_config
from ..utils.variables import process_input as process_variables


def setup_key_bindings():
    """Set up vim-style key bindings"""
    from prompt_toolkit.key_binding.bindings.vi import load_vi_bindings

    kb = KeyBindings()
    kb.add_binding("escape", "i")(load_vi_bindings())
    return kb


def get_prompt_message():
    """Return simple prompt"""
    return ANSI(f"{Colors.MAGENTA}λ {Colors.RESET}")


class InteractiveMode:
    """Interactive command mode for Claude AI"""

    def __init__(self):
        # Load custom system prompt or use default
        custom_prompt = ConfigLoader.get_system_prompt()
        self.system_prompt = custom_prompt if custom_prompt else DEFAULT_SYSTEM_PROMPT
        self.client = ClaudeClient()

        # Load conversation history with timeout from config
        model_prefs = ConfigLoader.get_model_preferences()
        load_timeout = model_prefs.get("conversation_load_timeout", 3.0)
        self.interactions = load_conversation_state_with_timeout(timeout=load_timeout)
        self.session = PromptSession(
            history=FileHistory(HISTORY_FILE),
            key_bindings=setup_key_bindings(),
            editing_mode=EditingMode.VI,
            message=get_prompt_message,
        )
        # Ensure upload cache dir exists
        os.makedirs(UPLOAD_CACHE_DIR, exist_ok=True)

    def show_history(self, n=None):
        """Display command history, optionally limited to last n entries"""
        try:
            with open(HISTORY_FILE) as f:
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
            user_short = (
                interaction.query[:50] + "..."
                if len(interaction.query) > 50
                else interaction.query
            )
            user_color = theme_config.get_color("user")
            assistant_color = theme_config.get_color("assistant")
            index_color = theme_config.get_color("index")
            print(
                f"{index_color}{i}.{Colors.RESET} {user_color}User:{Colors.RESET} {user_short}"
            )
            assistant_short = (
                interaction.response[:50] + "..."
                if len(interaction.response) > 50
                else interaction.response
            )
            print(f"   {assistant_color}Claude:{Colors.RESET} {assistant_short}")
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
            print(
                f"{Colors.RED}No files found matching the provided patterns.{Colors.RESET}"
            )
            return True

        # Prepare files for upload
        print(
            f"{Colors.BLUE}Processing {len(file_paths)} files for upload...{Colors.RESET}"
        )
        uploaded_files, text_files_content = prepare_files_for_upload(file_paths)

        # Display summary
        image_files_count = len(uploaded_files)
        if image_files_count > 0:
            total_size = sum(f["size"] for f in uploaded_files)
            print(
                f"{Colors.GREEN}Ready to send {image_files_count} image files ({total_size/1024:.1f} KB):{Colors.RESET}"
            )
            for i, f in enumerate(uploaded_files, 1):
                print(
                    f"  {i}. {f['file_name']} ({f['size']/1024:.1f} KB, {f['mime_type']})"
                )

        has_text_content = bool(text_files_content.strip())
        if has_text_content:
            print_info("Text files will be included in your message.")

        if not image_files_count and not has_text_content:
            print_error("No supported files found to upload.")
            return True

        # Prompt for a message to send with the files
        print(
            f"\n{Colors.CYAN}Enter a message to send with these files (or press Enter to just upload):{Colors.RESET}"
        )
        message = input("> ")

        # Generate response with the uploaded files
        spinner = Spinner()
        spinner.start()
        response, self.interactions = self.client.generate_response(
            message,
            self.system_prompt,
            self.interactions,
            uploaded_files,
            text_files_content,
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
        # Check for special commands first (before variable processing)
        if user_prompt.lower() in ["exit", "quit"]:
            save_conversation_state(self.interactions)
            return False
        if user_prompt.lower() == "h":
            self.show_history()
            return True
        if user_prompt.lower().startswith("h "):
            try:
                n = int(user_prompt.split()[1])
                self.show_history(n)
            except (IndexError, ValueError):
                print("Usage: h <number> - shows last N entries from history")
            return True
        if user_prompt.lower() == "c":
            self.show_conversation()
            return True
        if user_prompt.lower().startswith("c "):
            try:
                n = int(user_prompt.split()[1])
                self.show_conversation(n)
            except (IndexError, ValueError):
                print("Usage: c <number> - shows last N conversation exchanges")
            return True
        if user_prompt.lower() == "clear":
            self.clear_conversation()
            return True
        if user_prompt.lower().startswith("upload "):
            args = user_prompt.split()[1:]
            return self.handle_upload_command(args)
        if user_prompt.lower() in ["help", "?"]:
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
            print("  vars   - Show all stored variables")
            print("  var=value - Set a variable (e.g., name=John)")
            print("  exit   - Exit the program")
            return True
        if user_prompt.lower() == "vars":
            from ..utils.variables import get_variable_manager

            variables = get_variable_manager().list_variables()
            if variables:
                print("Stored variables:")
                for name, value in variables.items():
                    print(f"  {name} = {value}")
            else:
                print("No variables stored")
            return True
        # Now handle variable assignments and interpolation
        processed_prompt, was_assignment = process_variables(user_prompt)

        # If it was a variable assignment, show the result and return
        if was_assignment:
            print(processed_prompt)
            return True

        # Use the processed prompt for further command processing
        user_prompt = processed_prompt

        spinner = Spinner()
        spinner.start()
        response, self.interactions = self.client.generate_response(
            user_prompt, self.system_prompt, self.interactions
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

        while True:
            try:
                user_input = self.session.prompt()
                if not self.process_input(user_input):
                    break
            except (KeyboardInterrupt, EOFError):
                save_conversation_state(self.interactions)
                break
