# Plugins Module

Plugin system for extending AI CLI functionality with variable system integration.

## Files

- `__init__.py` - Module initialization
- `base.py` - Base plugin classes and interfaces
- `decorators.py` - Decorators for plugin development
- `plugin_manager.py` - Plugin loading and management

## Description

This module provides a plugin architecture that allows extending the CLI with custom functionality through a well-defined plugin interface. All plugins have access to the persistent variable system for enhanced state management.

## Variable System Integration

### Plugin Features
Plugins can leverage the variable system for:
- **State Persistence**: Store plugin-specific data across sessions
- **User Preferences**: Remember user settings and configurations
- **Data Sharing**: Share data between different plugins
- **Context Awareness**: Access user-defined variables for personalized behavior

### Plugin Development
```python
from ..Utils.variables import VariableManager

class MyPlugin(BasePlugin):
    def __init__(self):
        self.variables = VariableManager()
    
    def execute(self, args):
        # Access variables
        user_pref = self.variables.get_variable('user_preference')
        
        # Set plugin data
        self.variables.set_variable('plugin_last_run', str(datetime.now()))
```

### Benefits
- **Enhanced Plugins**: Plugins can maintain persistent state
- **User Customization**: Store user preferences for plugin behavior
- **Cross-Plugin Communication**: Share data between different plugins
- **Session Continuity**: Plugin state survives CLI restarts