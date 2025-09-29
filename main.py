"""
Aria Voice Studio v4.1
Voice training application

Your voice, your journey, your authentic self
"""

import sys
from utils.error_handler import setup_global_error_handling, disable_global_error_handling
from voice.trainer import VoiceTrainer
from utils.file_operations import get_logger

# Initialize global error handling as early as possible
setup_global_error_handling()


def main():
    """Launch Aria Voice Studio GUI application"""
    logger = get_logger()

    try:
        # Use default config file for GUI-only operation
        trainer = VoiceTrainer(config_file="data/voice_config.json")

        # Launch GUI
        from gui.main_window import launch_gui
        sys.exit(launch_gui(trainer))

    except Exception as e:
        logger.critical(f"Failed to start application: {e}")
        # Show user-friendly error dialog if possible
        try:
            from PyQt6.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "Aria Voice Studio Error",
                               f"Failed to start application:\n{e}\n\nPlease check your audio system and try again.")
        except Exception:
            # Fallback if GUI can't be shown
            pass
        sys.exit(1)
    finally:
        disable_global_error_handling()


if __name__ == "__main__":
    main()
