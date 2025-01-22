import sys
import os
import json
from datetime import datetime
from anthropic import Anthropic
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.history import FileHistory
from prompt_toolkit.filters import vi_mode
from prompt_toolkit.shortcuts import prompt
import threading
import time

# File paths
HISTORY_FILE = os.path.expanduser("~/.claude_history")

# ANSI color codes
class Colors:
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    CYAN = '\033[36m'
    RED = '\033[31m'
    ORANGE = '\033[38;5;208m'  # Bright orange color
    RESET = '\033[0m'

class Spinner:
    """An enhanced spinner class with a smooth animation"""
    def __init__(self):
        self.spinning = False
        self.frames = [
            "?", "?", "?", "?", "?", "?", "?", "?", "?", "?"
        ]
        self.loading_messages = [
            "Thinking", "Processing", "Contemplating", 
            "Analyzing", "Computing", "Pondering"
        ]
        self.spinner_idx = 0
        self.message_idx = 0
        self.dots = 0
        self.message_update_counter = 0

    def spin(self):
        while self.spinning:
            if self.message_update_counter % 20 == 0:
                self.message_idx = (self.message_idx + 1) % len(self.loading_messages)
                self.dots = 0
            
            if self.message_update_counter % 5 == 0:
                self.dots = (self.dots + 1) % 4
            
            message = self.loading_messages[self.message_idx]
            dots = "." * self.dots
            spaces = " " * (3 - self.dots)
            
            spinner = self.frames[self.spinner_idx]
            line = f"\r{Colors.ORANGE}{spinner} {message}{dots}{spaces}{Colors.RESET}"
            
            sys.stdout.write(line)
            sys.stdout.flush()
            
            self.spinner_idx = (self.spinner_idx + 1) % len(self.frames)
            self.message_update_counter += 1
            time.sleep(0.1)
        
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()

    def start(self):
        self.spinning = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()

    def stop(self):
        self.spinning = False
        if hasattr(self, 'thread'):
            self.thread.join()

def read_token(file_path="~/.claude_token"):
    """Reads the API key from a file or environment variable."""
    file_path = os.path.expanduser(file_path)
    if "CLAUDE_API_KEY" in os.environ:
        return os.environ["CLAUDE_API_KEY"]
    elif os.path.exists(file_path):
        with open(file_path, "r") as file:
            return file.read().strip()
    else:
        raise FileNotFoundError("Token file not found and 'CLAUDE_API_KEY' environment variable is not set.")

def setup_key_bindings():
    """Set up vim-style key bindings"""
    from prompt_toolkit.key_binding.bindings.vi import load_vi_bindings
    kb = KeyBindings()
    kb.add_binding('escape', 'i')(load_vi_bindings())
    return kb

def get_prompt_message():
    """Return simple prompt"""
    return ANSI(f'{Colors.GREEN}>{Colors.RESET} ')

def generate_response(client, prompt, system_prompt="You are a helpful assistant."):
    """Generates a response using Claude."""
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024
        )
        return response.content[0].text if response.content else "No response generated."
    except Exception as e:
        return f"Error while generating response: {e}"

class InteractiveMode:
    def __init__(self):
        self.system_prompt = "You are a helpful assistant."
        self.client = Anthropic(api_key=read_token())
        self.session = PromptSession(
            history=FileHistory(HISTORY_FILE),
            key_bindings=setup_key_bindings(),
            editing_mode=EditingMode.VI,
            message=get_prompt_message
        )

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

    def process_input(self, user_prompt):
        if user_prompt.lower() in ["exit", "quit"]:
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
        elif user_prompt.lower() in ["help", "?"]:
            print("Available commands:")
            print("  help, ? - Show this help")
            print("  h      - Show full history")
            print("  h N    - Show last N history entries")
            print("  exit   - Exit the program")
            return True
        else:
            spinner = Spinner()
            spinner.start()
            response = generate_response(self.client, user_prompt, self.system_prompt)
            spinner.stop()
            print(f"{Colors.BLUE}<{Colors.RESET} {Colors.CYAN}{response}{Colors.RESET}")
            return True

    def run(self):
        while True:
            try:
                user_input = self.session.prompt()
                if not self.process_input(user_input):
                    break
            except (KeyboardInterrupt, EOFError):
                break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        client = Anthropic(api_key=read_token())
        query = " ".join(sys.argv[1:])
        spinner = Spinner()
        try:
            spinner.start()
            reply = generate_response(client, query)
            spinner.stop()
            print(f"{Colors.BLUE}<{Colors.RESET} {Colors.CYAN}{reply}{Colors.RESET}")
        except (KeyboardInterrupt, EOFError):
            spinner.stop()
            sys.exit(1)
        except Exception:
            spinner.stop()
            print(f"{Colors.RED}An error occurred while processing your request. Please try again.{Colors.RESET}")
    else:
        interactive = InteractiveMode()
        interactive.run()
