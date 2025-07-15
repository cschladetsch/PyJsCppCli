"""
Tests for configuration management
"""

import pytest
import tempfile
import json
import yaml
from pathlib import Path
from ai.utils.config import (
    APIConfig,
    UIConfig,
    LoggingConfig,
    SecurityConfig,
    Config,
    ConfigManager,
    get_config
)


class TestConfigClasses:
    """Test configuration data classes."""
    
    def test_api_config_defaults(self):
        """Test APIConfig default values."""
        config = APIConfig()
        assert config.model == "claude-3-5-sonnet-20241022"
        assert config.max_tokens == 1024
        assert config.temperature == 0.7
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.base_url is None
    
    def test_ui_config_defaults(self):
        """Test UIConfig default values."""
        config = UIConfig()
        assert config.enable_colors is True
        assert config.spinner_style == "dots"
        assert config.show_timestamps is False
        assert config.page_size == 20
        assert config.auto_save is True
    
    def test_logging_config_defaults(self):
        """Test LoggingConfig default values."""
        config = LoggingConfig()
        assert config.level == "INFO"
        assert config.enable_file_logging is True
        assert config.log_file is None
        assert config.max_log_size == 10 * 1024 * 1024
        assert config.backup_count == 5
    
    def test_security_config_defaults(self):
        """Test SecurityConfig default values."""
        config = SecurityConfig()
        assert config.enable_input_validation is True
        assert config.max_input_length == 10000
        assert config.max_file_size == 5 * 1024 * 1024
        assert '.txt' in config.allowed_file_types
        assert '.py' in config.allowed_file_types


class TestConfig:
    """Test main Config class."""
    
    def test_config_creation(self):
        """Test Config creation with all sub-configs."""
        config = Config(
            api=APIConfig(),
            ui=UIConfig(),
            logging=LoggingConfig(),
            security=SecurityConfig()
        )
        
        assert isinstance(config.api, APIConfig)
        assert isinstance(config.ui, UIConfig)
        assert isinstance(config.logging, LoggingConfig)
        assert isinstance(config.security, SecurityConfig)
    
    def test_config_from_dict(self):
        """Test Config creation from dictionary."""
        data = {
            'api': {'model': 'custom-model', 'max_tokens': 2048},
            'ui': {'enable_colors': False, 'spinner_style': 'moon'},
            'logging': {'level': 'DEBUG'},
            'security': {'max_input_length': 5000}
        }
        
        config = Config.from_dict(data)
        
        assert config.api.model == 'custom-model'
        assert config.api.max_tokens == 2048
        assert config.ui.enable_colors is False
        assert config.ui.spinner_style == 'moon'
        assert config.logging.level == 'DEBUG'
        assert config.security.max_input_length == 5000
    
    def test_config_to_dict(self):
        """Test Config conversion to dictionary."""
        config = Config(
            api=APIConfig(model='test-model'),
            ui=UIConfig(enable_colors=False),
            logging=LoggingConfig(level='DEBUG'),
            security=SecurityConfig()
        )
        
        data = config.to_dict()
        
        assert data['api']['model'] == 'test-model'
        assert data['ui']['enable_colors'] is False
        assert data['logging']['level'] == 'DEBUG'
        assert 'security' in data
    
    def test_config_save_json(self):
        """Test saving config to JSON file."""
        config = Config(
            api=APIConfig(model='test-model'),
            ui=UIConfig(),
            logging=LoggingConfig(),
            security=SecurityConfig()
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            config.save(tmp_path)
            
            # Verify file was created and contains expected data
            assert tmp_path.exists()
            with open(tmp_path, 'r') as f:
                data = json.load(f)
            
            assert data['api']['model'] == 'test-model'
        finally:
            tmp_path.unlink()
    
    def test_config_save_yaml(self):
        """Test saving config to YAML file."""
        config = Config(
            api=APIConfig(model='test-model'),
            ui=UIConfig(),
            logging=LoggingConfig(),
            security=SecurityConfig()
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            config.save(tmp_path)
            
            # Verify file was created and contains expected data
            assert tmp_path.exists()
            with open(tmp_path, 'r') as f:
                data = yaml.safe_load(f)
            
            assert data['api']['model'] == 'test-model'
        finally:
            tmp_path.unlink()


class TestConfigManager:
    """Test ConfigManager class."""
    
    def test_config_manager_init(self):
        """Test ConfigManager initialization."""
        manager = ConfigManager()
        assert manager.config_path is None
        assert manager._config is None
    
    def test_config_manager_init_with_path(self):
        """Test ConfigManager initialization with path."""
        test_path = "/test/path/config.yml"
        manager = ConfigManager(test_path)
        assert manager.config_path == Path(test_path)
    
    def test_load_config_file_json(self):
        """Test loading config from JSON file."""
        config_data = {
            'api': {'model': 'json-model', 'max_tokens': 1500},
            'ui': {'enable_colors': False}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            json.dump(config_data, tmp)
            tmp_path = Path(tmp.name)
        
        try:
            manager = ConfigManager(tmp_path)
            config = manager.load_config()
            
            assert config.api.model == 'json-model'
            assert config.api.max_tokens == 1500
            assert config.ui.enable_colors is False
        finally:
            tmp_path.unlink()
    
    def test_load_config_file_yaml(self):
        """Test loading config from YAML file."""
        config_data = {
            'api': {'model': 'yaml-model', 'temperature': 0.5},
            'logging': {'level': 'DEBUG'}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as tmp:
            yaml.dump(config_data, tmp)
            tmp_path = Path(tmp.name)
        
        try:
            manager = ConfigManager(tmp_path)
            config = manager.load_config()
            
            assert config.api.model == 'yaml-model'
            assert config.api.temperature == 0.5
            assert config.logging.level == 'DEBUG'
        finally:
            tmp_path.unlink()
    
    def test_load_config_with_env_override(self, monkeypatch):
        """Test loading config with environment variable override."""
        # Set environment variables
        monkeypatch.setenv('ASK_API_MODEL', 'env-model')
        monkeypatch.setenv('ASK_LOG_LEVEL', 'ERROR')
        monkeypatch.setenv('ASK_NO_COLOR', '1')
        
        manager = ConfigManager()
        config = manager.load_config()
        
        assert config.api.model == 'env-model'
        assert config.logging.level == 'ERROR'
        assert config.ui.enable_colors is False
    
    def test_create_default_config(self):
        """Test creating default configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'config.yml'
            
            manager = ConfigManager()
            created_path = manager.create_default_config(config_path)
            
            assert created_path == config_path
            assert config_path.exists()
            
            # Verify content
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)
            
            assert 'api' in data
            assert 'ui' in data
            assert 'logging' in data
            assert 'security' in data