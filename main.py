"""
Aria Voice Studio - Main Application Launcher

Run with:
    python main.py
"""

import sys
import warnings

warnings.filterwarnings("ignore", message="pkg_resources is deprecated", category=UserWarning)

from utils.error_handler import setup_global_error_handling, disable_global_error_handling
from voice.trainer import VoiceTrainer
from utils.file_operations import get_logger, cleanup_all_old_backups

setup_global_error_handling()


def main():
    logger = get_logger()
    
    # Clean up old backups on startup (keeps only recent 3 backups per file)
    try:
        cleanup_all_old_backups(data_dir="data", days_to_keep=30, max_backups_per_file=3)
    except Exception as e:
        logger.warning(f"Could not clean up old backups: {e}")

    try:
        trainer = VoiceTrainer(config_file="data/voice_config.json")
        from gui.main_window import launch_gui
        sys.exit(launch_gui(trainer))

    except Exception as e:
        logger.critical(f"Failed to start application: {e}")
        try:
            from PyQt6.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "Aria Voice Studio Error",
                f"Failed to start application:\n{e}\n\nPlease check your audio system and try again."
            )
        except Exception:
            pass
        sys.exit(1)
    finally:
        disable_global_error_handling()


if __name__ == "__main__":
    main()
