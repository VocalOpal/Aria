"""
Atomic file operations and enhanced logging utilities for Aria Voice Studio.
Provides safe file I/O operations that prevent data corruption.
"""

import json
import os
import shutil
import tempfile
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union
from datetime import datetime


class AtomicFileWriter:
    """Context manager for atomic file writing operations"""

    def __init__(self, target_path: Union[str, Path], mode: str = 'w', **kwargs):
        self.target_path = Path(target_path)
        self.mode = mode
        self.kwargs = kwargs
        self.temp_file = None
        self.temp_path = None

    def __enter__(self):
        """Create temporary file for writing"""
        # Ensure parent directory exists
        self.target_path.parent.mkdir(parents=True, exist_ok=True)

        # Create temporary file in same directory as target
        temp_dir = self.target_path.parent
        self.temp_file = tempfile.NamedTemporaryFile(
            mode=self.mode,
            dir=temp_dir,
            prefix=f'.{self.target_path.name}.tmp.',
            delete=False,
            **self.kwargs
        )
        self.temp_path = Path(self.temp_file.name)
        return self.temp_file

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close temporary file and atomically move to target"""
        if self.temp_file:
            self.temp_file.close()

        if exc_type is None:
            # Success - atomically replace target file
            try:
                shutil.move(str(self.temp_path), str(self.target_path))
            except Exception as e:
                # Clean up temp file if move fails
                self._cleanup_temp()
                raise e
        else:
            # Exception occurred - clean up temp file
            self._cleanup_temp()

    def _cleanup_temp(self):
        """Clean up temporary file"""
        if self.temp_path and self.temp_path.exists():
            try:
                self.temp_path.unlink()
            except OSError:
                pass  # Ignore cleanup errors


def save_json_atomic(file_path: Union[str, Path], data: Dict[str, Any],
                    indent: int = 2, **kwargs) -> bool:
    """
    Atomically save JSON data to file.

    Args:
        file_path: Target file path
        data: Data to save as JSON
        indent: JSON indentation
        **kwargs: Additional arguments passed to json.dump()

    Returns:
        True if successful, False otherwise
    """
    try:
        with AtomicFileWriter(file_path) as f:
            json.dump(data, f, indent=indent, **kwargs)
        return True
    except Exception as e:
        logging.error(f"Failed to save JSON to {file_path}: {e}")
        return False


def load_json_safe(file_path: Union[str, Path],
                  default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Safely load JSON data from file with fallback.

    Args:
        file_path: Source file path
        default: Default value if file doesn't exist or is invalid

    Returns:
        Loaded data or default value
    """
    if default is None:
        default = {}

    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        logging.warning(f"Could not load JSON from {file_path}: {e}")
        return default


def backup_file(file_path: Union[str, Path], max_backups: int = 5) -> bool:
    """
    Create a backup of the file with timestamp.

    Args:
        file_path: File to backup
        max_backups: Maximum number of backups to keep

    Returns:
        True if backup was created successfully
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return False

    try:
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = file_path.parent / "backups" / backup_name

        # Ensure backup directory exists
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy file to backup location
        shutil.copy2(file_path, backup_path)

        # Clean up old backups
        _cleanup_old_backups(backup_path.parent, file_path.stem, max_backups)

        logging.info(f"Created backup: {backup_path}")
        return True

    except Exception as e:
        logging.error(f"Failed to create backup of {file_path}: {e}")
        return False


def _cleanup_old_backups(backup_dir: Path, file_stem: str, max_backups: int):
    """Remove old backup files, keeping only the most recent ones"""
    try:
        # Find all backup files for this file
        backup_pattern = f"{file_stem}_*"
        backup_files = list(backup_dir.glob(backup_pattern))

        # Sort by modification time (newest first)
        backup_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        # Remove excess backups
        for old_backup in backup_files[max_backups:]:
            old_backup.unlink()
            logging.debug(f"Removed old backup: {old_backup}")

    except Exception as e:
        logging.warning(f"Failed to cleanup old backups: {e}")


class AriaLogger:
    """Enhanced logging setup for Aria Voice Studio"""

    @staticmethod
    def setup_logging(log_dir: Union[str, Path] = "logs",
                     log_level: str = "INFO") -> logging.Logger:
        """
        Setup comprehensive logging for the application.

        Args:
            log_dir: Directory for log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)

        Returns:
            Configured logger instance
        """
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create logger
        logger = logging.getLogger('aria_voice_studio')
        logger.setLevel(getattr(logging, log_level.upper()))

        # Clear any existing handlers
        logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Only show warnings/errors in console
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler (rotating by date)
        log_file = log_dir / f"aria_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Error file handler (errors only)
        error_file = log_dir / f"aria_errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.FileHandler(error_file)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)

        logger.info("Logging system initialized")
        return logger

    @staticmethod
    def log_system_info(logger: logging.Logger):
        """Log system information for debugging"""
        import platform
        import sys

        logger.info("=== System Information ===")
        logger.info(f"Platform: {platform.platform()}")
        logger.info(f"Python: {sys.version}")
        logger.info(f"Working Directory: {os.getcwd()}")

        # Log audio system info if available
        try:
            import pyaudio
            pa = pyaudio.PyAudio()
            logger.info(f"PyAudio version: {pyaudio.__version__}")
            logger.info(f"Audio devices: {pa.get_device_count()}")
            pa.terminate()
        except Exception as e:
            logger.warning(f"Could not get audio system info: {e}")


# Global logger instance
_logger = None

def get_logger() -> logging.Logger:
    """Get the global Aria logger instance"""
    global _logger
    if _logger is None:
        _logger = AriaLogger.setup_logging()
    return _logger


def log_function_call(func_name: str, args: tuple = (), kwargs: dict = None):
    """Log function calls for debugging"""
    logger = get_logger()
    kwargs_str = f", kwargs={kwargs}" if kwargs else ""
    logger.debug(f"Called {func_name}(args={args}{kwargs_str})")


def log_performance(operation: str, duration: float):
    """Log performance metrics"""
    logger = get_logger()
    logger.info(f"Performance: {operation} took {duration:.3f}s")


# Context manager for performance logging
class PerformanceTimer:
    """Context manager for timing operations"""

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            log_performance(self.operation_name, duration)


# Convenience functions
def safe_save_config(config_data: Dict[str, Any], config_file: Union[str, Path]) -> bool:
    """Safely save configuration with backup and atomic operations"""
    config_file = Path(config_file)

    # Create backup if file exists
    if config_file.exists():
        backup_file(config_file)

    # Atomically save new config
    return save_json_atomic(config_file, config_data)


def safe_load_config(config_file: Union[str, Path],
                    default_config: Dict[str, Any]) -> Dict[str, Any]:
    """Safely load configuration with fallback to defaults"""
    return load_json_safe(config_file, default_config)