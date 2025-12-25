"""
Unified Logging System

Provides a consistent logging interface across the entire application.
All modules should use get_logger() to obtain their logger instance.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

try:
    import colorlog

    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False


class LoggerManager:
    """Singleton manager for application logging configuration."""

    _instance: Optional["LoggerManager"] = None
    _initialized: bool = False

    def __new__(cls) -> "LoggerManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._loggers: dict[str, logging.Logger] = {}
        self._config: dict = {}

    def configure(self, config: dict) -> None:
        """
        Configure logging from config dictionary.

        Args:
            config: Logging configuration from config.yml
        """
        self._config = config
        log_config = config.get("logging", {})

        # Get settings
        level_str = log_config.get("level", "INFO").upper()
        level = getattr(logging, level_str, logging.INFO)
        log_format = log_config.get(
            "format", "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )
        date_format = log_config.get("date_format", "%Y-%m-%d %H:%M:%S")

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        # Clear existing handlers
        root_logger.handlers.clear()

        # Console handler
        console_config = log_config.get("console", {})
        if console_config.get("enabled", True):
            console_handler = self._create_console_handler(
                level=level,
                log_format=log_format,
                date_format=date_format,
                colorized=console_config.get("colorized", True),
            )
            root_logger.addHandler(console_handler)

        # File handler
        file_config = log_config.get("file", {})
        if file_config.get("enabled", False):
            file_handler = self._create_file_handler(
                filepath=file_config.get("path", "logs/app.log"),
                level=level,
                log_format=log_format,
                date_format=date_format,
                max_size_mb=file_config.get("max_size_mb", 10),
                backup_count=file_config.get("backup_count", 5),
            )
            root_logger.addHandler(file_handler)

    def _create_console_handler(
        self,
        level: int,
        log_format: str,
        date_format: str,
        colorized: bool,
    ) -> logging.Handler:
        """Create console handler with optional color support."""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        if colorized and HAS_COLORLOG:
            color_format = log_format.replace(
                "%(levelname)-8s", "%(log_color)s%(levelname)-8s%(reset)s"
            )
            formatter = colorlog.ColoredFormatter(
                color_format,
                datefmt=date_format,
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
            )
        else:
            formatter = logging.Formatter(log_format, datefmt=date_format)

        handler.setFormatter(formatter)
        return handler

    def _create_file_handler(
        self,
        filepath: str,
        level: int,
        log_format: str,
        date_format: str,
        max_size_mb: int,
        backup_count: int,
    ) -> logging.Handler:
        """Create rotating file handler."""
        # Ensure log directory exists
        log_path = Path(filepath)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        handler = RotatingFileHandler(
            filepath,
            maxBytes=max_size_mb * 1024 * 1024,
            backupCount=backup_count,
            encoding="utf-8",
        )
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
        return handler

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get or create a logger with the given name.

        Args:
            name: Logger name (typically __name__ of the module)

        Returns:
            Configured logger instance
        """
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        return self._loggers[name]


# Global logger manager instance
_logger_manager = LoggerManager()


def configure_logging(config: dict) -> None:
    """
    Configure the logging system with the provided configuration.

    Args:
        config: Full application configuration dictionary
    """
    _logger_manager.configure(config)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given module name.

    This is the primary function that should be used throughout
    the application to obtain logger instances.

    Usage:
        from src.logger import get_logger

        logger = get_logger(__name__)
        logger.info("This is a log message")
        logger.error("Error occurred", exc_info=True)

    Args:
        name: Module name (use __name__)

    Returns:
        Configured logger instance
    """
    return _logger_manager.get_logger(name)
