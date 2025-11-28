"""
Aria Voice Studio - Public Beta (v5) - Safety Widget
Modern safety monitoring widget adapted for gradient design system
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QDialog,
    QDialogButtonBox, QTextEdit, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime

from ..design_system import (
    AriaColors, AriaTypography, AriaSpacing, AriaRadius,
    InfoCard, PrimaryButton, SecondaryButton
)


class SafetyWarningWidget(QWidget):
    """Widget for displaying voice safety warnings with modern design"""

    warning_dismissed = pyqtSignal()
    break_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.current_warnings = []
        self.init_ui()

    def init_ui(self):
        """Initialize safety warning UI with gradient aesthetic"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(AriaSpacing.MD)

        # Warning header
        self.warning_header = QLabel()
        self.warning_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.warning_header.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {AriaColors.RED},
                    stop:1 {AriaColors.RED_HOVER}
                );
                color: white;
                font-size: {AriaTypography.HEADING}px;
                font-weight: 600;
                padding: {AriaSpacing.MD}px;
                border-radius: {AriaRadius.MD}px;
                border: 2px solid {AriaColors.RED};
            }}
        """)
        self.warning_header.setVisible(False)
        layout.addWidget(self.warning_header)

        # Warning content
        self.warning_content = QLabel()
        self.warning_content.setWordWrap(True)
        self.warning_content.setStyleSheet(f"""
            QLabel {{
                background-color: rgba(241, 76, 76, 0.15);
                color: white;
                padding: {AriaSpacing.LG}px;
                border: 1px solid rgba(241, 76, 76, 0.4);
                border-radius: {AriaRadius.MD}px;
                font-size: {AriaTypography.BODY}px;
                line-height: 1.6;
            }}
        """)
        self.warning_content.setVisible(False)
        layout.addWidget(self.warning_content)

        # Action buttons
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(AriaSpacing.MD)

        self.take_break_button = PrimaryButton("Take Break")
        self.take_break_button.clicked.connect(self.request_break)
        self.take_break_button.setVisible(False)

        self.dismiss_button = SecondaryButton("Dismiss")
        self.dismiss_button.clicked.connect(self.dismiss_warning)
        self.dismiss_button.setVisible(False)

        self.button_layout.addStretch()
        self.button_layout.addWidget(self.take_break_button)
        self.button_layout.addWidget(self.dismiss_button)
        self.button_layout.addStretch()

        layout.addLayout(self.button_layout)

    def show_warning(self, warning_data):
        """Display a safety warning"""
        warning_type = warning_data.get('type', 'unknown')
        message = warning_data.get('message', 'Safety warning')
        severity = warning_data.get('severity', 'medium')

        # Store warning
        self.current_warnings.append({
            'type': warning_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now()
        })

        # Update UI
        icon = "⚠️"  if severity == "high" else "⚡"
        self.warning_header.setText(f"{icon} Voice Safety Alert")
        self.warning_content.setText(message)

        # Show components
        self.warning_header.setVisible(True)
        self.warning_content.setVisible(True)
        self.take_break_button.setVisible(True)
        self.dismiss_button.setVisible(True)

        # Auto-dismiss low severity warnings
        if severity == "low":
            QTimer.singleShot(5000, self.dismiss_warning)

    def dismiss_warning(self):
        """Dismiss the current warning"""
        self.warning_header.setVisible(False)
        self.warning_content.setVisible(False)
        self.take_break_button.setVisible(False)
        self.dismiss_button.setVisible(False)
        self.warning_dismissed.emit()

    def request_break(self):
        """Request a training break"""
        self.dismiss_warning()
        self.break_requested.emit()

    def clear_all_warnings(self):
        """Clear all warnings"""
        self.current_warnings.clear()
        self.dismiss_warning()


class VoiceSafetyGUICoordinator:
    """Coordinates safety monitoring with GUI components"""

    def __init__(self, safety_monitor):
        self.safety_monitor = safety_monitor
        self.registered_widgets = {}

    def register_safety_widget(self, context_key, widget):
        """Register a safety widget for a specific context"""
        self.registered_widgets[context_key] = widget

    def handle_safety_warning(self, warning_data, context_key='default'):
        """Handle safety warning and update appropriate widget"""
        if context_key in self.registered_widgets:
            widget = self.registered_widgets[context_key]
            widget.show_warning(warning_data)

    def show_safety_summary(self, session_duration, context_key='default'):
        """Show safety summary after session"""
        if not self.safety_monitor:
            return

        summary = self.safety_monitor.get_session_summary()

        if summary and context_key in self.registered_widgets:
            # Create summary dialog
            dialog = SafetySummaryDialog(summary, session_duration)
            dialog.exec()

    def clear_all_warnings(self):
        """Clear warnings from all registered widgets"""
        for widget in self.registered_widgets.values():
            widget.clear_all_warnings()


class SafetySummaryDialog(QDialog):
    """Dialog showing session safety summary"""

    def __init__(self, summary, duration_minutes):
        super().__init__()
        self.summary = summary
        self.duration = duration_minutes
        self.init_ui()

    def init_ui(self):
        """Initialize summary dialog UI"""
        self.setWindowTitle("Session Safety Summary")
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL)
        layout.setSpacing(AriaSpacing.LG)

        # Apply gradient background
        self.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {AriaColors.GRADIENT_BLUE_DARK},
                    stop:1 {AriaColors.GRADIENT_PINK}
                );
            }}
            QLabel {{
                color: white;
                background: transparent;
            }}
        """)

        # Title
        title = QLabel("🎯 Training Session Summary")
        title.setFont(QFont(AriaTypography.FAMILY, AriaTypography.TITLE, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Duration
        duration_text = f"Session Duration: {self.duration:.1f} minutes"
        duration_label = QLabel(duration_text)
        duration_label.setFont(QFont(AriaTypography.FAMILY, AriaTypography.BODY))
        duration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(duration_label)

        # Summary card
        summary_card = QFrame()
        summary_card.setStyleSheet(f"""
            QFrame {{
                background-color: {AriaColors.CARD_BG};
                border-radius: {AriaRadius.LG}px;
                border: 1px solid {AriaColors.WHITE_25};
                padding: {AriaSpacing.LG}px;
            }}
        """)

        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setSpacing(AriaSpacing.SM)

        # Safety stats
        if self.summary:
            warnings_count = len(self.summary.get('warnings', []))
            status = "Excellent" if warnings_count == 0 else "Good" if warnings_count < 3 else "Review Needed"

            stats_text = f"""
            <p><b>Safety Status:</b> {status}</p>
            <p><b>Warnings:</b> {warnings_count}</p>
            <p><b>Recommendations:</b> Take regular breaks every 15-20 minutes</p>
            """

            stats_label = QLabel(stats_text)
            stats_label.setWordWrap(True)
            stats_label.setStyleSheet(f"color: white; font-size: {AriaTypography.BODY}px;")
            summary_layout.addWidget(stats_label)

        layout.addWidget(summary_card)

        # Recommendations
        rec_label = QLabel("💡 Remember to stay hydrated and rest your voice regularly!")
        rec_label.setWordWrap(True)
        rec_label.setStyleSheet(f"color: {AriaColors.WHITE_85}; font-size: {AriaTypography.BODY_SMALL}px;")
        rec_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(rec_label)

        # Close button
        close_button = PrimaryButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)
