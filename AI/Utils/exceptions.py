"""
Custom exceptions for Ask CLI

This module defines custom exceptions that provide better error handling
and user feedback throughout the application.
"""

from typing import Any, Dict, Optional


class AskError(Exception):
    """Base exception class for Ask CLI."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize AskError.

        Args:
            message: Error message
            details: Optional dictionary with additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """String representation of the error."""
        return self.message


class ConfigurationError(AskError):
    """Raised when there's a configuration-related error."""


class APIError(AskError):
    """Raised when there's an API-related error."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize APIError.

        Args:
            message: Error message
            status_code: HTTP status code
            response_data: Response data from API
        """
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class AuthenticationError(APIError):
    """Raised when there's an authentication error."""


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after: Optional[int] = None):
        """
        Initialize RateLimitError.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
        """
        super().__init__(message)
        self.retry_after = retry_after


class ValidationError(AskError):
    """Raised when input validation fails."""


class FileError(AskError):
    """Raised when there's a file-related error."""

    def __init__(self, message: str, file_path: Optional[str] = None):
        """
        Initialize FileError.

        Args:
            message: Error message
            file_path: Path to the problematic file
        """
        super().__init__(message)
        self.file_path = file_path


class NetworkError(AskError):
    """Raised when there's a network-related error."""


class InterruptedError(AskError):
    """Raised when operation is interrupted by user."""


class TokenLimitError(APIError):
    """Raised when token limit is exceeded."""


class ModelError(APIError):
    """Raised when there's a model-related error."""


def handle_api_error(error: Exception) -> AskError:
    """
    Convert various API errors to appropriate AskError subclasses.

    Args:
        error: The original exception

    Returns:
        Appropriate AskError subclass
    """
    import requests

    if isinstance(error, requests.exceptions.ConnectionError):
        return NetworkError(
            "Failed to connect to API. Please check your internet connection."
        )

    if isinstance(error, requests.exceptions.Timeout):
        return NetworkError("Request timed out. Please try again.")

    if isinstance(error, requests.exceptions.HTTPError):
        if error.response.status_code == 401:
            return AuthenticationError("Invalid API key or authentication failed.")
        if error.response.status_code == 429:
            return RateLimitError(
                "Rate limit exceeded. Please wait before making more requests."
            )
        if error.response.status_code == 413:
            return TokenLimitError("Request too large. Please reduce input size.")
        return APIError(
            f"API error: {error.response.status_code}",
            status_code=error.response.status_code,
        )

    if isinstance(error, KeyboardInterrupt):
        return InterruptedError("Operation interrupted by user.")

    return AskError(f"Unexpected error: {str(error)}")


def format_error_message(error: AskError) -> str:
    """
    Format error message for user display.

    Args:
        error: The error to format

    Returns:
        Formatted error message
    """
    if isinstance(error, AuthenticationError):
        return (
            f"❌ Authentication Error: {error.message}\n"
            "Please check your API key configuration."
        )

    if isinstance(error, RateLimitError):
        msg = f"🚧 Rate Limit Error: {error.message}"
        if hasattr(error, "retry_after") and error.retry_after:
            msg += f"\nPlease wait {error.retry_after} seconds before retrying."
        return msg

    if isinstance(error, ValidationError):
        return f"⚠️  Validation Error: {error.message}"

    if isinstance(error, FileError):
        msg = f"📁 File Error: {error.message}"
        if hasattr(error, "file_path") and error.file_path:
            msg += f"\nFile: {error.file_path}"
        return msg

    if isinstance(error, NetworkError):
        return f"🌐 Network Error: {error.message}"

    if isinstance(error, ConfigurationError):
        return f"⚙️  Configuration Error: {error.message}"

    if isinstance(error, InterruptedError):
        return f"⏹️  {error.message}"

    if isinstance(error, APIError):
        return f"🔌 API Error: {error.message}"

    return f"❗ Error: {error.message}"
