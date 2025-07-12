"""
Output formatting utilities with semantic color schemes
"""

from .colors import Colors
from .markdown_renderer import render_markdown
from .theme_config import theme_config
from typing import Optional

class OutputFormatter:
    """Formats different types of output with appropriate colors and styles"""
    
    @staticmethod
    def format_prompt(text: str) -> str:
        """Format user prompt/input indicator"""
        color = theme_config.get_color("prompt")
        return f"{color}{text}{Colors.RESET}"
    
    @staticmethod
    def format_response_intro(intro: str) -> str:
        """Format the response introduction"""
        response_color = theme_config.get_color("response")
        info_color = theme_config.get_color("info")
        return f"{response_color}<{Colors.RESET} {info_color}{intro}{Colors.RESET}"
    
    @staticmethod
    def format_response(content: str, use_markdown: bool = True) -> str:
        """
        Format AI response content with optional markdown rendering.
        
        Args:
            content: The response content
            use_markdown: Whether to render markdown with glow
            
        Returns:
            Formatted response
        """
        if use_markdown:
            markdown_config = theme_config.get_markdown_config()
            return render_markdown(content, 
                                 style=markdown_config["style"], 
                                 width=markdown_config["width"])
        else:
            response_color = theme_config.get_color("response")
            return f"{response_color}{content}{Colors.RESET}"
    
    @staticmethod
    def format_error(message: str) -> str:
        """Format error messages"""
        error_color = theme_config.get_color("error")
        return f"{error_color}Error: {message}{Colors.RESET}"
    
    @staticmethod
    def format_warning(message: str) -> str:
        """Format warning messages"""
        warning_color = theme_config.get_color("warning")
        return f"{warning_color}Warning: {message}{Colors.RESET}"
    
    @staticmethod
    def format_success(message: str) -> str:
        """Format success messages"""
        success_color = theme_config.get_color("success")
        return f"{success_color}✓ {message}{Colors.RESET}"
    
    @staticmethod
    def format_info(message: str) -> str:
        """Format informational messages"""
        info_color = theme_config.get_color("info")
        return f"{info_color}{message}{Colors.RESET}"
    
    @staticmethod
    def format_header(text: str, level: int = 1) -> str:
        """Format header text"""
        if level == 1:
            header_color = theme_config.get_color("header")
            return f"{header_color}{text}{Colors.RESET}"
        elif level == 2:
            return f"{Colors.BRIGHT_BLUE}{text}{Colors.RESET}"
        else:
            return f"{Colors.BLUE}{text}{Colors.RESET}"
    
    @staticmethod
    def format_code(code: str, language: Optional[str] = None) -> str:
        """Format code snippets"""
        if language:
            header = f"{Colors.MUTED}```{language}{Colors.RESET}\n"
            footer = f"\n{Colors.MUTED}```{Colors.RESET}"
            return f"{header}{Colors.CODE}{code}{Colors.RESET}{footer}"
        else:
            return f"{Colors.CODE}{code}{Colors.RESET}"
    
    @staticmethod
    def format_list_item(item: str, number: Optional[int] = None) -> str:
        """Format list items"""
        if number is not None:
            prefix = f"{Colors.BRIGHT_CYAN}{number}.{Colors.RESET}"
        else:
            prefix = f"{Colors.BRIGHT_CYAN}•{Colors.RESET}"
        return f"{prefix} {item}"
    
    @staticmethod
    def format_file_path(path: str) -> str:
        """Format file paths"""
        return f"{Colors.UNDERLINE}{Colors.BRIGHT_MAGENTA}{path}{Colors.RESET}"
    
    @staticmethod
    def format_command(command: str) -> str:
        """Format shell commands"""
        return f"{Colors.BOLD}{Colors.LIME}$ {command}{Colors.RESET}"
    
    @staticmethod
    def format_muted(text: str) -> str:
        """Format muted/secondary text"""
        return f"{Colors.MUTED}{text}{Colors.RESET}"
    
    @staticmethod
    def format_highlight(text: str, color: str = "YELLOW") -> str:
        """Highlight text with specified color"""
        color_attr = getattr(Colors, color.upper(), Colors.YELLOW)
        return f"{color_attr}{text}{Colors.RESET}"


# Convenience functions for common formatting needs
def print_error(message: str):
    """Print an error message with formatting"""
    print(OutputFormatter.format_error(message))

def print_warning(message: str):
    """Print a warning message with formatting"""
    print(OutputFormatter.format_warning(message))

def print_success(message: str):
    """Print a success message with formatting"""
    print(OutputFormatter.format_success(message))

def print_info(message: str):
    """Print an info message with formatting"""
    print(OutputFormatter.format_info(message))

def print_response(intro: str, content: str, use_markdown: bool = True):
    """Print a formatted AI response"""
    print(OutputFormatter.format_response_intro(intro))
    print(OutputFormatter.format_response(content, use_markdown))

def print_header(text: str, level: int = 1):
    """Print a formatted header"""
    print(OutputFormatter.format_header(text, level))

def print_code(code: str, language: Optional[str] = None):
    """Print formatted code"""
    print(OutputFormatter.format_code(code, language))