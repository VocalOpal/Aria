"""
Display Settings
UI preferences and visualization options
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel,  # type: ignore
                            QSpinBox, QCheckBox)
from .shared_utils import BaseSettingsTab, SettingsWidgetFactory


class DisplaySettings(BaseSettingsTab):
    """Display and UI configuration settings"""

    def __init__(self, config_manager, voice_trainer):
        super().__init__(config_manager, voice_trainer)
        self.smooth_display_check = None
        self.display_range_spin = None
        self.exact_numbers_check = None

    def create_tab_widget(self) -> QWidget:
        """Create the display settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Display options
        display_group = SettingsWidgetFactory.create_group_box("Display Options")
        display_layout = QGridLayout()

        # Smooth display
        self.smooth_display_check = QCheckBox("Enable Smooth Display")
        self.smooth_display_check.setChecked(True)
        self.smooth_display_check.stateChanged.connect(self.on_setting_changed)
        display_layout.addWidget(self.smooth_display_check, 0, 0, 1, 2)

        # Display range size
        self.display_range_spin = QSpinBox()
        self.display_range_spin.setRange(5, 50)
        self.display_range_spin.setValue(10)
        self.display_range_spin.valueChanged.connect(self.on_setting_changed)
        self.create_grid_row(display_layout, 1, "Display Range Size (Hz):", self.display_range_spin,
                           "Size of pitch display range")

        # Exact numbers mode
        self.exact_numbers_check = QCheckBox("Show Exact Numbers")
        self.exact_numbers_check.setChecked(False)
        self.exact_numbers_check.stateChanged.connect(self.on_setting_changed)
        display_layout.addWidget(self.exact_numbers_check, 2, 0, 1, 2)
        display_layout.addWidget(QLabel("Show precise Hz vs ranges"), 2, 2)

        display_group.setLayout(display_layout)
        layout.addWidget(display_group)

        # Display help info
        help_group = SettingsWidgetFactory.create_group_box("Display Help")
        help_layout = QVBoxLayout()

        help_text = SettingsWidgetFactory.create_info_text_edit(
            "Display Settings Guide:\n\n"
            "• Smooth Display: Reduces visual jitter for smoother feedback\n"
            "• Display Range Size: Controls how much frequency range is shown\n"
            "• Exact Numbers: Toggle between precise Hz values and friendly ranges\n\n"
            "Recommendations:\n"
            "• Keep smooth display enabled for better visual experience\n"
            "• Smaller display range (5-10 Hz) for precise training\n"
            "• Larger display range (15-30 Hz) for broader overview\n"
            "• Enable exact numbers if you prefer technical precision"
        )
        help_layout.addWidget(help_text)

        help_group.setLayout(help_layout)
        layout.addWidget(help_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def load_settings(self):
        """Load current settings into UI controls"""
        # Display settings
        self.smooth_display_check.setChecked(self.get_config_value('smooth_display_enabled', True))
        self.display_range_spin.setValue(self.get_config_value('display_range_size', 10))
        self.exact_numbers_check.setChecked(self.get_config_value('exact_numbers_mode', False))

    def save_settings(self) -> dict:
        """Return current settings as dict"""
        return {
            'smooth_display_enabled': self.smooth_display_check.isChecked(),
            'display_range_size': self.display_range_spin.value(),
            'exact_numbers_mode': self.exact_numbers_check.isChecked()
        }

    def validate_settings(self) -> tuple[bool, str]:
        """Validate current settings"""
        # All display settings are within acceptable ranges by widget constraints
        return True, ""

    def is_smooth_display_enabled(self) -> bool:
        """Check if smooth display is enabled"""
        return self.smooth_display_check.isChecked()

    def get_display_range_size(self) -> int:
        """Get current display range size"""
        return self.display_range_spin.value()

    def is_exact_numbers_mode(self) -> bool:
        """Check if exact numbers mode is enabled"""
        return self.exact_numbers_check.isChecked()