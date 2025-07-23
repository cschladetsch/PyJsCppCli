"""
Tests for validation utilities
"""

import pytest
import tempfile
from pathlib import Path
from ask.Utils.validation import (
    validate_input_length,
    sanitize_input,
    validate_file_path,
    validate_file_type,
    validate_file_size,
    validate_url,
    validate_api_key,
    validate_command_input
)
from ask.Utils.exceptions import ValidationError, FileError


class TestInputValidation:
    """Test input validation functions."""
    
    def test_validate_input_length_valid(self):
        """Test input length validation with valid input."""
        text = "This is a valid input"
        result = validate_input_length(text, max_length=100)
        assert result == text
    
    def test_validate_input_length_too_long(self):
        """Test input length validation with too long input."""
        text = "x" * 1000
        with pytest.raises(ValidationError, match="Input text too long"):
            validate_input_length(text, max_length=100)
    
    def test_sanitize_input_basic(self):
        """Test basic input sanitization."""
        text = "Hello\x00World\x0B"
        result = sanitize_input(text)
        assert result == "HelloWorld"
    
    def test_sanitize_input_whitespace(self):
        """Test whitespace normalization."""
        text = "  Hello   World  \n\n  "
        result = sanitize_input(text)
        assert result == "Hello World"


class TestFileValidation:
    """Test file validation functions."""
    
    def test_validate_file_path_valid(self):
        """Test file path validation with valid file."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test content")
            tmp_path = Path(tmp.name)
        
        try:
            result = validate_file_path(tmp_path)
            assert result == tmp_path.resolve()
        finally:
            tmp_path.unlink()
    
    def test_validate_file_path_not_exists(self):
        """Test file path validation with non-existent file."""
        with pytest.raises(FileError, match="File not found"):
            validate_file_path("/nonexistent/file.txt")
    
    def test_validate_file_type_valid(self):
        """Test file type validation with allowed type."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            result = validate_file_type(tmp_path, allowed_types=[".txt", ".md"])
            assert result is True
        finally:
            tmp_path.unlink()
    
    def test_validate_file_type_invalid(self):
        """Test file type validation with disallowed type."""
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            with pytest.raises(ValidationError, match="File type not allowed"):
                validate_file_type(tmp_path, allowed_types=[".txt", ".md"])
        finally:
            tmp_path.unlink()
    
    def test_validate_file_size_valid(self):
        """Test file size validation with valid size."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"small content")
            tmp_path = Path(tmp.name)
        
        try:
            result = validate_file_size(tmp_path, max_size=1000)
            assert result > 0
        finally:
            tmp_path.unlink()
    
    def test_validate_file_size_too_large(self):
        """Test file size validation with too large file."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"x" * 1000)
            tmp_path = Path(tmp.name)
        
        try:
            with pytest.raises(ValidationError, match="File too large"):
                validate_file_size(tmp_path, max_size=100)
        finally:
            tmp_path.unlink()


class TestURLValidation:
    """Test URL validation functions."""
    
    def test_validate_url_valid_https(self):
        """Test URL validation with valid HTTPS URL."""
        url = "https://example.com/path"
        result = validate_url(url)
        assert result == url
    
    def test_validate_url_valid_http(self):
        """Test URL validation with valid HTTP URL."""
        url = "http://localhost:8080/api"
        result = validate_url(url)
        assert result == url
    
    def test_validate_url_invalid_format(self):
        """Test URL validation with invalid format."""
        with pytest.raises(ValidationError, match="Invalid URL format"):
            validate_url("not-a-url")
    
    def test_validate_url_dangerous_scheme(self):
        """Test URL validation with dangerous scheme."""
        with pytest.raises(ValidationError, match="URL scheme not allowed"):
            validate_url("file:///etc/passwd")


class TestAPIKeyValidation:
    """Test API key validation functions."""
    
    def test_validate_api_key_valid(self):
        """Test API key validation with valid key."""
        api_key = "sk-ant-api03-abcdef1234567890"
        result = validate_api_key(api_key)
        assert result == api_key
    
    def test_validate_api_key_empty(self):
        """Test API key validation with empty key."""
        with pytest.raises(ValidationError, match="API key cannot be empty"):
            validate_api_key("")
    
    def test_validate_api_key_invalid_format(self):
        """Test API key validation with invalid format."""
        with pytest.raises(ValidationError, match="Invalid API key format"):
            validate_api_key("invalid-key-format")
    
    def test_validate_api_key_too_short(self):
        """Test API key validation with too short key."""
        with pytest.raises(ValidationError, match="API key too short"):
            validate_api_key("sk-ant-123")
    
    def test_validate_api_key_invalid_chars(self):
        """Test API key validation with invalid characters."""
        with pytest.raises(ValidationError, match="API key contains invalid characters"):
            validate_api_key("sk-ant-api03-<script>alert('xss')</script>")


class TestCommandValidation:
    """Test command input validation functions."""
    
    def test_validate_command_input_valid(self):
        """Test command validation with valid command."""
        command = "help"
        result = validate_command_input(command)
        assert result == command
    
    def test_validate_command_input_empty(self):
        """Test command validation with empty command."""
        with pytest.raises(ValidationError, match="Command cannot be empty"):
            validate_command_input("")
    
    def test_validate_command_input_whitespace_only(self):
        """Test command validation with whitespace only."""
        with pytest.raises(ValidationError, match="Command cannot be empty"):
            validate_command_input("   \n\t   ")
    
    def test_validate_command_input_dangerous_pattern(self):
        """Test command validation with dangerous patterns."""
        dangerous_commands = [
            "help; rm -rf /",
            "help && rm file.txt",
            "help | rm file.txt",
            "help `rm file.txt`",
            "help $(rm file.txt)"
        ]
        
        for cmd in dangerous_commands:
            with pytest.raises(ValidationError, match="potentially dangerous patterns"):
                validate_command_input(cmd)