#!/usr/bin/env python3
"""
Main entry point for the AI CLI
"""

import sys
import subprocess
import os
import importlib.util

def check_and_install_dependencies():
    """Check if required dependencies are installed, install if missing"""
    required_packages = {
        'anthropic': 'anthropic>=0.44.0',
        'prompt_toolkit': 'prompt_toolkit>=3.0.39',
        'pyperclip': 'pyperclip>=1.8.2'
    }
    
    missing_packages = []
    for module_name, package_spec in required_packages.items():
        if importlib.util.find_spec(module_name) is None:
            missing_packages.append(package_spec)
    
    if missing_packages:
        print("Missing dependencies detected. Installing...")
        
        # Try different installation methods
        install_methods = [
            # Method 1: Try with --user flag
            [sys.executable, '-m', 'pip', 'install', '--user'] + missing_packages,
            # Method 2: Try with --user and --break-system-packages
            [sys.executable, '-m', 'pip', 'install', '--user', '--break-system-packages'] + missing_packages,
            # Method 3: Try without any flags (for virtual environments)
            [sys.executable, '-m', 'pip', 'install'] + missing_packages,
        ]
        
        for method in install_methods:
            try:
                result = subprocess.run(method, capture_output=True, text=True)
                if result.returncode == 0:
                    print("Dependencies installed successfully!")
                    print("Restarting to load new packages...")
                    # Restart the script to pick up newly installed packages
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                else:
                    continue
            except Exception:
                continue
        
        # If all methods fail, provide manual instructions
        print("\nAutomatic installation failed. Please install manually:")
        print(f"pip install {' '.join(missing_packages)}")
        print("\nOr if you have permission issues:")
        print(f"pip install --user --break-system-packages {' '.join(missing_packages)}")
        return False
    
    return True

if __name__ == "__main__":
    # Check and install dependencies before importing
    if not check_and_install_dependencies():
        sys.exit(1)
    
    # Import after dependencies are installed
    from ai.cli import main
    sys.exit(main())
