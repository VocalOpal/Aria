"""
Voice Goals and Presets Settings
Handles voice training objectives and preset configurations
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QSpinBox, QComboBox  # type: ignore
from voice.presets import VoicePresets
from .shared_utils import BaseSettingsTab, SettingsWidgetFactory


class VoiceGoalsSettings(BaseSettingsTab):
    """Voice goals and presets configuration"""

    def __init__(self, config_manager, voice_trainer):
        super().__init__(config_manager, voice_trainer)
        self.voice_presets = VoicePresets()
        self.preset_combo = None
        self.preset_info_label = None
        self.base_goal_spin = None
        self.current_goal_spin = None
        self.goal_increment_spin = None

    def create_tab_widget(self) -> QWidget:
        """Create the voice goals settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Voice preset selection
        preset_group = SettingsWidgetFactory.create_group_box("Voice Training Preset")
        preset_layout = QVBoxLayout()

        self.preset_combo = QComboBox()
        preset_descriptions = {
            'mtf': 'MTF Voice Training - Feminine speech patterns with gradual pitch elevation',
            'ftm': 'FTM Voice Training - Lower pitch range and chest resonance',
            'nonbinary_higher': 'Non-Binary (Higher) - Androgynous voice with slight elevation',
            'nonbinary_lower': 'Non-Binary (Lower) - Androgynous voice with slight deepening',
            'nonbinary_neutral': 'Non-Binary (Neutral) - Current range with improved control',
            'custom': 'Custom Configuration - Manually configured settings'
        }

        for preset_key, description in preset_descriptions.items():
            self.preset_combo.addItem(description, preset_key)

        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        preset_layout.addWidget(QLabel("Select training goal:"))
        preset_layout.addWidget(self.preset_combo)

        # Preset info display
        self.preset_info_label = SettingsWidgetFactory.create_info_label("")
        preset_layout.addWidget(self.preset_info_label)

        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)

        # Manual goal settings
        goals_group = SettingsWidgetFactory.create_group_box("Manual Goal Configuration")
        goals_layout = QGridLayout()

        # Base goal
        self.base_goal_spin = QSpinBox()
        self.base_goal_spin.setRange(80, 400)
        self.base_goal_spin.setValue(165)
        self.base_goal_spin.valueChanged.connect(self.on_setting_changed)
        self.create_grid_row(goals_layout, 0, "Base Goal (Hz):", self.base_goal_spin)

        # Current goal
        self.current_goal_spin = QSpinBox()
        self.current_goal_spin.setRange(80, 400)
        self.current_goal_spin.setValue(165)
        self.current_goal_spin.valueChanged.connect(self.on_setting_changed)
        self.create_grid_row(goals_layout, 1, "Current Goal (Hz):", self.current_goal_spin)

        # Goal increment
        self.goal_increment_spin = QSpinBox()
        self.goal_increment_spin.setRange(-10, 10)
        self.goal_increment_spin.setValue(3)
        self.goal_increment_spin.valueChanged.connect(self.on_setting_changed)
        self.create_grid_row(goals_layout, 2, "Goal Increment (Hz):", self.goal_increment_spin,
                           "Positive values raise pitch, negative values lower pitch")

        goals_group.setLayout(goals_layout)
        layout.addWidget(goals_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def load_settings(self):
        """Load current settings into UI controls"""
        # Voice goals
        self.base_goal_spin.setValue(self.get_config_value('base_goal', 165))
        self.current_goal_spin.setValue(self.get_config_value('current_goal', 165))
        self.goal_increment_spin.setValue(self.get_config_value('goal_increment', 3))

        # Set current preset
        current_preset = self.get_config_value('current_preset', 'custom')
        for i in range(self.preset_combo.count()):
            if self.preset_combo.itemData(i) == current_preset:
                self.preset_combo.setCurrentIndex(i)
                break

        self.update_preset_info()

    def save_settings(self) -> dict:
        """Return current settings as dict"""
        return {
            'base_goal': self.base_goal_spin.value(),
            'current_goal': self.current_goal_spin.value(),
            'goal_increment': self.goal_increment_spin.value(),
            'current_preset': self.preset_combo.currentData()
        }

    def on_preset_changed(self):
        """Handle preset selection change"""
        self.on_setting_changed()
        self.update_preset_info()

    def update_preset_info(self):
        """Update preset information display"""
        preset_key = self.preset_combo.currentData()
        if preset_key in self.voice_presets.presets:
            preset = self.voice_presets.presets[preset_key]

            info_text = f"Description: {preset['description']}\n\n"
            info_text += f"Target Frequency: {preset['target_frequency']} Hz\n"
            info_text += f"Base Frequency: {preset['base_frequency']} Hz\n"
            info_text += f"Goal Increment: {preset['goal_increment']} Hz\n\n"

            if 'tips' in preset:
                info_text += "Training Tips:\n"
                for tip in preset['tips']:
                    info_text += f"• {tip}\n"

            self.preset_info_label.setText(info_text)

    def get_selected_preset(self) -> str:
        """Get currently selected preset key"""
        return self.preset_combo.currentData()

    def validate_settings(self) -> tuple[bool, str]:
        """Validate current settings"""
        base_goal = self.base_goal_spin.value()
        current_goal = self.current_goal_spin.value()

        if abs(current_goal - base_goal) > 100:
            return False, "Current goal is too far from base goal (>100 Hz difference)"

        return True, ""