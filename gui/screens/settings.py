from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,  # type: ignore
                            QLabel, QTabWidget, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal  # type: ignore
from PyQt6.QtGui import QFont  # type: ignore
from ..design_system import AriaDesignSystem
from ..settings.shared_utils import SettingsStyler, SettingsWidgetFactory
from ..settings.voice_goals_settings import VoiceGoalsSettings
from ..settings.training_settings import TrainingSettings
from ..settings.audio_settings import AudioSettings
from ..settings.display_settings import DisplaySettings
from ..settings.advanced_settings import AdvancedSettings


class SettingsScreen(QWidget):
    """Settings and configuration screen"""

    back_requested = pyqtSignal()

    def __init__(self, voice_trainer):
        super().__init__()
        self.voice_trainer = voice_trainer
        self.config_manager = voice_trainer.config_manager
        self.current_config = self.config_manager.get_config()
        self.settings_changed = False

        # Initialize settings modules
        self.voice_goals = VoiceGoalsSettings(self.config_manager, voice_trainer)
        self.training_settings = TrainingSettings(self.config_manager, voice_trainer)
        self.audio_settings = AudioSettings(self.config_manager, voice_trainer)
        self.display_settings = DisplaySettings(self.config_manager, voice_trainer)
        self.advanced_settings = AdvancedSettings(self.config_manager, voice_trainer)

        # Connect settings change callbacks
        for settings_module in [self.voice_goals, self.training_settings, self.audio_settings,
                               self.display_settings, self.advanced_settings]:
            settings_module.set_settings_changed_callback(self.on_setting_changed)

        self.init_ui()
        self.load_current_settings()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Header card
        header_frame = self._create_header()
        layout.addWidget(header_frame)

        # Create tabs for different settings categories
        tab_widget = self._create_tab_widget()
        layout.addWidget(tab_widget)

        # Save/Reset buttons
        button_frame = self._create_action_buttons()
        layout.addWidget(button_frame)

        # Apply overall styling
        self.setStyleSheet(SettingsStyler.apply_main_settings_style() + f"""
            QGroupBox {{
                font-size: {AriaDesignSystem.FONTS['md']}pt;
                font-weight: 600;
                color: {AriaDesignSystem.COLORS['text_primary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: {AriaDesignSystem.RADIUS['md']};
                margin: 8px 0px;
                padding-top: 12px;
                background-color: {AriaDesignSystem.COLORS['bg_secondary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                background-color: {AriaDesignSystem.COLORS['bg_secondary']};
            }}
        """)

        self.setLayout(layout)

    def _create_header(self) -> QFrame:
        """Create the header section with back button and title"""
        header_frame = QFrame()
        header_frame.setProperty("style", "card")
        header_frame.setStyleSheet(SettingsStyler.apply_card_style())
        header_layout = QHBoxLayout(header_frame)
        header_layout.setSpacing(16)

        back_button = SettingsWidgetFactory.create_action_button("← Back to Menu", "secondary")
        back_button.clicked.connect(self.handle_back_button)
        header_layout.addWidget(back_button)

        # Title section
        title_container = QVBoxLayout()
        title = QLabel("Settings & Configuration")
        title.setFont(QFont(AriaDesignSystem.FONTS['family_primary'], AriaDesignSystem.FONTS['xxl'], QFont.Weight.Bold))
        title.setProperty("style", "heading")
        title.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['xxl']}pt;
                font-weight: 600;
                background: transparent;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_container.addWidget(title)

        subtitle = QLabel("Customize your voice training experience")
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_secondary']};
                font-size: {AriaDesignSystem.FONTS['md']}pt;
                background: transparent;
                margin-top: 4px;
            }}
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_container.addWidget(subtitle)

        header_layout.addLayout(title_container)
        header_layout.addStretch()

        return header_frame

    def _create_tab_widget(self) -> QTabWidget:
        """Create the main tab widget with all settings categories"""
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(SettingsStyler.apply_tab_widget_style())

        # Add all settings tabs
        tab_widget.addTab(self.voice_goals.create_tab_widget(), "Voice Goals")
        tab_widget.addTab(self.training_settings.create_tab_widget(), "Training Settings")
        tab_widget.addTab(self.audio_settings.create_tab_widget(), "Audio Settings")
        tab_widget.addTab(self.display_settings.create_tab_widget(), "Display Settings")
        tab_widget.addTab(self.advanced_settings.create_tab_widget(), "Advanced")

        return tab_widget

    def _create_action_buttons(self) -> QFrame:
        """Create the save/reset action buttons"""
        button_frame = QFrame()
        button_frame.setProperty("style", "card")
        button_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AriaDesignSystem.COLORS['bg_secondary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: {AriaDesignSystem.RADIUS['lg']};
                padding: 20px;
            }}
        """)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(16)

        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        save_button.setProperty("style", "success")
        save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaDesignSystem.COLORS['success']};
                border: none;
                border-radius: {AriaDesignSystem.RADIUS['md']};
                padding: 12px 24px;
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['md']}pt;
                font-weight: 600;
                min-height: 40px;
                min-width: 140px;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
            QPushButton:pressed {{
                background-color: #047857;
            }}
        """)

        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.reset_to_defaults)
        reset_button.setProperty("style", "danger")
        reset_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaDesignSystem.COLORS['error']};
                border: none;
                border-radius: {AriaDesignSystem.RADIUS['md']};
                padding: 12px 24px;
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['md']}pt;
                font-weight: 600;
                min-height: 40px;
                min-width: 140px;
            }}
            QPushButton:hover {{
                background-color: #dc2626;
            }}
            QPushButton:pressed {{
                background-color: #b91c1c;
            }}
        """)

        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(reset_button)

        return button_frame

    def load_current_settings(self):
        """Load current settings into all UI controls"""
        # Load settings in each module
        self.voice_goals.load_settings()
        self.training_settings.load_settings()
        self.audio_settings.load_settings()
        self.display_settings.load_settings()
        self.advanced_settings.load_settings()

    def on_setting_changed(self):
        """Mark that settings have been changed"""
        self.settings_changed = True

    def save_settings(self):
        """Save current settings to configuration"""
        try:
            # Validate all settings first
            validation_errors = []
            for module_name, module in [
                ("Voice Goals", self.voice_goals),
                ("Training Settings", self.training_settings),
                ("Audio Settings", self.audio_settings),
                ("Display Settings", self.display_settings),
                ("Advanced Settings", self.advanced_settings)
            ]:
                is_valid, error_msg = module.validate_settings()
                if not is_valid:
                    validation_errors.append(f"{module_name}: {error_msg}")

            if validation_errors:
                QMessageBox.warning(self, "Validation Error",
                                  "Please fix the following errors:\n\n" + "\n".join(validation_errors))
                return

            # Collect all settings from modules
            new_config = {}
            new_config.update(self.voice_goals.save_settings())
            new_config.update(self.training_settings.save_settings())
            new_config.update(self.audio_settings.save_settings())
            new_config.update(self.display_settings.save_settings())
            new_config.update(self.advanced_settings.save_settings())

            # Apply preset if changed
            preset_key = self.voice_goals.get_selected_preset()
            if preset_key != 'custom':
                if self.config_manager.apply_preset(preset_key):
                    QMessageBox.information(self, "Settings Saved", f"Preset '{preset_key}' applied successfully!")
                else:
                    QMessageBox.warning(self, "Preset Error", "Could not apply preset, but other settings were saved.")

            # Update configuration
            success = self.config_manager.update_config(new_config)

            if success:
                self.settings_changed = False
                self.current_config = self.config_manager.get_config()
                QMessageBox.information(self, "Settings Saved", "All settings have been saved successfully!")
            else:
                QMessageBox.warning(self, "Save Error", "Some settings could not be saved. Please try again.")

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "SettingsScreen.save_settings")
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")

    def reset_to_defaults(self):
        """Reset all settings to defaults with confirmation"""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?\n\n"
            "This will:\n"
            "• Reset all training parameters\n"
            "• Reset audio and display settings\n"
            "• Keep your onboarding completion status\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.config_manager.reset_to_defaults()
                if success:
                    self.current_config = self.config_manager.get_config()
                    self.load_current_settings()
                    self.settings_changed = False
                    QMessageBox.information(self, "Reset Complete", "All settings have been reset to defaults.")
                else:
                    QMessageBox.warning(self, "Reset Failed", "Could not reset settings. Please try again.")
            except Exception as e:
                from utils.error_handler import log_error
                log_error(e, "SettingsScreen.reset_to_defaults")
                QMessageBox.critical(self, "Error", f"Failed to reset settings: {str(e)}")

    def handle_back_button(self):
        """Handle back button with unsaved changes warning"""
        if self.settings_changed:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved settings changes.\n\n"
                "Do you want to save them before leaving?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )

            if reply == QMessageBox.StandardButton.Save:
                self.save_settings()
                if not self.settings_changed:  # Only leave if save was successful
                    self.back_requested.emit()
            elif reply == QMessageBox.StandardButton.Discard:
                self.back_requested.emit()
            # Cancel does nothing, stays on settings page
        else:
            self.back_requested.emit()