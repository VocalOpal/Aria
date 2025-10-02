
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from ..design_system import (
    AriaColors, AriaTypography, AriaSpacing, AriaRadius,
    InfoCard, PrimaryButton, SecondaryButton, CircularProgress, create_gradient_background,
    TitleLabel, HeadingLabel, BodyLabel, CaptionLabel, create_scroll_container
)

# Import exercise specs from old GUI
from gui.exercises.exercise_spec import (
    ExerciseSpec, create_breathing_spec, create_humming_spec,
    create_pitch_slides_spec, create_lip_trills_spec,
    create_resonance_shift_spec, create_straw_phonation_spec
)


class ExerciseCard(QFrame):
    """Individual exercise card with gradient styling"""

    clicked = pyqtSignal(ExerciseSpec)

    def __init__(self, exercise_spec):
        super().__init__()
        self.exercise_spec = exercise_spec
        self.init_ui()

    def init_ui(self):
        """Initialize exercise card UI"""
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(200)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {AriaColors.CARD_BG_LIGHT},
                    stop:1 {AriaColors.CARD_BG_PINK_LIGHT}
                );
                border-radius: {AriaRadius.LG}px;
                border: 1px solid {AriaColors.WHITE_25};
            }}
            QFrame:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(111, 162, 200, 0.5),
                    stop:1 rgba(232, 151, 189, 0.5)
                );
                border: 1px solid {AriaColors.WHITE_45};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL)
        layout.setSpacing(AriaSpacing.MD)

        # Exercise name
        layout.addWidget(HeadingLabel(self.exercise_spec.name))

        # Description
        desc_label = BodyLabel(self.exercise_spec.description)
        desc_label.setStyleSheet(f"""
            color: {AriaColors.WHITE_85};
            font-size: {AriaTypography.BODY_SMALL}px;
            background: transparent;
        """)
        layout.addWidget(desc_label)

        # Difficulty badge
        difficulty_badge = QLabel(self.exercise_spec.difficulty)
        difficulty_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        difficulty_badge.setFixedHeight(24)
        difficulty_badge.setStyleSheet(f"""
            color: white;
            background-color: {self.exercise_spec.get_difficulty_color()};
            border-radius: 12px;
            padding: 4px 12px;
            font-size: {AriaTypography.BODY_SMALL}px;
            font-weight: 500;
        """)
        layout.addWidget(difficulty_badge, alignment=Qt.AlignmentFlag.AlignLeft)

        # Duration
        duration_label = QLabel(f"Duration: {self.exercise_spec.format_duration()}")
        duration_label.setStyleSheet(f"""
            color: {AriaColors.WHITE_70};
            font-size: {AriaTypography.BODY_SMALL}px;
            background: transparent;
        """)
        layout.addWidget(duration_label)

        layout.addStretch()

        # Start button
        start_btn = PrimaryButton("Start Exercise")
        start_btn.setMinimumSize(140, 40)
        start_btn.clicked.connect(lambda: self.clicked.emit(self.exercise_spec))
        layout.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def mousePressEvent(self, event):
        """Handle click on card"""
        self.clicked.emit(self.exercise_spec)
        super().mousePressEvent(event)


class ExerciseRunnerView(QWidget):
    """Active exercise runner with timer and real-time feedback"""

    exercise_completed = pyqtSignal()
    exercise_stopped = pyqtSignal()

    def __init__(self, exercise_spec, voice_trainer):
        super().__init__()
        self.exercise_spec = exercise_spec
        self.voice_trainer = voice_trainer
        self.training_controller = voice_trainer.training_controller
        self.session_active = False
        self.start_time = 0
        self.elapsed_time = 0

        # Real-time data
        self.current_pitch = 0

        self.init_ui()

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.setInterval(100)  # 10 FPS

    def init_ui(self):
        """Initialize exercise runner UI"""
        # Gradient background
        content = QFrame()
        content.setStyleSheet(create_gradient_background())

        layout = QVBoxLayout(content)
        layout.setContentsMargins(AriaSpacing.GIANT, AriaSpacing.GIANT, AriaSpacing.GIANT, AriaSpacing.GIANT)
        layout.setSpacing(AriaSpacing.XL)

        # Title
        title = QLabel(self.exercise_spec.name)
        title.setStyleSheet(f"""
            color: white;
            font-size: {AriaTypography.TITLE}px;
            font-weight: bold;
            background: transparent;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Instructions card
        inst_card = InfoCard("Instructions", min_height=120)
        inst_label = QLabel(self.exercise_spec.instructions)
        inst_label.setWordWrap(True)
        inst_label.setStyleSheet(f"color: white; font-size: {AriaTypography.BODY}px; background: transparent;")
        inst_card.content_layout.addWidget(inst_label)
        layout.addWidget(inst_card)

        # Progress row
        progress_row = QHBoxLayout()
        progress_row.setSpacing(AriaSpacing.LG)

        # Circular timer
        timer_card = InfoCard("Timer", min_height=260)
        self.progress_circle = CircularProgress(percentage=0, size=140)
        timer_card.content_layout.addWidget(self.progress_circle, alignment=Qt.AlignmentFlag.AlignCenter)
        self.time_label = QLabel(f"0 / {self.exercise_spec.default_duration}s")
        self.time_label.setStyleSheet(f"color: white; font-size: {AriaTypography.BODY}px; font-weight: 600; background: transparent; margin-top: 8px;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_card.content_layout.addWidget(self.time_label)
        progress_row.addWidget(timer_card)

        # Metrics card (if exercise requires pitch)
        if self.exercise_spec.requires_pitch:
            metrics_card = InfoCard("Live Feedback", min_height=260)

            self.pitch_label = QLabel("-- Hz")
            self.pitch_label.setStyleSheet("color: white; font-size: 36px; font-weight: bold; background: transparent;")
            self.pitch_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            metrics_card.content_layout.addWidget(self.pitch_label)

            if self.exercise_spec.target_pitch_range[0] > 0:
                target_label = QLabel(f"Target: {self.exercise_spec.target_pitch_range[0]}-{self.exercise_spec.target_pitch_range[1]} Hz")
                target_label.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.BODY_SMALL}px; background: transparent;")
                target_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                metrics_card.content_layout.addWidget(target_label)

            progress_row.addWidget(metrics_card)

        layout.addLayout(progress_row)

        # Tips card
        if self.exercise_spec.tips:
            tips_card = InfoCard("Tips", min_height=150)
            tips_html = "<ul style='margin: 0; padding-left: 20px;'>"
            for tip in self.exercise_spec.tips[:3]:  # Show first 3 tips
                tips_html += f"<li style='margin-bottom: 6px;'>{tip}</li>"
            tips_html += "</ul>"
            tips_label = QLabel(tips_html)
            tips_label.setWordWrap(True)
            tips_label.setStyleSheet(f"color: {AriaColors.WHITE_85}; font-size: {AriaTypography.BODY_SMALL}px; background: transparent;")
            tips_card.content_layout.addWidget(tips_label)
            layout.addWidget(tips_card)

        # Control buttons
        controls = QHBoxLayout()
        controls.setSpacing(AriaSpacing.LG)
        controls.addStretch()

        self.start_stop_btn = PrimaryButton("Start Exercise")
        self.start_stop_btn.setMinimumSize(180, 56)
        self.start_stop_btn.clicked.connect(self.toggle_exercise)
        controls.addWidget(self.start_stop_btn)

        stop_btn = SecondaryButton("Back to List")
        stop_btn.setMinimumSize(140, 44)
        stop_btn.clicked.connect(self.handle_back)
        controls.addWidget(stop_btn)

        controls.addStretch()
        layout.addLayout(controls)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(content)

    def toggle_exercise(self):
        """Toggle exercise start/stop"""
        if self.session_active:
            self.stop_exercise()
        else:
            self.start_exercise()

    def start_exercise(self):
        """Start exercise with backend integration"""
        try:
            import time
            self.session_active = True
            self.start_time = time.time()
            self.elapsed_time = 0

            # Update UI
            self.start_stop_btn.setText("Stop Exercise")

            # Start backend if exercise requires pitch
            if self.exercise_spec.requires_pitch and self.training_controller:
                config = self.voice_trainer.config_manager.get_config()
                self.training_controller.start_live_training(config, self.handle_audio_callback)

            # Start timer
            self.update_timer.start()

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "ExerciseRunnerView.start_exercise")

    def stop_exercise(self):
        """Stop exercise"""
        try:
            self.session_active = False

            # Stop backend
            if self.exercise_spec.requires_pitch and self.training_controller:
                self.training_controller.stop_live_training()

            # Stop timer
            self.update_timer.stop()

            # Update UI
            self.start_stop_btn.setText("Start Exercise")

            # Save progress
            self.save_exercise_progress()

            # Check if completed
            if self.elapsed_time >= self.exercise_spec.default_duration:
                self.exercise_completed.emit()
            else:
                self.exercise_stopped.emit()

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "ExerciseRunnerView.stop_exercise")

    def handle_audio_callback(self, callback_type, data):
        """Handle audio callbacks from training controller"""
        if callback_type == 'training_status':
            self.current_pitch = data.get('pitch', 0)

    def update_display(self):
        """Update timer and metrics"""
        if not self.session_active:
            return

        import time
        self.elapsed_time = int(time.time() - self.start_time)

        # Update progress circle
        progress_pct = min(100, (self.elapsed_time / self.exercise_spec.default_duration) * 100)
        self.progress_circle.set_percentage(progress_pct)

        # Update time label
        remaining = max(0, self.exercise_spec.default_duration - self.elapsed_time)
        self.time_label.setText(f"{self.elapsed_time} / {self.exercise_spec.default_duration}s\n({remaining}s remaining)")

        # Update pitch if available
        if self.exercise_spec.requires_pitch and self.current_pitch > 0:
            self.pitch_label.setText(f"{int(self.current_pitch)} Hz")

            # Check if in target range
            if self.exercise_spec.target_pitch_range[0] > 0:
                min_hz, max_hz = self.exercise_spec.target_pitch_range
                if min_hz <= self.current_pitch <= max_hz:
                    self.pitch_label.setStyleSheet("color: #52C55A; font-size: 36px; font-weight: bold; background: transparent;")
                else:
                    self.pitch_label.setStyleSheet("color: white; font-size: 36px; font-weight: bold; background: transparent;")

        # Auto-complete when time is up
        if self.elapsed_time >= self.exercise_spec.default_duration:
            self.stop_exercise()

    def save_exercise_progress(self):
        """Save exercise progress to backend"""
        try:
            progress_data = {
                'exercise_name': self.exercise_spec.name,
                'duration': self.elapsed_time,
                'completed': self.elapsed_time >= self.exercise_spec.default_duration,
                'timestamp': import_time_now().isoformat()
            }

            # TODO: Save to session_manager when exercise history is implemented
            # self.voice_trainer.session_manager.save_exercise_result(progress_data)

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "ExerciseRunnerView.save_exercise_progress")

    def handle_back(self):
        """Handle back button"""
        if self.session_active:
            self.stop_exercise()
        self.exercise_stopped.emit()

    def cleanup(self):
        """Cleanup resources"""
        if self.session_active:
            self.stop_exercise()
        if self.update_timer:
            self.update_timer.stop()


class ExercisesScreen(QWidget):
    """Main exercises screen with category-based layout"""

    def __init__(self, voice_trainer):
        super().__init__()
        self.voice_trainer = voice_trainer
        self.current_view = "list"  # "list" or "runner"
        self.current_runner = None

        # Load exercises from backend
        self.exercises = self.load_exercises()

        self.init_ui()

    def load_exercises(self):
        """Load exercise specs from backend"""
        # Create exercises using backend specs
        exercises = {
            'warmup': [
                create_breathing_spec(),
                create_humming_spec(),
                create_lip_trills_spec()
            ],
            'resonance': [
                create_resonance_shift_spec(),
                create_pitch_slides_spec()
            ],
            'advanced': [
                create_straw_phonation_spec()
            ]
        }
        return exercises

    def init_ui(self):
        """Initialize exercises UI"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Create list view
        self.list_view = self.create_list_view()
        self.main_layout.addWidget(self.list_view)

    def create_list_view(self):
        """Create exercise list view with categories"""
        # Gradient background
        content = QFrame()
        content.setStyleSheet(create_gradient_background())

        layout = QVBoxLayout(content)
        layout.setContentsMargins(AriaSpacing.GIANT, AriaSpacing.GIANT, AriaSpacing.GIANT, AriaSpacing.GIANT)
        layout.setSpacing(AriaSpacing.XL)

        # Title
        title = QLabel("Voice Exercises & Warm-ups")
        title.setStyleSheet(f"""
            color: white;
            font-size: {AriaTypography.TITLE}px;
            font-weight: bold;
            background: transparent;
        """)
        layout.addWidget(title)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("QWidget { background: transparent; }")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(AriaSpacing.XXL)

        # Categories
        categories = [
            ('warmup', 'Warmups & Foundation', 'Essential exercises to prepare your voice'),
            ('resonance', 'Resonance Training', 'Develop head resonance and pitch control'),
            ('advanced', 'Advanced Techniques', 'Advanced exercises for experienced users')
        ]

        for cat_key, cat_title, cat_desc in categories:
            if cat_key in self.exercises:
                # Category header
                cat_frame = QFrame()
                cat_layout = QVBoxLayout(cat_frame)
                cat_layout.setSpacing(AriaSpacing.MD)

                cat_label = QLabel(cat_title)
                cat_label.setStyleSheet(f"""
                    color: white;
                    font-size: {AriaTypography.HEADING}px;
                    font-weight: 600;
                    background: transparent;
                """)
                cat_layout.addWidget(cat_label)

                cat_desc_label = QLabel(cat_desc)
                cat_desc_label.setStyleSheet(f"""
                    color: {AriaColors.WHITE_70};
                    font-size: {AriaTypography.BODY_SMALL}px;
                    background: transparent;
                """)
                cat_layout.addWidget(cat_desc_label)

                # Exercise grid for this category
                grid = QGridLayout()
                grid.setSpacing(AriaSpacing.LG)

                for i, exercise_spec in enumerate(self.exercises[cat_key]):
                    card = ExerciseCard(exercise_spec)
                    card.clicked.connect(self.start_exercise)
                    grid.addWidget(card, i // 2, i % 2)

                cat_layout.addLayout(grid)
                scroll_layout.addWidget(cat_frame)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        return content

    def start_exercise(self, exercise_spec):
        """Start an exercise"""
        try:
            # Hide list view
            self.list_view.hide()

            # Create and show runner view
            self.current_runner = ExerciseRunnerView(exercise_spec, self.voice_trainer)
            self.current_runner.exercise_completed.connect(self.on_exercise_completed)
            self.current_runner.exercise_stopped.connect(self.return_to_list)
            self.main_layout.addWidget(self.current_runner)

            self.current_view = "runner"

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "ExercisesScreen.start_exercise")

    def on_exercise_completed(self):
        """Handle exercise completion"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Exercise Complete",
            f"Great job! You completed {self.current_runner.exercise_spec.name}."
        )
        self.return_to_list()

    def return_to_list(self):
        """Return to exercise list"""
        try:
            # Cleanup runner
            if self.current_runner:
                self.current_runner.cleanup()
                self.main_layout.removeWidget(self.current_runner)
                self.current_runner.deleteLater()
                self.current_runner = None

            # Show list view
            self.list_view.show()
            self.current_view = "list"

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "ExercisesScreen.return_to_list")

    def cleanup(self):
        """Cleanup resources"""
        if self.current_runner:
            self.current_runner.cleanup()


def import_time_now():
    """Helper to get current datetime"""
    from datetime import datetime
    return datetime.now()
