#!/usr/bin/env python3
"""Demonstrate the PyClaudeCli system after refactoring."""

from AI.Utils.variables import VariableManager
from AI.Modes.interactive import InteractiveMode
from AI.Api.client import ClaudeClient

def main():
    print("=== PyClaudeCli System Demo ===\n")
    
    # Test variable system
    vm = VariableManager()
    
    # Clear any existing demo variables
    for var in ['demo_user', 'demo_lang', 'demo_version']:
        vm.delete_variable(var)
    
    # Set new variables
    vm.set_variable('demo_user', 'Alice')
    vm.set_variable('demo_lang', 'Python')
    vm.set_variable('demo_version', '3.11')
    
    # Test interpolation
    test_string = "Hello demo_user! You are using demo_lang demo_version."
    result = vm.interpolate_variables(test_string)
    
    print("Variable System Test:")
    print(f"  Input:  {test_string}")
    print(f"  Output: {result}")
    
    # List all variables
    print("\nStored Variables:")
    variables = vm.list_variables()
    if variables:
        for name, value in sorted(variables.items()):
            print(f"  {name} = {value}")
    else:
        print("  (none)")
    
    # Test imports
    print("\nImport Test:")
    try:
        from AI.Utils.colors import Colors
        print("  ✅ Colors module imported")
        from AI.Utils.config_loader import ConfigLoader
        print("  ✅ ConfigLoader module imported")
        from AI.Utils.markdown_renderer import MarkdownRenderer
        print("  ✅ MarkdownRenderer module imported")
        print("\n✅ All systems operational!")
    except Exception as e:
        print(f"  ❌ Import error: {e}")
    
    # Clean up demo variables
    for var in ['demo_user', 'demo_lang', 'demo_version']:
        vm.delete_variable(var)

if __name__ == "__main__":
    main()