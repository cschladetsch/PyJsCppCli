"""
Constants and configuration for Ask CLI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Where magic numbers become meaningful names,
and configuration dreams come true!
"""

import os

# File paths - Primary (new standard)
HISTORY_FILE = os.path.expanduser("~/.ask_history")
CONVERSATION_STATE_FILE = os.path.expanduser("~/.ask_conversation_state.json")
CONVERSATION_LOG_FILE = os.path.expanduser("~/.ask_conversation.md")
UPLOAD_CACHE_DIR = os.path.expanduser("~/.ask_uploads")
TOKEN_FILE = os.path.expanduser("~/.claude_token")

# File paths - Legacy (for backward compatibility)
LEGACY_HISTORY_FILE = os.path.expanduser("~/.claude_history")
LEGACY_CONVERSATION_STATE_FILE = os.path.expanduser("~/.claude_conversation_state.json")
LEGACY_TOKEN_FILE = os.path.expanduser("~/.ask_token")

# API configuration
DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_MAX_TOKENS = 1024
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."

# UI Configuration - The Spinner Symphony!
SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]  # Classic dots

# Alternative spinner collections for future fun!
FANCY_SPINNERS = {
    "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
    "bouncing": ["⠁", "⠂", "⠄", "⠂"],
    "growing": ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "▊", "▋", "▌", "▍", "▎"],
    "moon": ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"],
    "clock": ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚", "🕛"],
    "earth": ["🌍", "🌎", "🌏"],
    "hearts": ["💛", "💙", "💜", "💚", "❤️"],
    "weather": ["☀️", "🌤️", "⛅", "🌥️", "☁️", "🌧️", "⛈️", "🌧️", "🌥️", "⛅", "🌤️"],
}

# Spinner messages that make waiting fun!
SPINNER_MESSAGES = [
    "Thinking ",
    "Processing ",
    "Contemplating ",
    "Analyzing ",
    "Computing ",
    "Pondering ",
    "Consulting ",
    "Brewing ",
    "Synthesizing ",
    "Channeling ",
    "Quantum ",
    "Reading ",
    "Decoding ",
    "Assembling ",
    "Calibrating ",
]

# Fun response intros (currently unused, but ready for action!)
RESPONSE_INTROS = [
    "Ah, interesting question!",
    "Let me think about that...",
    "Great question!",
    "Here's what I found:",
    "After careful consideration:",
    "I've analyzed your request:",
]

# Terminal color sequences (for future enhancements)
RAINBOW_COLORS = [
    "\033[91m",  # Red
    "\033[93m",  # Yellow
    "\033[92m",  # Green
    "\033[96m",  # Cyan
    "\033[94m",  # Blue
    "\033[95m",  # Magenta
]
