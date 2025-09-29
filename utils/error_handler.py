"""
Centralized Error Handling System for Aria Voice Studio
Captures all Python errors, exceptions, and warnings globally with daily logging.
"""

import sys
import logging
import warnings
import traceback
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Any


class GlobalErrorHandler:
    """Centralized error handler that captures all exceptions and warnings."""

    _instance: Optional['GlobalErrorHandler'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'GlobalErrorHandler':
        """Singleton pattern to ensure only one error handler exists."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the error handler if not already initialized."""
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self._original_excepthook = None
        self._original_showwarning = None
        self._logger = None
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up daily log file with proper formatting."""
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Create daily log file
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = log_dir / f"errors-{today}.log"

        # Configure logger
        self._logger = logging.getLogger("aria_error_handler")
        self._logger.setLevel(logging.WARNING)  # Capture warnings and errors

        # Remove existing handlers to avoid duplicates
        for handler in self._logger.handlers[:]:
            self._logger.removeHandler(handler)

        # File handler for errors
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self._logger.addHandler(file_handler)

        # Prevent propagation to avoid duplicate console output
        self._logger.propagate = False

    def _log_exception(self, exc_type: type, exc_value: Exception, exc_traceback: Any,
                      context: str = "Unhandled Exception") -> None:
        """Log exception details to the daily log file."""
        try:
            error_details = {
                'context': context,
                'type': exc_type.__name__ if exc_type else 'Unknown',
                'message': str(exc_value) if exc_value else 'No message',
                'traceback': ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)) if exc_traceback else 'No traceback'
            }

            log_message = f"""
{context}:
  Error Type: {error_details['type']}
  Message: {error_details['message']}
  Stack Trace:
{error_details['traceback']}
{'='*80}"""

            self._logger.error(log_message)

        except Exception as logging_error:
            # Fallback: write directly to file if logging fails
            try:
                today = datetime.now().strftime("%Y-%m-%d")
                log_file = Path("logs") / f"errors-{today}.log"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n{timestamp} | CRITICAL | Logging system failure: {logging_error}\n")
                    f.write(f"{timestamp} | ERROR | Original error: {exc_type.__name__}: {exc_value}\n")

            except Exception:
                # Last resort: print to stderr
                print(f"CRITICAL: Error handler failed completely. Original error: {exc_type.__name__}: {exc_value}",
                      file=sys.stderr)

    def _exception_handler(self, exc_type: type, exc_value: Exception, exc_traceback: Any) -> None:
        """Custom exception handler that logs errors and calls original handler."""
        # Log the exception
        self._log_exception(exc_type, exc_value, exc_traceback, "Unhandled Exception")

        # Call original exception handler for normal behavior
        if self._original_excepthook:
            self._original_excepthook(exc_type, exc_value, exc_traceback)
        else:
            sys.__excepthook__(exc_type, exc_value, exc_traceback)

    def _warning_handler(self, message: Any, category: type, filename: str,
                        lineno: int, file: Any = None, line: str = None) -> None:
        """Custom warning handler that logs warnings."""
        try:
            # Filter out known third-party library warnings that we can't fix
            message_str = str(message)

            # Skip pygame pkg_resources deprecation warning (external library issue)
            if ("pkg_resources is deprecated" in message_str and
                "pygame" in filename):
                # Still call original handler but don't log this noise
                if self._original_showwarning:
                    self._original_showwarning(message, category, filename, lineno, file, line)
                return

            # Skip other common third-party deprecation warnings we can't control
            skip_patterns = [
                ("pkg_resources is deprecated", "site-packages"),
                ("deprecated", "site-packages/pygame"),
                ("deprecated", "site-packages/numpy"),
                ("deprecated", "site-packages/scipy"),
                ("deprecated", "site-packages/matplotlib"),
            ]

            for pattern, path_pattern in skip_patterns:
                if pattern in message_str and path_pattern in filename:
                    # Call original handler but don't log
                    if self._original_showwarning:
                        self._original_showwarning(message, category, filename, lineno, file, line)
                    return

            warning_details = f"""
Warning Captured:
  Category: {category.__name__ if category else 'Unknown'}
  Message: {message}
  File: {filename}:{lineno}
  Line: {line if line else 'N/A'}
{'='*80}"""

            self._logger.warning(warning_details)

        except Exception as logging_error:
            # Fallback logging
            try:
                today = datetime.now().strftime("%Y-%m-%d")
                log_file = Path("logs") / f"errors-{today}.log"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n{timestamp} | WARNING | {category.__name__}: {message} ({filename}:{lineno})\n")

            except Exception:
                pass  # Silently fail for warnings

        # Call original warning handler if it exists
        if self._original_showwarning:
            self._original_showwarning(message, category, filename, lineno, file, line)

    def enable(self) -> None:
        """Enable global error and warning capture."""
        if not self._original_excepthook:
            # Store original handlers
            self._original_excepthook = sys.excepthook
            self._original_showwarning = warnings.showwarning

            # Install custom handlers
            sys.excepthook = self._exception_handler
            warnings.showwarning = self._warning_handler

            # Log that error handling is now active
            self._logger.info("Global error handling system activated")

    def disable(self) -> None:
        """Disable global error and warning capture and restore original handlers."""
        if self._original_excepthook:
            sys.excepthook = self._original_excepthook
            warnings.showwarning = self._original_showwarning

            self._logger.info("Global error handling system deactivated")

            self._original_excepthook = None
            self._original_showwarning = None

    def log_custom_error(self, error: Exception, context: str = "Custom Error") -> None:
        """Manually log a custom error with context."""
        self._log_exception(type(error), error, error.__traceback__, context)

    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            self.disable()
        except Exception:
            pass


# Global instance
_global_error_handler = None


def setup_global_error_handling() -> GlobalErrorHandler:
    """Set up and enable global error handling. Returns the handler instance."""
    global _global_error_handler

    if _global_error_handler is None:
        _global_error_handler = GlobalErrorHandler()

    _global_error_handler.enable()
    return _global_error_handler


def disable_global_error_handling() -> None:
    """Disable global error handling."""
    global _global_error_handler

    if _global_error_handler:
        _global_error_handler.disable()


def get_error_handler() -> Optional[GlobalErrorHandler]:
    """Get the current global error handler instance."""
    return _global_error_handler


def log_error(error: Exception, context: str = "Manual Error Log") -> None:
    """Convenience function to manually log an error."""
    global _global_error_handler

    if _global_error_handler:
        _global_error_handler.log_custom_error(error, context)
    else:
        # Fallback if error handler not initialized
        setup_global_error_handling().log_custom_error(error, context)