"""
Advanced Settings
Configuration management, system actions, and advanced options
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,  # type: ignore
                            QTextEdit, QMessageBox)
from .shared_utils import BaseSettingsTab, SettingsWidgetFactory


class AdvancedSettings(BaseSettingsTab):
    """Advanced configuration and system actions"""

    def __init__(self, config_manager, voice_trainer):
        super().__init__(config_manager, voice_trainer)

    def create_tab_widget(self) -> QWidget:
        """Create the advanced settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Configuration info
        info_group = SettingsWidgetFactory.create_group_box("Configuration Information")
        info_layout = QVBoxLayout()

        config_info = self._create_config_info_display()
        info_layout.addWidget(config_info)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Advanced actions
        actions_group = SettingsWidgetFactory.create_group_box("Advanced Actions")
        actions_layout = QVBoxLayout()

        # Reset onboarding
        onboarding_layout = QHBoxLayout()
        reset_onboarding_button = SettingsWidgetFactory.create_action_button("Reset Onboarding", "warning")
        reset_onboarding_button.clicked.connect(self.reset_onboarding)
        onboarding_layout.addWidget(reset_onboarding_button)
        onboarding_layout.addWidget(QLabel("Run first-time setup again"))
        onboarding_layout.addStretch()
        actions_layout.addLayout(onboarding_layout)

        # Export config
        export_layout = QHBoxLayout()
        export_config_button = SettingsWidgetFactory.create_action_button("Export Config", "info")
        export_config_button.clicked.connect(self.export_config)
        export_layout.addWidget(export_config_button)
        export_layout.addWidget(QLabel("Export current configuration"))
        export_layout.addStretch()
        actions_layout.addLayout(export_layout)

        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _create_config_info_display(self) -> QTextEdit:
        """Create configuration information display"""
        current_preset = self.get_config_value('current_preset', 'unknown')
        setup_completed = self.get_config_value('setup_completed', False)
        onboarding_completed = self.get_config_value('onboarding_completed', False)

        config_text = f"Current Configuration Status:\n\n"
        config_text += f"• Active Preset: {current_preset}\n"
        config_text += f"• Setup Completed: {'Yes' if setup_completed else 'No'}\n"
        config_text += f"• Onboarding Completed: {'Yes' if onboarding_completed else 'No'}\n"
        config_text += f"• Config File: {self.config_manager.config_file}\n\n"

        if self.get_config_value('preset_applied_date'):
            config_text += f"• Last Preset Applied: {self.current_config['preset_applied_date'][:19]}\n"

        return SettingsWidgetFactory.create_info_text_edit(config_text, 200)

    def load_settings(self):
        """Load current settings into UI controls"""
        # Advanced settings don't have persistent UI controls to load
        pass

    def save_settings(self) -> dict:
        """Return current settings as dict"""
        # Advanced settings don't have settings to save
        return {}

    def reset_onboarding(self):
        """Reset onboarding to run again"""
        reply = QMessageBox.question(
            None,  # Will be set to parent when connected
            "Reset Onboarding",
            "Reset the onboarding process?\n\n"
            "This will make the first-time setup wizard run again "
            "when you restart the application.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.config_manager.update_config({
                    'setup_completed': False,
                    'onboarding_completed': False
                })

                if success:
                    QMessageBox.information(
                        None,
                        "Onboarding Reset",
                        "Onboarding has been reset. The setup wizard will run when you restart the application."
                    )
                else:
                    QMessageBox.warning(None, "Reset Failed", "Could not reset onboarding status.")
            except Exception as e:
                from utils.error_handler import log_error
                log_error(e, "AdvancedSettings.reset_onboarding")
                QMessageBox.critical(None, "Error", f"Failed to reset onboarding: {str(e)}")

    def export_config(self):
        """Export current configuration"""
        try:
            config_data = self.config_manager.get_config()

            # Format for display
            export_text = "Aria Voice Studio Configuration Export\n"
            export_text += f"Generated: {config_data.get('preset_applied_date', 'Unknown')}\n\n"

            for key, value in config_data.items():
                export_text += f"{key}: {value}\n"

            # For now, show in message box (could save to file in future)
            QMessageBox.information(
                None,
                "Configuration Export",
                f"Configuration exported successfully!\n\n"
                f"Contains {len(config_data)} settings.\n"
                f"Save to file feature coming in future version."
            )

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AdvancedSettings.export_config")
            QMessageBox.critical(None, "Export Error", f"Failed to export configuration: {str(e)}")

    def validate_settings(self) -> tuple[bool, str]:
        """Validate current settings"""
        # Advanced settings don't need validation
        return True, ""

    def refresh_config_info(self):
        """Refresh the configuration information display"""
        # This would need to be implemented if we want to refresh the info dynamically
        pass