"""Main application window with sidebar navigation."""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from PyQt6.QtGui import QFont, QKeyEvent, QIcon, QPixmap, QPainter, QColor, QLinearGradient, QDesktopServices

from .design_system import (
    AriaColors, create_sidebar, NavButton
)
from .screens.training import TrainingScreen
from .screens.onboarding import OnboardingScreen
from .screens.settings import SettingsScreen
from .screens.exercises import ExercisesScreen
from .screens.audio_analysis import AudioAnalysisScreen
from .screens.progress import ProgressScreen
from .screens.snapshot_comparison import SnapshotComparisonScreen
from .screens.health_dashboard import HealthDashboardScreen
from .components.shortcuts_help import ShortcutsDialog, get_modifier_qt
from .components.profile_switcher import ProfileDropdown
from .components.streak_calendar import StreakBadge
from .components.supporters_dialog import SupportersDialog
from .utils.toast_notifications import ToastNotification
from .easter_eggs import (
    SecretAboutDialog, KonamiCodeDetector, LogoClickDetector,
    DeveloperModeDialog, SecretMessageToast
)


class AriaMainWindow(QMainWindow):
    """Main application window with sidebar navigation"""

    def __init__(self, voice_trainer):
        super().__init__()
        self.voice_trainer = voice_trainer
        self.current_screen = None

        # Easter eggs setup
        self.logo_click_detector = LogoClickDetector(click_threshold=7)
        self.konami_detector = KonamiCodeDetector()
        
        self.init_ui()
        self.check_onboarding()
    
    def create_app_icon(self):
        """Load app icon from file"""
        import os
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "edited-photo.png")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        # Fallback to empty icon if file not found
        return QIcon()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Aria Voice Studio - Public Beta (v5)")
        
        # Get available screen geometry (EXCLUDES taskbar!)
        available = QApplication.primaryScreen().availableGeometry()
        
        # Calculate window size - content needs proper space to avoid cutoff
        # Target: 1520px width (sidebar 300px + content 1220px)
        # Target: 950px height (to fit all cards, logo, and content)
        ideal_width = 1520
        ideal_height = 950
        
        # Scale down ONLY if screen is too small, otherwise use ideal size
        # Use 96% max to leave small margin and avoid taskbar overlap
        if available.width() < ideal_width:
            window_width = int(available.width() * 0.96)
        else:
            window_width = ideal_width
            
        if available.height() < ideal_height:
            window_height = int(available.height() * 0.94)
        else:
            window_height = ideal_height
        
        # Center the window within available geometry
        x = available.x() + (available.width() - window_width) // 2
        y = available.y() + (available.height() - window_height) // 2
        
        self.setGeometry(x, y, window_width, window_height)
        
        # Set minimum size large enough to prevent any cutoff
        # Based on actual content requirements from screenshots
        self.setMinimumSize(1450, 850)
        
        # Set window icon
        self.setWindowIcon(self.create_app_icon())
        
        # Connect resize event to toggle sidebar text visibility
        self.installEventFilter(self)

        # Set main window background gradient
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5A7A95,
                    stop:1 #C88AA8
                );
            }
        """)

        # Main container
        main_widget = QWidget()
        main_widget.setStyleSheet("background: transparent;")
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create sidebar
        self.sidebar, self.sidebar_layout = create_sidebar()
        main_layout.addWidget(self.sidebar)

        # Connect logo click easter egg
        if hasattr(self.sidebar, 'aria_logo'):
            self.sidebar.aria_logo.mousePressEvent = lambda e: self.handle_logo_click()

        # Add navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("live", "🎤", "Live Voice Training"),
            ("exercises", "🏃", "Voice Exercises"),
            ("analysis", "📊", "Audio File Analysis"),
            ("progress", "📈", "Progress & Statistics"),
            ("health", "❤️", "Vocal Health"),
            ("journey", "🎵", "Voice Journey"),
            ("settings", "⚙️", "Settings")
        ]

        for key, icon, text in nav_items:
            btn = NavButton(icon, text, active=(key == "live"))
            btn.mousePressEvent = lambda e, k=key: self.navigate_to(k)
            self.nav_buttons[key] = btn
            self.sidebar_layout.addWidget(btn)

        self.sidebar_layout.addStretch()
        
        # Add streak badge if session manager available
        if hasattr(self.voice_trainer, 'session_manager'):
            streak_container = QWidget()
            streak_container.setStyleSheet("background: transparent;")
            streak_layout = QVBoxLayout(streak_container)
            streak_layout.setContentsMargins(16, 0, 16, 8)
            streak_layout.setSpacing(0)
            
            self.streak_badge = StreakBadge(self.voice_trainer.session_manager)
            streak_layout.addWidget(self.streak_badge)
            
            self.sidebar_layout.addWidget(streak_container)
        
        # Add profile switcher if profile manager available
        if hasattr(self.voice_trainer, 'profile_manager'):
            profile_container = QWidget()
            profile_container.setStyleSheet("background: transparent;")
            profile_layout = QVBoxLayout(profile_container)
            profile_layout.setContentsMargins(16, 0, 16, 8)
            profile_layout.setSpacing(0)
            
            self.profile_switcher = ProfileDropdown(self.voice_trainer.profile_manager)
            self.profile_switcher.profile_changed.connect(self.handle_profile_switch)
            profile_layout.addWidget(self.profile_switcher)
            
            self.sidebar_layout.addWidget(profile_container)
        
        # Support/Donation section (optimized)
        support_container = QWidget()
        support_container.setStyleSheet("background: transparent; border: none;")
        support_container_layout = QVBoxLayout(support_container)
        support_container_layout.setContentsMargins(12, 4, 12, 8)
        support_container_layout.setSpacing(0)
        
        support_widget = QWidget()
        support_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(111, 162, 200, 0.12),
                    stop:1 rgba(232, 151, 189, 0.12));
                border-radius: 10px;
                border: none;
            }
        """)
        support_layout = QVBoxLayout(support_widget)
        support_layout.setContentsMargins(12, 8, 12, 8)
        support_layout.setSpacing(5)
        
        # Ko-Fi emoji + title
        kofi_header = QLabel("☕ Support Aria")
        kofi_header.setStyleSheet("""
            color: rgba(255, 255, 255, 0.95);
            font-size: 13px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)
        support_layout.addWidget(kofi_header)
        
        # Message (shorter)
        support_msg = QLabel("Help support development & future features!")
        support_msg.setWordWrap(True)
        support_msg.setStyleSheet("""
            color: rgba(255, 255, 255, 0.65);
            font-size: 11px;
            background: transparent;
            border: none;
        """)
        support_layout.addWidget(support_msg)
        
        # Buttons container
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(6)
        
        # Ko-Fi button
        kofi_btn = QPushButton("💝 Donate")
        kofi_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF5E5B,
                    stop:1 #FF9B71);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF7875,
                    stop:1 #FFB088);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #E54D4A,
                    stop:1 #E88A60);
            }
        """)
        kofi_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        kofi_btn.clicked.connect(self.open_kofi)
        buttons_layout.addWidget(kofi_btn, 1)
        
        # Supporters button
        supporters_btn = QPushButton("🏆")
        supporters_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.25);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.08);
            }
        """)
        supporters_btn.setToolTip("View Supporters")
        supporters_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        supporters_btn.clicked.connect(self.show_supporters)
        buttons_layout.addWidget(supporters_btn, 0)
        
        support_layout.addLayout(buttons_layout)
        support_container_layout.addWidget(support_widget)
        
        self.sidebar_layout.addWidget(support_container)
        
        # Help section at bottom - aligned with nav buttons
        help_widget = QWidget()
        help_widget.setStyleSheet("background: transparent;")
        help_layout = QHBoxLayout(help_widget)
        help_layout.setContentsMargins(32, 8, 32, 24)
        help_layout.setSpacing(0)
        
        help_label = QLabel("Need help? Press ?")
        help_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.6);
            font-size: 13px;
            font-weight: 500;
            background: transparent;
        """)
        help_label.setCursor(Qt.CursorShape.PointingHandCursor)
        help_label.mousePressEvent = lambda e: self.show_shortcuts_dialog()
        
        help_layout.addWidget(help_label)
        help_layout.addStretch()
        
        self.sidebar_layout.addWidget(help_widget)

        # Content stack
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)

        # Initialize screens
        self.training_screen = TrainingScreen(self.voice_trainer)
        self.exercises_screen = ExercisesScreen(self.voice_trainer)
        self.analysis_screen = AudioAnalysisScreen(self.voice_trainer)
        self.progress_screen = ProgressScreen(self.voice_trainer)
        self.health_screen = HealthDashboardScreen(self.voice_trainer)
        self.journey_screen = SnapshotComparisonScreen(self.voice_trainer)
        self.settings_screen = SettingsScreen(self.voice_trainer)

        self.content_stack.addWidget(self.training_screen)
        self.content_stack.addWidget(self.exercises_screen)
        self.content_stack.addWidget(self.analysis_screen)
        self.content_stack.addWidget(self.progress_screen)
        self.content_stack.addWidget(self.health_screen)
        self.content_stack.addWidget(self.journey_screen)
        self.content_stack.addWidget(self.settings_screen)

        # Map screens
        self.screen_map = {
            "live": 0,
            "exercises": 1,
            "analysis": 2,
            "progress": 3,
            "health": 4,
            "journey": 5,
            "settings": 6
        }

    def check_onboarding(self):
        """Check if onboarding is needed"""
        try:
            if self.voice_trainer.is_onboarding_needed():
                self.show_onboarding()
            else:
                self.navigate_to("live")
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AriaMainWindow.check_onboarding")
            self.navigate_to("live")

    def show_onboarding(self):
        """Show onboarding screen"""
        try:
            onboarding = OnboardingScreen(self.voice_trainer)
            onboarding.onboarding_completed.connect(self.on_onboarding_completed)
            onboarding.onboarding_cancelled.connect(self.on_onboarding_cancelled)

            # Replace content stack temporarily
            self.sidebar.hide()
            self.content_stack.hide()

            temp_widget = QWidget()
            temp_layout = QVBoxLayout(temp_widget)
            temp_layout.setContentsMargins(0, 0, 0, 0)
            temp_layout.addWidget(onboarding)

            self.setCentralWidget(temp_widget)
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AriaMainWindow.show_onboarding")
            self.navigate_to("live")

    def on_onboarding_completed(self, config):
        """Handle onboarding completion"""
        try:
            self.voice_trainer.config_manager.update_config(config)
            self.voice_trainer.config_manager.mark_onboarding_complete()
            
            # Create default profiles based on user's onboarding choices
            if hasattr(self.voice_trainer, 'profile_manager'):
                if not self.voice_trainer.profile_manager.profiles:
                    self.voice_trainer.profile_manager._create_default_profiles(config)
            
            self.restore_main_ui()
            self.navigate_to("live")
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AriaMainWindow.on_onboarding_completed")
            self.restore_main_ui()

    def on_onboarding_cancelled(self):
        """Handle onboarding cancellation"""
        try:
            self.voice_trainer.config_manager.mark_onboarding_complete()
            self.restore_main_ui()
            self.navigate_to("live")
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AriaMainWindow.on_onboarding_cancelled")
            self.restore_main_ui()

    def restore_main_ui(self):
        """Restore main UI after onboarding"""
        self.init_ui()
        self.sidebar.show()
        self.content_stack.show()

    def open_kofi(self):
        """Open Ko-Fi donation page in default browser"""
        kofi_url = "https://ko-fi.com/hopefulopal"
        QDesktopServices.openUrl(QUrl(kofi_url))
    
    def show_supporters(self):
        """Show supporters leaderboard dialog"""
        dialog = SupportersDialog(self)
        dialog.exec()
    
    def navigate_to(self, screen_key):
        """Navigate to a specific screen"""
        if screen_key in self.screen_map:
            # Cleanup previous screen if needed
            if hasattr(self, 'current_screen') and self.current_screen:
                prev_widget = self.content_stack.widget(self.screen_map.get(self.current_screen, 0))
                if hasattr(prev_widget, 'cleanup'):
                    prev_widget.cleanup()
            
            # Update navigation button states
            for key, btn in self.nav_buttons.items():
                btn.set_active(key == screen_key)

            # Switch screen
            self.content_stack.setCurrentIndex(self.screen_map[screen_key])
            self.current_screen = screen_key
            
            # Refresh streak badge
            if hasattr(self, 'streak_badge'):
                self.streak_badge.refresh()

    def keyPressEvent(self, event: QKeyEvent):
        """Handle global keyboard shortcuts"""
        key = event.key()
        modifiers = event.modifiers()
        ctrl_or_cmd = get_modifier_qt()

        # Global shortcuts
        if key == Qt.Key.Key_Question:
            # ? - Show shortcuts help
            self.show_shortcuts_dialog()
            event.accept()
            return

        if key == Qt.Key.Key_Escape:
            # Esc - Go back / Cancel action
            # Delegate to current screen first
            current_widget = self.content_stack.currentWidget()
            if hasattr(current_widget, 'handle_escape_key'):
                current_widget.handle_escape_key()
            event.accept()
            return

        if modifiers & ctrl_or_cmd:
            if key == Qt.Key.Key_K:
                # Ctrl/Cmd+K - Open search (placeholder)
                ToastNotification.show_toast(self, "Search coming soon", icon="⌨️")
                event.accept()
                return
            elif key == Qt.Key.Key_E:
                # Ctrl/Cmd+E - Go to exercises
                self.navigate_to("exercises")
                ToastNotification.show_toast(self, "Exercises", icon="⌨️")
                event.accept()
                return
            elif key == Qt.Key.Key_S:
                # Ctrl/Cmd+S - Go to settings
                self.navigate_to("settings")
                ToastNotification.show_toast(self, "Settings", icon="⌨️")
                event.accept()
                return

        # Delegate to current screen for screen-specific shortcuts
        current_widget = self.content_stack.currentWidget()
        if hasattr(current_widget, 'keyPressEvent'):
            current_widget.keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def show_shortcuts_dialog(self):
        """Show keyboard shortcuts help dialog"""
        try:
            dialog = ShortcutsDialog(self)
            dialog.exec()
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AriaMainWindow.show_shortcuts_dialog")

    def handle_profile_switch(self, profile_id):
        """Handle profile switching"""
        from PyQt6.QtWidgets import QMessageBox
        
        try:
            # Check if training is active
            if hasattr(self.voice_trainer, 'training_controller'):
                if self.voice_trainer.training_controller.is_training_active:
                    # Show confirmation dialog
                    reply = QMessageBox.question(
                        self,
                        "Switch Profile?",
                        "Switching profiles will stop the current training session. Continue?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.No:
                        return
                    
                    # Stop training
                    self.voice_trainer.training_controller.stop_live_training()
            
            # Switch profile
            if hasattr(self.voice_trainer, 'profile_manager'):
                success = self.voice_trainer.profile_manager.switch_profile(profile_id)
                
                if success:
                    # Reload config from new profile
                    self.reload_profile_config()
                    
                    # Refresh profile switcher - force update after profile switch
                    if hasattr(self, 'profile_switcher'):
                        from PyQt6.QtCore import QTimer
                        # Delay refresh to ensure profile is fully switched
                        QTimer.singleShot(50, self.profile_switcher.refresh)
                        QTimer.singleShot(100, self.profile_switcher.update)
                    
                    # Refresh all screens
                    self.refresh_all_screens()
                    
                    # Show success message
                    profile = self.voice_trainer.profile_manager.get_current()
                    if profile:
                        ToastNotification.show_toast(self, f"Switched to {profile.name}", icon="✅")
                else:
                    ToastNotification.show_toast(self, "Failed to switch profile", icon="❌", error=True)
                    
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AriaMainWindow.handle_profile_switch")
            import traceback
            print(f"Profile switch error: {e}")
            print(traceback.format_exc())
            ToastNotification.show_toast(self, f"Error: {str(e)}", icon="❌", error=True)
    
    def reload_profile_config(self):
        """Reload configuration from current profile"""
        try:
            if hasattr(self.voice_trainer, 'profile_manager') and hasattr(self.voice_trainer, 'config_manager'):
                profile = self.voice_trainer.profile_manager.get_current()
                if profile:
                    # Update config file path to profile-specific config
                    config_path = self.voice_trainer.profile_manager.get_profile_config_path()
                    self.voice_trainer.config_manager.config_file = config_path
                    self.voice_trainer.config_manager.load_config()
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AriaMainWindow.reload_profile_config")
    
    def refresh_all_screens(self):
        """Refresh all screens to reflect new profile config"""
        try:
            # Refresh training screen
            if hasattr(self.training_screen, 'refresh'):
                self.training_screen.refresh()
            
            # Refresh progress screen
            if hasattr(self.progress_screen, 'refresh'):
                self.progress_screen.refresh()
            
            # Refresh settings screen
            if hasattr(self.settings_screen, 'refresh'):
                self.settings_screen.refresh()
                
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AriaMainWindow.refresh_all_screens")
    
    def show_random_motivational_message(self):
        """Show random motivational message on startup"""
        ToastNotification.show_toast(
            self,
            SecretMessageToast.get_random_message(),
            icon="💫",
            duration=3500
        )
    
    def handle_logo_click(self):
        """Handle logo clicks for easter egg ✨"""
        if self.logo_click_detector.click():
            # Show secret about dialog
            dialog = SecretAboutDialog(self)
            dialog.exec()
    
    def keyPressEvent(self, event):
        """Handle key presses for Konami code 🎮"""
        if self.konami_detector.key_pressed(event.key()):
            # Konami code activated!
            dialog = DeveloperModeDialog(self)
            dialog.exec()
            # Show toast
            ToastNotification.show_toast(
                self,
                "🎮 Achievement Unlocked: The Konami Chronicles",
                icon="🏆",
                duration=4000
            )
        super().keyPressEvent(event)

    def eventFilter(self, obj, event):
        """Filter events to handle window state changes"""
        if obj == self and event.type() == event.Type.WindowStateChange:
            self.update_sidebar_text_visibility()
        elif obj == self and event.type() == event.Type.Resize:
            self.update_sidebar_text_visibility()
        return super().eventFilter(obj, event)
    
    def update_sidebar_text_visibility(self):
        """Show/hide sidebar text based on window state"""
        if hasattr(self, 'sidebar'):
            is_fullscreen = self.isMaximized() or self.isFullScreen()
            
            if hasattr(self.sidebar, 'sidebar_title'):
                self.sidebar.sidebar_title.setVisible(is_fullscreen)
            if hasattr(self.sidebar, 'sidebar_version'):
                self.sidebar.sidebar_version.setVisible(is_fullscreen)

    def closeEvent(self, event):
        """Handle application closing"""
        try:
            # Stop any active training
            if hasattr(self.training_screen, 'stop_training'):
                self.training_screen.stop_training()

            # Cleanup voice trainer
            if hasattr(self.voice_trainer, 'cleanup'):
                self.voice_trainer.cleanup()

            event.accept()
        except Exception as e:
            try:
                from utils.error_handler import log_error
                log_error(e, "AriaMainWindow.closeEvent")
            except:
                pass
            event.accept()


def launch_gui(voice_trainer):
    """Launch the GUI application"""
    app = QApplication(sys.argv)
    window = AriaMainWindow(voice_trainer)
    window.show()
    return app.exec()
