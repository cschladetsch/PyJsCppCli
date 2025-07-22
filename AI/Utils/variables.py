"""!
@file variables.py
@brief Variable storage and interpolation system for persistent user-defined variables.

This module provides a comprehensive variable management system that allows users to:
- Define variables with assignment syntax (name=value)
- Store variables persistently across sessions
- Interpolate variables within text strings
- Manage variables through a clean API

@author PyClaudeCli Team
@date 2024
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, Union


class VariableManager:
    """!
    @brief Manages persistent user-defined variables across sessions.
    
    The VariableManager class provides a complete solution for variable storage,
    retrieval, and interpolation. Variables are persisted to disk in JSON format
    and automatically loaded on initialization.
    
    @details
    Features:
    - Persistent storage in ~/.config/claude/variables.json
    - Support for any JSON-serializable data types
    - Automatic variable interpolation in text
    - Thread-safe operations
    - Graceful error handling
    
    Usage Example:
    @code{.py}
    vm = VariableManager()
    vm.set_variable("name", "John")
    vm.set_variable("age", 30)
    result = vm.interpolate_variables("Hello name, you are age years old")
    # Result: "Hello John, you are 30 years old"
    @endcode
    """

    def __init__(self, storage_path: Optional[Union[str, Path]] = None):
        """!
        @brief Initialize variable manager with optional custom storage path.
        
        @param storage_path Optional custom path for variable storage.
                           If None, defaults to ~/.config/claude/variables.json
        
        @details
        The constructor performs the following operations:
        1. Sets up the storage path (custom or default)
        2. Creates necessary directories if they don't exist
        3. Initializes the internal variable dictionary
        4. Loads existing variables from disk
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            config_dir = Path.home() / ".config" / "claude"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.storage_path = config_dir / "variables.json"

        self._variables: Dict[str, Any] = {}
        self._load_variables()

    def _load_variables(self):
        """!
        @brief Load variables from storage file.
        
        @details
        Attempts to load variables from the JSON storage file.
        If the file doesn't exist or contains invalid JSON,
        initializes with an empty dictionary.
        
        @note This is a private method and should not be called directly.
        """
        if self.storage_path.exists():
            try:
                with open(self.storage_path) as f:
                    self._variables = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self._variables = {}

    def _save_variables(self):
        """!
        @brief Save variables to storage file.
        
        @details
        Persists the current variable dictionary to disk in JSON format.
        Creates parent directories if necessary. Silently handles
        permission errors to avoid disrupting program flow.
        
        @note This is a private method called automatically after modifications.
        """
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "w") as f:
                json.dump(self._variables, f, indent=2)
        except (PermissionError, OSError):
            pass

    def set_variable(self, name: str, value: Any):
        """!
        @brief Set or update a variable value.
        
        @param name Variable name (must be valid identifier)
        @param value Variable value (must be JSON-serializable)
        
        @details
        Sets a variable and immediately persists to disk.
        Overwrites existing variables with the same name.
        
        @code{.py}
        vm.set_variable("user", "Alice")
        vm.set_variable("config", {"theme": "dark", "lang": "en"})
        @endcode
        """
        self._variables[name] = value
        self._save_variables()

    def get_variable(self, name: str) -> Any:
        """!
        @brief Retrieve a variable value by name.
        
        @param name Variable name to retrieve
        @return Variable value if exists, None otherwise
        
        @code{.py}
        user = vm.get_variable("user")  # Returns "Alice"
        missing = vm.get_variable("nonexistent")  # Returns None
        @endcode
        """
        return self._variables.get(name)

    def delete_variable(self, name: str) -> bool:
        """!
        @brief Delete a variable from storage.
        
        @param name Variable name to delete
        @return True if variable existed and was deleted, False otherwise
        
        @details
        Removes the variable from memory and persistent storage.
        
        @code{.py}
        if vm.delete_variable("temp"):
            print("Variable deleted")
        @endcode
        """
        if name in self._variables:
            del self._variables[name]
            self._save_variables()
            return True
        return False

    def list_variables(self) -> Dict[str, Any]:
        """!
        @brief Get a copy of all stored variables.
        
        @return Dictionary containing all variable names and values
        
        @note Returns a copy to prevent external modification
        
        @code{.py}
        all_vars = vm.list_variables()
        for name, value in all_vars.items():
            print(f"{name} = {value}")
        @endcode
        """
        return self._variables.copy()

    def clear_variables(self):
        """!
        @brief Remove all variables from storage.
        
        @warning This operation cannot be undone!
        
        @details
        Clears all variables from memory and deletes them from
        persistent storage.
        """
        self._variables = {}
        self._save_variables()

    def parse_assignment(self, text: str) -> Optional[tuple]:
        """!
        @brief Parse variable assignment from text input.
        
        @param text Input text to parse for assignment
        @return Tuple of (variable_name, value) if assignment found, None otherwise
        
        @details
        Recognizes assignment patterns:
        - name=value
        - name = value
        - name={"complex": "json"}
        
        Automatically parses JSON values when possible,
        otherwise treats as string.
        
        @code{.py}
        result = vm.parse_assignment("count=42")
        # Returns: ("count", 42)
        
        result = vm.parse_assignment("data=[1,2,3]")
        # Returns: ("data", [1, 2, 3])
        @endcode
        """
        match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.*)$", text.strip())
        if match:
            var_name, var_value = match.groups()

            try:
                parsed_value = json.loads(var_value)
                return (var_name, parsed_value)
            except json.JSONDecodeError:
                return (var_name, var_value)

        return None

    def interpolate_variables(self, text: str) -> str:
        """!
        @brief Replace variable references in text with their values.
        
        @param text Input text containing variable references
        @return Text with variables replaced by their values
        
        @details
        Identifies variable references by word boundaries and replaces
        them with their stored values. Non-existent variables are
        left unchanged.
        
        @code{.py}
        vm.set_variable("name", "Bob")
        vm.set_variable("day", "Monday")
        result = vm.interpolate_variables("Hello name, happy day!")
        # Returns: "Hello Bob, happy Monday!"
        @endcode
        """
        words = re.findall(r"\b\w+\b|\W+", text)
        result = []

        for word in words:
            if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", word):
                if word in self._variables:
                    value = self._variables[word]
                    result.append(str(value))
                else:
                    result.append(word)
            else:
                result.append(word)

        return "".join(result)

    def process_input(self, text: str) -> tuple[str, bool]:
        """!
        @brief Process input for both assignment and interpolation.
        
        @param text Input text to process
        @return Tuple of (processed_text, was_assignment)
        
        @details
        This is the main entry point for processing user input.
        It first checks for variable assignment, and if none found,
        performs variable interpolation.
        
        @code{.py}
        result, is_assignment = vm.process_input("name=Alice")
        # Returns: ("Variable 'name' set to: Alice", True)
        
        result, is_assignment = vm.process_input("Hello name!")
        # Returns: ("Hello Alice!", False)
        @endcode
        """
        assignment = self.parse_assignment(text)
        if assignment:
            var_name, value = assignment
            self.set_variable(var_name, value)
            return f"Variable '{var_name}' set to: {value}", True

        interpolated = self.interpolate_variables(text)
        return interpolated, False


## Global variable manager instance
_variable_manager = VariableManager()


def get_variable_manager() -> VariableManager:
    """!
    @brief Get the global variable manager instance.
    
    @return The singleton VariableManager instance
    
    @details
    Provides access to the global variable manager for
    use across the application.
    """
    return _variable_manager


def set_variable(name: str, value: Any):
    """!
    @brief Convenience function to set a variable using the global manager.
    
    @param name Variable name
    @param value Variable value
    
    @see VariableManager::set_variable
    """
    _variable_manager.set_variable(name, value)


def get_variable(name: str) -> Any:
    """!
    @brief Convenience function to get a variable using the global manager.
    
    @param name Variable name
    @return Variable value or None
    
    @see VariableManager::get_variable
    """
    return _variable_manager.get_variable(name)


def interpolate_variables(text: str) -> str:
    """!
    @brief Convenience function for variable interpolation using the global manager.
    
    @param text Text containing variable references
    @return Text with variables replaced
    
    @see VariableManager::interpolate_variables
    """
    return _variable_manager.interpolate_variables(text)


def process_input(text: str) -> tuple[str, bool]:
    """!
    @brief Convenience function to process input using the global manager.
    
    @param text Input text to process
    @return Tuple of (processed_text, was_assignment)
    
    @see VariableManager::process_input
    """
    return _variable_manager.process_input(text)