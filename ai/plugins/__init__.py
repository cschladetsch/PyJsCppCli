"""
Plugin system for Ask CLI

This module provides a plugin architecture that allows extending
the CLI with custom functionality through a well-defined interface.
"""

from .base import BasePlugin, PluginError
from .decorators import command_plugin, plugin_hook
from .plugin_manager import Plugin, PluginManager

__all__ = [
    "PluginManager",
    "Plugin",
    "BasePlugin",
    "PluginError",
    "plugin_hook",
    "command_plugin",
]
