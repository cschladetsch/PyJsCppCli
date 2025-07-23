"""
Plugin manager for Ask CLI

This module manages plugin loading, execution, and lifecycle.
"""

import importlib
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

from ..utils.config import get_config
from ..utils.logging import get_logger
from .base import (
    BasePlugin,
    CommandPlugin,
    FilterPlugin,
    FormatterPlugin,
    PluginExecutionError,
    PluginMetadata,
    PluginType,
)

logger = get_logger(__name__)


@dataclass
class Plugin:
    """Plugin wrapper with metadata and instance."""

    metadata: PluginMetadata
    instance: BasePlugin
    module_path: Optional[str] = None
    enabled: bool = True


class PluginManager:
    """
    Manages plugin loading, execution, and lifecycle.

    The plugin manager handles:
    - Loading plugins from directories
    - Managing plugin dependencies
    - Executing plugins in priority order
    - Plugin configuration and state
    """

    def __init__(self):
        """Initialize the plugin manager."""
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_directories: List[Path] = []
        self.hooks: Dict[str, List[Callable]] = {}
        self._initialized = False

        # Default plugin directories
        config = get_config()
        self.plugin_directories = [
            Path.home() / ".ask" / "plugins",
            Path(__file__).parent.parent / "plugins" / "builtin",
            Path.cwd() / "plugins",
        ]

    def initialize(self) -> None:
        """Initialize the plugin manager and load plugins."""
        if self._initialized:
            return

        logger.info("Initializing plugin manager")

        # Create plugin directories if they don't exist
        for directory in self.plugin_directories:
            directory.mkdir(parents=True, exist_ok=True)

        # Load plugins from all directories
        for directory in self.plugin_directories:
            if directory.exists():
                self._load_plugins_from_directory(directory)

        # Initialize loaded plugins
        self._initialize_plugins()

        self._initialized = True
        logger.info(f"Plugin manager initialized with {len(self.plugins)} plugins")

    def _load_plugins_from_directory(self, directory: Path) -> None:
        """
        Load plugins from a directory.

        Args:
            directory: Directory to scan for plugins
        """
        logger.debug(f"Loading plugins from {directory}")

        # Look for Python files and packages
        for item in directory.iterdir():
            if (
                item.is_file()
                and item.suffix == ".py"
                and not item.name.startswith("_")
            ):
                self._load_plugin_from_file(item)
            elif item.is_dir() and not item.name.startswith("_"):
                init_file = item / "__init__.py"
                if init_file.exists():
                    self._load_plugin_from_package(item)

    def _load_plugin_from_file(self, file_path: Path) -> None:
        """
        Load a plugin from a Python file.

        Args:
            file_path: Path to the plugin file
        """
        try:
            module_name = file_path.stem
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                logger.warning(f"Could not load plugin spec from {file_path}")
                return

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Look for plugin classes and functions
            self._extract_plugins_from_module(module, str(file_path))

        except Exception as e:
            logger.error(f"Failed to load plugin from {file_path}: {e}")

    def _load_plugin_from_package(self, package_path: Path) -> None:
        """
        Load a plugin from a Python package.

        Args:
            package_path: Path to the plugin package
        """
        try:
            # Add package parent to sys.path temporarily
            parent_path = str(package_path.parent)
            if parent_path not in sys.path:
                sys.path.insert(0, parent_path)

            try:
                module = importlib.import_module(package_path.name)
                self._extract_plugins_from_module(module, str(package_path))
            finally:
                # Remove from sys.path
                if parent_path in sys.path:
                    sys.path.remove(parent_path)

        except Exception as e:
            logger.error(f"Failed to load plugin package from {package_path}: {e}")

    def _extract_plugins_from_module(self, module: Any, module_path: str) -> None:
        """
        Extract plugins from a loaded module.

        Args:
            module: Loaded module
            module_path: Path to the module
        """
        # Look for plugin classes
        for name in dir(module):
            obj = getattr(module, name)

            # Check if it's a plugin class
            if (
                isinstance(obj, type)
                and issubclass(obj, BasePlugin)
                and obj != BasePlugin
            ):
                self._register_plugin_class(obj, module_path)

            # Check if it's a decorated function
            elif callable(obj) and hasattr(obj, "_is_command_plugin"):
                self._register_function_plugin(obj, module_path)

    def _register_plugin_class(
        self, plugin_class: Type[BasePlugin], module_path: str
    ) -> None:
        """
        Register a plugin class.

        Args:
            plugin_class: Plugin class to register
            module_path: Path to the module containing the plugin
        """
        try:
            instance = plugin_class()
            metadata = instance.metadata

            if metadata.name in self.plugins:
                logger.warning(f"Plugin {metadata.name} already registered, skipping")
                return

            plugin = Plugin(
                metadata=metadata, instance=instance, module_path=module_path
            )

            self.plugins[metadata.name] = plugin
            logger.debug(f"Registered plugin: {metadata.name}")

        except Exception as e:
            logger.error(
                f"Failed to register plugin class {plugin_class.__name__}: {e}"
            )

    def _register_function_plugin(self, func: Callable, module_path: str) -> None:
        """
        Register a function-based plugin.

        Args:
            func: Function with plugin metadata
            module_path: Path to the module containing the function
        """
        try:
            metadata = func._plugin_metadata

            if metadata.name in self.plugins:
                logger.warning(f"Plugin {metadata.name} already registered, skipping")
                return

            # Create a wrapper plugin class
            class FunctionPlugin(BasePlugin):
                def __init__(self, func, metadata):
                    super().__init__()
                    self.func = func
                    self._metadata = metadata

                @property
                def metadata(self) -> PluginMetadata:
                    return self._metadata

                def initialize(self, config: Dict[str, Any]) -> None:
                    self._initialized = True

                def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
                    return self.func(context)

            instance = FunctionPlugin(func, metadata)

            plugin = Plugin(
                metadata=metadata, instance=instance, module_path=module_path
            )

            self.plugins[metadata.name] = plugin
            logger.debug(f"Registered function plugin: {metadata.name}")

        except Exception as e:
            logger.error(f"Failed to register function plugin {func.__name__}: {e}")

    def _initialize_plugins(self) -> None:
        """Initialize all loaded plugins."""
        config = get_config()

        for name, plugin in self.plugins.items():
            try:
                if plugin.enabled and not plugin.instance.initialized:
                    plugin_config = getattr(config, "plugins", {}).get(name, {})
                    plugin.instance.initialize(plugin_config)
                    logger.debug(f"Initialized plugin: {name}")
            except Exception as e:
                logger.error(f"Failed to initialize plugin {name}: {e}")
                plugin.enabled = False

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """
        Get a plugin by name.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None if not found
        """
        return self.plugins.get(name)

    def get_plugins_by_type(self, plugin_type: PluginType) -> List[Plugin]:
        """
        Get all plugins of a specific type.

        Args:
            plugin_type: Type of plugins to retrieve

        Returns:
            List of plugins of the specified type
        """
        return [
            plugin
            for plugin in self.plugins.values()
            if plugin.metadata.plugin_type == plugin_type and plugin.enabled
        ]

    def execute_command_plugin(
        self, command: str, args: List[str], context: Dict[str, Any]
    ) -> Any:
        """
        Execute a command plugin.

        Args:
            command: Command name
            args: Command arguments
            context: Execution context

        Returns:
            Command result

        Raises:
            PluginExecutionError: If execution fails
        """
        command_plugins = self.get_plugins_by_type(PluginType.COMMAND)

        for plugin in command_plugins:
            if isinstance(plugin.instance, CommandPlugin):
                if plugin.instance.get_command_name() == command:
                    try:
                        return plugin.instance.handle_command(args, context)
                    except Exception as e:
                        raise PluginExecutionError(
                            f"Command plugin {plugin.metadata.name} failed: {e}",
                            plugin.metadata.name,
                        )

        raise PluginExecutionError(f"Command plugin not found: {command}")

    def execute_filter_plugins(
        self, data: str, context: Dict[str, Any], filter_type: str
    ) -> str:
        """
        Execute filter plugins on data.

        Args:
            data: Data to filter
            context: Execution context
            filter_type: Type of filtering ("input" or "output")

        Returns:
            Filtered data
        """
        filter_plugins = self.get_plugins_by_type(PluginType.FILTER)

        # Sort by priority
        filter_plugins.sort(key=lambda p: p.metadata.priority.value, reverse=True)

        result = data
        for plugin in filter_plugins:
            if isinstance(plugin.instance, FilterPlugin):
                try:
                    if filter_type == "input":
                        result = plugin.instance.filter_input(result, context)
                    elif filter_type == "output":
                        result = plugin.instance.filter_output(result, context)
                except Exception as e:
                    logger.error(f"Filter plugin {plugin.metadata.name} failed: {e}")
                    # Continue with other plugins

        return result

    def execute_formatter_plugin(
        self, response: str, format_name: str, context: Dict[str, Any]
    ) -> str:
        """
        Execute a formatter plugin.

        Args:
            response: Response to format
            format_name: Name of the format
            context: Execution context

        Returns:
            Formatted response

        Raises:
            PluginExecutionError: If formatter not found or execution fails
        """
        formatter_plugins = self.get_plugins_by_type(PluginType.FORMATTER)

        for plugin in formatter_plugins:
            if isinstance(plugin.instance, FormatterPlugin):
                if plugin.instance.get_format_name() == format_name:
                    try:
                        return plugin.instance.format_response(response, context)
                    except Exception as e:
                        raise PluginExecutionError(
                            f"Formatter plugin {plugin.metadata.name} failed: {e}",
                            plugin.metadata.name,
                        )

        raise PluginExecutionError(f"Formatter plugin not found: {format_name}")

    def list_plugins(self) -> List[Plugin]:
        """
        List all loaded plugins.

        Returns:
            List of all plugins
        """
        return list(self.plugins.values())

    def enable_plugin(self, name: str) -> bool:
        """
        Enable a plugin.

        Args:
            name: Plugin name

        Returns:
            True if plugin was enabled successfully
        """
        plugin = self.get_plugin(name)
        if plugin:
            plugin.enabled = True
            plugin.instance.enabled = True
            logger.info(f"Enabled plugin: {name}")
            return True
        return False

    def disable_plugin(self, name: str) -> bool:
        """
        Disable a plugin.

        Args:
            name: Plugin name

        Returns:
            True if plugin was disabled successfully
        """
        plugin = self.get_plugin(name)
        if plugin:
            plugin.enabled = False
            plugin.instance.enabled = False
            logger.info(f"Disabled plugin: {name}")
            return True
        return False

    def cleanup(self) -> None:
        """Clean up all plugins."""
        for plugin in self.plugins.values():
            try:
                plugin.instance.cleanup()
            except Exception as e:
                logger.error(f"Failed to cleanup plugin {plugin.metadata.name}: {e}")

        self.plugins.clear()
        self._initialized = False
        logger.info("Plugin manager cleaned up")


# Global plugin manager instance
_plugin_manager = PluginManager()


def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance."""
    if not _plugin_manager._initialized:
        _plugin_manager.initialize()
    return _plugin_manager
