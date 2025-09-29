from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,  # type: ignore
                            QLabel, QFrame, QTextEdit, QMessageBox, QDialog,
                            QDialogButtonBox, QScrollArea, QCheckBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal  # type: ignore
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap  # type: ignore
from datetime import datetime
from ..design_system import AriaDesignSystem


class SafetyWarningWidget(QWidget):
    """Widget for displaying voice safety warnings and recommendations"""

    warning_dismissed = pyqtSignal()
    break_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.current_warnings = []
        self.init_ui()

    def init_ui(self):
        """Initialize the safety warning UI with modern design"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # Warning header
        self.warning_header = QLabel()
        self.warning_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.warning_header.setStyleSheet(f"""
            QLabel {{
                background-color: {AriaDesignSystem.COLORS['error']};
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['md']}pt;
                font-weight: 600;
                padding: 12px;
                border-radius: {AriaDesignSystem.RADIUS['md']};
                border: 1px solid {AriaDesignSystem.COLORS['error']};
            }}
        """)
        self.warning_header.setVisible(False)
        layout.addWidget(self.warning_header)

        # Warning content area
        self.warning_content = QLabel()
        self.warning_content.setWordWrap(True)
        self.warning_content.setStyleSheet(f"""
            QLabel {{
                background-color: {AriaDesignSystem.COLORS['warning_bg']};
                color: {AriaDesignSystem.COLORS['text_primary']};
                padding: 16px;
                border: 1px solid {AriaDesignSystem.COLORS['warning']};
                border-radius: {AriaDesignSystem.RADIUS['md']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                line-height: 1.5;
            }}
        """)
        self.warning_content.setVisible(False)
        layout.addWidget(self.warning_content)

        # Action buttons
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(12)

        self.take_break_button = QPushButton("Take Break")
        self.take_break_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaDesignSystem.COLORS['primary']};
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                color: white;
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-weight: 600;
                min-height: 36px;
            }}
            QPushButton:hover {{
                background-color: {AriaDesignSystem.COLORS['primary_hover']};
            }}
        """)
        self.take_break_button.clicked.connect(self.request_break)
        self.take_break_button.setVisible(False)

        self.dismiss_button = QPushButton("Dismiss")
        self.dismiss_button.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {AriaDesignSystem.COLORS['border_normal']};
                border-radius: 6px;
                padding: 10px 16px;
                color: {AriaDesignSystem.COLORS['text_secondary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-weight: 500;
                min-height: 36px;
            }}
            QPushButton:hover {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                color: {AriaDesignSystem.COLORS['text_primary']};
            }}
        """)
        self.dismiss_button.clicked.connect(self.dismiss_warning)
        self.dismiss_button.setVisible(False)

        self.button_layout.addWidget(self.take_break_button)
        self.button_layout.addWidget(self.dismiss_button)
        self.button_layout.addStretch()

        layout.addLayout(self.button_layout)
        self.setLayout(layout)

        # Auto-hide timer
        self.auto_hide_timer = QTimer()
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self.auto_dismiss)

    def show_warning(self, warning):
        """Display a safety warning"""
        warning_type = warning.get('type', 'unknown')
        message = warning.get('message', '')
        suggestion = warning.get('suggestion', '')

        # Set header text and color based on warning type
        if warning_type == 'break_reminder':
            self.warning_header.setText("Break Reminder")
            self.warning_header.setStyleSheet(f"""
                QLabel {{
                    background-color: {AriaDesignSystem.COLORS['info']};
                    color: {AriaDesignSystem.COLORS['text_primary']};
                    font-size: {AriaDesignSystem.FONTS['md']}pt;
                    font-weight: 600;
                    padding: 12px;
                    border-radius: 6px;
                    border: 1px solid {AriaDesignSystem.COLORS['info']};
                }}
            """)
            auto_hide_time = 8000  # 8 seconds
        elif warning_type in ['max_session', 'daily_limit']:
            self.warning_header.setText("Session Limit Warning")
            self.warning_header.setStyleSheet(f"""
                QLabel {{
                    background-color: {AriaDesignSystem.COLORS['warning']};
                    color: {AriaDesignSystem.COLORS['text_primary']};
                    font-size: {AriaDesignSystem.FONTS['md']}pt;
                    font-weight: 600;
                    padding: 12px;
                    border-radius: 6px;
                    border: 1px solid {AriaDesignSystem.COLORS['warning']};
                }}
            """)
            auto_hide_time = 15000  # 15 seconds
        elif warning_type in ['high_pitch_strain', 'excessive_force']:
            self.warning_header.setText("Vocal Strain Alert")
            self.warning_header.setStyleSheet(f"""
                QLabel {{
                    background-color: {AriaDesignSystem.COLORS['error']};
                    color: {AriaDesignSystem.COLORS['text_primary']};
                    font-size: {AriaDesignSystem.FONTS['md']}pt;
                    font-weight: 600;
                    padding: 12px;
                    border-radius: 6px;
                    border: 1px solid {AriaDesignSystem.COLORS['error']};
                }}
            """)
            auto_hide_time = 20000  # 20 seconds
        else:
            self.warning_header.setText("Voice Safety Notice")
            self.warning_header.setStyleSheet(f"""
                QLabel {{
                    background-color: {AriaDesignSystem.COLORS['info']};
                    color: {AriaDesignSystem.COLORS['text_primary']};
                    font-size: {AriaDesignSystem.FONTS['md']}pt;
                    font-weight: 600;
                    padding: 12px;
                    border-radius: 6px;
                    border: 1px solid {AriaDesignSystem.COLORS['info']};
                }}
            """)
            auto_hide_time = 10000  # 10 seconds

        # Set content
        content_text = f"{message}\n\nSuggestion: {suggestion}"
        self.warning_content.setText(content_text)

        # Show appropriate buttons
        if warning_type in ['break_reminder', 'max_session']:
            self.take_break_button.setVisible(True)
        else:
            self.take_break_button.setVisible(False)

        self.dismiss_button.setVisible(True)

        # Show all components
        self.warning_header.setVisible(True)
        self.warning_content.setVisible(True)

        # Start auto-hide timer
        self.auto_hide_timer.start(auto_hide_time)

        # Store current warning
        self.current_warnings.append(warning)

    def dismiss_warning(self):
        """Dismiss the current warning"""
        self.hide_warning()
        self.warning_dismissed.emit()

    def request_break(self):
        """Request a training break"""
        self.hide_warning()
        self.break_requested.emit()

    def auto_dismiss(self):
        """Auto-dismiss warning after timeout"""
        self.dismiss_warning()

    def hide_warning(self):
        """Hide all warning components"""
        self.warning_header.setVisible(False)
        self.warning_content.setVisible(False)
        self.take_break_button.setVisible(False)
        self.dismiss_button.setVisible(False)
        self.auto_hide_timer.stop()
        self.current_warnings.clear()

    def has_active_warning(self):
        """Check if there's an active warning displayed"""
        return self.warning_header.isVisible()


class SafetySummaryDialog(QDialog):
    """Dialog for showing post-session safety summary"""

    def __init__(self, session_duration, safety_summary, parent=None):
        super().__init__(parent)
        self.session_duration = session_duration
        self.safety_summary = safety_summary
        self.init_ui()

    def init_ui(self):
        """Initialize the safety summary dialog with modern design"""
        self.setWindowTitle("Voice Safety Summary")
        self.setFixedSize(500, 450)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {AriaDesignSystem.COLORS['bg_primary']};
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-family: {AriaDesignSystem.FONTS['family_primary']};
            }}
        """)

        # Main layout with proper spacing like onboarding
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(24)

        # Content frame (matches onboarding content frame)
        content_frame = QFrame()
        content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AriaDesignSystem.COLORS['bg_secondary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: 12px;
                padding: 24px;
            }}
        """)
        layout = QVBoxLayout(content_frame)
        layout.setSpacing(20)

        # Title (matches onboarding title style)
        title = QLabel("Voice Safety Summary")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont(AriaDesignSystem.FONTS['family_primary'], 18, QFont.Weight.Bold))
        title.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['primary']};
            margin-bottom: 8px;
        """)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("How did your voice training session go?")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_secondary']};
            font-size: {AriaDesignSystem.FONTS['md']}pt;
            margin-bottom: 16px;
        """)
        layout.addWidget(subtitle)

        # Session info card
        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(8)

        session_info = QLabel(f"Session Duration: {self.session_duration:.1f} minutes")
        session_info.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_primary']};
            font-weight: 600;
            font-size: {AriaDesignSystem.FONTS['md']}pt;
        """)
        info_layout.addWidget(session_info)

        if self.safety_summary:
            daily_total = self.safety_summary.get('daily_total_minutes', 0)
            daily_info = QLabel(f"Daily Total: {daily_total:.1f} minutes")
            daily_info.setStyleSheet(f"""
                color: {AriaDesignSystem.COLORS['text_muted']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
            """)
            info_layout.addWidget(daily_info)

        layout.addWidget(info_frame)

        # Safety status
        if self.safety_summary:
            status = self.safety_summary.get('session_safety_status', 'unknown')
            status_text = self.get_status_message(status)
            status_color = self.get_status_color(status)

            status_frame = QFrame()
            status_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {status_color};
                    border-radius: 8px;
                    padding: 16px;
                }}
            """)
            status_layout = QVBoxLayout(status_frame)
            status_layout.setContentsMargins(0, 0, 0, 0)

            status_label = QLabel(status_text)
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_label.setWordWrap(True)
            status_label.setStyleSheet(f"""
                color: white;
                font-weight: 600;
                font-size: {AriaDesignSystem.FONTS['md']}pt;
                background: transparent;
            """)
            status_layout.addWidget(status_label)
            layout.addWidget(status_frame)

            # Recommendations
            recommendations = self.safety_summary.get('recommendations', [])
            if recommendations:
                rec_frame = QFrame()
                rec_frame.setStyleSheet(f"""
                    QFrame {{
                        background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                        border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                        border-radius: 8px;
                        padding: 16px;
                    }}
                """)
                rec_layout = QVBoxLayout(rec_frame)
                rec_layout.setSpacing(12)

                rec_label = QLabel("Recommendations:")
                rec_label.setStyleSheet(f"""
                    color: {AriaDesignSystem.COLORS['text_primary']};
                    font-weight: 600;
                    font-size: {AriaDesignSystem.FONTS['md']}pt;
                """)
                rec_layout.addWidget(rec_label)

                for rec in recommendations:
                    rec_item = QLabel(f"• {rec}")
                    rec_item.setWordWrap(True)
                    rec_item.setStyleSheet(f"""
                        color: {AriaDesignSystem.COLORS['text_secondary']};
                        font-size: {AriaDesignSystem.FONTS['sm']}pt;
                        margin-left: 8px;
                        margin-bottom: 4px;
                    """)
                    rec_layout.addWidget(rec_item)

                layout.addWidget(rec_frame)

        # Vocal health tip
        tip_frame = QFrame()
        tip_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                border: 1px solid {AriaDesignSystem.COLORS['success']};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        tip_layout = QVBoxLayout(tip_frame)
        tip_layout.setSpacing(8)

        tip_label = QLabel("💡 Vocal Health Tip")
        tip_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['success']};
            font-weight: 600;
            font-size: {AriaDesignSystem.FONTS['md']}pt;
        """)
        tip_layout.addWidget(tip_label)

        tip_text = QLabel("Remember to stay hydrated and avoid straining your voice. "
                         "Consistent, gentle practice is more effective than pushing too hard.")
        tip_text.setWordWrap(True)
        tip_text.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_secondary']};
            font-size: {AriaDesignSystem.FONTS['sm']}pt;
            line-height: 1.4;
        """)
        tip_layout.addWidget(tip_text)

        layout.addWidget(tip_frame)

        main_layout.addWidget(content_frame)

        # Buttons (matches onboarding button style)
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(12)

        # Spacer
        button_layout.addStretch()

        # OK button
        ok_button = QPushButton("Got it!")
        ok_button.clicked.connect(self.accept)
        ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaDesignSystem.COLORS['primary']};
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                color: white;
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-weight: 600;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {AriaDesignSystem.COLORS['primary_hover']};
            }}
        """)
        button_layout.addWidget(ok_button)

        main_layout.addWidget(button_container)

    def get_status_message(self, status):
        """Get status message based on safety status"""
        if status == 'good':
            return "✅ Great session! Your voice usage was within healthy limits"
        elif status == 'break_suggested':
            return "💧 Good session! Remember to take breaks during longer practices"
        elif status == 'caution':
            return "⚠️ Long session completed. Consider shorter sessions tomorrow"
        else:
            return "ℹ️ Session completed"

    def get_status_color(self, status):
        """Get color based on safety status"""
        if status == 'good':
            return "#4CAF50"
        elif status == 'break_suggested':
            return "#2196F3"
        elif status == 'caution':
            return "#ff9800"
        else:
            return "#666"


class VoiceSafetyGUICoordinator:
    """Coordinates voice safety with GUI components"""

    def __init__(self, safety_monitor, main_window=None):
        self.safety_monitor = safety_monitor
        self.main_window = main_window
        self.safety_widgets = {}  # Track safety widgets on different screens
        self.warnings_enabled = True

    def register_safety_widget(self, screen_name, safety_widget):
        """Register a safety widget for a specific screen"""
        self.safety_widgets[screen_name] = safety_widget

        # Connect widget signals
        safety_widget.warning_dismissed.connect(self.on_warning_dismissed)
        safety_widget.break_requested.connect(self.on_break_requested)

    def handle_safety_warning(self, warning, current_screen=None):
        """Handle safety warning by showing it on appropriate screen"""
        if not self.warnings_enabled:
            return

        # Show warning on current screen if available
        if current_screen and current_screen in self.safety_widgets:
            safety_widget = self.safety_widgets[current_screen]
            safety_widget.show_warning(warning)
        else:
            # Show warning on all registered widgets
            for widget in self.safety_widgets.values():
                widget.show_warning(warning)

    def show_safety_summary(self, session_duration, current_screen=None):
        """Show post-session safety summary"""
        safety_summary = self.safety_monitor.get_session_safety_summary()

        # Show dialog
        parent = self.main_window if self.main_window else None
        dialog = SafetySummaryDialog(session_duration, safety_summary, parent)
        dialog.exec()

    def on_warning_dismissed(self):
        """Handle warning dismissal"""
        # Could add analytics or logging here
        pass

    def on_break_requested(self):
        """Handle break request from safety widget"""
        # Could pause training, show break timer, etc.
        if self.main_window:
            # Return to main menu for break
            self.main_window.show_main_navigation()

    def set_warnings_enabled(self, enabled):
        """Enable or disable safety warnings"""
        self.warnings_enabled = enabled

    def clear_all_warnings(self):
        """Clear warnings from all registered widgets"""
        for widget in self.safety_widgets.values():
            widget.hide_warning()