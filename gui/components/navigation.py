from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame)  # type: ignore
from PyQt6.QtCore import Qt, QTimer  # type: ignore
from PyQt6.QtGui import QFont  # type: ignore
from ..design_system import AriaDesignSystem, safe_apply_stylesheet


class NavigationWidget(QWidget):
    """Main navigation interface"""

    def __init__(self, voice_trainer, main_window=None):
        super().__init__()
        self.voice_trainer = voice_trainer
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        """Initialize modern navigation UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(0)

        # Header section
        header_frame = QFrame()
        header_frame.setProperty("style", "card")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(32, 32, 32, 32)
        header_layout.setSpacing(8)

        # Modern title
        title = QLabel("Aria Voice Studio")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont(AriaDesignSystem.FONTS['family_primary'], AriaDesignSystem.FONTS['xxxl'], QFont.Weight.Bold))
        title.setProperty("style", "heading")
        title.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['primary']};
                margin-bottom: 8px;
                background: transparent;
            }}
        """)
        header_layout.addWidget(title)

        # Version indicator
        version = QLabel("v4.1")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setProperty("style", "caption")
        version.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_muted']};
                font-size: {AriaDesignSystem.FONTS['xs']}pt;
                background: transparent;
                margin-bottom: 16px;
            }}
        """)
        header_layout.addWidget(version)

        # Subtitle with better typography
        subtitle = QLabel("Your voice, your journey, your authentic self")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setProperty("style", "subheading")
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_secondary']};
                font-size: {AriaDesignSystem.FONTS['lg']}pt;
                font-style: italic;
                background: transparent;
                margin-bottom: 24px;
            }}
        """)
        header_layout.addWidget(subtitle)

        main_layout.addWidget(header_frame)
        main_layout.addSpacing(24)

        # Navigation buttons section
        nav_frame = QFrame()
        nav_frame.setProperty("style", "card")
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(24, 24, 24, 24)
        nav_layout.setSpacing(12)

        # Section title
        nav_title = QLabel("Training Modules")
        nav_title.setProperty("style", "subheading")
        nav_title.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['lg']}pt;
                font-weight: 600;
                background: transparent;
                margin-bottom: 16px;
            }}
        """)
        nav_layout.addWidget(nav_title)

        # Create modern menu buttons
        self.create_modern_button("Live Voice Training", "Real-time pitch monitoring and feedback", self.show_training, nav_layout)
        self.create_modern_button("Voice Exercises", "Guided warm-ups and training routines", self.show_exercises, nav_layout)
        self.create_modern_button("Audio File Analysis", "Analyze recordings and track progress", self.show_analysis, nav_layout)
        self.create_modern_button("Progress & Statistics", "View achievements and improvements", self.show_progress, nav_layout)
        self.create_modern_button("Settings & Config", "Customize your training experience", self.show_settings, nav_layout)

        main_layout.addWidget(nav_frame)
        main_layout.addStretch()

    def create_modern_button(self, title, description, callback, layout):
        """Create a modern menu button with title and description"""
        button_frame = QFrame()
        button_frame.setObjectName("nav_button")
        button_frame.setCursor(Qt.CursorShape.PointingHandCursor)

        # Create the layout for the button content
        button_layout = QVBoxLayout(button_frame)
        button_layout.setContentsMargins(20, 16, 20, 16)
        button_layout.setSpacing(4)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['md']}pt;
                font-weight: 600;
                background: transparent;
            }}
        """)
        button_layout.addWidget(title_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_secondary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                background: transparent;
            }}
        """)
        button_layout.addWidget(desc_label)

        # Style the frame as a clickable button
        button_frame.setStyleSheet(f"""
            QFrame#nav_button {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: {AriaDesignSystem.RADIUS['lg']};
                padding: 0px;
            }}
            QFrame#nav_button:hover {{
                background-color: {AriaDesignSystem.COLORS['bg_accent']};
                border-color: {AriaDesignSystem.COLORS['primary']};
            }}
        """)

        # Make it clickable
        def mousePressEvent(event):
            if event.button() == Qt.MouseButton.LeftButton:
                # Visual feedback
                button_frame.setStyleSheet(f"""
                    QFrame#nav_button {{
                        background-color: {AriaDesignSystem.COLORS['primary']};
                        border-color: {AriaDesignSystem.COLORS['primary']};
                        border-radius: {AriaDesignSystem.RADIUS['lg']};
                    }}
                """)
                callback()
                # Reset style after click - use safe style application
                reset_stylesheet = f"""
                    QFrame#nav_button {{
                        background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                        border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                        border-radius: {AriaDesignSystem.RADIUS['lg']};
                    }}
                    QFrame#nav_button:hover {{
                        background-color: {AriaDesignSystem.COLORS['bg_accent']};
                        border-color: {AriaDesignSystem.COLORS['primary']};
                    }}
                """
                QTimer.singleShot(100, lambda: safe_apply_stylesheet(button_frame, reset_stylesheet))

        button_frame.mousePressEvent = mousePressEvent
        layout.addWidget(button_frame)


    def show_training(self):
        """Show live training screen"""
        if self.main_window:
            self.main_window.show_training_screen()

    def show_exercises(self):
        """Show exercises screen"""
        if self.main_window:
            self.main_window.show_exercises_screen()

    def show_analysis(self):
        """Show analysis screen"""
        if self.main_window:
            self.main_window.show_audio_analysis_screen()

    def show_progress(self):
        """Show progress screen"""
        if self.main_window:
            self.main_window.show_progress_screen()

    def show_settings(self):
        """Show settings screen"""
        if self.main_window:
            self.main_window.show_settings_screen()