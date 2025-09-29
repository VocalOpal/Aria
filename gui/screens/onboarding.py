from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,  # type: ignore
                            QLabel, QComboBox, QMessageBox, QFrame, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal  # type: ignore
from PyQt6.QtGui import QFont  # type: ignore
from ..design_system import AriaDesignSystem


class OnboardingWidget(QWidget):
    """Clean first-time user setup wizard"""

    onboarding_completed = pyqtSignal(dict)
    onboarding_cancelled = pyqtSignal()

    def __init__(self, voice_trainer):
        super().__init__()
        self.voice_trainer = voice_trainer
        self.current_step = 0
        self.total_steps = 4
        self.config_data = {
            'voice_goals': '',
            'voice_preset': ''
        }
        self.init_ui()

    def init_ui(self):
        """Initialize clean onboarding UI"""
        # Main layout with consistent spacing
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(30)

        # Header section
        self.create_header(main_layout)

        # Progress bar
        self.create_progress_bar(main_layout)

        # Content area
        self.create_content_area(main_layout)

        # Navigation buttons
        self.create_navigation(main_layout)

        # Apply styling
        self.setStyleSheet(f"""
            OnboardingWidget {{
                background-color: {AriaDesignSystem.COLORS['bg_primary']};
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-family: {AriaDesignSystem.FONTS['family_primary']};
            }}
        """)

        # Show first step
        self.update_display()

    def create_header(self, layout):
        """Create clean header section"""
        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        # Main title
        self.title_label = QLabel("Welcome to Aria Voice Studio")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont(AriaDesignSystem.FONTS['family_primary'], 22, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['primary']};
            margin-bottom: 8px;
        """)
        header_layout.addWidget(self.title_label)

        # Subtitle
        self.subtitle_label = QLabel("Let's set up your voice training")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_secondary']};
            font-size: {AriaDesignSystem.FONTS['md']}pt;
        """)
        header_layout.addWidget(self.subtitle_label)

        layout.addWidget(header_container)

    def create_progress_bar(self, layout):
        """Create simple progress indicator"""
        progress_container = QWidget()
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(8)

        # Step indicator
        self.step_label = QLabel("Step 1 of 4")
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.step_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_muted']};
            font-size: {AriaDesignSystem.FONTS['sm']}pt;
        """)
        progress_layout.addWidget(self.step_label)

        # Progress bar
        progress_bar_container = QWidget()
        progress_bar_container.setFixedHeight(4)
        progress_bar_container.setStyleSheet(f"""
            background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
            border-radius: 2px;
        """)

        self.progress_fill = QWidget(progress_bar_container)
        self.progress_fill.setStyleSheet(f"""
            background-color: {AriaDesignSystem.COLORS['primary']};
            border-radius: 2px;
        """)
        self.progress_fill.setGeometry(0, 0, 0, 4)

        progress_layout.addWidget(progress_bar_container)
        layout.addWidget(progress_container)

    def create_content_area(self, layout):
        """Create main content area"""
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AriaDesignSystem.COLORS['bg_secondary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: 12px;
                padding: 40px;
            }}
        """)

        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setSpacing(24)
        layout.addWidget(self.content_frame)

    def create_navigation(self, layout):
        """Create navigation buttons"""
        nav_container = QWidget()
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(12)

        # Cancel button (left)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_onboarding)
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {AriaDesignSystem.COLORS['border_normal']};
                border-radius: 6px;
                padding: 10px 20px;
                color: {AriaDesignSystem.COLORS['text_secondary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                color: {AriaDesignSystem.COLORS['text_primary']};
            }}
        """)
        nav_layout.addWidget(self.cancel_btn)

        # Spacer
        nav_layout.addStretch()

        # Back button
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self.prev_step)
        self.back_btn.setEnabled(False)
        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {AriaDesignSystem.COLORS['bg_accent']};
            }}
            QPushButton:disabled {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                color: {AriaDesignSystem.COLORS['text_muted']};
                opacity: 0.5;
            }}
        """)
        nav_layout.addWidget(self.back_btn)

        # Next button
        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self.next_step)
        self.next_btn.setStyleSheet(f"""
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
        nav_layout.addWidget(self.next_btn)

        layout.addWidget(nav_container)

    def update_display(self):
        """Update the display for current step"""
        # Clear content
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Update progress
        progress_percent = (self.current_step / (self.total_steps - 1)) * 100
        self.step_label.setText(f"Step {self.current_step + 1} of {self.total_steps}")

        # Animate progress bar
        content_width = self.content_frame.width() if hasattr(self, 'content_frame') else 400
        progress_width = int((content_width - 80) * progress_percent / 100)  # 80px for padding
        self.progress_fill.setFixedWidth(max(0, progress_width))

        # Update navigation
        self.back_btn.setEnabled(self.current_step > 0)

        if self.current_step == self.total_steps - 1:
            self.next_btn.setText("Complete Setup")
            self.next_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AriaDesignSystem.COLORS['success']};
                    border: none;
                    border-radius: 6px;
                    padding: 10px 24px;
                    color: white;
                    font-size: {AriaDesignSystem.FONTS['sm']}pt;
                    font-weight: 600;
                    min-width: 120px;
                }}
                QPushButton:hover {{
                    background-color: {AriaDesignSystem.COLORS['success_hover']};
                }}
            """)
        else:
            self.next_btn.setText("Next →")
            self.next_btn.setStyleSheet(f"""
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

        # Show appropriate step content
        if self.current_step == 0:
            self.show_welcome_step()
        elif self.current_step == 1:
            self.show_goals_step()
        elif self.current_step == 2:
            self.show_preset_step()
        elif self.current_step == 3:
            self.show_complete_step()

    def show_welcome_step(self):
        """Welcome step - simple and clean"""
        self.title_label.setText("Welcome to Aria Voice Studio")
        self.subtitle_label.setText("Your voice training journey starts here")

        # Tagline
        tagline = QLabel("Your voice, your journey, your authentic self")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['primary']};
            font-size: {AriaDesignSystem.FONTS['lg']}pt;
            font-weight: 500;
            margin-bottom: 20px;
        """)
        self.content_layout.addWidget(tagline)

        # Description
        description = QLabel("Aria provides inclusive voice training for everyone - whether you're working on feminization, masculinization, or general voice improvement.")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_primary']};
            font-size: {AriaDesignSystem.FONTS['md']}pt;
            line-height: 1.5;
            margin-bottom: 30px;
        """)
        self.content_layout.addWidget(description)

        # Feature list
        features_text = """Real-time pitch monitoring • Voice exercises • Audio analysis • Progress tracking"""
        features = QLabel(features_text)
        features.setAlignment(Qt.AlignmentFlag.AlignCenter)
        features.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_secondary']};
            font-size: {AriaDesignSystem.FONTS['sm']}pt;
        """)
        self.content_layout.addWidget(features)

        # Spacer
        self.content_layout.addStretch()

    def show_goals_step(self):
        """Goals selection step"""
        self.title_label.setText("What are your voice goals?")
        self.subtitle_label.setText("Choose the option that best fits your needs")

        # Instructions
        instructions = QLabel("Select your primary voice training goal:")
        instructions.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_primary']};
            font-size: {AriaDesignSystem.FONTS['md']}pt;
            margin-bottom: 20px;
        """)
        self.content_layout.addWidget(instructions)

        # Goals dropdown
        self.goals_combo = QComboBox()
        self.goals_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_normal']};
                border-radius: 6px;
                padding: 12px 16px;
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['md']}pt;
                min-height: 20px;
            }}
            QComboBox:hover {{
                border-color: {AriaDesignSystem.COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {AriaDesignSystem.COLORS['bg_secondary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_normal']};
                border-radius: 6px;
                color: {AriaDesignSystem.COLORS['text_primary']};
                selection-background-color: {AriaDesignSystem.COLORS['primary']};
            }}
        """)

        self.goals_combo.addItems([
            "Feminine voice development (MTF)",
            "Masculine voice development (FTM)",
            "Androgynous voice (Non-binary higher)",
            "Androgynous voice (Non-binary lower)",
            "Neutral voice control (Non-binary)",
            "General voice improvement",
            "Singing and performance",
            "Public speaking confidence"
        ])

        self.content_layout.addWidget(self.goals_combo)

        # Note
        note = QLabel("You can change this later in Settings")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_muted']};
            font-size: {AriaDesignSystem.FONTS['sm']}pt;
            font-style: italic;
            margin-top: 16px;
        """)
        self.content_layout.addWidget(note)

        # Spacer
        self.content_layout.addStretch()

    def show_preset_step(self):
        """Preset selection step"""
        self.title_label.setText("Choose your training preset")
        self.subtitle_label.setText("This sets your initial pitch targets")

        # Instructions
        instructions = QLabel("Select a voice preset to start with:")
        instructions.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_primary']};
            font-size: {AriaDesignSystem.FONTS['md']}pt;
            margin-bottom: 20px;
        """)
        self.content_layout.addWidget(instructions)

        # Preset dropdown
        self.preset_combo = QComboBox()
        self.preset_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_normal']};
                border-radius: 6px;
                padding: 12px 16px;
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['md']}pt;
                min-height: 20px;
            }}
            QComboBox:hover {{
                border-color: {AriaDesignSystem.COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {AriaDesignSystem.COLORS['bg_secondary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_normal']};
                border-radius: 6px;
                color: {AriaDesignSystem.COLORS['text_primary']};
                selection-background-color: {AriaDesignSystem.COLORS['primary']};
            }}
        """)

        self.preset_combo.addItems([
            "MTF - Feminine voice training (165-265 Hz)",
            "FTM - Masculine voice training (85-180 Hz)",
            "Non-Binary Higher - Androgynous elevation (180-240 Hz)",
            "Non-Binary Lower - Androgynous deepening (120-200 Hz)",
            "Non-Binary Neutral - Range control (140-220 Hz)",
            "Custom - I'll set my own targets"
        ])

        self.content_layout.addWidget(self.preset_combo)

        # Note
        note = QLabel("Don't worry - the app will adapt as you progress!")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_muted']};
            font-size: {AriaDesignSystem.FONTS['sm']}pt;
            font-style: italic;
            margin-top: 16px;
        """)
        self.content_layout.addWidget(note)

        # Spacer
        self.content_layout.addStretch()

    def show_complete_step(self):
        """Completion step"""
        self.title_label.setText("You're all set!")
        self.subtitle_label.setText("Ready to start your voice training journey")

        # Success message
        success_msg = QLabel("🎉 Your voice training setup is complete!")
        success_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        success_msg.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['success']};
            font-size: {AriaDesignSystem.FONTS['lg']}pt;
            font-weight: 600;
            margin-bottom: 30px;
        """)
        self.content_layout.addWidget(success_msg)

        # Summary
        summary_frame = QFrame()
        summary_frame.setStyleSheet(f"""
            background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
            border-radius: 8px;
            padding: 20px;
        """)
        summary_layout = QVBoxLayout(summary_frame)

        summary_title = QLabel("Your Configuration:")
        summary_title.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_primary']};
            font-size: {AriaDesignSystem.FONTS['md']}pt;
            font-weight: 600;
            margin-bottom: 10px;
        """)
        summary_layout.addWidget(summary_title)

        goals_text = self.config_data.get('voice_goals', 'Not set')
        preset_text = self.config_data.get('voice_preset', 'Not set').split(' - ')[0]

        goals_label = QLabel(f"• Goals: {goals_text}")
        goals_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_secondary']};
            font-size: {AriaDesignSystem.FONTS['sm']}pt;
        """)
        summary_layout.addWidget(goals_label)

        preset_label = QLabel(f"• Preset: {preset_text}")
        preset_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_secondary']};
            font-size: {AriaDesignSystem.FONTS['sm']}pt;
        """)
        summary_layout.addWidget(preset_label)

        self.content_layout.addWidget(summary_frame)

        # Next steps
        next_steps = QLabel("Next: Try the voice exercises or upload an audio file for analysis")
        next_steps.setAlignment(Qt.AlignmentFlag.AlignCenter)
        next_steps.setWordWrap(True)
        next_steps.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_primary']};
            font-size: {AriaDesignSystem.FONTS['md']}pt;
            margin-top: 20px;
        """)
        self.content_layout.addWidget(next_steps)

        # Spacer
        self.content_layout.addStretch()

    def next_step(self):
        """Move to next step"""
        # Save current step data
        if self.current_step == 1 and hasattr(self, 'goals_combo'):
            self.config_data['voice_goals'] = self.goals_combo.currentText()
        elif self.current_step == 2 and hasattr(self, 'preset_combo'):
            self.config_data['voice_preset'] = self.preset_combo.currentText()

        if self.current_step == self.total_steps - 1:
            self.complete_onboarding()
        else:
            self.current_step += 1
            self.update_display()

    def prev_step(self):
        """Move to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self.update_display()

    def cancel_onboarding(self):
        """Cancel onboarding"""
        reply = QMessageBox.question(
            self, 'Cancel Setup',
            'Are you sure you want to cancel the setup?\n\nYou can run setup again from Settings.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.onboarding_cancelled.emit()

    def complete_onboarding(self):
        """Complete onboarding"""
        try:
            config = {
                'setup_completed': True,
                'voice_goals': self.config_data.get('voice_goals', ''),
                'voice_preset': self.config_data.get('voice_preset', ''),
                'onboarding_date': str(datetime.now().isoformat())
            }

            self.onboarding_completed.emit(config)

            QMessageBox.information(
                self, 'Setup Complete',
                'Welcome to Aria Voice Studio!\n\nYour configuration has been saved.',
                QMessageBox.StandardButton.Ok
            )
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "OnboardingWidget.complete_onboarding")

            QMessageBox.critical(
                self, 'Setup Error',
                'There was an error completing the setup.',
                QMessageBox.StandardButton.Ok
            )
            self.onboarding_cancelled.emit()