"""
Logging configuration and utilities for Ask CLI

This module provides centralized logging configuration with different
log levels and formatters for development and production use.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        # Add color to the levelname
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
            )

        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    enable_console: bool = True,
    enable_colors: bool = True,
) -> logging.Logger:
    """
    Set up logging configuration for the Ask CLI.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        enable_console: Whether to enable console logging
        enable_colors: Whether to enable colored output

    Returns:
        Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger("ask_cli")
    logger.setLevel(getattr(logging, level.upper()))

    # Clear any existing handlers
    logger.handlers.clear()

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )

    simple_formatter = logging.Formatter("%(levelname)s: %(message)s")

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)

        if enable_colors and sys.stdout.isatty():
            console_handler.setFormatter(ColoredFormatter("%(levelname)s: %(message)s"))
        else:
            console_handler.setFormatter(simple_formatter)

        logger.addHandler(console_handler)

    # File handler
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "ask_cli") -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def setup_default_logging() -> logging.Logger:
    """
    Set up default logging configuration.

    Returns:
        Configured logger instance
    """
    # Determine log level from environment
    log_level = os.getenv("ASK_LOG_LEVEL", "INFO")

    # Set up log file path
    log_dir = Path.home() / ".ask_logs"
    log_file = log_dir / f"ask_{datetime.now().strftime('%Y%m%d')}.log"

    # Enable colors unless explicitly disabled
    enable_colors = os.getenv("ASK_NO_COLOR") is None

    return setup_logging(
        level=log_level,
        log_file=str(log_file),
        enable_console=True,
        enable_colors=enable_colors,
    )


# Global logger instance
logger = setup_default_logging()
