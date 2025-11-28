"""Settings screen with configuration management."""

import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QMessageBox, QPushButton, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from __init__ import __version__ as APP_VERSION
from utils.error_handler import log_error

from ..design_system import (
    AriaColors, AriaTypography, AriaSpacing, AriaRadius,
    InfoCard, PrimaryButton, SecondaryButton, create_gradient_background,
    StyledLabel, StyledComboBox, StyledSpinBox, StyledDoubleSpinBox, StyledCheckBox,
    TitleLabel, create_scroll_container
)


class CollapsibleSection(QFrame):
    """Collapsible section for advanced settings"""
    
    def __init__(self, title="Advanced Settings"):
        super().__init__()
        self.is_expanded = False
        self.content_widget = None
        self.init_ui(title)
    
    def init_ui(self, title):
        """Initialize collapsible UI"""
        self.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border: none;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(AriaSpacing.MD)
        
        # Header button
        self.header_btn = QPushButton(f"▶ {title}")
        self.header_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {AriaColors.CARD_BG_LIGHT},
                    stop:1 {AriaColors.CARD_BG_PINK_LIGHT}
                );
                border-radius: {AriaRadius.LG}px;
                border: none;
                padding: {AriaSpacing.LG}px;
                color: white;
                font-size: {AriaTypography.SUBHEADING}px;
                font-weight: 600;
                text-align: left;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(111, 162, 200, 0.55),
                    stop:1 rgba(232, 151, 189, 0.55)
                );
            }}
        """)
        self.header_btn.clicked.connect(self.toggle)
        layout.addWidget(self.header_btn)
        
        # Content container (hidden by default)
        self.content_container = QFrame()
        self.content_container.setStyleSheet("QFrame { background: transparent; border: none; }")
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(AriaSpacing.LG)
        self.content_container.hide()
        layout.addWidget(self.content_container)
    
    def toggle(self):
        """Toggle expanded/collapsed state"""
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            self.header_btn.setText(self.header_btn.text().replace("▶", "▼"))
            self.content_container.show()
        else:
            self.header_btn.setText(self.header_btn.text().replace("▼", "▶"))
            self.content_container.hide()
    
    def add_widget(self, widget):
        """Add widget to content area"""
        self.content_layout.addWidget(widget)


class SettingsScreen(QWidget):
    """Settings screen with card layout and full backend integration"""

    settings_changed = pyqtSignal()

    def __init__(self, voice_trainer):
        super().__init__()
        self.voice_trainer = voice_trainer
        self.config_manager = voice_trainer.config_manager
        self.current_config = {}
        self.has_changes = False

        # Store widget references for loading/saving
        self.widgets = {}

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """Initialize settings UI"""
        # Gradient background
        content = QFrame()
        content.setStyleSheet(create_gradient_background())

        layout = QVBoxLayout(content)
        layout.setContentsMargins(AriaSpacing.GIANT, AriaSpacing.GIANT, AriaSpacing.GIANT, AriaSpacing.GIANT)
        layout.setSpacing(AriaSpacing.XL)

        # Title
        layout.addWidget(TitleLabel("⚙️ Settings"))

        # Scroll area for settings cards
        scroll = create_scroll_container()

        scroll_content = QWidget()
        scroll_content.setStyleSheet("QWidget { background: transparent; }")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(24)

        # === BASIC SETTINGS ===
        
        # Voice Goals Card
        goals_card = self.create_voice_goals_card()
        scroll_layout.addWidget(goals_card)

        # Training Settings Card (simplified)
        training_card = self.create_basic_training_settings_card()
        scroll_layout.addWidget(training_card)

        # Display Settings Card (simplified)
        display_card = self.create_basic_display_settings_card()
        scroll_layout.addWidget(display_card)

        # === ADVANCED SETTINGS (Collapsible) ===
        
        advanced_section = CollapsibleSection("⚙️ Advanced Settings")
        
        # Audio Settings Card
        audio_card = self.create_audio_settings_card()
        advanced_section.add_widget(audio_card)
        
        # Advanced Training Card
        advanced_training_card = self.create_advanced_training_settings_card()
        advanced_section.add_widget(advanced_training_card)
        
        # Advanced Audio & Safety Card
        advanced_audio_safety_card = self.create_advanced_audio_safety_card()
        advanced_section.add_widget(advanced_audio_safety_card)
        
        scroll_layout.addWidget(advanced_section)

        # Danger Zone Card
        danger_card = self.create_danger_zone_card()
        scroll_layout.addWidget(danger_card)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)

        layout.addWidget(scroll)

        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(AriaSpacing.LG)
        buttons_layout.addStretch()

        reset_btn = SecondaryButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(reset_btn)

        update_btn = SecondaryButton("Check for Updates")
        update_btn.clicked.connect(self.check_for_updates)
        buttons_layout.addWidget(update_btn)

        save_btn = PrimaryButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_btn)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(content)

    def create_voice_goals_card(self):
        """Create voice goals settings card"""
        card = InfoCard("Voice Goals & Presets", min_height=240)

        # Voice Preset section
        preset_label = StyledLabel("Voice Training Preset:")
        card.content_layout.addWidget(preset_label)

        self.widgets['voice_preset'] = StyledComboBox()
        self.widgets['voice_preset'].addItems([
            "MTF - Feminine voice training",
            "FTM - Masculine voice training",
            "Non-Binary (Higher)",
            "Non-Binary (Lower)",
            "Custom"
        ])
        self.widgets['voice_preset'].currentTextChanged.connect(self.on_preset_changed)
        card.content_layout.addWidget(self.widgets['voice_preset'])

        # Visual spacer
        card.content_layout.addSpacing(AriaSpacing.XL)

        # Target Pitch Range section
        range_label = StyledLabel("Target Pitch Range (Hz):")
        card.content_layout.addWidget(range_label)

        range_layout = QHBoxLayout()
        range_layout.setSpacing(AriaSpacing.LG)

        # Min pitch
        min_container = QVBoxLayout()
        min_container.setSpacing(AriaSpacing.XS)
        min_label = StyledLabel("Minimum", style="caption")
        self.widgets['target_min'] = StyledSpinBox()
        self.widgets['target_min'].setRange(50, 400)
        self.widgets['target_min'].setValue(165)
        min_container.addWidget(min_label)
        min_container.addWidget(self.widgets['target_min'])
        range_layout.addLayout(min_container)

        # Max pitch
        max_container = QVBoxLayout()
        max_container.setSpacing(AriaSpacing.XS)
        max_label = StyledLabel("Maximum", style="caption")
        self.widgets['target_max'] = StyledSpinBox()
        self.widgets['target_max'].setRange(50, 400)
        self.widgets['target_max'].setValue(265)
        max_container.addWidget(max_label)
        max_container.addWidget(self.widgets['target_max'])
        range_layout.addLayout(max_container)

        range_layout.addStretch()
        card.content_layout.addLayout(range_layout)

        return card

    def create_basic_training_settings_card(self):
        """Create basic training settings card"""
        card = InfoCard("Training Settings", min_height=240)

        # Safety Monitoring
        self.widgets['safety_enabled'] = StyledCheckBox("Enable Safety Monitoring")
        self.widgets['safety_enabled'].setChecked(True)
        card.content_layout.addWidget(self.widgets['safety_enabled'])

        safety_desc = QLabel("Alerts you when vocal strain is detected")
        safety_desc.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.CAPTION}px; background: transparent; font-style: italic; margin-left: 28px;")
        safety_desc.setWordWrap(True)
        card.content_layout.addWidget(safety_desc)

        card.content_layout.addSpacing(AriaSpacing.MD)

        # Auto-save Sessions
        self.widgets['autosave'] = StyledCheckBox("Auto-save Training Sessions")
        self.widgets['autosave'].setChecked(True)
        card.content_layout.addWidget(self.widgets['autosave'])

        autosave_desc = QLabel("Automatically saves your training history")
        autosave_desc.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.CAPTION}px; background: transparent; font-style: italic; margin-left: 28px;")
        autosave_desc.setWordWrap(True)
        card.content_layout.addWidget(autosave_desc)

        card.content_layout.addSpacing(AriaSpacing.LG)

        # Session Duration Warning (minutes)
        duration_label = StyledLabel("Session Duration Warning (minutes):")
        card.content_layout.addWidget(duration_label)

        self.widgets['session_warning'] = StyledSpinBox()
        self.widgets['session_warning'].setRange(5, 60)
        self.widgets['session_warning'].setValue(15)
        card.content_layout.addWidget(self.widgets['session_warning'])

        duration_desc = QLabel("Reminds you to take breaks after this duration")
        duration_desc.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.CAPTION}px; background: transparent; font-style: italic;")
        duration_desc.setWordWrap(True)
        card.content_layout.addWidget(duration_desc)

        return card

    def create_basic_display_settings_card(self):
        """Create basic display settings card"""
        card = InfoCard("Display & Feedback", min_height=200)

        # Smooth Display
        self.widgets['smooth_display'] = StyledCheckBox("Smooth Pitch Display")
        self.widgets['smooth_display'].setChecked(True)
        card.content_layout.addWidget(self.widgets['smooth_display'])

        smooth_desc = QLabel("Reduces jitter in real-time pitch readings for easier monitoring")
        smooth_desc.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.CAPTION}px; background: transparent; font-style: italic; margin-left: 28px;")
        smooth_desc.setWordWrap(True)
        card.content_layout.addWidget(smooth_desc)

        card.content_layout.addSpacing(AriaSpacing.MD)

        # Alert Sounds
        self.widgets['alert_sounds_enabled'] = StyledCheckBox("Enable Alert Sounds")
        self.widgets['alert_sounds_enabled'].setChecked(True)
        card.content_layout.addWidget(self.widgets['alert_sounds_enabled'])

        alert_desc = QLabel("Play audio cues for feedback and safety warnings")
        alert_desc.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.CAPTION}px; background: transparent; font-style: italic; margin-left: 28px;")
        alert_desc.setWordWrap(True)
        card.content_layout.addWidget(alert_desc)
        
        card.content_layout.addSpacing(AriaSpacing.MD)
        
        # Show Spectrogram
        self.widgets['show_spectrogram'] = StyledCheckBox("Show Real-time Spectrogram")
        self.widgets['show_spectrogram'].setChecked(False)
        card.content_layout.addWidget(self.widgets['show_spectrogram'])
        
        spec_desc = QLabel("Display frequency spectrum visualization with formant highlighting (experimental)")
        spec_desc.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.CAPTION}px; background: transparent; font-style: italic; margin-left: 28px;")
        spec_desc.setWordWrap(True)
        card.content_layout.addWidget(spec_desc)

        return card

    def create_audio_settings_card(self):
        """Create audio settings card"""
        card = InfoCard("Microphone & Audio", min_height=280)

        # Microphone Sensitivity
        sens_label = StyledLabel("Microphone Sensitivity:")
        card.content_layout.addWidget(sens_label)

        self.widgets['mic_sensitivity'] = StyledDoubleSpinBox()
        self.widgets['mic_sensitivity'].setRange(0.1, 2.0)
        self.widgets['mic_sensitivity'].setValue(1.0)
        self.widgets['mic_sensitivity'].setSingleStep(0.1)
        card.content_layout.addWidget(self.widgets['mic_sensitivity'])

        sens_desc = QLabel("Adjust input volume sensitivity (1.0 = default)")
        sens_desc.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.CAPTION}px; background: transparent; font-style: italic;")
        sens_desc.setWordWrap(True)
        card.content_layout.addWidget(sens_desc)

        card.content_layout.addSpacing(AriaSpacing.LG)

        # Noise Gate Threshold
        gate_label = StyledLabel("Noise Gate Threshold:")
        card.content_layout.addWidget(gate_label)

        self.widgets['noise_gate'] = StyledDoubleSpinBox()
        self.widgets['noise_gate'].setRange(0.0, 1.0)
        self.widgets['noise_gate'].setValue(0.02)
        self.widgets['noise_gate'].setSingleStep(0.01)
        card.content_layout.addWidget(self.widgets['noise_gate'])

        gate_desc = QLabel("Filters background noise (lower = more sensitive)")
        gate_desc.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.CAPTION}px; background: transparent; font-style: italic;")
        gate_desc.setWordWrap(True)
        card.content_layout.addWidget(gate_desc)

        card.content_layout.addSpacing(AriaSpacing.LG)

        # Sample Rate
        rate_label = StyledLabel("Sample Rate (Hz):")
        card.content_layout.addWidget(rate_label)

        self.widgets['sample_rate'] = StyledComboBox()
        self.widgets['sample_rate'].addItems(["22050", "44100", "48000"])
        card.content_layout.addWidget(self.widgets['sample_rate'])

        rate_desc = QLabel("Audio quality (higher = better, 44100 recommended)")
        rate_desc.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.CAPTION}px; background: transparent; font-style: italic;")
        rate_desc.setWordWrap(True)
        card.content_layout.addWidget(rate_desc)

        return card

    def create_advanced_training_settings_card(self):
        """Create advanced training settings card"""
        card = InfoCard("Advanced Training Controls", min_height=160)

        # Auto-pause on critical strain
        self.widgets['auto_pause_strain'] = StyledCheckBox("Auto-pause on critical strain")
        self.widgets['auto_pause_strain'].setChecked(True)
        card.content_layout.addWidget(self.widgets['auto_pause_strain'])

        auto_pause_desc = QLabel("⚠️ Automatically pauses training when critical vocal strain is detected")
        auto_pause_desc.setStyleSheet(f"color: {AriaColors.YELLOW}; font-size: {AriaTypography.CAPTION}px; background: transparent; font-style: italic; margin-left: 28px; font-weight: bold;")
        auto_pause_desc.setWordWrap(True)
        auto_pause_desc.setToolTip("Warning: Disabling this may lead to vocal damage. Only disable if you understand the risks.")
        card.content_layout.addWidget(auto_pause_desc)

        card.content_layout.addSpacing(AriaSpacing.MD)

        # Show Resonance Data
        self.widgets['show_resonance'] = StyledCheckBox("Show Resonance Analysis (Experimental)")
        self.widgets['show_resonance'].setChecked(True)
        card.content_layout.addWidget(self.widgets['show_resonance'])

        resonance_desc = QLabel("Displays advanced resonance metrics and formant tracking")
        resonance_desc.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.CAPTION}px; background: transparent; font-style: italic; margin-left: 28px;")
        resonance_desc.setWordWrap(True)
        card.content_layout.addWidget(resonance_desc)

        return card

    def create_advanced_audio_safety_card(self):
        """Create advanced audio and safety settings card"""
        card = InfoCard("Advanced Audio & Safety", min_height=350)

        # === ALERT SOUNDS SECTION ===
        alerts_header = StyledLabel("Alert Sound Settings")
        alerts_header.setStyleSheet(f"color: {AriaColors.WHITE_100}; font-size: {AriaTypography.SUBHEADING}px; font-weight: 600; background: transparent;")
        card.content_layout.addWidget(alerts_header)
        card.content_layout.addSpacing(AriaSpacing.SM)

        # Alert volume slider
        volume_label = StyledLabel("Alert Volume:")
        card.content_layout.addWidget(volume_label)

        self.widgets['alert_volume'] = StyledDoubleSpinBox()
        self.widgets['alert_volume'].setRange(0.0, 1.0)
        self.widgets['alert_volume'].setValue(0.7)
        self.widgets['alert_volume'].setSingleStep(0.1)
        card.content_layout.addWidget(self.widgets['alert_volume'])

        volume_desc = QLabel("Adjust beep volume (0.0 = silent, 1.0 = maximum)")
        volume_desc.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.CAPTION}px; background: transparent; font-style: italic;")
        volume_desc.setWordWrap(True)
        card.content_layout.addWidget(volume_desc)

        card.content_layout.addSpacing(AriaSpacing.LG)

        # === VOCAL ROUGHNESS SECTION ===
        roughness_header = StyledLabel("Vocal Strain Detection")
        roughness_header.setStyleSheet(f"color: {AriaColors.WHITE_100}; font-size: {AriaTypography.SUBHEADING}px; font-weight: 600; background: transparent;")
        card.content_layout.addWidget(roughness_header)
        card.content_layout.addSpacing(AriaSpacing.SM)

        # Enable vocal roughness
        self.widgets['vocal_roughness_enabled'] = StyledCheckBox("Enable Vocal Roughness Monitoring")
        self.widgets['vocal_roughness_enabled'].setChecked(True)
        card.content_layout.addWidget(self.widgets['vocal_roughness_enabled'])

        roughness_desc = QLabel("Monitors jitter, shimmer, and HNR to detect vocal strain")
        roughness_desc.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.CAPTION}px; background: transparent; font-style: italic; margin-left: 28px;")
        roughness_desc.setWordWrap(True)
        card.content_layout.addWidget(roughness_desc)

        card.content_layout.addSpacing(AriaSpacing.MD)

        # Roughness sensitivity
        sensitivity_label = StyledLabel("Strain Detection Sensitivity:")
        card.content_layout.addWidget(sensitivity_label)

        self.widgets['roughness_sensitivity'] = StyledComboBox()
        self.widgets['roughness_sensitivity'].addItems(["Low", "Normal", "High"])
        self.widgets['roughness_sensitivity'].setCurrentText("Normal")
        card.content_layout.addWidget(self.widgets['roughness_sensitivity'])

        sensitivity_desc = QLabel("Higher sensitivity detects subtle strain earlier")
        sensitivity_desc.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.CAPTION}px; background: transparent; font-style: italic;")
        sensitivity_desc.setWordWrap(True)
        card.content_layout.addWidget(sensitivity_desc)

        card.content_layout.addSpacing(AriaSpacing.LG)

        # === PITCH SMOOTHING SECTION ===
        smoothing_header = StyledLabel("Pitch Processing")
        smoothing_header.setStyleSheet(f"color: {AriaColors.WHITE_100}; font-size: {AriaTypography.SUBHEADING}px; font-weight: 600; background: transparent;")
        card.content_layout.addWidget(smoothing_header)
        card.content_layout.addSpacing(AriaSpacing.SM)

        # Enable pitch smoothing
        self.widgets['pitch_smoothing'] = StyledCheckBox("Enable Pitch Smoothing (250ms)")
        self.widgets['pitch_smoothing'].setChecked(True)
        card.content_layout.addWidget(self.widgets['pitch_smoothing'])

        smoothing_desc = QLabel("Applies temporal smoothing to reduce pitch detection jitter")
        smoothing_desc.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.CAPTION}px; background: transparent; font-style: italic; margin-left: 28px;")
        smoothing_desc.setWordWrap(True)
        card.content_layout.addWidget(smoothing_desc)

        card.content_layout.addSpacing(AriaSpacing.MD)

        # Pitch confidence threshold
        confidence_label = StyledLabel("Pitch Confidence Threshold:")
        card.content_layout.addWidget(confidence_label)

        self.widgets['pitch_confidence'] = StyledDoubleSpinBox()
        self.widgets['pitch_confidence'].setRange(0.0, 1.0)
        self.widgets['pitch_confidence'].setValue(0.5)
        self.widgets['pitch_confidence'].setSingleStep(0.1)
        card.content_layout.addWidget(self.widgets['pitch_confidence'])

        confidence_desc = QLabel("Minimum confidence for pitch detection (higher = more strict)")
        confidence_desc.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.CAPTION}px; background: transparent; font-style: italic;")
        confidence_desc.setWordWrap(True)
        card.content_layout.addWidget(confidence_desc)

        return card

    def create_danger_zone_card(self):
        """Create danger zone settings card"""
        card = InfoCard("⚠️ Danger Zone", min_height=180)
        
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(200, 50, 50, 0.2),
                    stop:1 rgba(200, 100, 50, 0.2)
                );
                border-radius: {AriaRadius.XL}px;
                border: 1px solid rgba(255, 100, 100, 0.4);
            }}
            QLabel {{
                background: transparent;
                border: none;
                padding: 0px;
            }}
        """)

        danger_desc = QLabel("⚠️ These actions are permanent and cannot be undone. Use with caution.")
        danger_desc.setStyleSheet(f"""
            color: {AriaColors.YELLOW};
            font-size: {AriaTypography.BODY}px;
            background: transparent;
            font-weight: bold;
            border: none;
            padding: 0px;
        """)
        danger_desc.setWordWrap(True)
        card.content_layout.addWidget(danger_desc)

        card.content_layout.addSpacing(AriaSpacing.LG)

        # Clear all data button
        clear_btn = QPushButton("Clear All Training Data")
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaColors.RED};
                color: white;
                border: none;
                border-radius: {AriaRadius.MD}px;
                padding: {AriaSpacing.MD}px {AriaSpacing.LG}px;
                font-size: {AriaTypography.BODY}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {AriaColors.RED_HOVER};
            }}
        """)
        clear_btn.clicked.connect(self.clear_all_data)
        card.content_layout.addWidget(clear_btn)

        clear_desc = QLabel("Permanently deletes all sessions, progress, and settings")
        clear_desc.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.CAPTION}px; background: transparent; font-style: italic; border: none; padding: 0px;")
        clear_desc.setWordWrap(True)
        card.content_layout.addWidget(clear_desc)

        return card

    def on_preset_changed(self, preset_text):
        """Handle preset change"""
        # Map presets to target ranges
        preset_ranges = {
            "MTF - Feminine voice training": (165, 265),
            "FTM - Masculine voice training": (85, 180),
            "Non-Binary (Higher)": (145, 220),
            "Non-Binary (Lower)": (100, 165),
            "Custom": None
        }

        if preset_text in preset_ranges and preset_ranges[preset_text]:
            min_hz, max_hz = preset_ranges[preset_text]
            self.widgets['target_min'].setValue(min_hz)
            self.widgets['target_max'].setValue(max_hz)

    def load_settings(self):
        """Load settings from config manager"""
        try:
            config = self.config_manager.get_config()
            self.current_config = config.copy()

            # Voice Goals
            # Map stored preset to display text
            preset_map = {
                'MTF': "MTF - Feminine voice training",
                'FTM': "FTM - Masculine voice training",
            }
            
            stored_preset = config.get('voice_preset', '')
            if 'MTF' in stored_preset or config.get('goal_increment', 0) > 0:
                self.widgets['voice_preset'].setCurrentText("MTF - Feminine voice training")
            elif 'FTM' in stored_preset or config.get('goal_increment', 0) < 0:
                self.widgets['voice_preset'].setCurrentText("FTM - Masculine voice training")
            elif 'Higher' in stored_preset:
                self.widgets['voice_preset'].setCurrentText("Non-Binary (Higher)")
            elif 'Lower' in stored_preset:
                self.widgets['voice_preset'].setCurrentText("Non-Binary (Lower)")
            else:
                self.widgets['voice_preset'].setCurrentText("Custom")

            # Target Range
            target_range = config.get('target_pitch_range', [165, 265])
            self.widgets['target_min'].setValue(target_range[0])
            self.widgets['target_max'].setValue(target_range[1])

            # Audio Settings
            self.widgets['mic_sensitivity'].setValue(config.get('sensitivity', 1.0))
            self.widgets['noise_gate'].setValue(config.get('noise_threshold', 0.02))
            sample_rate = str(config.get('sample_rate', 44100))
            if sample_rate in ["22050", "44100", "48000"]:
                self.widgets['sample_rate'].setCurrentText(sample_rate)

            # Training Settings
            self.widgets['safety_enabled'].setChecked(config.get('safety_monitoring_enabled', True))
            self.widgets['auto_pause_strain'].setChecked(config.get('auto_pause_on_strain', True))
            self.widgets['autosave'].setChecked(config.get('auto_save_sessions', True))
            self.widgets['session_warning'].setValue(config.get('session_duration_target', 15) // 60)

            # Display Settings
            self.widgets['smooth_display'].setChecked(config.get('smooth_display_enabled', True))
            self.widgets['alert_sounds_enabled'].setChecked(config.get('alert_sounds_enabled', True))
            self.widgets['show_resonance'].setChecked(config.get('resonance_display_enabled', True))

            # Advanced Settings
            self.widgets['alert_volume'].setValue(config.get('alert_volume', 0.7))
            self.widgets['vocal_roughness_enabled'].setChecked(config.get('vocal_roughness_enabled', True))
            
            roughness_sens = config.get('roughness_sensitivity', 'normal')
            self.widgets['roughness_sensitivity'].setCurrentText(roughness_sens.capitalize())
            
            self.widgets['pitch_smoothing'].setChecked(config.get('pitch_smoothing_enabled', True))
            self.widgets['pitch_confidence'].setValue(config.get('pitch_confidence_threshold', 0.5))

            self.has_changes = False

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "SettingsScreen.load_settings")

    def save_settings(self):
        """Save settings to config manager"""
        try:
            # Build config update dictionary
            updates = {}

            # Voice Goals
            preset_text = self.widgets['voice_preset'].currentText()
            
            # Map display text back to config values
            preset_map = {
                "MTF - Feminine voice training": 'MTF',
                "FTM - Masculine voice training": 'FTM',
            }
            
            updates['voice_preset'] = preset_text
            updates['target_pitch_range'] = [
                self.widgets['target_min'].value(),
                self.widgets['target_max'].value()
            ]

            # Audio Settings
            updates['sensitivity'] = self.widgets['mic_sensitivity'].value()
            updates['noise_threshold'] = self.widgets['noise_gate'].value()
            updates['sample_rate'] = int(self.widgets['sample_rate'].currentText())

            # Training Settings
            updates['safety_monitoring_enabled'] = self.widgets['safety_enabled'].isChecked()
            updates['auto_pause_on_strain'] = self.widgets['auto_pause_strain'].isChecked()
            updates['auto_save_sessions'] = self.widgets['autosave'].isChecked()
            updates['session_duration_target'] = self.widgets['session_warning'].value() * 60

            # Display Settings
            updates['smooth_display_enabled'] = self.widgets['smooth_display'].isChecked()
            updates['alert_sounds_enabled'] = self.widgets['alert_sounds_enabled'].isChecked()
            updates['resonance_display_enabled'] = self.widgets['show_resonance'].isChecked()

            # Advanced Settings
            updates['alert_volume'] = self.widgets['alert_volume'].value()
            updates['vocal_roughness_enabled'] = self.widgets['vocal_roughness_enabled'].isChecked()
            updates['roughness_sensitivity'] = self.widgets['roughness_sensitivity'].currentText().lower()
            updates['pitch_smoothing_enabled'] = self.widgets['pitch_smoothing'].isChecked()
            updates['pitch_confidence_threshold'] = self.widgets['pitch_confidence'].value()

            # Save to config manager
            success = self.config_manager.update_config(updates)

            if success:
                QMessageBox.information(
                    self,
                    "Settings Saved",
                    "Your settings have been saved successfully."
                )
                self.settings_changed.emit()
                self.has_changes = False
            else:
                QMessageBox.warning(
                    self,
                    "Save Failed",
                    "Failed to save settings. Please try again."
                )

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "SettingsScreen.save_settings")
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while saving settings:\n{str(e)}"
            )

    def refresh(self):
        """Refresh settings UI to latest config/profile."""
        self.load_settings()

    def check_for_updates(self):
        """Check GitHub for latest release and compare to local version."""
        from PyQt6.QtWidgets import QMessageBox
        import json
        import urllib.request

        config = self.config_manager.get_config()
        # Default to the current Aria repo if not configured
        owner = config.get('update_repo_owner', 'VocalOpal')
        repo = config.get('update_repo_name', 'Aria')
        api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"

        try:
            with urllib.request.urlopen(api_url, timeout=6) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            latest = data.get('tag_name') or data.get('name') or "unknown"
            html_url = data.get('html_url', f"https://github.com/{owner}/{repo}/releases")
            zip_url = data.get('zipball_url')

            local_version = APP_VERSION if APP_VERSION else "unknown"

            if latest != "unknown" and local_version != "unknown" and latest.strip() == local_version.strip():
                QMessageBox.information(
                    self,
                    "Up to Date",
                    f"You're on the latest version ({local_version})."
                )
            else:
                reply = QMessageBox.question(
                    self,
                    "Update Available" if latest != "unknown" else "Check Updates",
                    f"Latest release: {latest}\nYour version: {local_version}\n\nDownload and install now?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                if reply == QMessageBox.StandardButton.Yes and zip_url:
                    self._download_and_install_update(zip_url, latest, html_url)
                else:
                    QMessageBox.information(
                        self,
                        "Update Link",
                        f"Download the latest release here:\n{html_url}"
                    )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Update Check Failed",
                f"Could not check for updates.\nReason: {e}"
            )

    def _download_and_install_update(self, zip_url: str, latest_tag: str, release_url: str) -> None:
        """Download latest release zip, overlay code (preserving data), and restart."""
        from PyQt6.QtWidgets import QMessageBox
        import urllib.request
        try:
            tmp_dir = Path(tempfile.mkdtemp(prefix="aria_update_"))
            zip_path = tmp_dir / f"aria-{latest_tag or 'latest'}.zip"

            # Download archive
            with urllib.request.urlopen(zip_url, timeout=30) as resp, open(zip_path, "wb") as f:
                shutil.copyfileobj(resp, f)

            # Extract
            extract_dir = tmp_dir / "extracted"
            extract_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_dir)

            extracted_roots = [p for p in extract_dir.iterdir() if p.is_dir()]
            if not extracted_roots:
                raise RuntimeError("Downloaded archive was empty.")

            new_root = extracted_roots[0]
            app_root = Path(__file__).resolve().parents[2]

            preserve = {"data", "logs", ".git", ".github", "__pycache__", "venv", "env"}

            # Overlay new files into current app (preserve data/logs and virtualenvs)
            for item in new_root.iterdir():
                if item.name in preserve:
                    continue
                dest = app_root / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest)

            QMessageBox.information(
                self,
                "Update Installed",
                f"Aria has been updated to {latest_tag}.\nThe app will restart now."
            )

            # Restart app from updated codebase
            python = sys.executable
            main_path = app_root / "main.py"
            subprocess.Popen([python, str(main_path)], close_fds=True)
            QApplication.instance().quit()

        except Exception as e:
            log_error(e, "SettingsScreen._download_and_install_update")
            QMessageBox.warning(
                self,
                "Update Failed",
                f"Could not install the update.\n\nDownload manually:\n{release_url}\n\nReason: {e}"
            )

    def reset_settings(self):
        """Reset settings to defaults"""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.config_manager.reset_to_defaults()
                self.load_settings()
                QMessageBox.information(
                    self,
                    "Settings Reset",
                    "All settings have been reset to their default values."
                )
                self.settings_changed.emit()
            except Exception as e:
                from utils.error_handler import log_error
                log_error(e, "SettingsScreen.reset_settings")

    def clear_all_data(self):
        """Clear all training data"""
        reply = QMessageBox.warning(
            self,
            "⚠️ Clear All Data",
            "This will permanently delete:\n\n"
            "• All training sessions\n"
            "• Progress history\n"
            "• Voice snapshots\n"
            "• Configuration settings\n\n"
            "This action CANNOT be undone!\n\n"
            "Are you absolutely sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Double confirmation
            confirm = QMessageBox.critical(
                self,
                "⚠️ FINAL WARNING",
                "This is your last chance!\n\n"
                "All your data will be permanently deleted.\n\n"
                "Type 'DELETE' to confirm:",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel
            )

            if confirm == QMessageBox.StandardButton.Ok:
                try:
                    # Clear all data
                    self.config_manager.clear_all_data()
                    self.voice_trainer.session_manager.clear_all_data()
                    
                    QMessageBox.information(
                        self,
                        "Data Cleared",
                        "All training data has been permanently deleted."
                    )
                    
                    # Reload default settings
                    self.load_settings()
                    self.settings_changed.emit()
                    
                except Exception as e:
                    from utils.error_handler import log_error
                    log_error(e, "SettingsScreen.clear_all_data")
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"An error occurred while clearing data:\n{str(e)}"
                    )
