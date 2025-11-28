"""Keyboard shortcuts help dialog."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence

from ..design_system import (
    AriaColors, AriaTypography, AriaSpacing, AriaRadius,
    SecondaryButton, TitleLabel, HeadingLabel, BodyLabel
)
import platform


class ShortcutsDialog(QDialog):
    """Dialog displaying all available keyboard shortcuts"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        self.setMinimumSize(700, 600)
        self.init_ui()

    def init_ui(self):
        """Initialize the shortcuts dialog UI"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL)
        layout.setSpacing(AriaSpacing.XL)

        # Set dialog background
        self.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5A7A95,
                    stop:1 #C88AA8
                );
            }}
        """)

        # Title
        title = TitleLabel("⌨️ Keyboard Shortcuts")
        layout.addWidget(title)

        # Scroll area for shortcuts
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(AriaSpacing.XL)

        # Determine modifier key based on platform
        mod_key = "Cmd" if platform.system() == "Darwin" else "Ctrl"

        # Define shortcut categories
        shortcuts = [
            ("Global Shortcuts", [
                ("?", "Show this help dialog"),
                ("Esc", "Go back / Cancel action"),
                (f"{mod_key}+K", "Open search (coming soon)"),
                (f"{mod_key}+E", "Go to Exercises"),
                (f"{mod_key}+S", "Go to Settings"),
            ]),
            ("Training Screen", [
                ("Space", "Start/Stop training"),
                ("R", "Record snapshot"),
                ("Esc", "Stop training"),
            ]),
            ("Exercises Screen", [
                ("Space", "Start/Pause exercise"),
                ("Esc", "Stop exercise"),
                ("R", "Record exercise session"),
            ]),
            ("Navigation", [
                (f"{mod_key}+1", "Live Training (coming soon)"),
                (f"{mod_key}+2", "Exercises (coming soon)"),
                (f"{mod_key}+3", "Analysis (coming soon)"),
                (f"{mod_key}+4", "Progress (coming soon)"),
                (f"{mod_key}+5", "Settings (coming soon)"),
            ])
        ]

        # Create shortcut sections
        for category, items in shortcuts:
            section_card = self._create_shortcut_section(category, items)
            scroll_layout.addWidget(section_card)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_btn = SecondaryButton("Close")
        close_btn.clicked.connect(self.accept)
        close_layout.addWidget(close_btn)
        close_layout.addStretch()
        layout.addLayout(close_layout)

    def _create_shortcut_section(self, title, shortcuts):
        """Create a section card for shortcuts category"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(111, 162, 200, 0.4),
                    stop:1 rgba(232, 151, 189, 0.4)
                );
                border-radius: {AriaRadius.LG}px;
                border: 1px solid {AriaColors.WHITE_25};
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(AriaSpacing.XXL, AriaSpacing.LG, AriaSpacing.XXL, AriaSpacing.LG)
        card_layout.setSpacing(AriaSpacing.MD)

        # Section title
        section_title = HeadingLabel(title)
        card_layout.addWidget(section_title)

        # Add shortcuts
        for key, description in shortcuts:
            shortcut_row = self._create_shortcut_row(key, description)
            card_layout.addWidget(shortcut_row)

        return card

    def _create_shortcut_row(self, key, description):
        """Create a single shortcut row"""
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, AriaSpacing.XS, 0, AriaSpacing.XS)
        layout.setSpacing(AriaSpacing.LG)

        # Key badge
        key_badge = QLabel(key)
        key_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        key_badge.setMinimumWidth(120)
        key_badge.setStyleSheet(f"""
            QLabel {{
                background-color: rgba(255, 255, 255, 0.15);
                color: white;
                border: 1px solid {AriaColors.WHITE_45};
                border-radius: {AriaRadius.SM}px;
                padding: {AriaSpacing.XS}px {AriaSpacing.MD}px;
                font-size: {AriaTypography.BODY}px;
                font-weight: 600;
                font-family: monospace;
            }}
        """)
        layout.addWidget(key_badge)

        # Description
        desc_label = BodyLabel(description)
        layout.addWidget(desc_label, stretch=1)

        return row


def get_modifier_key():
    """Get the platform-specific modifier key name"""
    return "Cmd" if platform.system() == "Darwin" else "Ctrl"


def get_modifier_qt():
    """Get the Qt modifier key constant"""
    return Qt.KeyboardModifier.ControlModifier if platform.system() != "Darwin" else Qt.KeyboardModifier.MetaModifier
