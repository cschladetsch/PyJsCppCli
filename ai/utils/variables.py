"""
Variable storage and interpolation system for persistent user-defined variables.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, Union


class VariableManager:
    """Manages persistent user-defined variables across sessions."""
    
    def __init__(self, storage_path: Optional[Union[str, Path]] = None):
        """Initialize variable manager with storage path."""
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            config_dir = Path.home() / ".config" / "claude"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.storage_path = config_dir / "variables.json"
        
        self._variables: Dict[str, Any] = {}
        self._load_variables()
    
    def _load_variables(self):
        """Load variables from storage file."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    self._variables = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self._variables = {}
    
    def _save_variables(self):
        """Save variables to storage file."""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump(self._variables, f, indent=2)
        except (PermissionError, OSError):
            # Silently ignore if we can't save (e.g., invalid path)
            pass
    
    def set_variable(self, name: str, value: Any):
        """Set a variable value."""
        self._variables[name] = value
        self._save_variables()
    
    def get_variable(self, name: str) -> Any:
        """Get a variable value."""
        return self._variables.get(name)
    
    def delete_variable(self, name: str) -> bool:
        """Delete a variable. Returns True if variable existed."""
        if name in self._variables:
            del self._variables[name]
            self._save_variables()
            return True
        return False
    
    def list_variables(self) -> Dict[str, Any]:
        """Get all variables."""
        return self._variables.copy()
    
    def clear_variables(self):
        """Clear all variables."""
        self._variables = {}
        self._save_variables()
    
    def parse_assignment(self, text: str) -> Optional[tuple]:
        """
        Parse variable assignment from text.
        Returns (variable_name, value) if assignment found, None otherwise.
        Supports: var=value, var = value
        """
        # Match variable assignment pattern
        match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.*)$', text.strip())
        if match:
            var_name, var_value = match.groups()
            
            # Try to parse as JSON for complex types
            try:
                parsed_value = json.loads(var_value)
                return (var_name, parsed_value)
            except json.JSONDecodeError:
                # Treat as string
                return (var_name, var_value)
        
        return None
    
    def interpolate_variables(self, text: str) -> str:
        """
        Replace variable references in text with their values.
        Uses simple word boundaries to identify variables.
        """
        # Split text into words and check each for variable substitution
        words = re.findall(r'\b\w+\b|\W+', text)
        result = []
        
        for word in words:
            # Check if this word is a variable name (alphanumeric identifier)
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', word):
                # Check if variable exists (not just if it's None)
                if word in self._variables:
                    value = self._variables[word]
                    result.append(str(value))
                else:
                    result.append(word)
            else:
                result.append(word)
        
        return ''.join(result)
    
    def process_input(self, text: str) -> tuple[str, bool]:
        """
        Process input text for variable assignments and interpolation.
        Returns (processed_text, was_assignment).
        """
        # Check for variable assignment
        assignment = self.parse_assignment(text)
        if assignment:
            var_name, value = assignment
            self.set_variable(var_name, value)
            return f"Variable '{var_name}' set to: {value}", True
        
        # Interpolate variables in the text
        interpolated = self.interpolate_variables(text)
        return interpolated, False


# Global variable manager instance
_variable_manager = VariableManager()


def get_variable_manager() -> VariableManager:
    """Get the global variable manager."""
    return _variable_manager


def set_variable(name: str, value: Any):
    """Set a variable value."""
    _variable_manager.set_variable(name, value)


def get_variable(name: str) -> Any:
    """Get a variable value."""
    return _variable_manager.get_variable(name)


def interpolate_variables(text: str) -> str:
    """Replace variable references in text with their values."""
    return _variable_manager.interpolate_variables(text)


def process_input(text: str) -> tuple[str, bool]:
    """Process input for variable assignments and interpolation."""
    return _variable_manager.process_input(text)