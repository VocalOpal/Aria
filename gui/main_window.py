"""
Main GUI window for Aria Voice Studio
Coordinates all GUI components and integrates with business logic
"""

import sys
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget  # type: ignore
from PyQt6.QtCore import Qt  # type: ignore
from PyQt6.QtGui import QFont  # type: ignore

from .components.navigation import NavigationWidget
from .screens.onboarding import OnboardingWidget
from .screens.training import TrainingScreen
from .exercises import ExercisesManager
from .screens.audio_analysis import AudioAnalysisScreen
from .screens.progress import ProgressScreen
from .screens.settings import SettingsScreen
from .design_system import AriaDesignSystem

class AriaMainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, voice_trainer):
        super().__init__()
        self.voice_trainer = voice_trainer
        self.onboarding_widget = None
        self.init_ui()
        self.check_onboarding()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Aria Voice Studio v4.1")
        self.setGeometry(100, 100, 1200, 800)  # Slightly larger for better content display

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove default margins for full-screen design
        layout.setSpacing(0)

        self.navigation = NavigationWidget(self.voice_trainer, self)
        layout.addWidget(self.navigation)

        # Apply our modern design system
        self.setStyleSheet(AriaDesignSystem.get_complete_stylesheet())

    def check_onboarding(self):
        """Check if onboarding is needed"""
        try:
            if self.voice_trainer.is_onboarding_needed():
                self.show_onboarding()
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AriaMainWindow.check_onboarding")

            self.show_main_navigation()

    def show_onboarding(self):
        """Show onboarding wizard"""
        try:
            self.onboarding_widget = OnboardingWidget(self.voice_trainer)
            self.onboarding_widget.onboarding_completed.connect(self.on_onboarding_completed)
            self.onboarding_widget.onboarding_cancelled.connect(self.on_onboarding_cancelled)
            self.setCentralWidget(self.onboarding_widget)
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AriaMainWindow.show_onboarding")

            self.show_main_navigation()

    def on_onboarding_completed(self, config):
        """Handle onboarding completion"""
        try:

            self.voice_trainer.config_manager.update_config(config)
            self.voice_trainer.config_manager.mark_onboarding_complete()

            self.show_main_navigation()
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AriaMainWindow.on_onboarding_completed")

            self.show_main_navigation()

    def on_onboarding_cancelled(self):
        """Handle onboarding cancellation"""
        try:

            self.voice_trainer.config_manager.mark_onboarding_complete()
            self.show_main_navigation()
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AriaMainWindow.on_onboarding_cancelled")

            self.show_main_navigation()

    def show_main_navigation(self):
        """Show main navigation interface"""
        try:
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            self.navigation = NavigationWidget(self.voice_trainer, self)
            layout.addWidget(self.navigation)
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AriaMainWindow.show_main_navigation")

            self.close()

    def show_training_screen(self):
        """Show live training screen"""
        try:
            self.training_screen = TrainingScreen(self.voice_trainer)
            self.training_screen.back_requested.connect(self.show_main_navigation)
            self.setCentralWidget(self.training_screen)
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AriaMainWindow.show_training_screen")

            self.show_main_navigation()

    def show_exercises_screen(self):
        """Show voice exercises screen"""
        try:
            self.exercises_screen = ExercisesManager(self.voice_trainer)
            self.exercises_screen.back_requested.connect(self.show_main_navigation)
            self.setCentralWidget(self.exercises_screen)
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AriaMainWindow.show_exercises_screen")

            self.show_main_navigation()

    def show_audio_analysis_screen(self):
        """Show audio file analysis screen"""
        try:
            self.audio_analysis_screen = AudioAnalysisScreen(self.voice_trainer)
            self.audio_analysis_screen.back_requested.connect(self.show_main_navigation)
            self.setCentralWidget(self.audio_analysis_screen)
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AriaMainWindow.show_audio_analysis_screen")

            self.show_main_navigation()

    def show_progress_screen(self):
        """Show progress tracking screen"""
        try:
            self.progress_screen = ProgressScreen(self.voice_trainer)
            self.progress_screen.back_requested.connect(self.show_main_navigation)
            self.setCentralWidget(self.progress_screen)
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AriaMainWindow.show_progress_screen")

            self.show_main_navigation()

    def show_settings_screen(self):
        """Show settings and configuration screen"""
        try:
            self.settings_screen = SettingsScreen(self.voice_trainer)
            self.settings_screen.back_requested.connect(self.show_main_navigation)
            self.setCentralWidget(self.settings_screen)
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AriaMainWindow.show_settings_screen")

            self.show_main_navigation()

    def closeEvent(self, event):
        """Handle application closing with interrupt-safe cleanup"""
        try:
            # First, stop any active training to prevent audio conflicts
            if hasattr(self, 'training_screen') and self.training_screen:
                try:
                    if hasattr(self.training_screen, 'stop_training'):
                        self.training_screen.stop_training()
                except (KeyboardInterrupt, SystemExit):
                    pass  # Don't let interrupts prevent other cleanup
                except Exception:
                    pass  # Ignore errors during screen cleanup

            # Cleanup voice trainer resources (audio, timers, etc.)
            if hasattr(self.voice_trainer, 'cleanup'):
                try:
                    self.voice_trainer.cleanup()
                except KeyboardInterrupt:
                    # Handle Ctrl+C during cleanup - force cleanup to complete
                    try:
                        # Try essential cleanup only
                        if hasattr(self.voice_trainer.audio_coordinator, 'stop_audio'):
                            self.voice_trainer.audio_coordinator.stop_audio()
                    except Exception:
                        pass  # Even if this fails, continue shutdown
                except Exception as e:
                    from utils.error_handler import log_error
                    log_error(e, "AriaMainWindow.closeEvent.cleanup")

            event.accept()

        except KeyboardInterrupt:
            # If user interrupts during shutdown, force accept the close event
            event.accept()
        except Exception as e:
            try:
                from utils.error_handler import log_error
                log_error(e, "AriaMainWindow.closeEvent")
            except Exception:
                # If even error logging fails, just exit
                pass
            event.accept()

def launch_gui(voice_trainer):
    """Launch the GUI application"""
    app = QApplication(sys.argv)
    window = AriaMainWindow(voice_trainer)
    window.show()
    return app.exec()