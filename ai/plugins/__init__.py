"""
Plugin system for Ask CLI

This module provides a plugin architecture that allows extending
the CLI with custom functionality through a well-defined interface.
"""

from .plugin_manager import PluginManager, Plugin
from .decorators import plugin_hook, command_plugin
from .base import BasePlugin, PluginError

__all__ = [
    'PluginManager',
    'Plugin', 
    'BasePlugin',
    'PluginError',
    'plugin_hook',
    'command_plugin'
]