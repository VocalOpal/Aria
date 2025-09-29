"""
Audio Settings
Microphone sensitivity, noise thresholds, and voice detection parameters
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel,  # type: ignore
                            QDoubleSpinBox, QSlider, QTextEdit)
from PyQt6.QtCore import Qt  # type: ignore
from .shared_utils import BaseSettingsTab, SettingsWidgetFactory


class AudioSettings(BaseSettingsTab):
    """Audio processing and sensitivity settings"""

    def __init__(self, config_manager, voice_trainer):
        super().__init__(config_manager, voice_trainer)
        self.sensitivity_slider = None
        self.sensitivity_label = None
        self.vad_threshold_spin = None
        self.noise_threshold_spin = None

    def create_tab_widget(self) -> QWidget:
        """Create the audio settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Sensitivity settings
        sensitivity_group = SettingsWidgetFactory.create_group_box("Audio Sensitivity")
        sensitivity_layout = QGridLayout()

        # Overall sensitivity
        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setRange(50, 200)  # 0.5 to 2.0 scale
        self.sensitivity_slider.setValue(100)  # 1.0 default
        self.sensitivity_slider.valueChanged.connect(self.on_sensitivity_changed)
        sensitivity_layout.addWidget(QLabel("Detection Sensitivity:"), 0, 0)
        sensitivity_layout.addWidget(self.sensitivity_slider, 0, 1)

        self.sensitivity_label = QLabel("1.0")
        self.sensitivity_label.setFixedWidth(40)
        sensitivity_layout.addWidget(self.sensitivity_label, 0, 2)

        # VAD threshold
        self.vad_threshold_spin = QDoubleSpinBox()
        self.vad_threshold_spin.setRange(0.001, 0.1)
        self.vad_threshold_spin.setSingleStep(0.001)
        self.vad_threshold_spin.setDecimals(3)
        self.vad_threshold_spin.setValue(0.01)
        self.vad_threshold_spin.valueChanged.connect(self.on_setting_changed)
        self.create_grid_row(sensitivity_layout, 1, "Voice Activity Threshold:", self.vad_threshold_spin,
                           "Lower = more sensitive")

        # Noise threshold
        self.noise_threshold_spin = QDoubleSpinBox()
        self.noise_threshold_spin.setRange(0.001, 0.2)
        self.noise_threshold_spin.setSingleStep(0.001)
        self.noise_threshold_spin.setDecimals(3)
        self.noise_threshold_spin.setValue(0.02)
        self.noise_threshold_spin.valueChanged.connect(self.on_setting_changed)
        self.create_grid_row(sensitivity_layout, 2, "Noise Threshold:", self.noise_threshold_spin,
                           "Background noise level")

        sensitivity_group.setLayout(sensitivity_layout)
        layout.addWidget(sensitivity_group)

        # Audio help info
        help_group = SettingsWidgetFactory.create_group_box("Audio Settings Help")
        help_layout = QVBoxLayout()

        help_text = SettingsWidgetFactory.create_info_text_edit(
            "Audio Settings Guide:\n\n"
            "• Detection Sensitivity: Higher values make pitch detection more responsive\n"
            "• Voice Activity Threshold: Determines what counts as voice vs silence\n"
            "• Noise Threshold: Filters out background noise\n\n"
            "If you're having issues:\n"
            "• Microphone not detecting: Lower voice activity threshold\n"
            "• Too much background noise: Raise noise threshold\n"
            "• Choppy detection: Adjust sensitivity slider"
        )
        help_layout.addWidget(help_text)

        help_group.setLayout(help_layout)
        layout.addWidget(help_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def load_settings(self):
        """Load current settings into UI controls"""
        # Audio settings
        sensitivity = self.get_config_value('sensitivity', 1.0)
        self.sensitivity_slider.setValue(int(sensitivity * 100))
        self.sensitivity_label.setText(f"{sensitivity:.1f}")
        self.vad_threshold_spin.setValue(self.get_config_value('vad_threshold', 0.01))
        self.noise_threshold_spin.setValue(self.get_config_value('noise_threshold', 0.02))

    def save_settings(self) -> dict:
        """Return current settings as dict"""
        return {
            'sensitivity': self.sensitivity_slider.value() / 100.0,
            'vad_threshold': self.vad_threshold_spin.value(),
            'noise_threshold': self.noise_threshold_spin.value()
        }

    def on_sensitivity_changed(self):
        """Handle sensitivity slider change"""
        value = self.sensitivity_slider.value() / 100.0
        self.sensitivity_label.setText(f"{value:.1f}")
        self.on_setting_changed()

    def validate_settings(self) -> tuple[bool, str]:
        """Validate current settings"""
        vad_threshold = self.vad_threshold_spin.value()
        noise_threshold = self.noise_threshold_spin.value()

        if vad_threshold >= noise_threshold:
            return False, "Voice activity threshold should be lower than noise threshold"

        return True, ""

    def get_current_sensitivity(self) -> float:
        """Get current sensitivity value"""
        return self.sensitivity_slider.value() / 100.0

    def reset_audio_defaults(self):
        """Reset audio settings to defaults"""
        self.sensitivity_slider.setValue(100)
        self.sensitivity_label.setText("1.0")
        self.vad_threshold_spin.setValue(0.01)
        self.noise_threshold_spin.setValue(0.02)