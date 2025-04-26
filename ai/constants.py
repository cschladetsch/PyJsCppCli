"""
Constants and configuration for AI CLI
"""

import os

# File paths - Primary (new standard)
HISTORY_FILE = os.path.expanduser("~/.ai_history")
CONVERSATION_STATE_FILE = os.path.expanduser("~/.ai_conversation_state.json")
UPLOAD_CACHE_DIR = os.path.expanduser("~/.ai_uploads")
TOKEN_FILE = os.path.expanduser("~/.ai_token")

# File paths - Legacy (for backward compatibility)
LEGACY_HISTORY_FILE = os.path.expanduser("~/.claude_history")
LEGACY_CONVERSATION_STATE_FILE = os.path.expanduser("~/.claude_conversation_state.json")
LEGACY_TOKEN_FILE = os.path.expanduser("~/.claude_token")

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
