"""Training screen with live voice monitoring and circular visualizer."""

import time
from collections import deque
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QDialog, QDialogButtonBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut

from ..design_system import (
    AriaColors, AriaTypography, AriaSpacing, AriaRadius,
    InfoCard, PrimaryButton, SecondaryButton,
    CircularProgress, create_gradient_background, add_card_shadow,
    MetricRow, BodyLabel, CaptionLabel
)
from ..components.pitch_visualizer import ModernPitchVisualizer
from ..components.safety_widget import SafetyWarningWidget, VoiceSafetyGUICoordinator
from ..components.spectrogram_widget import CompactSpectrogramWidget
from ..components import SessionSummaryDialog
from ..utils.toast_notifications import ToastNotification
from core.session_templates import get_all_templates
from core.voice_snapshots import VoiceSnapshotManager


class TrainingScreen(QWidget):
    """Main training screen - dashboard view with full backend integration"""

    back_requested = pyqtSignal()

    def __init__(self, voice_trainer):
        super().__init__()
        self.voice_trainer = voice_trainer
        self.training_active = False
        self.session_start_time = 0
        self.current_pitch = 0

        # Backend components
        self.audio_analyzer = None
        self.training_controller = None
        self.safety_coordinator = None
        self.snapshot_manager = VoiceSnapshotManager()

        # Pitch tracking
        self.pitch_readings = deque(maxlen=200)
        self.display_pitch_buffer = deque(maxlen=10)
        self.smoothed_pitch = 0
        
        # Audio buffer for snapshots
        self.audio_buffer = deque(maxlen=48000 * 10)
        
        # Auto-pause state
        self.is_paused = False
        self.last_critical_warning_time = 0
        
        # Spectrogram widget (created lazily when needed)
        self.spectrogram_widget = None
        self.show_spectrogram = False

        self.init_ui()
        self.setup_components()

        # Timer for updating stats
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.setInterval(50)  # 20 FPS

    def init_ui(self):
        """Initialize the training screen UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Content area with gradient background
        content = QFrame()
        content.setStyleSheet(create_gradient_background())

        layout = QVBoxLayout(content)
        layout.setContentsMargins(AriaSpacing.GIANT, AriaSpacing.GIANT, AriaSpacing.GIANT, AriaSpacing.GIANT)
        layout.setSpacing(AriaSpacing.XL)

        # === Quick Start Section with Emergency Stop ===
        quick_start_card = self.create_quick_start_section()
        layout.addWidget(quick_start_card)

        # === Visualizer Card ===
        visualizer_card = QFrame()
        visualizer_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {AriaColors.CARD_BG_LIGHT},
                    stop:1 {AriaColors.CARD_BG_PINK_LIGHT}
                );
                border-radius: {AriaRadius.XL}px;
                border: 1px solid {AriaColors.WHITE_25};
            }}
        """)
        add_card_shadow(visualizer_card)

        viz_layout = QVBoxLayout(visualizer_card)
        viz_layout.setContentsMargins(AriaSpacing.MD, AriaSpacing.MD, AriaSpacing.MD, AriaSpacing.MD)  # Tighter margins
        viz_layout.setSpacing(0)

        self.visualizer = ModernPitchVisualizer()
        self.visualizer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        viz_layout.addWidget(self.visualizer)

        layout.addWidget(visualizer_card, stretch=3)

        # === Info Cards Row ===
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(AriaSpacing.LG)

        # Session Analytics Card - simplified, essential metrics only
        self.analytics_card = InfoCard("Session Stats", min_height=260)  # Increased height
        self.analytics_card.content_layout.addStretch()

        # Current pitch display - large and centered
        self.pitch_label = QLabel("185 Hz")
        self.pitch_label.setStyleSheet(f"color: white; font-size: {AriaTypography.HEADING}px; font-weight: 700; background: transparent; margin: 4px 0;")
        self.pitch_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.analytics_card.content_layout.addWidget(self.pitch_label)

        # Spacing between pitch and metrics
        self.analytics_card.content_layout.addSpacing(8)

        # Duration metric - centered
        duration_container = QWidget()
        duration_container.setStyleSheet("background: transparent;")
        duration_layout = QVBoxLayout(duration_container)
        duration_layout.setContentsMargins(0, 0, 0, 0)
        duration_layout.setSpacing(2)
        
        duration_label = QLabel("Duration")
        duration_label.setStyleSheet(f"color: {AriaColors.WHITE_85}; font-size: {AriaTypography.CAPTION}px; font-weight: 500; background: transparent;")
        duration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        duration_layout.addWidget(duration_label)
        
        self.duration_value = QLabel("00:00:00")
        self.duration_value.setStyleSheet(f"color: white; font-size: {AriaTypography.BODY_SMALL}px; font-weight: 600; background: transparent;")
        self.duration_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        duration_layout.addWidget(self.duration_value)
        
        self.analytics_card.content_layout.addWidget(duration_container)

        self.analytics_card.content_layout.addSpacing(6)

        # Avg Pitch metric - centered
        avg_container = QWidget()
        avg_container.setStyleSheet("background: transparent;")
        avg_layout = QVBoxLayout(avg_container)
        avg_layout.setContentsMargins(0, 0, 0, 0)
        avg_layout.setSpacing(2)
        
        avg_label = QLabel("Avg Pitch")
        avg_label.setStyleSheet(f"color: {AriaColors.WHITE_85}; font-size: {AriaTypography.CAPTION}px; font-weight: 500; background: transparent;")
        avg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avg_layout.addWidget(avg_label)
        
        self.avg_value = QLabel("185 Hz")
        self.avg_value.setStyleSheet(f"color: white; font-size: {AriaTypography.BODY_SMALL}px; font-weight: 600; background: transparent;")
        self.avg_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avg_layout.addWidget(self.avg_value)
        
        self.analytics_card.content_layout.addWidget(avg_container)

        self.analytics_card.content_layout.addSpacing(6)

        # Stability metric - centered
        stability_container = QWidget()
        stability_container.setStyleSheet("background: transparent;")
        stability_layout = QVBoxLayout(stability_container)
        stability_layout.setContentsMargins(0, 0, 0, 0)
        stability_layout.setSpacing(2)
        
        stability_label = QLabel("Stability")
        stability_label.setStyleSheet(f"color: {AriaColors.WHITE_85}; font-size: {AriaTypography.CAPTION}px; font-weight: 500; background: transparent;")
        stability_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stability_layout.addWidget(stability_label)
        
        self.stability_value = QLabel("78%")
        self.stability_value.setStyleSheet(f"color: white; font-size: {AriaTypography.BODY_SMALL}px; font-weight: 600; background: transparent;")
        self.stability_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stability_layout.addWidget(self.stability_value)
        
        self.analytics_card.content_layout.addWidget(stability_container)
        
        self.analytics_card.content_layout.addStretch()
        
        # Keep references for backward compatibility
        self.hz_value_top = self.pitch_label
        self.duration_metric = duration_container
        self.avg_metric = avg_container
        self.stability_metric = stability_container
        
        # Create hidden widgets for resonance/formant to prevent errors
        self.resonance_value = QLabel("Balanced")
        self.formant_value = QLabel("-- Hz")

        # Safety Monitor Card
        self.safety_card = InfoCard("Safety Monitor", min_height=210)
        self.safety_card.content_layout.addStretch()
        self.check_label = QLabel("\u2714")
        self.check_label.setStyleSheet(f"color: {AriaColors.GREEN}; font-size: 56px; background: transparent; font-weight: bold;")
        self.safety_card.content_layout.addWidget(self.check_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.safety_msg = QLabel("No Strain Detected. Keep it up.")
        self.safety_msg.setStyleSheet(f"color: white; font-size: {AriaTypography.BODY}px; font-weight: 500; background: transparent; margin-top: 6px;")
        self.safety_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.safety_msg.setWordWrap(True)
        self.safety_card.content_layout.addWidget(self.safety_msg)
        self.safety_card.content_layout.addStretch()

        # Safety warning widget (hidden by default)
        self.safety_widget = SafetyWarningWidget()
        self.safety_card.content_layout.addWidget(self.safety_widget)

        # Goal Progress Card
        self.goal_card = InfoCard("Your Goal", min_height=240)
        self.goal_card.content_layout.addStretch()
        self.progress_widget = CircularProgress(percentage=35, size=110)
        self.goal_card.content_layout.addWidget(self.progress_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        self.complete_label = QLabel("35% Complete")
        self.complete_label.setStyleSheet(f"color: white; font-size: {AriaTypography.SUBHEADING}px; font-weight: bold; background: transparent; margin-top: 8px;")
        self.complete_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.goal_card.content_layout.addWidget(self.complete_label)

        self.range_label = QLabel("Feminine Range (165-220 Hz)")
        self.range_label.setStyleSheet(f"color: {AriaColors.WHITE_85}; font-size: {AriaTypography.BODY_SMALL}px; background: transparent;")
        self.range_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.goal_card.content_layout.addWidget(self.range_label)
        self.goal_card.content_layout.addStretch()

        cards_layout.addWidget(self.analytics_card, stretch=1)
        cards_layout.addWidget(self.safety_card, stretch=1)
        cards_layout.addWidget(self.goal_card, stretch=1)

        layout.addLayout(cards_layout)
        
        # === Spectrogram (optionally shown) ===
        self.spectrogram_container = QFrame()
        self.spectrogram_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {AriaColors.CARD_BG_LIGHT},
                    stop:1 {AriaColors.CARD_BG_PINK_LIGHT}
                );
                border-radius: {AriaRadius.XL}px;
                border: 1px solid {AriaColors.WHITE_25};
            }}
        """)
        add_card_shadow(self.spectrogram_container)
        
        spec_layout = QVBoxLayout(self.spectrogram_container)
        spec_layout.setContentsMargins(AriaSpacing.LG, AriaSpacing.LG, AriaSpacing.LG, AriaSpacing.LG)
        
        # Will add spectrogram widget here if enabled
        self.spectrogram_container.hide()
        layout.addWidget(self.spectrogram_container)

        # === Control Buttons ===
        controls = QHBoxLayout()
        controls.setSpacing(AriaSpacing.XL)
        controls.addStretch()

        # Snapshot button (shown only during training)
        self.snapshot_btn = SecondaryButton("📸 Record Snapshot")
        self.snapshot_btn.setMinimumSize(200, 50)
        self.snapshot_btn.clicked.connect(self.record_snapshot)
        self.snapshot_btn.hide()
        controls.addWidget(self.snapshot_btn)

        # Start Training button
        self.start_btn = PrimaryButton("Start Training")
        self.start_btn.clicked.connect(self.toggle_training)

        controls.addWidget(self.start_btn)
        controls.addStretch()

        layout.addLayout(controls)

        main_layout.addWidget(content)

    def create_quick_start_section(self):
        """Create Quick Start section with template buttons and emergency stop"""
        quick_start_frame = QFrame()
        quick_start_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {AriaColors.CARD_BG_LIGHT},
                    stop:1 {AriaColors.CARD_BG_PINK_LIGHT}
                );
                border-radius: {AriaRadius.XL}px;
                border: none;
            }}
        """)
        add_card_shadow(quick_start_frame)
        
        qs_layout = QVBoxLayout(quick_start_frame)
        qs_layout.setContentsMargins(AriaSpacing.XL, AriaSpacing.XL, AriaSpacing.XL, AriaSpacing.XL)
        qs_layout.setSpacing(AriaSpacing.MD)
        
        # Header row with Emergency Stop button
        header_row = QHBoxLayout()
        header_row.setSpacing(AriaSpacing.LG)
        
        header_label = QLabel("Quick Start")
        header_label.setStyleSheet(f"""
            color: white;
            font-size: {AriaTypography.SUBHEADING}px;
            font-weight: 600;
            background: transparent;
        """)
        header_row.addWidget(header_label)
        header_row.addStretch()
        
        # Emergency Stop button (hidden by default)
        self.emergency_stop_btn = QPushButton("🛑 STOP & REST")
        self.emergency_stop_btn.setMinimumSize(140, 55)
        self.emergency_stop_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaColors.RED};
                color: white;
                border: none;
                border-radius: {AriaRadius.MD}px;
                font-size: {AriaTypography.BODY}px;
                font-weight: 600;
                padding: {AriaSpacing.SM}px {AriaSpacing.LG}px;
            }}
            QPushButton:hover {{
                background-color: {AriaColors.RED_HOVER};
            }}
            QPushButton:pressed {{
                background-color: #D03E3E;
            }}
        """)
        self.emergency_stop_btn.clicked.connect(self.emergency_stop)
        self.emergency_stop_btn.hide()
        header_row.addWidget(self.emergency_stop_btn)
        
        qs_layout.addLayout(header_row)
        
        # Template buttons row
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(AriaSpacing.MD)
        
        templates = get_all_templates()
        for template in templates:
            btn = self.create_template_button(template)
            buttons_layout.addWidget(btn)
        
        qs_layout.addLayout(buttons_layout)
        
        # Setup keyboard shortcut
        self.emergency_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.emergency_shortcut.activated.connect(self.emergency_stop)
        
        return quick_start_frame

    def create_template_button(self, template):
        """Create a styled template button"""
        btn = QPushButton(f"{template.icon} {template.name}")
        
        # Alternate between primary and secondary styles
        is_primary = template.name in ["Full Training", "Quick Practice"]
        
        if is_primary:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 {AriaColors.PRIMARY},
                        stop:1 {AriaColors.PINK}
                    );
                    color: white;
                    border: none;
                    border-radius: {AriaRadius.MD}px;
                    padding: {AriaSpacing.MD}px {AriaSpacing.LG}px;
                    font-size: {AriaTypography.BODY_SMALL}px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 {AriaColors.TEAL},
                        stop:1 {AriaColors.PRIMARY}
                    );
                }}
                QPushButton:pressed {{
                    background: {AriaColors.TEAL};
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {AriaColors.WHITE_15};
                    color: white;
                    border: 1px solid {AriaColors.WHITE_25};
                    border-radius: {AriaRadius.MD}px;
                    padding: {AriaSpacing.MD}px {AriaSpacing.LG}px;
                    font-size: {AriaTypography.BODY_SMALL}px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background: {AriaColors.WHITE_25};
                    border-color: {AriaColors.WHITE_45};
                }}
                QPushButton:pressed {{
                    background: {AriaColors.WHITE_35};
                }}
            """)
        
        btn.clicked.connect(lambda: self.start_template_session(template))
        btn.setToolTip(f"{template.description}\n{template.get_duration_display()}")
        
        return btn

    def start_template_session(self, template):
        """Start a session using the selected template"""
        if self.training_active:
            return
        
        # Prevent double-clicks
        if hasattr(self, '_navigating') and self._navigating:
            return
        self._navigating = True
        
        try:
            # Update goal range based on template
            self.voice_trainer.config_manager.update_config({'target_pitch_range': list(template.goal_range)})
            
            # Update display
            self.range_label.setText(f"{template.name} ({template.goal_range[0]}-{template.goal_range[1]} Hz)")
            
            # Navigate to Exercises screen to perform the template's exercises
            # Find parent main window and navigate
            parent = self.parent()
            while parent is not None:
                if hasattr(parent, 'navigate_to'):
                    parent.navigate_to('exercises')
                    # Also pass the template to exercises screen if needed
                    if hasattr(parent, 'content_stack'):
                        exercises_screen = parent.content_stack.widget(1)  # Index 1 is ExercisesScreen
                        if hasattr(exercises_screen, 'load_template'):
                            exercises_screen.load_template(template)
                    break
                parent = parent.parent()
        finally:
            # Reset navigation flag after a short delay
            QTimer.singleShot(500, lambda: setattr(self, '_navigating', False))

    def toggle_training(self):
        """Toggle training start/stop"""
        self.training_active = not self.training_active

        if self.training_active:
            self.start_training()
        else:
            self.stop_training()

    def setup_components(self):
        """Setup backend components"""
        try:
            # Get components from voice trainer
            self.training_controller = self.voice_trainer.training_controller
            self.audio_analyzer = self.voice_trainer.factory.get_component('voice_analyzer')

            # Setup safety coordinator
            safety_monitor = self.voice_trainer.factory.get_component('safety_monitor')
            if safety_monitor:
                self.safety_coordinator = VoiceSafetyGUICoordinator(safety_monitor)
                self.safety_coordinator.register_safety_widget('training', self.safety_widget)
                self.safety_widget.break_requested.connect(self.handle_break_request)

            # Load target range from config
            config = self.voice_trainer.config_manager.get_config()
            target_range = config.get('target_pitch_range', [165, 265])
            goal_description = config.get('voice_goal_description', 'Feminine Range (165-220 Hz)')
            self.range_label.setText(goal_description)

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "TrainingScreen.setup_components")

    def start_training(self):
        """Start voice training session with full backend integration"""
        try:
            # Get configuration
            config = self.voice_trainer.config_manager.get_config()

            # Start backend training
            success = self.training_controller.start_live_training(config, self.handle_audio_callback)

            if not success:
                self.safety_msg.setText("⚠ Error: Could not start audio system. Check microphone.")
                self.safety_msg.setStyleSheet(f"color: {AriaColors.RED}; font-size: {AriaTypography.BODY}px;")
                self.training_active = False
                return

            # Update state
            self.training_active = True
            self.session_start_time = time.time()
            self.pitch_readings.clear()
            self.display_pitch_buffer.clear()
            self.current_pitch = 0
            self.smoothed_pitch = 0
            self.audio_buffer.clear()

            # Update UI
            self.start_btn.setText("Stop Training")
            self.snapshot_btn.show()
            self.emergency_stop_btn.show()
            self.visualizer.start_animation()
            self.update_timer.start()

            # Reset safety display
            self.check_label.setText("\u2714")
            self.check_label.setStyleSheet(f"color: {AriaColors.GREEN}; font-size: 56px; background: transparent; font-weight: bold;")
            self.safety_msg.setText("No Strain Detected. Keep it up.")
            self.safety_msg.setStyleSheet(f"color: white; font-size: {AriaTypography.BODY}px; font-weight: 500; background: transparent;")

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "TrainingScreen.start_training")
            self.training_active = False

    def stop_training(self):
        """Stop voice training session"""
        from utils.error_handler import log_error

        session_duration = 0

        try:
            # Calculate session duration
            if self.session_start_time:
                session_duration = (time.time() - self.session_start_time) / 60  # Minutes
        except Exception as e:
            log_error(e, "TrainingScreen.stop_training - calculating session duration")

        # Stop backend training (critical - must not fail)
        try:
            self.training_controller.stop_live_training()
        except Exception as e:
            log_error(e, "TrainingScreen.stop_training - stop_live_training")

        # Update training state
        self.training_active = False

        # Update UI elements (each with separate error handling)
        try:
            self.start_btn.setText("Start Training")
            self.snapshot_btn.hide()
            self.emergency_stop_btn.hide()
        except Exception as e:
            log_error(e, "TrainingScreen.stop_training - updating start button")

        try:
            self.visualizer.stop_animation()
        except Exception as e:
            log_error(e, "TrainingScreen.stop_training - stopping visualizer")

        try:
            self.update_timer.stop()
        except Exception as e:
            log_error(e, "TrainingScreen.stop_training - stopping timer")
        
        # Check for milestone auto-save
        try:
            if session_duration >= 1.0:
                should_save = self.snapshot_manager.increment_session()
                if should_save and len(self.audio_buffer) > 0:
                    self.auto_save_milestone_snapshot()
        except Exception as e:
            log_error(e, "TrainingScreen.stop_training - milestone check")

        # Show session summary if session was long enough
        try:
            if session_duration >= 1.0:
                # Get session data from session manager
                session_data = None
                all_sessions = []
                if hasattr(self.voice_trainer, 'session_manager'):
                    sessions = self.voice_trainer.session_manager.get_recent_sessions(days=1)
                    if sessions:
                        session_data = sessions[0]  # Most recent session
                    
                    # Get all sessions for pattern analysis
                    all_sessions = self.voice_trainer.session_manager.get_recent_sessions(days=90)
                
                # Show session summary dialog with recommendations
                if session_data:
                    dialog = SessionSummaryDialog(session_data, self, all_sessions=all_sessions)
                    dialog.exec()
                
                # Also show safety summary if configured
                if self.safety_coordinator:
                    self.safety_coordinator.show_safety_summary(session_duration, 'training')
        except Exception as e:
            log_error(e, "TrainingScreen.stop_training - showing session summary")

    def handle_audio_callback(self, callback_type, data):
        """Handle callbacks from training controller"""
        if callback_type == 'noise_feedback':
            # Show noise calibration message
            message = data.get('message', '')
            if '🤫' in message:
                # Calibrating - show microphone icon
                self.check_label.setText("🎤")
                self.check_label.setStyleSheet(f"color: {AriaColors.TEAL}; font-size: 56px; background: transparent; font-weight: bold;")
            else:
                # Calibration complete - show checkmark
                self.check_label.setText("✓")
                self.check_label.setStyleSheet(f"color: {AriaColors.GREEN}; font-size: 56px; background: transparent; font-weight: bold;")
            self.safety_msg.setText(message)
            self.safety_msg.setStyleSheet(f"color: {AriaColors.WHITE_95}; font-size: {AriaTypography.BODY}px; font-weight: 500; background: transparent;")
        
        elif callback_type == 'training_status':
            raw_pitch = data.get('pitch', 0)
            if raw_pitch > 0:
                self.current_pitch = self._smooth_pitch(raw_pitch)
                if self.current_pitch > 0:
                    self.pitch_readings.append(self.current_pitch)
            
            audio_chunk = data.get('audio_data')
            if audio_chunk is not None:
                import numpy as np
                if isinstance(audio_chunk, np.ndarray):
                    self.audio_buffer.extend(audio_chunk.tolist())
                    # Update spectrogram if enabled
                    if self.show_spectrogram and self.spectrogram_widget:
                        self.spectrogram_widget.update_audio(audio_chunk)
                elif isinstance(audio_chunk, list):
                    self.audio_buffer.extend(audio_chunk)
                    # Update spectrogram if enabled
                    if self.show_spectrogram and self.spectrogram_widget:
                        import numpy as np
                        self.spectrogram_widget.update_audio(np.array(audio_chunk))

        elif callback_type == 'safety_warning':
            # Show safety warning
            if self.safety_coordinator:
                self.safety_coordinator.handle_safety_warning(data, 'training')
            # Update safety card
            self.check_label.setText("⚠")
            self.check_label.setStyleSheet(f"color: {AriaColors.RED}; font-size: 56px; background: transparent; font-weight: bold;")
            self.safety_msg.setText(data.get('message', 'Voice strain detected'))
            self.safety_msg.setStyleSheet(f"color: {AriaColors.RED}; font-size: {AriaTypography.BODY}px; font-weight: 500; background: transparent;")
            
            # Auto-pause on critical strain
            severity = data.get('severity', 'medium')
            if severity == 'critical':
                config = self.voice_trainer.config_manager.get_config()
                if config.get('auto_pause_on_strain', True):
                    self.auto_pause_for_strain(data)

    def _smooth_pitch(self, new_pitch):
        """Apply pitch smoothing"""
        if new_pitch <= 0:
            return self.smoothed_pitch

        # Simple outlier detection
        if len(self.display_pitch_buffer) > 3:
            recent_avg = sum(self.display_pitch_buffer) / len(self.display_pitch_buffer)
            if abs(new_pitch - recent_avg) > (recent_avg * 0.4):
                return self.smoothed_pitch

        # Add to buffer
        self.display_pitch_buffer.append(new_pitch)

        # Calculate smoothed pitch
        if len(self.display_pitch_buffer) > 0:
            if self.smoothed_pitch > 0:
                self.smoothed_pitch = (self.smoothed_pitch * 0.5 + new_pitch * 0.5)
            else:
                self.smoothed_pitch = new_pitch

        return self.smoothed_pitch

    def handle_break_request(self):
        """Handle break request from safety widget"""
        if self.training_active:
            self.stop_training()

    def update_stats(self):
        """Update real-time display"""
        if not self.training_active:
            return

        try:
            # Update pitch display
            current_pitch = self.current_pitch
            if current_pitch > 0:
                self.visualizer.set_pitch(current_pitch)
                self.pitch_label.setText(f"{int(current_pitch)} Hz")
                self.hz_value_top.setText(f"{int(current_pitch)} Hz")

            # Update duration
            if self.session_start_time:
                duration = int(time.time() - self.session_start_time)
                hours = duration // 3600
                minutes = (duration % 3600) // 60
                seconds = duration % 60
                self.duration_value.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

            # Update average pitch
            if len(self.pitch_readings) > 0:
                avg_pitch = sum(self.pitch_readings) / len(self.pitch_readings)
                self.avg_value.setText(f"{int(avg_pitch)} Hz")

            # Update stability (based on pitch variance)
            if len(self.pitch_readings) > 10:
                import statistics
                std_dev = statistics.stdev(list(self.pitch_readings)[-50:])
                avg = statistics.mean(list(self.pitch_readings)[-50:])
                stability = max(0, min(100, 100 - (std_dev / avg * 100)))
                self.stability_value.setText(f"{int(stability)}%")

            # Update progress (based on target range)
            config = self.voice_trainer.config_manager.get_config()
            target_range = config.get('target_pitch_range', [165, 265])
            if len(self.pitch_readings) > 0:
                in_range = sum(1 for p in list(self.pitch_readings)[-50:] if target_range[0] <= p <= target_range[1])
                progress = (in_range / min(len(list(self.pitch_readings)[-50:]), 50)) * 100
                self.progress_widget.set_percentage(progress)
                self.complete_label.setText(f"{int(progress)}% Complete")

            # Update resonance and formants (if enabled in settings)
            if config.get('resonance_display_enabled', True) and self.audio_analyzer:
                try:
                    # Try to use formant-based resonance quality first
                    formant_data = self.audio_analyzer.get_formant_data()
                    if formant_data and formant_data.get('quality'):
                        quality_info = formant_data['quality']
                        quality = quality_info.get('quality', 'Unknown')
                        self.resonance_value.setText(quality)
                        
                        # Update formant values display
                        formants = formant_data.get('formants')
                        if formants:
                            f1 = int(formants.get('F1', 0))
                            f2 = int(formants.get('F2', 0))
                            f3 = int(formants.get('F3', 0))
                            
                            # Update spectrogram with formant data
                            if self.show_spectrogram and self.spectrogram_widget:
                                self.spectrogram_widget.update_formants([f1, f2, f3])
                            
                            # Color-code based on brightness (F2/F3 average)
                            brightness = quality_info.get('brightness', 0.5)
                            if brightness > 0.7:
                                color = AriaColors.PINK  # Very bright
                            elif brightness > 0.55:
                                color = AriaColors.TEAL  # Bright
                            elif brightness < 0.3:
                                color = "#8B7355"  # Dark/warm (brownish)
                            else:
                                color = "white"  # Balanced
                            
                            self.formant_value.setText(f"F1:{f1} F2:{f2} F3:{f3}")
                            self.formant_value.setStyleSheet(f"color: {color}; font-size: {AriaTypography.BODY_SMALL}px; font-weight: 600; background: transparent;")
                    else:
                        # Fallback to spectral centroid resonance
                        resonance_data = self.audio_analyzer.current_resonance
                        if resonance_data and resonance_data.get('updated', 0) > 0:
                            quality = resonance_data.get('quality', 'Unknown')
                            frequency = resonance_data.get('frequency', 0)

                            # Display format: "Bright (↑) 1650Hz" or just "Balanced"
                            if frequency > 0:
                                self.resonance_value.setText(f"{quality} {frequency}Hz")
                            else:
                                self.resonance_value.setText(quality)
                        
                        # No formant data available
                        self.formant_value.setText("-- Hz")
                except Exception as resonance_error:
                    pass  # Silently fail if resonance not available
            
                # Update spectrogram display if enabled
                if self.show_spectrogram and self.spectrogram_widget:
                    # Refresh spectrogram every 10 frames (0.5s at 20 FPS)
                    if not hasattr(self, '_spec_frame_counter'):
                        self._spec_frame_counter = 0
                    self._spec_frame_counter += 1
                    if self._spec_frame_counter >= 10:
                        self.spectrogram_widget.refresh_display()
                    self._spec_frame_counter = 0

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "TrainingScreen.update_stats")

    def toggle_spectrogram(self, enabled):
        """Toggle spectrogram visualization
        
        Args:
            enabled: bool - Whether to show spectrogram
        """
        self.show_spectrogram = enabled
        
        if enabled:
            # Create spectrogram widget if it doesn't exist
            if not self.spectrogram_widget:
                self.spectrogram_widget = CompactSpectrogramWidget()
                # Add to container
                spec_layout = self.spectrogram_container.layout()
                spec_layout.addWidget(self.spectrogram_widget)
            
            # Show container
            self.spectrogram_container.show()
        else:
            # Hide container
            self.spectrogram_container.hide()
    
    def refresh_from_settings(self):
        """Refresh training screen based on current settings"""
        config = self.voice_trainer.config_manager.get_config()
        
        # Toggle spectrogram based on settings
        show_spec = config.get('show_spectrogram', False)
        self.toggle_spectrogram(show_spec)
    
    def cleanup(self):
        """Cleanup resources"""
        from utils.error_handler import log_error

        # Stop training if active
        try:
            if self.training_active:
                self.stop_training()
        except Exception as e:
            log_error(e, "TrainingScreen.cleanup - stop_training")

        # Stop update timer
        try:
            if self.update_timer:
                self.update_timer.stop()
        except Exception as e:
            log_error(e, "TrainingScreen.cleanup - stopping timer")

        # Clear safety warnings
        try:
            if self.safety_coordinator:
                self.safety_coordinator.clear_all_warnings()
        except Exception as e:
            log_error(e, "TrainingScreen.cleanup - clearing safety warnings")

    def record_snapshot(self):
        """Record a voice snapshot from the current session"""
        import numpy as np
        
        if not self.training_active or len(self.audio_buffer) == 0:
            return
        
        try:
            audio_data = np.array(list(self.audio_buffer))
            
            session_stats = {
                'avg_pitch': sum(self.pitch_readings) / len(self.pitch_readings) if len(self.pitch_readings) > 0 else 0,
                'min_pitch': min(self.pitch_readings) if len(self.pitch_readings) > 0 else 0,
                'max_pitch': max(self.pitch_readings) if len(self.pitch_readings) > 0 else 0,
                'avg_resonance': 0,
                'avg_hnr': 0,
                'total_time': time.time() - self.session_start_time if self.session_start_time else 0
            }
            
            snapshot_id = self.snapshot_manager.record_snapshot(
                audio_data=audio_data,
                sample_rate=48000,
                session_stats=session_stats,
                is_milestone=False,
                note=""
            )
            
            if snapshot_id:
                ToastNotification.show_toast(self, "Snapshot saved", icon="✓")
            else:
                ToastNotification.show_toast(self, "Failed to save snapshot", error=True)
                
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "TrainingScreen.record_snapshot")
            self.show_toast("Error saving snapshot", error=True)
    
    def auto_save_milestone_snapshot(self):
        """Auto-save a milestone snapshot"""
        import numpy as np
        
        try:
            if len(self.audio_buffer) == 0:
                return
            
            audio_data = np.array(list(self.audio_buffer))
            
            session_stats = {
                'avg_pitch': sum(self.pitch_readings) / len(self.pitch_readings) if len(self.pitch_readings) > 0 else 0,
                'min_pitch': min(self.pitch_readings) if len(self.pitch_readings) > 0 else 0,
                'max_pitch': max(self.pitch_readings) if len(self.pitch_readings) > 0 else 0,
                'avg_resonance': 0,
                'avg_hnr': 0,
                'total_time': time.time() - self.session_start_time if self.session_start_time else 0
            }
            
            snapshot_id = self.snapshot_manager.record_snapshot(
                audio_data=audio_data,
                sample_rate=48000,
                session_stats=session_stats,
                is_milestone=True,
                note=f"Milestone: Session #{self.snapshot_manager.session_count}"
            )
            
            if snapshot_id:
                ToastNotification.show_toast(
                    self, 
                    f"Milestone #{self.snapshot_manager.session_count} saved!", 
                    duration=3000,
                    icon="🎖️"
                )
                
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "TrainingScreen.auto_save_milestone_snapshot")
    
    def emergency_stop(self):
        """Emergency stop - immediately stop training and show rest modal"""
        if not self.training_active:
            return
        
        # Stop training
        self.stop_training()
        
        # Show rest modal
        self.show_rest_modal(emergency=True)
    
    def auto_pause_for_strain(self, warning_data):
        """Auto-pause training when critical strain is detected"""
        current_time = time.time()
        
        # Check if we need to pause (not already paused and not recently warned)
        if not self.is_paused and (current_time - self.last_critical_warning_time) > 30:
            self.last_critical_warning_time = current_time
            
            # Pause audio processing but keep UI active
            if self.training_controller:
                try:
                    # Temporarily stop audio
                    self.training_controller.stop_live_training()
                    self.is_paused = True
                    self.update_timer.stop()
                except Exception as e:
                    from utils.error_handler import log_error
                    log_error(e, "TrainingScreen.auto_pause_for_strain")
            
            # Show strain modal
            self.show_strain_modal(warning_data)
    
    def show_rest_modal(self, emergency=False):
        """Show rest modal dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Rest Required" if emergency else "Take a Break")
        dialog.setMinimumSize(400, 200)
        dialog.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {AriaColors.GRADIENT_BLUE_DARK},
                    stop:1 {AriaColors.GRADIENT_PINK}
                );
            }}
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(AriaSpacing.LG)
        layout.setContentsMargins(AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL)
        
        # Title
        title = QLabel("🛑 Training Stopped" if emergency else "💆 Time to Rest")
        title.setStyleSheet(f"color: white; font-size: {AriaTypography.TITLE}px; font-weight: bold; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Message
        msg = QLabel("Emergency stop activated. Take a break and rest your voice." if emergency else 
                    "Your voice needs rest. Stay hydrated and relax.")
        msg.setStyleSheet(f"color: {AriaColors.WHITE_85}; font-size: {AriaTypography.BODY}px; background: transparent;")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        layout.addWidget(msg)
        
        # OK button
        ok_btn = PrimaryButton("OK")
        ok_btn.clicked.connect(dialog.accept)
        layout.addWidget(ok_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        dialog.exec()
    
    def show_strain_modal(self, warning_data):
        """Show vocal strain detection modal"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Vocal Strain Detected")
        dialog.setMinimumSize(450, 250)
        dialog.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {AriaColors.GRADIENT_BLUE_DARK},
                    stop:1 {AriaColors.GRADIENT_PINK}
                );
            }}
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(AriaSpacing.LG)
        layout.setContentsMargins(AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL)
        
        # Title
        title = QLabel("⚠️ Vocal Strain Detected - Training Paused")
        title.setStyleSheet(f"color: {AriaColors.RED}; font-size: {AriaTypography.TITLE}px; font-weight: bold; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Message
        msg = QLabel(warning_data.get('message', 'Critical vocal strain detected. Please rest your voice.'))
        msg.setStyleSheet(f"color: {AriaColors.WHITE_85}; font-size: {AriaTypography.BODY}px; background: transparent;")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        layout.addWidget(msg)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(AriaSpacing.LG)
        
        # Rest Now button (green)
        rest_btn = QPushButton("Rest Now")
        rest_btn.setMinimumSize(140, 45)
        rest_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaColors.GREEN};
                color: white;
                border: none;
                border-radius: {AriaRadius.MD}px;
                font-size: {AriaTypography.BODY}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #45B84E;
            }}
        """)
        rest_btn.clicked.connect(lambda: self.handle_strain_response(dialog, rest=True))
        button_layout.addWidget(rest_btn)
        
        # Continue Carefully button (gray)
        continue_btn = QPushButton("Continue Carefully")
        continue_btn.setMinimumSize(140, 45)
        continue_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaColors.WHITE_35};
                color: white;
                border: 1px solid {AriaColors.WHITE_45};
                border-radius: {AriaRadius.MD}px;
                font-size: {AriaTypography.BODY}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {AriaColors.WHITE_45};
            }}
        """)
        continue_btn.clicked.connect(lambda: self.handle_strain_response(dialog, rest=False))
        button_layout.addWidget(continue_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def handle_strain_response(self, dialog, rest):
        """Handle user response to strain modal"""
        dialog.accept()
        
        if rest:
            # User chose to rest - keep training stopped
            self.is_paused = False
            self.training_active = False
            self.show_rest_modal(emergency=False)
        else:
            # User chose to continue - resume training
            self.is_paused = False
            if self.training_active:
                try:
                    # Resume training
                    config = self.voice_trainer.config_manager.get_config()
                    self.training_controller.start_live_training(config, self.handle_audio_callback)
                    self.update_timer.start()
                    
                    # Set timer for next warning (30 seconds)
                    self.last_critical_warning_time = time.time()
                except Exception as e:
                    from utils.error_handler import log_error
                    log_error(e, "TrainingScreen.handle_strain_response")
