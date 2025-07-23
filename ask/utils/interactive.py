"""
Interactive command mode for AI CLI
"""

import os

from prompt_toolkit import PromptSession
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings

from ..api.client import ClaudeClient
from ..constants import DEFAULT_SYSTEM_PROMPT, HISTORY_FILE, UPLOAD_CACHE_DIR
from .colors import Colors
from .io import (
    load_conversation_state,
    prepare_files_for_upload,
    resolve_file_paths,
    save_conversation_state,
)
from .spinner import Spinner


def setup_key_bindings():
    """Set up vim-style key bindings"""
    from prompt_toolkit.key_binding.bindings.vi import load_vi_bindings

    kb = KeyBindings()
    kb.add_binding("escape", "i")(load_vi_bindings())
    return kb


def get_prompt_message():
    """Return simple prompt"""
    return ANSI(f"{Colors.BLUE}λ{Colors.RESET} ")


class InteractiveMode:
    """Interactive command mode for the AI CLI"""

    def __init__(self):
        self.system_prompt = DEFAULT_SYSTEM_PROMPT
        self.client = ClaudeClient()
        self.message_history = load_conversation_state()
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
        if not self.message_history:
            print("No conversation history found.")
            return

        exchanges = []
        for i in range(0, len(self.message_history), 2):
            if i + 1 < len(self.message_history):
                exchanges.append(
                    (
                        self.message_history[i]["content"],
                        self.message_history[i + 1]["content"],
                    )
                )

        if n is not None:
            exchanges = exchanges[-n:]

        for i, (user, assistant) in enumerate(exchanges, 1):
            user_short = user[:50] + "..." if len(user) > 50 else user
            print(f"{i}. User: {user_short}")
            assistant_short = (
                assistant[:50] + "..." if len(assistant) > 50 else assistant
            )
            print(f"   Claude: {assistant_short}")
            print()

    def clear_conversation(self):
        """Clear the conversation history"""
        self.message_history = []
        save_conversation_state(self.message_history)
        print("Conversation history cleared.")

    def handle_upload_command(self, args):
        """Process the upload command with arguments"""
        if not args:
            print(
                f"{Colors.RED}Error: No files specified. Usage: upload <file1> [file2] ...{Colors.RESET}"
            )
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
        uploaded_files = prepare_files_for_upload(file_paths)

        # Display summary
        total_size = sum(f["size"] for f in uploaded_files)
        print(
            f"{Colors.GREEN}Ready to send {len(uploaded_files)} files ({total_size/1024:.1f} KB):{Colors.RESET}"
        )
        for i, f in enumerate(uploaded_files, 1):
            print(
                f"  {i}. {f['file_name']} ({f['size']/1024:.1f} KB, {f['mime_type']})"
            )

        # Prompt for a message to send with the files
        print(
            f"\n{Colors.CYAN}Enter a message to send with these files (or press Enter to just upload):{Colors.RESET}"
        )
        message = input("> ")

        # Generate response with the uploaded files
        spinner = Spinner()
        spinner.start()
        response, self.message_history = self.client.generate_response(
            message, self.system_prompt, self.message_history, uploaded_files
        )
        spinner.stop()
        print(f"{Colors.BLUE}<{Colors.RESET} {Colors.CYAN}{response}{Colors.RESET}")
        save_conversation_state(self.message_history)
        return True

    def process_input(self, user_prompt):
        """Process user input and execute appropriate action"""
        if user_prompt.lower() in ["exit", "quit"]:
            save_conversation_state(self.message_history)
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
            print("  exit   - Exit the program")
            return True
        spinner = Spinner()
        spinner.start()
        response, self.message_history = self.client.generate_response(
            user_prompt, self.system_prompt, self.message_history
        )
        spinner.stop()
        print(f"{Colors.BLUE}<{Colors.RESET} {Colors.CYAN}{response}{Colors.RESET}")
        save_conversation_state(self.message_history)
        return True

    def run(self):
        """Run the interactive mode main loop"""
        print(f"{Colors.GREEN}Claude{Colors.RESET}")
        # print(f"Type {Colors.CYAN}help{Colors.RESET} to see available commands")

        while True:
            try:
                user_input = self.session.prompt()
                if not self.process_input(user_input):
                    break
            except (KeyboardInterrupt, EOFError):
                save_conversation_state(self.message_history)
                break
