"""
Base plugin classes and interfaces for Ask CLI

This module defines the base plugin architecture and common interfaces
that all plugins must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class PluginType(Enum):
    """Types of plugins supported by the system."""

    COMMAND = "command"
    FILTER = "filter"
    FORMATTER = "formatter"
    PREPROCESSOR = "preprocessor"
    POSTPROCESSOR = "postprocessor"


class PluginPriority(Enum):
    """Plugin execution priority levels."""

    HIGHEST = 100
    HIGH = 75
    NORMAL = 50
    LOW = 25
    LOWEST = 0


@dataclass
class PluginMetadata:
    """Plugin metadata information."""

    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    priority: PluginPriority = PluginPriority.NORMAL
    dependencies: List[str] = None
    enabled: bool = True

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class PluginError(Exception):
    """Base exception for plugin-related errors."""

    def __init__(self, message: str, plugin_name: Optional[str] = None):
        super().__init__(message)
        self.plugin_name = plugin_name


class PluginLoadError(PluginError):
    """Raised when a plugin fails to load."""


class PluginExecutionError(PluginError):
    """Raised when a plugin fails during execution."""


class BasePlugin(ABC):
    """
    Base class for all plugins.

    All plugins must inherit from this class and implement the required methods.
    """

    def __init__(self):
        """Initialize the plugin."""
        self._metadata: Optional[PluginMetadata] = None
        self._enabled = True
        self._initialized = False

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """
        Get plugin metadata.

        Returns:
            PluginMetadata object containing plugin information
        """

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the plugin with configuration.

        Args:
            config: Plugin configuration dictionary

        Raises:
            PluginLoadError: If initialization fails
        """

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the plugin's main functionality.

        Args:
            context: Execution context with input data

        Returns:
            Modified context or result data

        Raises:
            PluginExecutionError: If execution fails
        """

    def cleanup(self) -> None:
        """
        Clean up plugin resources.

        Called when the plugin is being unloaded or the application is shutting down.
        """
        self._initialized = False

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate plugin configuration.

        Args:
            config: Configuration to validate

        Returns:
            True if configuration is valid

        Raises:
            PluginError: If configuration is invalid
        """
        return True

    @property
    def enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self._enabled and self.metadata.enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Enable or disable the plugin."""
        self._enabled = value

    @property
    def initialized(self) -> bool:
        """Check if plugin has been initialized."""
        return self._initialized

    def __str__(self) -> str:
        """String representation of the plugin."""
        return f"{self.metadata.name} v{self.metadata.version}"


class CommandPlugin(BasePlugin):
    """
    Base class for command plugins.

    Command plugins add new commands to the CLI interface.
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata with command type."""
        if self._metadata is None:
            self._metadata = PluginMetadata(
                name=self.__class__.__name__,
                version="1.0.0",
                description="Command plugin",
                author="Unknown",
                plugin_type=PluginType.COMMAND,
            )
        return self._metadata

    @abstractmethod
    def get_command_name(self) -> str:
        """
        Get the command name this plugin handles.

        Returns:
            Command name string
        """

    @abstractmethod
    def get_command_help(self) -> str:
        """
        Get help text for the command.

        Returns:
            Help text string
        """

    @abstractmethod
    def handle_command(self, args: List[str], context: Dict[str, Any]) -> Any:
        """
        Handle the command execution.

        Args:
            args: Command arguments
            context: Execution context

        Returns:
            Command result
        """


class FilterPlugin(BasePlugin):
    """
    Base class for filter plugins.

    Filter plugins modify input or output data as it flows through the system.
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata with filter type."""
        if self._metadata is None:
            self._metadata = PluginMetadata(
                name=self.__class__.__name__,
                version="1.0.0",
                description="Filter plugin",
                author="Unknown",
                plugin_type=PluginType.FILTER,
            )
        return self._metadata

    @abstractmethod
    def filter_input(self, data: str, context: Dict[str, Any]) -> str:
        """
        Filter input data.

        Args:
            data: Input data to filter
            context: Execution context

        Returns:
            Filtered data
        """

    @abstractmethod
    def filter_output(self, data: str, context: Dict[str, Any]) -> str:
        """
        Filter output data.

        Args:
            data: Output data to filter
            context: Execution context

        Returns:
            Filtered data
        """


class FormatterPlugin(BasePlugin):
    """
    Base class for formatter plugins.

    Formatter plugins change how output is displayed to the user.
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata with formatter type."""
        if self._metadata is None:
            self._metadata = PluginMetadata(
                name=self.__class__.__name__,
                version="1.0.0",
                description="Formatter plugin",
                author="Unknown",
                plugin_type=PluginType.FORMATTER,
            )
        return self._metadata

    @abstractmethod
    def format_response(self, response: str, context: Dict[str, Any]) -> str:
        """
        Format the response for display.

        Args:
            response: Raw response text
            context: Execution context

        Returns:
            Formatted response
        """

    @abstractmethod
    def get_format_name(self) -> str:
        """
        Get the name of this format.

        Returns:
            Format name string
        """
