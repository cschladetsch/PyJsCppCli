"""
Decorators for plugin system

This module provides decorators to simplify plugin development
and registration.
"""

from functools import wraps
from typing import Callable

from .base import PluginMetadata, PluginPriority, PluginType


def plugin_hook(hook_name: str, priority: PluginPriority = PluginPriority.NORMAL):
    """
    Decorator to mark a function as a plugin hook.

    Args:
        hook_name: Name of the hook point
        priority: Execution priority

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Add hook metadata
        wrapper._plugin_hook = hook_name
        wrapper._plugin_priority = priority

        return wrapper

    return decorator


def command_plugin(
    name: str,
    description: str = "",
    help_text: str = "",
    version: str = "1.0.0",
    author: str = "Unknown",
    priority: PluginPriority = PluginPriority.NORMAL,
):
    """
    Decorator to create a command plugin from a function.

    Args:
        name: Command name
        description: Plugin description
        help_text: Command help text
        version: Plugin version
        author: Plugin author
        priority: Execution priority

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Add command metadata
        wrapper._plugin_metadata = PluginMetadata(
            name=name,
            version=version,
            description=description,
            author=author,
            plugin_type=PluginType.COMMAND,
            priority=priority,
        )
        wrapper._command_name = name
        wrapper._command_help = help_text or description
        wrapper._is_command_plugin = True

        return wrapper

    return decorator


def filter_plugin(
    name: str,
    description: str = "",
    version: str = "1.0.0",
    author: str = "Unknown",
    priority: PluginPriority = PluginPriority.NORMAL,
    filter_type: str = "both",  # "input", "output", or "both"
):
    """
    Decorator to create a filter plugin from a function.

    Args:
        name: Plugin name
        description: Plugin description
        version: Plugin version
        author: Plugin author
        priority: Execution priority
        filter_type: Type of filtering ("input", "output", or "both")

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Add filter metadata
        wrapper._plugin_metadata = PluginMetadata(
            name=name,
            version=version,
            description=description,
            author=author,
            plugin_type=PluginType.FILTER,
            priority=priority,
        )
        wrapper._filter_type = filter_type
        wrapper._is_filter_plugin = True

        return wrapper

    return decorator


def formatter_plugin(
    name: str,
    format_name: str,
    description: str = "",
    version: str = "1.0.0",
    author: str = "Unknown",
    priority: PluginPriority = PluginPriority.NORMAL,
):
    """
    Decorator to create a formatter plugin from a function.

    Args:
        name: Plugin name
        format_name: Format name for this formatter
        description: Plugin description
        version: Plugin version
        author: Plugin author
        priority: Execution priority

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Add formatter metadata
        wrapper._plugin_metadata = PluginMetadata(
            name=name,
            version=version,
            description=description,
            author=author,
            plugin_type=PluginType.FORMATTER,
            priority=priority,
        )
        wrapper._format_name = format_name
        wrapper._is_formatter_plugin = True

        return wrapper

    return decorator


def preprocessor_plugin(
    name: str,
    description: str = "",
    version: str = "1.0.0",
    author: str = "Unknown",
    priority: PluginPriority = PluginPriority.NORMAL,
):
    """
    Decorator to create a preprocessor plugin from a function.

    Args:
        name: Plugin name
        description: Plugin description
        version: Plugin version
        author: Plugin author
        priority: Execution priority

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Add preprocessor metadata
        wrapper._plugin_metadata = PluginMetadata(
            name=name,
            version=version,
            description=description,
            author=author,
            plugin_type=PluginType.PREPROCESSOR,
            priority=priority,
        )
        wrapper._is_preprocessor_plugin = True

        return wrapper

    return decorator


def postprocessor_plugin(
    name: str,
    description: str = "",
    version: str = "1.0.0",
    author: str = "Unknown",
    priority: PluginPriority = PluginPriority.NORMAL,
):
    """
    Decorator to create a postprocessor plugin from a function.

    Args:
        name: Plugin name
        description: Plugin description
        version: Plugin version
        author: Plugin author
        priority: Execution priority

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Add postprocessor metadata
        wrapper._plugin_metadata = PluginMetadata(
            name=name,
            version=version,
            description=description,
            author=author,
            plugin_type=PluginType.POSTPROCESSOR,
            priority=priority,
        )
        wrapper._is_postprocessor_plugin = True

        return wrapper

    return decorator
