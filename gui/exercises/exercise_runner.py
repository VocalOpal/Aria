<<<<<<< HEAD
"""
ExerciseRunner - Clean inline runner panel for active exercises.

Usage:
    from gui.exercises.exercise_runner import ExerciseRunner
    runner = ExerciseRunner(exercise_spec, voice_trainer)
    runner.start_exercise()
"""

import time
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QProgressBar, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from ..design_system import AriaDesignSystem


class ExerciseRunner(QWidget):
    """Clean inline runner for active exercises - no nested frames"""

    exercise_stopped = pyqtSignal()

    def __init__(self, exercise_spec, voice_trainer):
        super().__init__()
        self.exercise_spec = exercise_spec
        self.voice_trainer = voice_trainer
        self.training_controller = voice_trainer.training_controller if voice_trainer else None
        self.session_active = False
        self.start_time = None
        self.update_timer = QTimer()
        self.init_ui()

    def init_ui(self):
        """Initialize clean runner UI - flat design with proper spacing"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header - exercise name and status
        self.create_header(layout)

        # Progress section
        self.create_progress_section(layout)

        # Metrics (only if required by exercise)
        self.create_metrics_section(layout)

        # Instructions
        self.create_instructions_section(layout)

        # Controls
        self.create_controls_section(layout)

        layout.addStretch()

    def create_header(self, layout):
        """Create clean header without frames"""
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)

        # Exercise name
        title = QLabel(f"Active: {self.exercise_spec.name}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont(AriaDesignSystem.FONTS['family_primary'], 18, QFont.Weight.Bold))
        title.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['success']};
            margin-bottom: 4px;
        """)
        header_layout.addWidget(title)

        # Time remaining
        self.time_label = QLabel("Starting...")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_primary']};
            font-size: {AriaDesignSystem.FONTS['md']}pt;
            font-weight: 500;
        """)
        header_layout.addWidget(self.time_label)

        layout.addLayout(header_layout)

    def create_progress_section(self, layout):
        """Create progress bar without frame wrapper"""
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(8)

        # Progress label
        progress_label = QLabel("Progress")
        progress_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_primary']};
            font-size: {AriaDesignSystem.FONTS['sm']}pt;
            font-weight: 600;
        """)
        progress_layout.addWidget(progress_label)

        # Progress bar - clean styling
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self.exercise_spec.default_duration)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: 6px;
                text-align: center;
                font-weight: 500;
                font-size: {AriaDesignSystem.FONTS['xs']}pt;
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                color: {AriaDesignSystem.COLORS['text_primary']};
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {AriaDesignSystem.COLORS['success']};
                border-radius: 5px;
            }}
        """)
        progress_layout.addWidget(self.progress_bar)

        layout.addLayout(progress_layout)

    def create_metrics_section(self, layout):
        """Create metrics section - only show required metrics"""
        metrics_required = self.exercise_spec.get_metrics_required()
        if not metrics_required:
            return

        metrics_layout = QVBoxLayout()
        metrics_layout.setSpacing(12)

        # Section title
        metrics_title = QLabel("Live Metrics")
        metrics_title.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_primary']};
            font-size: {AriaDesignSystem.FONTS['sm']}pt;
            font-weight: 600;
        """)
        metrics_layout.addWidget(metrics_title)

        # Only show pitch if exercise requires it
        if self.exercise_spec.requires_pitch:
            self.pitch_label = QLabel("Pitch: --")
            self.pitch_label.setStyleSheet(f"""
                color: {AriaDesignSystem.COLORS['text_secondary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                padding: 8px 12px;
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                border-radius: 6px;
            """)
            metrics_layout.addWidget(self.pitch_label)
        else:
            self.pitch_label = None

        # Only show resonance if exercise requires it
        if self.exercise_spec.requires_resonance:
            self.resonance_label = QLabel("Resonance: --")
            self.resonance_label.setStyleSheet(f"""
                color: {AriaDesignSystem.COLORS['resonance_color']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                padding: 8px 12px;
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                border-radius: 6px;
            """)
            metrics_layout.addWidget(self.resonance_label)
        else:
            self.resonance_label = None

        # Only show breathing if exercise requires it
        if self.exercise_spec.requires_breathing:
            self.breathing_label = QLabel("Breathing Quality")
            self.breathing_label.setStyleSheet(f"""
                color: {AriaDesignSystem.COLORS['success']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-weight: 600;
            """)
            metrics_layout.addWidget(self.breathing_label)

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
                    height: 18px;
                    font-size: {AriaDesignSystem.FONTS['xs']}pt;
                }}
                QProgressBar::chunk {{
                    background-color: {AriaDesignSystem.COLORS['success']};
                    border-radius: 5px;
                }}
            """)
            metrics_layout.addWidget(self.breathing_bar)
        else:
            self.breathing_label = None
            self.breathing_bar = None

        layout.addLayout(metrics_layout)

    def create_instructions_section(self, layout):
        """Create instructions without frame wrapper"""
        inst_layout = QVBoxLayout()
        inst_layout.setSpacing(8)

        # Instructions title
        inst_title = QLabel("Instructions")
        inst_title.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_primary']};
            font-size: {AriaDesignSystem.FONTS['sm']}pt;
            font-weight: 600;
        """)
        inst_layout.addWidget(inst_title)

        # Instructions text - clean background
        inst_text = QLabel(self.exercise_spec.instructions)
        inst_text.setWordWrap(True)
        inst_text.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_secondary']};
            font-size: {AriaDesignSystem.FONTS['sm']}pt;
            line-height: 1.4;
            padding: 12px;
            background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
            border-radius: 6px;
        """)
        inst_layout.addWidget(inst_text)

        layout.addLayout(inst_layout)

    def create_controls_section(self, layout):
        """Create control buttons"""
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)

        # Status label
        self.status_label = QLabel("Ready to start")
        self.status_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_muted']};
            font-size: {AriaDesignSystem.FONTS['sm']}pt;
        """)
        controls_layout.addWidget(self.status_label)
        controls_layout.addStretch()

        # Stop button
        self.stop_btn = QPushButton("Stop Exercise")
        self.stop_btn.clicked.connect(self.stop_exercise)
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaDesignSystem.COLORS['error']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: white;
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-weight: 600;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: #dc2626;
            }}
        """)
        controls_layout.addWidget(self.stop_btn)

        layout.addLayout(controls_layout)

    def start_exercise(self):
        """Start the exercise session"""
        self.session_active = True
        self.start_time = time.time()

        # Start update timer
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(100)  # 10 FPS updates

        self.status_label.setText("Exercise active")
        self.status_label.setStyleSheet(f"color: {AriaDesignSystem.COLORS['success']};")

        # Start actual exercise session if training controller available
        if self.training_controller:
            try:
                self.training_controller.start_exercise(
                    self.exercise_spec.name.lower().replace(' ', '_'),
                    self.exercise_spec.__dict__,
                    self.handle_exercise_callback
                )
            except Exception as e:
                self.status_label.setText(f"Error: {e}")
                self.status_label.setStyleSheet(f"color: {AriaDesignSystem.COLORS['error']};")

    def handle_exercise_callback(self, callback_type, data):
        """Handle callbacks from training controller"""
        if callback_type == 'exercise_complete':
            self.stop_exercise()
        elif callback_type == 'noise_feedback':
            message = data.get('message', '')
            self.status_label.setText(message)

    def update_display(self):
        """Update exercise progress display"""
        if not self.session_active:
            return

        # Calculate remaining time
        current_time = time.time()
        elapsed = current_time - self.start_time if self.start_time else 0
        remaining = max(0, self.exercise_spec.default_duration - elapsed)

        if remaining <= 0:
            self.stop_exercise()
            return

        # Update progress bar
        self.progress_bar.setValue(int(elapsed))

        # Update time display
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        self.time_label.setText(f"Time remaining: {minutes:02d}:{seconds:02d}")

        # Update metrics if available
        self.update_metrics()

    def update_metrics(self):
        """Update live metrics display"""
        if not self.voice_trainer or not hasattr(self.voice_trainer, 'audio_coordinator'):
            return

        try:
            analyzer = getattr(self.voice_trainer.audio_coordinator, 'analyzer', None)
            if not analyzer:
                return

            # Update pitch if required and label exists
            if self.pitch_label and hasattr(analyzer, 'current_pitch'):
                pitch = getattr(analyzer, 'current_pitch', 0)
                if pitch > 0:
                    self.pitch_label.setText(f"Pitch: {pitch:.0f} Hz")
                else:
                    self.pitch_label.setText("Pitch: --")

            # Update resonance if required and label exists
            if self.resonance_label and hasattr(analyzer, 'current_resonance'):
                resonance_data = getattr(analyzer, 'current_resonance', {})
                if resonance_data and resonance_data.get('quality') != 'Unknown':
                    freq = resonance_data.get('frequency', 0)
                    quality = resonance_data.get('quality', 'Unknown')
                    self.resonance_label.setText(f"Resonance: {quality} ({freq:.0f} Hz)")
                else:
                    self.resonance_label.setText("Resonance: --")

            # Update breathing if required and bar exists
            if self.breathing_bar and hasattr(analyzer, 'breathing_quality'):
                quality = getattr(analyzer, 'breathing_quality', 0)
                self.breathing_bar.setValue(int(quality * 100))

        except (AttributeError, RuntimeError):
            # Handle case where widgets or analyzer are deleted/unavailable
            pass

    def stop_exercise(self):
        """Stop the exercise session"""
        self.session_active = False
        self.update_timer.stop()

        # Stop training controller session
        if self.training_controller:
            try:
                completion_rate = self.training_controller.stop_exercise()
                if completion_rate >= 1.0:
                    self.status_label.setText("Exercise completed!")
                    self.status_label.setStyleSheet(f"color: {AriaDesignSystem.COLORS['success']};")
                else:
                    self.status_label.setText(f"Exercise stopped ({completion_rate*100:.0f}% complete)")
                    self.status_label.setStyleSheet(f"color: {AriaDesignSystem.COLORS['text_muted']};")
            except Exception:
                self.status_label.setText("Exercise stopped")
                self.status_label.setStyleSheet(f"color: {AriaDesignSystem.COLORS['text_muted']};")

        self.exercise_stopped.emit()

    def cleanup(self):
        """Clean up resources"""
        if self.session_active:
            self.stop_exercise()