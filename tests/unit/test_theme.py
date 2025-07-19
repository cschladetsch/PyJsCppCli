"""Unit tests for theme configuration functionality"""

import pytest
from unittest.mock import patch, mock_open
import json
from ai.utils.theme_config import THEMES, get_theme, apply_theme


class TestThemeConfig:
    """Test cases for theme configuration"""
    
    def test_themes_available(self):
        """Test that themes are defined"""
        assert len(THEMES) > 0
        assert "default" in THEMES
        assert isinstance(THEMES, dict)
    
    def test_theme_structure(self):
        """Test that themes have correct structure"""
        assert all(isinstance(name, str) for name in THEMES.keys())
        
        # Check each theme has required keys
        required_keys = ["name", "description", "colors"]
        for theme_name, theme in THEMES.items():
            for key in required_keys:
                assert key in theme, f"Theme '{theme_name}' missing key '{key}'"
            
            # Check colors structure
            assert isinstance(theme["colors"], dict)
            color_keys = ["prompt", "response", "error", "warning", "success"]
            for color_key in color_keys:
                assert color_key in theme["colors"], f"Theme '{theme_name}' missing color '{color_key}'"
    
    def test_get_theme(self):
        """Test getting a theme"""
        theme = get_theme("default")
        assert theme is not None
        assert "name" in theme
        assert theme["name"] == "Default"
        
        # Test getting non-existent theme returns default
        theme = get_theme("nonexistent")
        assert theme == THEMES["default"]
    
    def test_apply_theme(self):
        """Test applying a theme"""
        # Test that apply_theme doesn't raise exceptions
        apply_theme("default")
        apply_theme("minimal")
        
        # Test applying non-existent theme uses default
        apply_theme("nonexistent")
    
    def test_theme_colors(self):
        """Test that theme colors are valid"""
        for theme_name, theme in THEMES.items():
            colors = theme["colors"]
            
            # Check that all color values are strings
            for color_name, color_value in colors.items():
                assert isinstance(color_value, str), f"Color '{color_name}' in theme '{theme_name}' is not a string"
                
                # Basic check that it looks like a color code or is empty
                if color_value:
                    assert "\033[" in color_value or color_value.startswith("\x1b["), \
                        f"Color '{color_name}' in theme '{theme_name}' doesn't look like ANSI color code"
    
    def test_theme_markdown_config(self):
        """Test that themes have markdown configuration"""
        for theme_name, theme in THEMES.items():
            if "markdown" in theme:
                markdown_config = theme["markdown"]
                assert isinstance(markdown_config, dict)
                
                if "style" in markdown_config:
                    assert isinstance(markdown_config["style"], str)
                if "width" in markdown_config:
                    assert isinstance(markdown_config["width"], int)
                    assert markdown_config["width"] > 0