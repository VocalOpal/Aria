import time
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,  # type: ignore
                            QLabel, QProgressBar, QFrame, QListWidget, QListWidgetItem,
                            QTextEdit, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal  # type: ignore
from PyQt6.QtGui import QFont  # type: ignore
from ..design_system import AriaDesignSystem


class ExerciseItemWidget(QWidget):
    """Clean exercise card following onboarding design patterns"""

    exercise_selected = pyqtSignal(str, dict)

    def __init__(self, exercise_name, exercise_data):
        super().__init__()
        self.exercise_name = exercise_name
        self.exercise_data = exercise_data
        self.init_ui()

    def init_ui(self):
        """Initialize clean exercise card UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Header with title and start button
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        # Title section
        title_section = QVBoxLayout()
        title_section.setSpacing(4)

        # Exercise name
        title = QLabel(self.exercise_data['name'])
        title.setFont(QFont(AriaDesignSystem.FONTS['family_primary'], AriaDesignSystem.FONTS['md'], QFont.Weight.Bold))
        title.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_primary']};
            font-weight: 600;
            background: transparent;
        """)
        title_section.addWidget(title)

        # Duration and focus info
        duration_text = f"{self.exercise_data['duration']}s"
        if self.exercise_data['breathing_focus']:
            duration_text += " • Breathing Focus"

        duration_label = QLabel(duration_text)
        duration_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_muted']};
            font-size: {AriaDesignSystem.FONTS['sm']}pt;
            background: transparent;
        """)
        title_section.addWidget(duration_label)
        header_layout.addLayout(title_section)

        header_layout.addStretch()

        # Start button (matches onboarding next button style)
        start_btn = QPushButton("Start →")
        start_btn.clicked.connect(self.start_exercise)
        start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaDesignSystem.COLORS['primary']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: white;
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-weight: 600;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {AriaDesignSystem.COLORS['primary_hover']};
            }}
        """)
        header_layout.addWidget(start_btn)
        layout.addLayout(header_layout)

        # Instructions
        instructions = QLabel(self.exercise_data['instructions'])
        instructions.setWordWrap(True)
        instructions.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_secondary']};
            font-size: {AriaDesignSystem.FONTS['sm']}pt;
            background: transparent;
            line-height: 1.4;
        """)
        layout.addWidget(instructions)

        # Card styling (matches onboarding content frame)
        self.setStyleSheet(f"""
            ExerciseItemWidget {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: 8px;
                margin: 4px 0px;
            }}
            ExerciseItemWidget:hover {{
                border-color: {AriaDesignSystem.COLORS['border_normal']};
            }}
        """)

    def start_exercise(self):
        """Start this exercise"""
        self.exercise_selected.emit(self.exercise_name, self.exercise_data)


class ActiveExerciseWidget(QWidget):
    """Clean active exercise interface following onboarding design patterns"""

    exercise_stopped = pyqtSignal()

    def __init__(self, exercise_name, exercise_data, voice_trainer):
        super().__init__()
        self.exercise_name = exercise_name
        self.exercise_data = exercise_data
        self.voice_trainer = voice_trainer
        self.training_controller = voice_trainer.training_controller
        self.session_active = False
        self.update_timer = QTimer()
        self.init_ui()
        self.start_exercise()

    def init_ui(self):
        """Initialize clean active exercise UI (follows onboarding single-content-frame pattern)"""
        # Use same layout structure as onboarding
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(24)

        # Single content frame (like onboarding)
        content_frame = QFrame()
        content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AriaDesignSystem.COLORS['bg_secondary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: 12px;
                padding: 32px;
            }}
        """)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setSpacing(24)

        # Exercise header section
        header_section = QVBoxLayout()
        header_section.setSpacing(8)

        # Exercise title (matches onboarding title style)
        title = QLabel(f"Active: {self.exercise_data['name']}")
        title.setFont(QFont(AriaDesignSystem.FONTS['family_primary'], 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['success']};
            margin-bottom: 8px;
        """)
        header_section.addWidget(title)

        # Time remaining
        self.time_label = QLabel("Time remaining: --:--")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_primary']};
            font-size: {AriaDesignSystem.FONTS['md']}pt;
            font-weight: 500;
        """)
        header_section.addWidget(self.time_label)
        content_layout.addLayout(header_section)

        # Progress section (inline, not separate card)
        progress_section = QVBoxLayout()
        progress_section.setSpacing(8)

        progress_label = QLabel("Exercise Progress")
        progress_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_primary']};
            font-size: {AriaDesignSystem.FONTS['md']}pt;
            font-weight: 600;
        """)
        progress_section.addWidget(progress_label)

        # Progress bar (matches onboarding progress bar style)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self.exercise_data['duration'])
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: 6px;
                text-align: center;
                font-weight: 500;
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                color: {AriaDesignSystem.COLORS['text_primary']};
                min-height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {AriaDesignSystem.COLORS['success']};
                border-radius: 5px;
            }}
        """)
        progress_section.addWidget(self.progress_bar)
        content_layout.addLayout(progress_section)

        # Only show relevant metrics based on exercise (cleaner logic)
        relevant_metrics = self.exercise_data.get('metrics_relevant', [])
        if relevant_metrics:
            metrics_section = QVBoxLayout()
            metrics_section.setSpacing(12)

            metrics_title = QLabel("Voice Metrics")
            metrics_title.setStyleSheet(f"""
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['md']}pt;
                font-weight: 600;
            """)
            metrics_section.addWidget(metrics_title)

            # Only show resonance if relevant to this exercise
            if 'resonance' in relevant_metrics:
                self.resonance_label = QLabel("Resonance: Unknown")
                self.resonance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.resonance_label.setStyleSheet(f"""
                    color: {AriaDesignSystem.COLORS['resonance_color']};
                    font-size: {AriaDesignSystem.FONTS['sm']}pt;
                    padding: 8px;
                    border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                    border-radius: 6px;
                    background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                """)
                disclaimer = ("Resonance detection is an approximation. "
                             "True resonance is a bodily, felt experience — this measurement is an aid, not a perfect calculation. "
                             "Results may vary with microphone quality, room acoustics, and voice characteristics.")
                self.resonance_label.setToolTip(disclaimer)
                metrics_section.addWidget(self.resonance_label)
            else:
                self.resonance_label = None

            content_layout.addLayout(metrics_section)

        # Simple display controls (only if relevant metrics exist)
        if relevant_metrics and 'resonance' in relevant_metrics:
            controls_section = QHBoxLayout()
            controls_section.setSpacing(12)

            controls_label = QLabel("Show:")
            controls_label.setStyleSheet(f"""
                color: {AriaDesignSystem.COLORS['text_secondary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
            """)
            controls_section.addWidget(controls_label)

            self.resonance_toggle = QPushButton("Resonance: ON")
            self.resonance_toggle.setCheckable(True)
            self.resonance_toggle.setChecked(True)
            self.resonance_toggle.clicked.connect(self.toggle_resonance_display)
            self.resonance_toggle.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AriaDesignSystem.COLORS['resonance_color']};
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-size: {AriaDesignSystem.FONTS['xs']}pt;
                    font-weight: 500;
                    min-width: 100px;
                }}
                QPushButton:hover {{
                    background-color: #9333ea;
                }}
            """)
            controls_section.addWidget(self.resonance_toggle)
            controls_section.addStretch()
            content_layout.addLayout(controls_section)
        else:
            self.resonance_toggle = None

        # Instructions section (inline within content frame)
        instructions_section = QVBoxLayout()
        instructions_section.setSpacing(12)

        instructions_title = QLabel("Instructions")
        instructions_title.setFont(QFont(AriaDesignSystem.FONTS['family_primary'], AriaDesignSystem.FONTS['md'], QFont.Weight.Bold))
        instructions_title.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_primary']};
            font-weight: 600;
        """)
        instructions_section.addWidget(instructions_title)

        instructions_text = QLabel(self.exercise_data['instructions'])
        instructions_text.setWordWrap(True)
        instructions_text.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_secondary']};
            font-size: {AriaDesignSystem.FONTS['sm']}pt;
            line-height: 1.4;
            padding: 12px;
            border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
            border-radius: 6px;
            background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
        """)
        instructions_section.addWidget(instructions_text)

        # Tips (if available)
        if 'tips' in self.exercise_data and self.exercise_data['tips']:
            tips_text = "\n".join([f"• {tip}" for tip in self.exercise_data['tips']])
            tips_label = QLabel(tips_text)
            tips_label.setWordWrap(True)
            tips_label.setStyleSheet(f"""
                color: {AriaDesignSystem.COLORS['text_muted']};
                font-size: {AriaDesignSystem.FONTS['xs']}pt;
                line-height: 1.3;
                margin-top: 8px;
            """)
            instructions_section.addWidget(tips_label)

        content_layout.addLayout(instructions_section)

        # Breathing quality (if applicable) - inline
        if self.exercise_data['breathing_focus']:
            breathing_section = QVBoxLayout()
            breathing_section.setSpacing(8)

            breathing_title = QLabel("Breathing Quality")
            breathing_title.setStyleSheet(f"""
                color: {AriaDesignSystem.COLORS['success']};
                font-size: {AriaDesignSystem.FONTS['md']}pt;
                font-weight: 600;
            """)
            breathing_section.addWidget(breathing_title)

            self.breathing_bar = QProgressBar()
            self.breathing_bar.setRange(0, 100)
            self.breathing_bar.setValue(0)
            self.breathing_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid {AriaDesignSystem.COLORS['success']};
                    border-radius: 6px;
                    text-align: center;
                    background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                    color: {AriaDesignSystem.COLORS['text_primary']};
                    font-size: {AriaDesignSystem.FONTS['xs']}pt;
                    min-height: 18px;
                }}
                QProgressBar::chunk {{
                    background-color: {AriaDesignSystem.COLORS['success']};
                    border-radius: 5px;
                }}
            """)
            breathing_section.addWidget(self.breathing_bar)
            content_layout.addLayout(breathing_section)
        else:
            self.breathing_bar = None

        # Status and stop button (at bottom of content frame)
        status_section = QVBoxLayout()
        status_section.setSpacing(16)

        # Status message
        self.status_label = QLabel("Starting exercise...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_muted']};
            font-size: {AriaDesignSystem.FONTS['sm']}pt;
            font-style: italic;
            padding: 8px;
            border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
            border-radius: 6px;
            background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
        """)
        status_section.addWidget(self.status_label)

        # Stop button (matches onboarding back button style)
        self.stop_btn = QPushButton("Stop Exercise")
        self.stop_btn.clicked.connect(self.stop_exercise)
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaDesignSystem.COLORS['error']};
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                color: white;
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-weight: 600;
                min-height: 36px;
            }}
            QPushButton:hover {{
                background-color: #dc2626;
            }}
        """)
        status_section.addWidget(self.stop_btn)
        content_layout.addLayout(status_section)

        # Add content frame to main layout
        main_layout.addWidget(content_frame)

    def start_exercise(self):
        """Start the actual exercise with audio processing"""
        try:
            # Start real exercise session through training controller
            success = self.training_controller.start_exercise(
                self.exercise_name,
                self.exercise_data,
                self.handle_exercise_callback
            )

            if success:
                self.session_active = True
                self.update_timer.timeout.connect(self.update_display)
                self.update_timer.start(100)  # 10 FPS updates
                self.status_label.setText("Exercise active - follow the instructions above")
                self.status_label.setStyleSheet("color: #4CAF50;")
            else:
                self.status_label.setText("Error: Could not start exercise audio system")
                self.status_label.setStyleSheet("color: #f44336;")

        except Exception as e:
            self.status_label.setText(f"Error starting exercise: {e}")
            self.status_label.setStyleSheet("color: #f44336;")

    def handle_exercise_callback(self, callback_type, data):
        """Handle callbacks from training controller during exercise"""
        if callback_type == 'training_status':
            # Update breathing quality if this exercise focuses on breathing
            if self.breathing_frame and 'exercise_info' in data:
                # Get breathing quality from the session (this would come from BreathingTracker)
                pass

        elif callback_type == 'exercise_complete':
            completion_rate = data.get('completion_rate', 0)
            self.status_label.setText(f"Exercise completed! ({completion_rate*100:.1f}% completion)")
            self.status_label.setStyleSheet("color: #4CAF50;")
            self.stop_exercise()

        elif callback_type == 'noise_feedback':
            message = data.get('message', '')
            self.status_label.setText(message)
            self.status_label.setStyleSheet("color: #FFC107;")

    def update_display(self):
        """Update exercise progress display"""
        if not self.session_active:
            return

        try:
            # Get remaining time from training controller
            if (self.training_controller.current_exercise and
                hasattr(self.training_controller.current_exercise, 'get_remaining_time')):

                remaining = self.training_controller.current_exercise.get_remaining_time()
                if remaining <= 0:
                    self.stop_exercise()
                    return

                # Update progress bar
                elapsed = self.exercise_data['duration'] - remaining
                self.progress_bar.setValue(int(elapsed))

                # Update time display
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)
                self.time_label.setText(f"Time remaining: {minutes:02d}:{seconds:02d}")

                # Update breathing quality if applicable
                if (self.breathing_frame and self.training_controller.current_exercise and
                    hasattr(self.training_controller.current_exercise, 'breathing_tracker')):

                    tracker = self.training_controller.current_exercise.breathing_tracker
                    if tracker:
                        quality = tracker.get_quality_score() * 100
                        self.breathing_bar.setValue(int(quality))

                # Update resonance display (only if toggle is enabled)
                try:
                    if (hasattr(self, 'resonance_toggle') and self.resonance_toggle.isChecked() and
                        hasattr(self.voice_trainer, 'audio_coordinator') and
                        self.voice_trainer.audio_coordinator and
                        hasattr(self.voice_trainer.audio_coordinator, 'analyzer')):
                        analyzer = self.voice_trainer.audio_coordinator.analyzer
                        if analyzer and hasattr(analyzer, 'current_resonance'):
                            resonance_data = analyzer.current_resonance
                            if resonance_data and resonance_data.get('quality') != 'Unknown':
                                freq = resonance_data.get('frequency', 0)
                                quality = resonance_data.get('quality', 'Unknown')
                                self.resonance_label.setText(f"Resonance: {quality} (approx. {freq:.0f} Hz)")
                            else:
                                self.resonance_label.setText("Resonance: Unknown")
                        else:
                            self.resonance_label.setText("Resonance: Unknown")
                    elif hasattr(self, 'resonance_toggle') and not self.resonance_toggle.isChecked():
                        self.resonance_label.setText("Resonance: Hidden")
                except (AttributeError, RuntimeError):
                    # Audio analyzer not available or deleted
                    if hasattr(self, 'resonance_toggle') and self.resonance_toggle.isChecked():
                        self.resonance_label.setText("Resonance: Unknown")

        except Exception as e:
            # Silently handle update errors
            pass

    def stop_exercise(self):
        """Stop the exercise session"""
        try:
            if self.session_active:
                completion_rate = self.training_controller.stop_exercise()
                self.session_active = False
                self.update_timer.stop()

                if completion_rate >= 1.0:
                    self.status_label.setText("Exercise completed successfully!")
                    self.status_label.setStyleSheet("color: #4CAF50;")
                else:
                    self.status_label.setText(f"Exercise stopped ({completion_rate*100:.1f}% completed)")
                    self.status_label.setStyleSheet("color: #888;")

            self.exercise_stopped.emit()

        except Exception as e:
            self.status_label.setText(f"Error stopping exercise: {e}")
            self.status_label.setStyleSheet("color: #f44336;")


    def toggle_resonance_display(self):
        """Toggle resonance metrics display"""
        if not self.resonance_toggle:
            return

        if self.resonance_toggle.isChecked():
            self.resonance_toggle.setText("Resonance: ON")
            self.resonance_toggle.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AriaDesignSystem.COLORS['resonance_color']};
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-size: {AriaDesignSystem.FONTS['xs']}pt;
                    font-weight: 500;
                    min-width: 100px;
                }}
                QPushButton:hover {{
                    background-color: #9333ea;
                }}
            """)
            if hasattr(self, 'resonance_label') and self.resonance_label:
                self.resonance_label.show()
        else:
            self.resonance_toggle.setText("Resonance: OFF")
            self.resonance_toggle.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AriaDesignSystem.COLORS['border_normal']};
                    color: {AriaDesignSystem.COLORS['text_primary']};
                    border: none;
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-size: {AriaDesignSystem.FONTS['xs']}pt;
                    font-weight: 500;
                    min-width: 100px;
                }}
                QPushButton:hover {{
                    background-color: {AriaDesignSystem.COLORS['border_strong']};
                }}
            """)
            if hasattr(self, 'resonance_label') and self.resonance_label:
                self.resonance_label.hide()


class ExercisesScreen(QWidget):
    """Voice exercises and warm-ups interface"""

    back_requested = pyqtSignal()

    def __init__(self, voice_trainer):
        super().__init__()
        self.voice_trainer = voice_trainer
        self.exercises_component = None
        self.active_exercise_widget = None
        self.retry_timer = QTimer()
        self.retry_timer.setSingleShot(True)
        self.retry_timer.timeout.connect(self.retry_load_exercises)
        self.init_ui()
        self.load_exercises()

    def init_ui(self):
        """Initialize exercises screen UI (matches onboarding layout structure)"""
        # Main layout with consistent spacing like onboarding
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(30)

        # Header section (mirrors onboarding design)
        self.create_header(main_layout)

        # Content area with proper spacing
        self.create_content_area(main_layout)

        # Apply consistent styling
        self.setStyleSheet(f"""
            ExercisesScreen {{
                background-color: {AriaDesignSystem.COLORS['bg_primary']};
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-family: {AriaDesignSystem.FONTS['family_primary']};
            }}
            QScrollArea {{
                background-color: {AriaDesignSystem.COLORS['bg_primary']};
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: {AriaDesignSystem.COLORS['bg_primary']};
            }}
        """)

        # Initially show exercises list
        self.show_exercises_list()

    def create_header(self, layout):
        """Create clean header section (matches onboarding design)"""
        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(16)

        # Navigation bar
        nav_bar = QWidget()
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(16)

        # Back button (consistent with onboarding cancel button)
        self.back_btn = QPushButton("← Back to Menu")
        self.back_btn.clicked.connect(self.back_requested.emit)
        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {AriaDesignSystem.COLORS['border_normal']};
                border-radius: 6px;
                padding: 10px 20px;
                color: {AriaDesignSystem.COLORS['text_secondary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                color: {AriaDesignSystem.COLORS['text_primary']};
            }}
        """)
        nav_layout.addWidget(self.back_btn)

        # Spacer
        nav_layout.addStretch()

        # Warmup routine button (positioned like a primary action)
        self.warmup_btn = QPushButton("Start 5-Min Warm-up")
        self.warmup_btn.clicked.connect(self.start_warmup_routine)
        self.warmup_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaDesignSystem.COLORS['primary']};
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                color: white;
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-weight: 600;
                min-width: 140px;
            }}
            QPushButton:hover {{
                background-color: {AriaDesignSystem.COLORS['primary_hover']};
            }}
        """)
        nav_layout.addWidget(self.warmup_btn)
        header_layout.addWidget(nav_bar)

        # Title section (mirrors onboarding header)
        title_section = QWidget()
        title_layout = QVBoxLayout(title_section)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)

        # Main title (matches onboarding title exactly)
        self.title_label = QLabel("Voice Exercises & Warm-ups")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont(AriaDesignSystem.FONTS['family_primary'], 22, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['primary']};
            margin-bottom: 8px;
        """)
        title_layout.addWidget(self.title_label)

        # Subtitle (matches onboarding subtitle style)
        self.subtitle_label = QLabel("Guided exercises to improve your voice quality and control")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_secondary']};
            font-size: {AriaDesignSystem.FONTS['md']}pt;
        """)
        title_layout.addWidget(self.subtitle_label)
        header_layout.addWidget(title_section)

        layout.addWidget(header_container)

    def create_content_area(self, layout):
        """Create main content area (similar to onboarding content frame)"""
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AriaDesignSystem.COLORS['bg_secondary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: 12px;
                padding: 40px;
            }}
        """)

        # This will be populated by show_exercises_list or show_active_exercise
        self.content_area = QWidget()
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.content_area)

        layout.addWidget(self.content_frame)

    def load_exercises(self):
        """Load exercises from component factory"""
        try:
            self.exercises_component = self.voice_trainer.factory.get_component('voice_exercises')
            # If loading succeeded, refresh the display
            if hasattr(self, 'content_area'):
                self.show_exercises_list()
        except Exception as e:
            self.exercises_component = None
            # Retry after a short delay
            if not self.retry_timer.isActive():
                self.retry_timer.start(2000)  # Retry after 2 seconds

    def retry_load_exercises(self):
        """Retry loading exercises after a delay"""
        self.load_exercises()

    def show_exercises_list(self):
        """Show list of available exercises"""
        # Clear content area
        if self.content_area.layout():
            while self.content_area.layout().count():
                child = self.content_area.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            self.content_area.setLayout(QVBoxLayout())

        layout = self.content_area.layout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Exercises scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")

        exercises_widget = QWidget()
        exercises_layout = QVBoxLayout(exercises_widget)
        exercises_layout.setSpacing(12)  # Consistent spacing

        # Try to reload exercises component if it failed initially
        if not self.exercises_component:
            self.load_exercises()

        if self.exercises_component:
            try:
                # With new modular structure, exercises_component is a dictionary of exercise instances
                exercises = self.exercises_component

                if exercises:
                    for exercise_name, exercise_instance in exercises.items():
                        exercise_data = exercise_instance.get_exercise_data()
                        exercise_item = ExerciseItemWidget(exercise_name, exercise_data)
                        exercise_item.exercise_selected.connect(self.start_single_exercise)
                        exercises_layout.addWidget(exercise_item)
                else:
                    # No exercises found - clean message
                    no_exercises = QLabel("No exercises available - component may still be initializing")
                    no_exercises.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    no_exercises.setStyleSheet(f"""
                        color: {AriaDesignSystem.COLORS['text_muted']};
                        font-size: {AriaDesignSystem.FONTS['md']}pt;
                        padding: 40px;
                    """)
                    exercises_layout.addWidget(no_exercises)
            except Exception as e:
                # Clean error message
                error_message = QLabel(f"Error loading exercises: {str(e)}")
                error_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
                error_message.setWordWrap(True)
                error_message.setStyleSheet(f"""
                    color: {AriaDesignSystem.COLORS['error']};
                    font-size: {AriaDesignSystem.FONTS['md']}pt;
                    padding: 40px;
                """)
                exercises_layout.addWidget(error_message)
        else:
            # Clean error message
            component_error = QLabel("Component Loading Error - Please restart the application")
            component_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
            component_error.setStyleSheet(f"""
                color: {AriaDesignSystem.COLORS['error']};
                font-size: {AriaDesignSystem.FONTS['md']}pt;
                padding: 40px;
            """)
            exercises_layout.addWidget(component_error)

        scroll_area.setWidget(exercises_widget)
        layout.addWidget(scroll_area)

    def start_single_exercise(self, exercise_name, exercise_data):
        """Start a single exercise"""
        self.show_active_exercise(exercise_name, exercise_data)

    def start_warmup_routine(self):
        """Start the full warm-up routine"""
        # For now, start with the first exercise in the warmup sequence
        # TODO: Implement full routine manager
        if self.exercises_component:
            sequence = self.exercises_component.get_warmup_sequence()
            if sequence:
                first_exercise = sequence[0]
                exercise_data = self.exercises_component.get_exercise(first_exercise)
                if exercise_data:
                    self.show_active_exercise(first_exercise, exercise_data)

    def show_active_exercise(self, exercise_name, exercise_data):
        """Show active exercise interface"""
        # Clear content area
        if self.content_area.layout():
            while self.content_area.layout().count():
                child = self.content_area.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            self.content_area.setLayout(QVBoxLayout())

        layout = self.content_area.layout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create active exercise widget
        self.active_exercise_widget = ActiveExerciseWidget(exercise_name, exercise_data, self.voice_trainer)
        self.active_exercise_widget.exercise_stopped.connect(self.show_exercises_list)
        layout.addWidget(self.active_exercise_widget)

    def cleanup(self):
        """Clean up resources when leaving screen"""
        if self.active_exercise_widget:
            self.active_exercise_widget.stop_exercise()