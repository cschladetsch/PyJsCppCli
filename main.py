#!/usr/bin/env python3
"""
Main entry point for the AI CLI
"""

import sys
import subprocess
import os
import importlib.util
import datetime

def check_and_install_dependencies():
    """Check if required dependencies are installed, install if missing"""
    required_packages = {
        'anthropic': 'anthropic>=0.44.0',
        'prompt_toolkit': 'prompt_toolkit>=3.0.39',
        'pyperclip': 'pyperclip>=1.8.2',
        'sdl2': 'PySDL2>=0.9.14',
        'numpy': 'numpy>=1.21.0'
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
    
    # Check for sox (for music playback)
    check_and_install_sox()
    
    return True

def check_and_install_sox():
    """Check if sox is installed for music playback"""
    try:
        # Check if running in WSL2
        is_wsl2 = False
        try:
            with open('/proc/version', 'r') as f:
                is_wsl2 = 'microsoft' in f.read().lower()
        except:
            pass
        
        if is_wsl2:
            # WSL2 - check if PowerShell is available for audio
            if subprocess.run(['which', 'powershell.exe'], capture_output=True).returncode != 0:
                print("Note: For startup music in WSL2, ensure Windows paths are accessible")
            return
        
        # Check if sox/play command exists
        result = subprocess.run(['which', 'play'], capture_output=True, text=True)
        if result.returncode == 0:
            return  # sox is already installed
        
        # Detect the platform and package manager
        if sys.platform == "darwin":  # macOS
            print("Installing sox for music playback (macOS)...")
            # Try homebrew first
            if subprocess.run(['which', 'brew'], capture_output=True).returncode == 0:
                subprocess.run(['brew', 'install', 'sox'], capture_output=True)
            else:
                print("Note: Install sox with 'brew install sox' for startup music")
        elif sys.platform.startswith("linux"):
            print("Note: For startup music, install sox:")
            # Check which package manager is available
            if subprocess.run(['which', 'apt-get'], capture_output=True).returncode == 0:
                print("  sudo apt-get install sox")
            elif subprocess.run(['which', 'yum'], capture_output=True).returncode == 0:
                print("  sudo yum install sox")
            elif subprocess.run(['which', 'dnf'], capture_output=True).returncode == 0:
                print("  sudo dnf install sox")
            elif subprocess.run(['which', 'pacman'], capture_output=True).returncode == 0:
                print("  sudo pacman -S sox")
            else:
                print("  Install sox using your system's package manager")
        elif sys.platform == "win32":
            print("Note: For startup music on Windows, download sox from http://sox.sourceforge.net")
    except Exception:
        # Silently ignore any errors checking for sox
        pass

if __name__ == "__main__":
    # Update build time
    build_info_path = os.path.join(os.path.dirname(__file__), 'ai', 'build_info.py')
    with open(build_info_path, 'w') as f:
        f.write('"""Build information for PyClaudeCli"""\n\n')
        f.write(f'BUILD_DATE = "{datetime.datetime.now().strftime("%Y-%m-%d")}"\n')
    
    # Check and install dependencies before importing
    if not check_and_install_dependencies():
        sys.exit(1)
    
    # Import after dependencies are installed
    from ai.cli import main
    from ai.utils.config_loader import ConfigLoader
    from ai.utils.music import MusicPlayer
    from pathlib import Path
    
    # Check if this is first run (config directory doesn't exist)
    config_dir = Path.home() / ".config" / "claude"
    if not config_dir.exists():
        print("\nFirst run detected. Setting up configuration...")
        ConfigLoader.create_default_configs()
        print(f"Created configuration files in {config_dir}")
        print("You can customize your settings by editing files in that directory.\n")
    
    sys.exit(main())
