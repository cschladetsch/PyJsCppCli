"""
Configuration management for Ask CLI

This module handles loading and managing configuration from various sources:
- Configuration files (YAML, JSON, TOML)
- Environment variables
- Command line arguments
- Default values
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict


@dataclass
class APIConfig:
    """API configuration settings."""
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 1024
    temperature: float = 0.7
    timeout: int = 30
    max_retries: int = 3
    base_url: Optional[str] = None


@dataclass
class UIConfig:
    """User interface configuration settings."""
    enable_colors: bool = True
    spinner_style: str = "dots"
    show_timestamps: bool = False
    page_size: int = 20
    auto_save: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    enable_file_logging: bool = True
    log_file: Optional[str] = None
    max_log_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    enable_input_validation: bool = True
    max_input_length: int = 10000
    allowed_file_types: list = None
    max_file_size: int = 5 * 1024 * 1024  # 5MB
    
    def __post_init__(self):
        if self.allowed_file_types is None:
            self.allowed_file_types = [
                '.txt', '.md', '.py', '.js', '.html', '.css', '.json', 
                '.yaml', '.yml', '.xml', '.csv', '.log'
            ]


@dataclass
class Config:
    """Main configuration class."""
    api: APIConfig
    ui: UIConfig
    logging: LoggingConfig
    security: SecurityConfig
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create Config from dictionary."""
        return cls(
            api=APIConfig(**data.get('api', {})),
            ui=UIConfig(**data.get('ui', {})),
            logging=LoggingConfig(**data.get('logging', {})),
            security=SecurityConfig(**data.get('security', {}))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Config to dictionary."""
        return asdict(self)
    
    def save(self, path: Union[str, Path]) -> None:
        """Save configuration to file."""
        path = Path(path)
        data = self.to_dict()
        
        if path.suffix.lower() == '.json':
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
        elif path.suffix.lower() in ['.yml', '.yaml']:
            with open(path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, indent=2)
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}")


class ConfigManager:
    """Configuration manager that loads config from multiple sources."""
    
    DEFAULT_CONFIG_PATHS = [
        Path.home() / '.ask' / 'config.yml',
        Path.home() / '.ask' / 'config.yaml',
        Path.home() / '.ask' / 'config.json',
        Path.cwd() / '.ask.yml',
        Path.cwd() / '.ask.yaml',
        Path.cwd() / '.ask.json',
    ]
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Optional path to specific config file
        """
        self.config_path = Path(config_path) if config_path else None
        self._config: Optional[Config] = None
    
    def load_config(self) -> Config:
        """
        Load configuration from available sources.
        
        Returns:
            Loaded configuration
        """
        if self._config is not None:
            return self._config
        
        # Start with default configuration
        config_data = {}
        
        # Load from config file
        config_file = self._find_config_file()
        if config_file:
            config_data = self._load_config_file(config_file)
        
        # Override with environment variables
        env_config = self._load_from_env()
        config_data = self._merge_config(config_data, env_config)
        
        # Create config object
        self._config = Config.from_dict(config_data)
        
        return self._config
    
    def _find_config_file(self) -> Optional[Path]:
        """Find the first available config file."""
        if self.config_path and self.config_path.exists():
            return self.config_path
        
        for path in self.DEFAULT_CONFIG_PATHS:
            if path.exists():
                return path
        
        return None
    
    def _load_config_file(self, path: Path) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(path, 'r') as f:
                if path.suffix.lower() == '.json':
                    return json.load(f)
                elif path.suffix.lower() in ['.yml', '.yaml']:
                    return yaml.safe_load(f) or {}
                else:
                    raise ValueError(f"Unsupported config file format: {path.suffix}")
        except Exception as e:
            print(f"Warning: Failed to load config file {path}: {e}")
            return {}
    
    def _load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}
        
        # API configuration
        if os.getenv('ASK_API_MODEL'):
            config.setdefault('api', {})['model'] = os.getenv('ASK_API_MODEL')
        if os.getenv('ASK_API_MAX_TOKENS'):
            config.setdefault('api', {})['max_tokens'] = int(os.getenv('ASK_API_MAX_TOKENS'))
        if os.getenv('ASK_API_TEMPERATURE'):
            config.setdefault('api', {})['temperature'] = float(os.getenv('ASK_API_TEMPERATURE'))
        
        # UI configuration
        if os.getenv('ASK_NO_COLOR'):
            config.setdefault('ui', {})['enable_colors'] = False
        if os.getenv('ASK_SPINNER_STYLE'):
            config.setdefault('ui', {})['spinner_style'] = os.getenv('ASK_SPINNER_STYLE')
        
        # Logging configuration
        if os.getenv('ASK_LOG_LEVEL'):
            config.setdefault('logging', {})['level'] = os.getenv('ASK_LOG_LEVEL')
        if os.getenv('ASK_LOG_FILE'):
            config.setdefault('logging', {})['log_file'] = os.getenv('ASK_LOG_FILE')
        
        return config
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two configuration dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_config(self) -> Config:
        """Get the current configuration."""
        return self.load_config()
    
    def create_default_config(self, path: Optional[Union[str, Path]] = None) -> Path:
        """
        Create a default configuration file.
        
        Args:
            path: Optional path for the config file
            
        Returns:
            Path to the created config file
        """
        if path is None:
            config_dir = Path.home() / '.ask'
            config_dir.mkdir(exist_ok=True)
            path = config_dir / 'config.yml'
        else:
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create default config
        config = Config(
            api=APIConfig(),
            ui=UIConfig(),
            logging=LoggingConfig(),
            security=SecurityConfig()
        )
        
        config.save(path)
        return path


# Global config manager instance
_config_manager = ConfigManager()


def get_config() -> Config:
    """Get the global configuration."""
    return _config_manager.get_config()


def reload_config() -> Config:
    """Reload the global configuration."""
    global _config_manager
    _config_manager._config = None
    return _config_manager.get_config()