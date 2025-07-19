"""
Configuration loader for user-customizable settings
"""

import json
import shutil
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigLoader:
    """Handles loading configuration from ~/.config/claude/"""

    CONFIG_DIR = Path.home() / ".config" / "claude"
    DEFAULT_CONFIG_DIR = Path(__file__).parent.parent.parent / "DefaultConfig"

    @classmethod
    def ensure_config_dir(cls):
        """Ensure the config directory exists"""
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_system_prompt(cls) -> Optional[str]:
        """Load custom system prompt from ~/.config/claude/system"""
        system_file = cls.CONFIG_DIR / "system"
        if system_file.exists():
            try:
                return system_file.read_text().strip()
            except Exception:
                return None
        return None

    @classmethod
    def get_aliases(cls) -> Dict[str, str]:
        """Load command aliases from ~/.config/claude/aliases.json"""
        aliases_file = cls.CONFIG_DIR / "aliases.json"
        if aliases_file.exists():
            try:
                return json.loads(aliases_file.read_text())
            except Exception:
                return {}
        return {}

    @classmethod
    def get_model_preferences(cls) -> Dict[str, Any]:
        """Load model preferences from ~/.config/claude/models.json"""
        models_file = cls.CONFIG_DIR / "models.json"
        if models_file.exists():
            try:
                return json.loads(models_file.read_text())
            except Exception:
                return {}
        return {}

    @classmethod
    def get_response_templates(cls) -> Dict[str, str]:
        """Load custom response templates from ~/.config/claude/templates.json"""
        templates_file = cls.CONFIG_DIR / "templates.json"
        if templates_file.exists():
            try:
                return json.loads(templates_file.read_text())
            except Exception:
                return {}
        return {}

    @classmethod
    def get_shortcuts(cls) -> Dict[str, str]:
        """Load keyboard shortcuts from ~/.config/claude/shortcuts.json"""
        shortcuts_file = cls.CONFIG_DIR / "shortcuts.json"
        if shortcuts_file.exists():
            try:
                return json.loads(shortcuts_file.read_text())
            except Exception:
                return {}
        return {}

    @classmethod
    def create_default_configs(cls):
        """Copy default configuration files from Config directory"""
        cls.ensure_config_dir()

        # List of config files to copy
        config_files = ["system", "aliases.json", "models.json", "templates.json"]

        # Copy each default config file if it doesn't exist
        for filename in config_files:
            source_file = cls.DEFAULT_CONFIG_DIR / filename
            dest_file = cls.CONFIG_DIR / filename

            if not dest_file.exists() and source_file.exists():
                shutil.copy2(source_file, dest_file)
