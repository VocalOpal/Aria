"""
Aria Voice Studio - Voice Training Application

This initialization file ensures global error handling is set up
for any module that imports from this package.
"""

# Import and initialize error handling for the entire application
from core.error_handler import setup_global_error_handling

# Initialize error handling when package is imported
setup_global_error_handling()

__version__ = "4.0"
__author__ = "Aria Voice Studio"
__description__ = "Voice training application that adapts to your progress"