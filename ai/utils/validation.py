"""
Input validation and sanitization utilities for Ask CLI

This module provides functions to validate and sanitize user input,
file uploads, and other data to ensure security and reliability.
"""

import os
import re
import mimetypes
from pathlib import Path
from typing import List, Optional, Union, Tuple
from .exceptions import ValidationError, FileError
from .config import get_config


def validate_input_length(text: str, max_length: Optional[int] = None) -> str:
    """
    Validate input text length.
    
    Args:
        text: Input text to validate
        max_length: Maximum allowed length (uses config if None)
        
    Returns:
        Validated text
        
    Raises:
        ValidationError: If text exceeds maximum length
    """
    if max_length is None:
        config = get_config()
        max_length = config.security.max_input_length
    
    if len(text) > max_length:
        raise ValidationError(f"Input text too long. Maximum length is {max_length} characters.")
    
    return text


def sanitize_input(text: str) -> str:
    """
    Sanitize input text by removing potentially dangerous content.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text
    """
    # Remove null bytes and control characters (except newlines and tabs)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def validate_file_path(file_path: Union[str, Path]) -> Path:
    """
    Validate file path for security and existence.
    
    Args:
        file_path: Path to validate
        
    Returns:
        Validated Path object
        
    Raises:
        FileError: If file path is invalid or dangerous
    """
    path = Path(file_path).resolve()
    
    # Check if file exists
    if not path.exists():
        raise FileError(f"File not found: {file_path}", str(path))
    
    # Check if it's actually a file
    if not path.is_file():
        raise FileError(f"Path is not a file: {file_path}", str(path))
    
    # Check for path traversal attempts
    try:
        # This will raise an exception if the path tries to escape
        path.relative_to(Path.cwd())
    except ValueError:
        # Allow absolute paths but check they're not trying to access system files
        if str(path).startswith(('/etc/', '/sys/', '/proc/', '/dev/')):
            raise FileError(f"Access to system files not allowed: {file_path}", str(path))
    
    return path


def validate_file_type(file_path: Union[str, Path], allowed_types: Optional[List[str]] = None) -> bool:
    """
    Validate file type based on extension and MIME type.
    
    Args:
        file_path: Path to file
        allowed_types: List of allowed file extensions (uses config if None)
        
    Returns:
        True if file type is allowed
        
    Raises:
        ValidationError: If file type is not allowed
    """
    path = Path(file_path)
    
    if allowed_types is None:
        config = get_config()
        allowed_types = config.security.allowed_file_types
    
    # Check file extension
    extension = path.suffix.lower()
    if extension not in allowed_types:
        raise ValidationError(
            f"File type not allowed: {extension}. "
            f"Allowed types: {', '.join(allowed_types)}"
        )
    
    # Check MIME type for additional validation
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type:
        # Basic MIME type validation
        if mime_type.startswith('application/x-') and extension not in ['.py', '.js', '.sh']:
            raise ValidationError(f"Potentially dangerous file type: {mime_type}")
    
    return True


def validate_file_size(file_path: Union[str, Path], max_size: Optional[int] = None) -> int:
    """
    Validate file size.
    
    Args:
        file_path: Path to file
        max_size: Maximum allowed size in bytes (uses config if None)
        
    Returns:
        File size in bytes
        
    Raises:
        ValidationError: If file is too large
    """
    path = Path(file_path)
    
    if max_size is None:
        config = get_config()
        max_size = config.security.max_file_size
    
    file_size = path.stat().st_size
    
    if file_size > max_size:
        raise ValidationError(
            f"File too large: {file_size} bytes. "
            f"Maximum size: {max_size} bytes ({max_size / (1024*1024):.1f} MB)"
        )
    
    return file_size


def validate_file_content(file_path: Union[str, Path]) -> str:
    """
    Validate and read file content safely.
    
    Args:
        file_path: Path to file
        
    Returns:
        File content as string
        
    Raises:
        FileError: If file cannot be read or contains invalid content
    """
    path = Path(file_path)
    
    try:
        # Try to read as text with various encodings
        encodings = ['utf-8', 'utf-16', 'latin-1', 'ascii']
        
        for encoding in encodings:
            try:
                with open(path, 'r', encoding=encoding) as f:
                    content = f.read()
                    # Basic content validation
                    if '\x00' in content:
                        raise FileError(f"Binary file detected: {file_path}", str(path))
                    return content
            except UnicodeDecodeError:
                continue
        
        # If all encodings fail, it's likely a binary file
        raise FileError(f"Unable to read file as text: {file_path}", str(path))
        
    except Exception as e:
        raise FileError(f"Error reading file: {e}", str(path))


def validate_url(url: str) -> str:
    """
    Validate URL format and safety.
    
    Args:
        url: URL to validate
        
    Returns:
        Validated URL
        
    Raises:
        ValidationError: If URL is invalid or potentially dangerous
    """
    # Basic URL format validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        raise ValidationError(f"Invalid URL format: {url}")
    
    # Check for potentially dangerous schemes
    if url.startswith(('file://', 'ftp://', 'javascript:', 'data:')):
        raise ValidationError(f"URL scheme not allowed: {url}")
    
    return url


def validate_api_key(api_key: str) -> str:
    """
    Validate API key format.
    
    Args:
        api_key: API key to validate
        
    Returns:
        Validated API key
        
    Raises:
        ValidationError: If API key format is invalid
    """
    if not api_key:
        raise ValidationError("API key cannot be empty")
    
    # Basic format validation for Anthropic API keys
    if not api_key.startswith('sk-ant-'):
        raise ValidationError("Invalid API key format")
    
    if len(api_key) < 20:
        raise ValidationError("API key too short")
    
    # Check for suspicious characters
    if re.search(r'[<>"\']', api_key):
        raise ValidationError("API key contains invalid characters")
    
    return api_key


def validate_command_input(command: str) -> str:
    """
    Validate command input for interactive mode.
    
    Args:
        command: Command to validate
        
    Returns:
        Validated command
        
    Raises:
        ValidationError: If command is invalid
    """
    # Remove excessive whitespace
    command = command.strip()
    
    if not command:
        raise ValidationError("Command cannot be empty")
    
    # Check for basic command injection patterns
    dangerous_patterns = [
        r';\s*rm\s',
        r';\s*del\s',
        r';\s*format\s',
        r'\|\s*rm\s',
        r'&&\s*rm\s',
        r'`[^`]*`',
        r'\$\([^)]*\)'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            raise ValidationError("Command contains potentially dangerous patterns")
    
    return command


def validate_file_upload(file_path: Union[str, Path]) -> Tuple[Path, str]:
    """
    Comprehensive file upload validation.
    
    Args:
        file_path: Path to file to upload
        
    Returns:
        Tuple of (validated_path, file_content)
        
    Raises:
        ValidationError or FileError: If validation fails
    """
    # Validate path
    path = validate_file_path(file_path)
    
    # Validate file type
    validate_file_type(path)
    
    # Validate file size
    validate_file_size(path)
    
    # Validate and read content
    content = validate_file_content(path)
    
    return path, content