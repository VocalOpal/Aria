"""
Training Settings
Alert behavior, analysis modes, and session management
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel,  # type: ignore
                            QDoubleSpinBox, QSpinBox, QComboBox)
from .shared_utils import BaseSettingsTab, SettingsWidgetFactory


class TrainingSettings(BaseSettingsTab):
    """Training behavior and session settings"""

    def __init__(self, config_manager, voice_trainer):
        super().__init__(config_manager, voice_trainer)
        self.dip_tolerance_spin = None
        self.alert_warning_spin = None
        self.high_pitch_spin = None
        self.analysis_mode_combo = None
        self.analysis_description = None
        self.auto_save_spin = None
        self.session_duration_spin = None
        self.max_duration_spin = None

    def create_tab_widget(self) -> QWidget:
        """Create the training settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Alert settings
        alert_group = SettingsWidgetFactory.create_group_box("Alert & Warning Settings")
        alert_layout = QGridLayout()

        # Dip tolerance
        self.dip_tolerance_spin = QDoubleSpinBox()
        self.dip_tolerance_spin.setRange(1.0, 15.0)
        self.dip_tolerance_spin.setSingleStep(0.5)
        self.dip_tolerance_spin.setDecimals(1)
        self.dip_tolerance_spin.setValue(6.0)
        self.dip_tolerance_spin.valueChanged.connect(self.on_setting_changed)
        self.create_grid_row(alert_layout, 0, "Dip Tolerance (seconds):", self.dip_tolerance_spin,
                           "Time below goal before alert")

        # Alert warning time
        self.alert_warning_spin = QDoubleSpinBox()
        self.alert_warning_spin.setRange(1.0, 10.0)
        self.alert_warning_spin.setSingleStep(0.5)
        self.alert_warning_spin.setDecimals(1)
        self.alert_warning_spin.setValue(5.0)
        self.alert_warning_spin.valueChanged.connect(self.on_setting_changed)
        self.create_grid_row(alert_layout, 1, "Alert Warning Time (seconds):", self.alert_warning_spin,
                           "Warning time before beep alert")

        # High pitch threshold
        self.high_pitch_spin = QSpinBox()
        self.high_pitch_spin.setRange(250, 500)
        self.high_pitch_spin.setValue(400)
        self.high_pitch_spin.valueChanged.connect(self.on_setting_changed)
        self.create_grid_row(alert_layout, 2, "High Pitch Threshold (Hz):", self.high_pitch_spin,
                           "Alert when pitch exceeds this")

        alert_group.setLayout(alert_layout)
        layout.addWidget(alert_group)

        # Analysis mode settings
        analysis_group = SettingsWidgetFactory.create_group_box("Voice Analysis Mode")
        analysis_layout = QGridLayout()

        self.analysis_mode_combo = QComboBox()
        self.analysis_mode_combo.addItems(["Strict", "Balanced", "Looser"])
        self.analysis_mode_combo.setCurrentText("Balanced")
        self.analysis_mode_combo.currentTextChanged.connect(self.on_setting_changed)
        self.analysis_mode_combo.currentTextChanged.connect(self.update_analysis_description)
        self.create_grid_row(analysis_layout, 0, "Analysis Mode:", self.analysis_mode_combo)

        # Analysis mode description
        self.analysis_description = SettingsWidgetFactory.create_info_label(
            "Natural feel - good balance of accuracy & smoothness", "secondary")
        analysis_layout.addWidget(self.analysis_description, 1, 0, 1, 3)

        # Mode details
        mode_details = SettingsWidgetFactory.create_info_label("""
<b>Strict:</b> Precise analysis with exact pitch tracking<br>
<b>Balanced:</b> Natural feel with good accuracy and smoothness<br>
<b>Looser:</b> Forgiving analysis that's smooth and encouraging
        """, "secondary")
        analysis_layout.addWidget(mode_details, 2, 0, 1, 3)

        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)

        # Session settings
        session_group = SettingsWidgetFactory.create_group_box("Session Management")
        session_layout = QGridLayout()

        # Auto-save interval
        self.auto_save_spin = QSpinBox()
        self.auto_save_spin.setRange(10, 300)
        self.auto_save_spin.setValue(30)
        self.auto_save_spin.valueChanged.connect(self.on_setting_changed)
        self.create_grid_row(session_layout, 0, "Auto-save Interval (seconds):", self.auto_save_spin)

        # Session duration target
        self.session_duration_spin = QSpinBox()
        self.session_duration_spin.setRange(5, 120)
        self.session_duration_spin.setValue(15)
        self.session_duration_spin.valueChanged.connect(self.on_setting_changed)
        self.create_grid_row(session_layout, 1, "Target Session Duration (minutes):", self.session_duration_spin)

        # Max recommended duration
        self.max_duration_spin = QSpinBox()
        self.max_duration_spin.setRange(15, 180)
        self.max_duration_spin.setValue(45)
        self.max_duration_spin.valueChanged.connect(self.on_setting_changed)
        self.create_grid_row(session_layout, 2, "Max Recommended Duration (minutes):", self.max_duration_spin)

        session_group.setLayout(session_layout)
        layout.addWidget(session_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def load_settings(self):
        """Load current settings into UI controls"""
        # Training settings
        self.dip_tolerance_spin.setValue(self.get_config_value('dip_tolerance_duration', 6.0))
        self.alert_warning_spin.setValue(self.get_config_value('alert_warning_time', 5.0))
        self.high_pitch_spin.setValue(self.get_config_value('high_pitch_threshold', 400))
        self.auto_save_spin.setValue(self.get_config_value('auto_save_interval', 30))
        self.session_duration_spin.setValue(self.get_config_value('session_duration_target', 900) // 60)
        self.max_duration_spin.setValue(self.get_config_value('max_recommended_duration', 2700) // 60)

        # Analysis mode
        analysis_mode = self.get_config_value('analysis_mode', 'Balanced')
        self.analysis_mode_combo.setCurrentText(analysis_mode)
        self.update_analysis_description(analysis_mode)

    def save_settings(self) -> dict:
        """Return current settings as dict"""
        return {
            'dip_tolerance_duration': self.dip_tolerance_spin.value(),
            'alert_warning_time': self.alert_warning_spin.value(),
            'high_pitch_threshold': self.high_pitch_spin.value(),
            'auto_save_interval': self.auto_save_spin.value(),
            'session_duration_target': self.session_duration_spin.value() * 60,
            'max_recommended_duration': self.max_duration_spin.value() * 60,
            'analysis_mode': self.analysis_mode_combo.currentText()
        }

    def update_analysis_description(self, mode: str):
        """Update the analysis mode description text"""
        descriptions = {
            "Strict": "Precise analysis - exact pitch tracking",
            "Balanced": "Natural feel - good balance of accuracy & smoothness",
            "Looser": "Forgiving analysis - smooth and encouraging"
        }
        self.analysis_description.setText(descriptions.get(mode, descriptions["Balanced"]))

    def validate_settings(self) -> tuple[bool, str]:
        """Validate current settings"""
        # Check that session duration doesn't exceed max duration
        target_duration = self.session_duration_spin.value()
        max_duration = self.max_duration_spin.value()

        if target_duration > max_duration:
            return False, "Target session duration cannot exceed maximum recommended duration"

        # Check reasonable alert timing
        dip_tolerance = self.dip_tolerance_spin.value()
        alert_warning = self.alert_warning_spin.value()

        if alert_warning >= dip_tolerance:
            return False, "Alert warning time should be less than dip tolerance"

        return True, ""