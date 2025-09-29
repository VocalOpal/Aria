"""
Shared utilities for settings components
Common widgets, styling, and validation helpers
"""

from PyQt6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout,  # type: ignore
                            QLabel, QSpinBox, QDoubleSpinBox, QComboBox,
                            QCheckBox, QSlider, QPushButton, QTextEdit)
from PyQt6.QtCore import Qt  # type: ignore
from PyQt6.QtGui import QFont  # type: ignore
from ..design_system import AriaDesignSystem


class SettingsWidgetFactory:
    """Factory for creating consistent settings widgets"""

    @staticmethod
    def create_group_box(title: str) -> QGroupBox:
        """Create a styled group box"""
        group = QGroupBox(title)
        group.setStyleSheet(f"""
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
        return group

    @staticmethod
    def create_info_text_edit(content: str, max_height: int = 150) -> QTextEdit:
        """Create a styled read-only text edit for info display"""
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setMaximumHeight(max_height)
        text_edit.setPlainText(content)
        text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                color: {AriaDesignSystem.COLORS['text_secondary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: {AriaDesignSystem.RADIUS['md']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                padding: 8px;
            }}
        """)
        return text_edit

    @staticmethod
    def create_info_label(text: str, style: str = "muted") -> QLabel:
        """Create a styled info label"""
        label = QLabel(text)
        label.setWordWrap(True)

        if style == "muted":
            label.setStyleSheet(f"""
                QLabel {{
                    color: {AriaDesignSystem.COLORS['text_muted']};
                    font-style: italic;
                    font-size: {AriaDesignSystem.FONTS['sm']}pt;
                    padding: 12px;
                    background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                    border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                    border-radius: {AriaDesignSystem.RADIUS['md']};
                }}
            """)
        elif style == "secondary":
            label.setStyleSheet(f"""
                QLabel {{
                    color: {AriaDesignSystem.COLORS['text_secondary']};
                    font-size: {AriaDesignSystem.FONTS['xs']}pt;
                    background: transparent;
                    margin-top: 8px;
                }}
            """)

        return label

    @staticmethod
    def create_action_button(text: str, style: str = "secondary") -> QPushButton:
        """Create a styled action button"""
        button = QPushButton(text)
        button.setProperty("style", style)

        color_map = {
            "warning": AriaDesignSystem.COLORS['warning'],
            "info": AriaDesignSystem.COLORS['info'],
            "secondary": AriaDesignSystem.COLORS['bg_tertiary']
        }

        hover_map = {
            "warning": "#d97706",
            "info": "#2563eb",
            "secondary": AriaDesignSystem.COLORS['bg_accent']
        }

        pressed_map = {
            "warning": "#b45309",
            "info": "#1d4ed8",
            "secondary": AriaDesignSystem.COLORS['bg_tertiary']
        }

        bg_color = color_map.get(style, color_map["secondary"])
        hover_color = hover_map.get(style, hover_map["secondary"])
        pressed_color = pressed_map.get(style, pressed_map["secondary"])

        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: {'none' if style != 'secondary' else f'1px solid {AriaDesignSystem.COLORS["border_normal"]}'};
                border-radius: {AriaDesignSystem.RADIUS['md']};
                padding: 8px 16px;
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-weight: 500;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """)

        return button


class SettingsValidator:
    """Validation helpers for settings values"""

    @staticmethod
    def validate_frequency_range(value: int, min_freq: int = 80, max_freq: int = 400) -> bool:
        """Validate frequency values are in reasonable range"""
        return min_freq <= value <= max_freq

    @staticmethod
    def validate_duration(value: float, min_duration: float = 0.1, max_duration: float = 300.0) -> bool:
        """Validate duration values are reasonable"""
        return min_duration <= value <= max_duration

    @staticmethod
    def validate_threshold(value: float, min_val: float = 0.001, max_val: float = 1.0) -> bool:
        """Validate threshold values are in valid range"""
        return min_val <= value <= max_val


class SettingsStyler:
    """Common styling utilities for settings components"""

    @staticmethod
    def apply_tab_widget_style():
        """Get tab widget stylesheet"""
        return f"""
            QTabWidget::pane {{
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                background-color: {AriaDesignSystem.COLORS['bg_primary']};
                border-radius: {AriaDesignSystem.RADIUS['lg']};
                padding: 16px;
            }}
            QTabBar::tab {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                color: {AriaDesignSystem.COLORS['text_secondary']};
                padding: 12px 20px;
                margin-right: 2px;
                margin-bottom: 2px;
                border-top-left-radius: {AriaDesignSystem.RADIUS['md']};
                border-top-right-radius: {AriaDesignSystem.RADIUS['md']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-weight: 500;
                min-width: 100px;
            }}
            QTabBar::tab:selected {{
                background-color: {AriaDesignSystem.COLORS['primary']};
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-weight: 600;
            }}
            QTabBar::tab:hover {{
                background-color: {AriaDesignSystem.COLORS['bg_accent']};
                color: {AriaDesignSystem.COLORS['text_primary']};
            }}
            QTabBar::tab:!selected {{
                margin-top: 2px;
            }}
        """

    @staticmethod
    def apply_main_settings_style():
        """Get main settings screen stylesheet"""
        return f"""
            SettingsScreen {{
                background-color: {AriaDesignSystem.COLORS['bg_primary']};
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-family: {AriaDesignSystem.FONTS['family_primary']};
            }}
        """

    @staticmethod
    def apply_card_style():
        """Get card frame stylesheet"""
        return f"""
            QFrame {{
                background-color: {AriaDesignSystem.COLORS['bg_secondary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: {AriaDesignSystem.RADIUS['lg']};
                padding: 24px;
            }}
        """


class BaseSettingsTab:
    """Base class for settings tabs with common functionality"""

    def __init__(self, config_manager, voice_trainer):
        self.config_manager = config_manager
        self.voice_trainer = voice_trainer
        self.current_config = config_manager.get_config()
        self.settings_changed_callback = None

    def set_settings_changed_callback(self, callback):
        """Set callback for when settings change"""
        self.settings_changed_callback = callback

    def on_setting_changed(self):
        """Called when any setting changes"""
        if self.settings_changed_callback:
            self.settings_changed_callback()

    def get_config_value(self, key: str, default=None):
        """Get configuration value safely"""
        return self.current_config.get(key, default)

    def create_grid_row(self, layout: QGridLayout, row: int, label_text: str,
                       widget, help_text: str = None):
        """Helper to create a consistent grid row"""
        layout.addWidget(QLabel(label_text), row, 0)
        layout.addWidget(widget, row, 1)
        if help_text:
            layout.addWidget(QLabel(help_text), row, 2)