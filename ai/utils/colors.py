"""
ANSI color utilities for terminal output with enhanced styling options
"""

class Colors:
    """ANSI color codes for terminal output"""
    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Extended colors
    ORANGE = '\033[38;5;208m'
    PURPLE = '\033[38;5;141m'
    PINK = '\033[38;5;205m'
    LIME = '\033[38;5;154m'
    TEAL = '\033[38;5;51m'
    LAVENDER = '\033[38;5;183m'
    
    # Text styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    STRIKETHROUGH = '\033[9m'
    
    # Reset
    RESET = '\033[0m'
    
    # Semantic color aliases for different output types
    ERROR = BRIGHT_RED
    WARNING = BRIGHT_YELLOW
    SUCCESS = BRIGHT_GREEN
    INFO = BRIGHT_CYAN
    PROMPT = GREEN
    RESPONSE = CYAN
    CODE = BRIGHT_MAGENTA
    HEADER = BOLD + BRIGHT_BLUE
    MUTED = BRIGHT_BLACK
