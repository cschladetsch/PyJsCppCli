"""
Theme configuration for customizable color schemes
"""

import os
import json
from typing import Dict, Optional
from .colors import Colors

# Default theme configurations
THEMES = {
    "default": {
        "name": "Default",
        "description": "Standard colorful theme",
        "colors": {
            "prompt": Colors.PROMPT,
            "response": Colors.RESPONSE,
            "error": Colors.ERROR,
            "warning": Colors.WARNING,
            "success": Colors.SUCCESS,
            "info": Colors.INFO,
            "header": Colors.HEADER,
            "code": Colors.CODE,
            "muted": Colors.MUTED
        },
        "markdown": {
            "style": "dark",
            "width": 100
        }
    },
    "minimal": {
        "name": "Minimal",
        "description": "Subdued colors for minimal distraction",
        "colors": {
            "prompt": Colors.WHITE,
            "response": Colors.WHITE,
            "error": Colors.RED,
            "warning": Colors.YELLOW,
            "success": Colors.GREEN,
            "info": Colors.CYAN,
            "header": Colors.BOLD + Colors.WHITE,
            "code": Colors.BRIGHT_BLACK,
            "muted": Colors.BRIGHT_BLACK
        },
        "markdown": {
            "style": "notty",
            "width": 80
        }
    },
    "vibrant": {
        "name": "Vibrant",
        "description": "Bright and colorful theme",
        "colors": {
            "prompt": Colors.BRIGHT_GREEN,
            "response": Colors.BRIGHT_CYAN,
            "error": Colors.BRIGHT_RED,
            "warning": Colors.BRIGHT_YELLOW,
            "success": Colors.LIME,
            "info": Colors.BRIGHT_BLUE,
            "header": Colors.BOLD + Colors.BRIGHT_MAGENTA,
            "code": Colors.PURPLE,
            "muted": Colors.DIM + Colors.WHITE
        },
        "markdown": {
            "style": "pink",
            "width": 120
        }
    },
    "terminal": {
        "name": "Terminal",
        "description": "Classic terminal colors",
        "colors": {
            "prompt": Colors.GREEN,
            "response": Colors.WHITE,
            "error": Colors.RED,
            "warning": Colors.YELLOW,
            "success": Colors.GREEN,
            "info": Colors.BLUE,
            "header": Colors.BOLD + Colors.WHITE,
            "code": Colors.CYAN,
            "muted": Colors.BRIGHT_BLACK
        },
        "markdown": {
            "style": "dark",
            "width": 100
        }
    }
}

class ThemeConfig:
    """Manages theme configuration and customization"""
    
    def __init__(self, config_dir: str = None):
        """
        Initialize theme configuration.
        
        Args:
            config_dir: Directory to store theme config (defaults to ~/.ai)
        """
        self.config_dir = config_dir or os.path.expanduser("~/.ai")
        self.config_path = os.path.join(self.config_dir, "theme.json")
        self.current_theme = "default"
        self.custom_themes = {}
        self._load_config()
    
    def _load_config(self):
        """Load theme configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.current_theme = config.get("current_theme", "default")
                    self.custom_themes = config.get("custom_themes", {})
        except (json.JSONDecodeError, IOError):
            # If config is corrupted or unreadable, use defaults
            pass
    
    def _save_config(self):
        """Save theme configuration to file"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            config = {
                "current_theme": self.current_theme,
                "custom_themes": self.custom_themes
            }
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError:
            # Silently fail if we can't write config
            pass
    
    def get_available_themes(self) -> Dict[str, dict]:
        """Get all available themes (built-in and custom)"""
        all_themes = THEMES.copy()
        all_themes.update(self.custom_themes)
        return all_themes
    
    def get_current_theme(self) -> dict:
        """Get the current active theme configuration"""
        all_themes = self.get_available_themes()
        return all_themes.get(self.current_theme, THEMES["default"])
    
    def set_theme(self, theme_name: str) -> bool:
        """
        Set the active theme.
        
        Args:
            theme_name: Name of the theme to activate
            
        Returns:
            True if theme was set successfully, False otherwise
        """
        all_themes = self.get_available_themes()
        if theme_name in all_themes:
            self.current_theme = theme_name
            self._save_config()
            return True
        return False
    
    def add_custom_theme(self, name: str, theme_config: dict) -> bool:
        """
        Add a custom theme.
        
        Args:
            name: Name for the custom theme
            theme_config: Theme configuration dictionary
            
        Returns:
            True if theme was added successfully
        """
        try:
            # Validate theme config has required structure
            required_keys = ["name", "description", "colors", "markdown"]
            if not all(key in theme_config for key in required_keys):
                return False
            
            self.custom_themes[name] = theme_config
            self._save_config()
            return True
        except:
            return False
    
    def remove_custom_theme(self, name: str) -> bool:
        """
        Remove a custom theme.
        
        Args:
            name: Name of the custom theme to remove
            
        Returns:
            True if theme was removed successfully
        """
        if name in self.custom_themes:
            del self.custom_themes[name]
            if self.current_theme == name:
                self.current_theme = "default"
            self._save_config()
            return True
        return False
    
    def get_color(self, color_type: str) -> str:
        """
        Get a color code for the specified type from current theme.
        
        Args:
            color_type: Type of color (prompt, response, error, etc.)
            
        Returns:
            ANSI color code
        """
        theme = self.get_current_theme()
        return theme["colors"].get(color_type, Colors.RESET)
    
    def get_markdown_config(self) -> dict:
        """Get markdown rendering configuration for current theme"""
        theme = self.get_current_theme()
        return theme.get("markdown", {"style": "dark", "width": 100})


# Global theme configuration instance
theme_config = ThemeConfig()