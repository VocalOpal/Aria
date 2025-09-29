import time
from collections import deque
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,  # type: ignore
                            QLabel, QProgressBar, QFrame, QGridLayout, QSizePolicy, QComboBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal  # type: ignore
from PyQt6.QtGui import QFont, QPainter, QPen, QColor  # type: ignore
from ..components.safety_widget import SafetyWarningWidget, VoiceSafetyGUICoordinator
from ..design_system import AriaDesignSystem


class PitchMeterWidget(QWidget):
    """Custom widget for displaying real-time pitch"""

    def __init__(self):
        super().__init__()
        self.current_pitch = 0
        self.target_min = 165
        self.target_max = 265
        self.setMinimumHeight(120)
        self.setStyleSheet(f"""
            PitchMeterWidget {{
                background-color: {AriaDesignSystem.COLORS['bg_secondary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: {AriaDesignSystem.RADIUS['lg']};
            }}
        """)

    def set_target_range(self, min_hz, max_hz):
        """Set target pitch range"""
        self.target_min = min_hz
        self.target_max = max_hz
        self.update()

    def set_current_pitch(self, pitch_hz):
        """Update current pitch reading"""
        self.current_pitch = pitch_hz
        self.update()

    def paintEvent(self, event):
        """Custom paint for pitch visualization"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background
        painter.fillRect(self.rect(), QColor(AriaDesignSystem.COLORS['bg_secondary']))

        # Calculate dimensions
        width = self.width() - 20
        height = self.height() - 20
        x_offset = 10
        y_offset = 10

        # Draw frequency scale (50-400 Hz range for display)
        min_display = 50
        max_display = 400

        # Draw target range
        if self.target_min > 0 and self.target_max > 0:
            target_start = x_offset + (self.target_min - min_display) / (max_display - min_display) * width
            target_width = (self.target_max - self.target_min) / (max_display - min_display) * width

            painter.setPen(QPen(QColor(AriaDesignSystem.COLORS['success']), 2))
            target_color = QColor(AriaDesignSystem.COLORS['success'])
            target_color.setAlpha(60)
            painter.setBrush(target_color)
            painter.drawRect(int(target_start), y_offset, int(target_width), height)

        # Draw current pitch indicator
        if self.current_pitch > 0:
            pitch_x = x_offset + (self.current_pitch - min_display) / (max_display - min_display) * width

            # Color based on whether in target range
            if self.target_min <= self.current_pitch <= self.target_max:
                color = QColor(AriaDesignSystem.COLORS['pitch_good'])  # Green for in range
            else:
                # Determine if close to range or far from range
                close_range = abs(self.current_pitch - ((self.target_min + self.target_max) / 2)) < 50
                if close_range:
                    color = QColor(AriaDesignSystem.COLORS['pitch_warning'])  # Amber for close
                else:
                    color = QColor(AriaDesignSystem.COLORS['pitch_error'])   # Red for far

            painter.setPen(QPen(color, 4))
            painter.drawLine(int(pitch_x), y_offset, int(pitch_x), y_offset + height)

        # Draw frequency labels
        painter.setPen(QPen(QColor(AriaDesignSystem.COLORS['text_muted']), 1))
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)

        for freq in [100, 150, 200, 250, 300, 350]:
            x = x_offset + (freq - min_display) / (max_display - min_display) * width
            painter.drawText(int(x - 10), self.height() - 5, f"{freq}")


class TrainingStatsWidget(QWidget):
    """Widget displaying training session statistics"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize modern stats display"""
        # Main container with card styling
        self.setStyleSheet(f"""
            TrainingStatsWidget {{
                background-color: {AriaDesignSystem.COLORS['bg_secondary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: {AriaDesignSystem.RADIUS['lg']};
                padding: {AriaDesignSystem.SPACING['md']};
            }}
        """)

        layout = QGridLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Session time
        self.session_label = QLabel("Session Time:")
        self.session_label.setStyleSheet(f"color: {AriaDesignSystem.COLORS['text_secondary']}; font-size: {AriaDesignSystem.FONTS['sm']}pt;")
        self.session_value = QLabel("00:00")
        self.session_value.setStyleSheet(f"font-weight: 600; color: {AriaDesignSystem.COLORS['primary']}; font-size: {AriaDesignSystem.FONTS['md']}pt;")

        # Current pitch
        self.pitch_label = QLabel("Current Pitch:")
        self.pitch_label.setStyleSheet(f"color: {AriaDesignSystem.COLORS['text_secondary']}; font-size: {AriaDesignSystem.FONTS['sm']}pt;")
        self.pitch_value = QLabel("-- Hz")
        self.pitch_value.setStyleSheet(f"font-weight: 600; color: {AriaDesignSystem.COLORS['warning']}; font-size: {AriaDesignSystem.FONTS['md']}pt;")

        # Target range
        self.target_label = QLabel("Target Range:")
        self.target_label.setStyleSheet(f"color: {AriaDesignSystem.COLORS['text_secondary']}; font-size: {AriaDesignSystem.FONTS['sm']}pt;")
        self.target_value = QLabel("165-265 Hz")
        self.target_value.setStyleSheet(f"font-weight: 600; color: {AriaDesignSystem.COLORS['text_muted']}; font-size: {AriaDesignSystem.FONTS['md']}pt;")

        # In-range percentage
        self.accuracy_label = QLabel("In Range:")
        self.accuracy_label.setStyleSheet(f"color: {AriaDesignSystem.COLORS['text_secondary']}; font-size: {AriaDesignSystem.FONTS['sm']}pt;")
        self.accuracy_value = QLabel("0%")
        self.accuracy_value.setStyleSheet(f"font-weight: 600; color: {AriaDesignSystem.COLORS['info']}; font-size: {AriaDesignSystem.FONTS['md']}pt;")

        # Resonance quality (approximate)
        self.resonance_label = QLabel("Resonance:")
        self.resonance_label.setStyleSheet(f"color: {AriaDesignSystem.COLORS['text_secondary']}; font-size: {AriaDesignSystem.FONTS['sm']}pt;")
        self.resonance_value = QLabel("Unknown")
        self.resonance_value.setStyleSheet(f"font-weight: 600; color: {AriaDesignSystem.COLORS['resonance_color']}; font-size: {AriaDesignSystem.FONTS['md']}pt;")

        # Layout stats
        layout.addWidget(self.session_label, 0, 0)
        layout.addWidget(self.session_value, 0, 1)
        layout.addWidget(self.pitch_label, 1, 0)
        layout.addWidget(self.pitch_value, 1, 1)
        layout.addWidget(self.target_label, 0, 2)
        layout.addWidget(self.target_value, 0, 3)
        layout.addWidget(self.accuracy_label, 1, 2)
        layout.addWidget(self.accuracy_value, 1, 3)
        layout.addWidget(self.resonance_label, 0, 4)
        layout.addWidget(self.resonance_value, 0, 5)

        # Add safety disclaimer tooltip for resonance
        disclaimer = ("Resonance detection is an approximation based on spectral analysis. "
                     "Results may vary with microphone quality, room acoustics, and voice characteristics. "
                     "Use as a general guide only.")
        self.resonance_label.setToolTip(disclaimer)
        self.resonance_value.setToolTip(disclaimer)

    def update_stats(self, session_time, current_pitch, target_range, in_range_pct, resonance_data=None):
        """Update displayed statistics"""
        minutes = int(session_time // 60)
        seconds = int(session_time % 60)
        self.session_value.setText(f"{minutes:02d}:{seconds:02d}")

        if current_pitch > 0:
            self.pitch_value.setText(f"{current_pitch:.1f} Hz")
        else:
            self.pitch_value.setText("-- Hz")

        if target_range:
            self.target_value.setText(f"{target_range[0]:.0f}-{target_range[1]:.0f} Hz")

        self.accuracy_value.setText(f"{in_range_pct:.1f}%")

        # Update resonance display with approximation notice
        if resonance_data and resonance_data.get('quality') != 'Unknown':
            freq = resonance_data.get('frequency', 0)
            quality = resonance_data.get('quality', 'Unknown')
            self.resonance_value.setText(f"{quality} (approx. {freq:.0f} Hz)" if freq > 0 else quality)
        else:
            self.resonance_value.setText("Unknown")


class TrainingScreen(QWidget):
    """Live voice training interface"""

    back_requested = pyqtSignal()

    def __init__(self, voice_trainer):
        super().__init__()
        self.voice_trainer = voice_trainer
        self.training_active = False
        self.session_start_time = 0
        self.current_pitch = 0
        self.update_timer = QTimer()
        self.audio_analyzer = None
        self.training_controller = None

        # Track pitch data for in-range calculation
        self.pitch_readings = deque(maxlen=200)  # Keep last 200 readings for accuracy calculation

        # Pitch smoothing for display
        self.display_pitch_buffer = deque(maxlen=10)  # Small buffer for smooth display
        self.smoothed_pitch = 0

        # Analysis sensitivity settings - will be loaded from config
        self.analysis_mode = "Balanced"  # Default mode
        self.mode_settings = {
            "Strict": {
                "outlier_threshold": 0.25,  # 25% deviation allowed
                "smoothing_weight": 0.3,    # Less smoothing for precision
                "confidence_window": 15,    # Larger window for confidence
                "range_tolerance": 1.0      # Exact range matching
            },
            "Balanced": {
                "outlier_threshold": 0.4,   # 40% deviation allowed
                "smoothing_weight": 0.5,    # Moderate smoothing
                "confidence_window": 10,    # Medium window
                "range_tolerance": 1.15     # 15% range expansion
            },
            "Looser": {
                "outlier_threshold": 0.6,   # 60% deviation allowed
                "smoothing_weight": 0.7,    # More smoothing for comfort
                "confidence_window": 8,     # Smaller window for responsiveness
                "range_tolerance": 1.3      # 30% range expansion
            }
        }
        self.init_ui()
        self.setup_components()

    def init_ui(self):
        """Initialize modern training screen UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        # Modern header with card styling
        header_frame = QFrame()
        header_frame.setProperty("style", "card")
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AriaDesignSystem.COLORS['bg_secondary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: {AriaDesignSystem.RADIUS['lg']};
                padding: {AriaDesignSystem.SPACING['md']};
            }}
        """)

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 16, 16, 16)

        # Modern back button
        self.back_btn = QPushButton("← Back to Menu")
        self.back_btn.clicked.connect(self.back_requested.emit)
        self.back_btn.setProperty("style", "secondary")
        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_normal']};
                border-radius: {AriaDesignSystem.RADIUS['md']};
                padding: {AriaDesignSystem.SPACING['sm']} {AriaDesignSystem.SPACING['md']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {AriaDesignSystem.COLORS['bg_accent']};
                border-color: {AriaDesignSystem.COLORS['border_strong']};
            }}
        """)
        header_layout.addWidget(self.back_btn)

        # Modern title
        title = QLabel("Live Voice Training")
        title.setFont(QFont(AriaDesignSystem.FONTS['family_primary'], AriaDesignSystem.FONTS['xl'], QFont.Weight.Bold))
        title.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_primary']};
                margin: 0px;
                background: transparent;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)

        # Analysis sensitivity selector
        sensitivity_layout = QVBoxLayout()
        sensitivity_layout.setSpacing(4)

        sensitivity_label = QLabel("Analysis Mode:")
        sensitivity_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['text_secondary']};
            font-size: {AriaDesignSystem.FONTS['xs']}pt;
            background: transparent;
        """)

        self.sensitivity_combo = QComboBox()
        self.sensitivity_combo.addItems(["Strict", "Balanced", "Looser"])
        self.sensitivity_combo.setCurrentText("Balanced")
        self.sensitivity_combo.currentTextChanged.connect(self.change_analysis_mode)
        self.sensitivity_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: {AriaDesignSystem.RADIUS['md']};
                padding: {AriaDesignSystem.SPACING['xs']} {AriaDesignSystem.SPACING['sm']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                color: {AriaDesignSystem.COLORS['text_primary']};
                min-width: 80px;
            }}
            QComboBox:hover {{
                border-color: {AriaDesignSystem.COLORS['border_normal']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {AriaDesignSystem.COLORS['text_secondary']};
                margin-right: 8px;
            }}
        """)

        sensitivity_layout.addWidget(sensitivity_label)
        sensitivity_layout.addWidget(self.sensitivity_combo)
        header_layout.addLayout(sensitivity_layout)

        layout.addWidget(header_frame)

        # Pitch visualization
        viz_frame = QFrame()
        viz_frame.setStyleSheet("background-color: #333; border-radius: 8px; margin: 10px;")
        viz_layout = QVBoxLayout(viz_frame)

        viz_title = QLabel("Real-time Pitch Monitor")
        viz_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        viz_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        viz_title.setStyleSheet("color: #fff; margin: 10px;")
        viz_layout.addWidget(viz_title)

        self.pitch_meter = PitchMeterWidget()
        viz_layout.addWidget(self.pitch_meter)

        layout.addWidget(viz_frame)

        # Statistics
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background-color: #333; border-radius: 8px; margin: 10px;")
        stats_layout = QVBoxLayout(stats_frame)

        stats_title = QLabel("Session Statistics")
        stats_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        stats_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_title.setStyleSheet("color: #fff; margin: 10px;")
        stats_layout.addWidget(stats_title)

        self.stats_widget = TrainingStatsWidget()
        stats_layout.addWidget(self.stats_widget)

        layout.addWidget(stats_frame)

        # Safety warnings widget
        self.safety_widget = SafetyWarningWidget()
        layout.addWidget(self.safety_widget)

        # Controls
        controls_layout = QHBoxLayout()

        self.start_btn = QPushButton("Start Training")
        self.start_btn.clicked.connect(self.toggle_training)
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14pt;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        controls_layout.addWidget(self.start_btn)

        layout.addLayout(controls_layout)

        # Status
        self.status_label = QLabel("Click 'Start Training' to begin real-time pitch monitoring")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #888; margin: 10px; font-style: italic;")
        layout.addWidget(self.status_label)

        # Apply overall styling
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

    def setup_components(self):
        """Setup voice training components"""
        try:
            # Get components from voice trainer
            self.training_controller = self.voice_trainer.training_controller
            self.audio_analyzer = self.voice_trainer.factory.get_component('voice_analyzer')

            # Setup safety coordinator
            safety_monitor = self.voice_trainer.factory.get_component('safety_monitor')
            if safety_monitor:
                self.safety_coordinator = VoiceSafetyGUICoordinator(safety_monitor)
                self.safety_coordinator.register_safety_widget('training', self.safety_widget)

                # Connect safety widget signals
                self.safety_widget.break_requested.connect(self.handle_break_request)
            else:
                self.safety_coordinator = None

            # Setup update timer
            self.update_timer.timeout.connect(self.update_display)
            self.update_timer.setInterval(25)  # 40 FPS for smooth updates

            # Get current configuration
            config = self.voice_trainer.config_manager.get_config()
            target_range = config.get('target_pitch_range', [165, 265])
            self.pitch_meter.set_target_range(target_range[0], target_range[1])

            # Load analysis mode from config (suppress config saving during initialization)
            saved_analysis_mode = config.get('analysis_mode', 'Balanced')
            self.analysis_mode = saved_analysis_mode
            self.sensitivity_combo.setCurrentText(saved_analysis_mode)

            # Suppress saving during initialization
            self._suppress_config_save = True
            self.change_analysis_mode(saved_analysis_mode)
            delattr(self, '_suppress_config_save')

        except Exception as e:
            self.status_label.setText(f"Error initializing components: {e}")
            self.status_label.setStyleSheet("color: #f44336;")

    def _smooth_pitch(self, new_pitch):
        """Apply smoothing and outlier detection based on analysis mode"""
        if new_pitch <= 0:
            return self.smoothed_pitch

        # Get current mode settings
        settings = self.mode_settings[self.analysis_mode]
        outlier_threshold = settings["outlier_threshold"]
        smoothing_weight = settings["smoothing_weight"]

        # Adaptive outlier detection based on mode
        if len(self.display_pitch_buffer) > 3:
            recent_avg = sum(self.display_pitch_buffer) / len(self.display_pitch_buffer)

            # Use mode-specific outlier threshold
            if abs(new_pitch - recent_avg) > (recent_avg * outlier_threshold):
                # In looser mode, still accept but reduce influence
                if self.analysis_mode == "Looser":
                    # Blend outlier with recent average
                    new_pitch = recent_avg + (new_pitch - recent_avg) * 0.3
                else:
                    # Strict/Balanced: reject outlier
                    return self.smoothed_pitch

        # Add valid/adjusted reading to buffer
        self.display_pitch_buffer.append(new_pitch)

        # Calculate smoothed pitch with mode-appropriate weighting
        if len(self.display_pitch_buffer) > 0:
            if self.smoothed_pitch > 0:
                # Exponential moving average for more responsive feel
                self.smoothed_pitch = (self.smoothed_pitch * (1 - smoothing_weight) +
                                     new_pitch * smoothing_weight)
            else:
                # First reading
                self.smoothed_pitch = new_pitch

        return self.smoothed_pitch

    def change_analysis_mode(self, mode):
        """Change the analysis sensitivity mode"""
        try:
            self.analysis_mode = mode
            # Update buffer size based on mode
            settings = self.mode_settings[mode]
            confidence_window = settings["confidence_window"]

            # Adjust display buffer size based on mode
            self.display_pitch_buffer = deque(maxlen=confidence_window)

            # Save to config for persistence across sessions (only when changed by user)
            if hasattr(self, '_suppress_config_save'):
                return  # Don't save during initialization

            # Make config save non-blocking and handle interrupts gracefully
            try:
                success = self.voice_trainer.config_manager.update_config({'analysis_mode': mode})
                if not success:
                    # Use proper error handling system
                    from utils.error_handler import log_error
                    log_error(RuntimeError("Failed to save analysis mode to configuration"),
                             "TrainingScreen.change_analysis_mode")
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully - don't crash, just skip config save
                pass
            except Exception as e:
                # Use proper error handling system instead of print
                from utils.error_handler import log_error
                log_error(e, "TrainingScreen.change_analysis_mode")
        except KeyboardInterrupt:
            # Handle Ctrl+C at the top level - ensure we don't crash during mode change
            pass

        # Show user-friendly feedback (with safety checks for UI lifecycle)
        mode_descriptions = {
            "Strict": "Precise analysis - exact pitch tracking",
            "Balanced": "Natural feel - good balance of accuracy & smoothness",
            "Looser": "Forgiving analysis - smooth and encouraging"
        }

        try:
            if hasattr(self, 'status_label') and self.status_label is not None:
                # Additional safety check to ensure widget hasn't been deleted
                if hasattr(self.status_label, 'setText'):
                    self.status_label.setText(f"Analysis mode: {mode} - {mode_descriptions[mode]}")
                    self.status_label.setStyleSheet("color: #2196F3; font-style: italic;")
        except RuntimeError:
            # Widget has been deleted - this is expected during cleanup
            pass

    def _safe_update_status(self, message, style="color: #888;"):
        """Safely update status label with proper lifecycle checks"""
        try:
            if hasattr(self, 'status_label') and self.status_label is not None:
                if hasattr(self.status_label, 'setText'):
                    self.status_label.setText(message)
                    self.status_label.setStyleSheet(style)
        except RuntimeError:
            # Widget has been deleted - this is expected during cleanup
            pass

    def _calculate_human_range_percentage(self, target_range):
        """Calculate in-range percentage with human-feeling analysis"""
        if len(self.pitch_readings) == 0:
            return 0

        settings = self.mode_settings[self.analysis_mode]
        range_tolerance = settings["range_tolerance"]

        # Expand target range based on analysis mode for more human feel
        min_hz = target_range[0] / range_tolerance
        max_hz = target_range[1] * range_tolerance

        # Use recent readings for more responsive feel (last 50 readings)
        recent_readings = list(self.pitch_readings)[-50:] if len(self.pitch_readings) > 50 else list(self.pitch_readings)

        # Count readings in expanded range
        in_range_count = 0
        for pitch in recent_readings:
            if min_hz <= pitch <= max_hz:
                in_range_count += 1
            elif self.analysis_mode == "Looser":
                # In looser mode, give partial credit for near-misses
                target_center = (target_range[0] + target_range[1]) / 2
                target_width = target_range[1] - target_range[0]

                # Calculate distance from center as percentage of range width
                distance_ratio = abs(pitch - target_center) / (target_width * 1.5)

                # Give partial credit if within 150% of range
                if distance_ratio <= 1.5:
                    partial_credit = max(0, 1 - (distance_ratio / 1.5))
                    in_range_count += partial_credit * 0.5  # Max 50% credit for near-misses

        # Calculate percentage with human-friendly rounding
        if len(recent_readings) > 0:
            raw_percentage = (in_range_count / len(recent_readings)) * 100

            # Apply mode-specific adjustments for encouragement
            if self.analysis_mode == "Looser" and raw_percentage > 30:
                # Slightly boost percentage in looser mode to encourage users
                raw_percentage = min(100, raw_percentage * 1.1)
            elif self.analysis_mode == "Strict":
                # More conservative in strict mode
                raw_percentage = raw_percentage * 0.9

            return max(0, min(100, raw_percentage))

        return 0

    def toggle_training(self):
        """Start or stop training session"""
        if not self.training_active:
            self.start_training()
        else:
            self.stop_training()

    def start_training(self):
        """Start live training session"""
        try:
            # Get configuration for training
            config = self.voice_trainer.config_manager.get_config()

            # Start actual live training with audio processing
            success = self.training_controller.start_live_training(config, self.handle_audio_callback)

            if not success:
                self.status_label.setText("Error: Could not start audio system. Check microphone.")
                self.status_label.setStyleSheet("color: #f44336;")
                return

            self.training_active = True
            self.session_start_time = time.time()

            # Clear previous pitch readings for fresh session
            self.pitch_readings.clear()
            self.display_pitch_buffer.clear()
            self.current_pitch = 0
            self.smoothed_pitch = 0

            # Update UI
            self.start_btn.setText("Stop Training")
            self.start_btn.setStyleSheet(self.start_btn.styleSheet().replace("#4CAF50", "#f44336"))
            self.status_label.setText("Training active - speak naturally to see your pitch")
            self.status_label.setStyleSheet("color: #4CAF50;")

            # Start update timer
            self.update_timer.start()

        except Exception as e:
            self.status_label.setText(f"Error starting training: {e}")
            self.status_label.setStyleSheet("color: #f44336;")

    def stop_training(self):
        """Stop live training session with interrupt-safe cleanup"""
        try:
            # Calculate session duration for safety summary
            session_duration = 0
            if hasattr(self, 'session_start_time') and self.session_start_time:
                session_duration = (time.time() - self.session_start_time) / 60  # Convert to minutes

            # Stop actual live training - this is critical and shouldn't be interrupted
            try:
                self.training_controller.stop_live_training()
            except KeyboardInterrupt:
                # Force stop even if interrupted
                self.training_active = False
                if hasattr(self, 'update_timer'):
                    self.update_timer.stop()
                raise  # Re-raise to let caller handle

            self.training_active = False

            # Show safety summary if session was long enough (but handle interrupts)
            try:
                if session_duration >= 1.0 and hasattr(self, 'safety_coordinator') and self.safety_coordinator:
                    self.safety_coordinator.show_safety_summary(session_duration, 'training')
            except KeyboardInterrupt:
                pass  # Skip safety summary if interrupted

            # Update UI (make it interrupt-safe)
            try:
                if hasattr(self, 'start_btn') and self.start_btn:
                    self.start_btn.setText("Start Training")
                    self.start_btn.setStyleSheet(self.start_btn.styleSheet().replace("#f44336", "#4CAF50"))
                if hasattr(self, 'status_label') and self.status_label:
                    self.status_label.setText("Training stopped. Session data saved.")
                    self.status_label.setStyleSheet("color: #888;")
            except (KeyboardInterrupt, RuntimeError):
                pass  # UI updates are not critical during forced shutdown

            # Stop update timer - this is critical
            if hasattr(self, 'update_timer') and self.update_timer:
                self.update_timer.stop()

        except KeyboardInterrupt:
            # Ensure training is marked as stopped even if interrupted
            self.training_active = False
            if hasattr(self, 'update_timer') and self.update_timer:
                self.update_timer.stop()
        except Exception as e:
            try:
                if hasattr(self, 'status_label') and self.status_label:
                    self.status_label.setText(f"Error stopping training: {e}")
                    self.status_label.setStyleSheet("color: #f44336;")
            except (KeyboardInterrupt, RuntimeError):
                pass

    def handle_audio_callback(self, callback_type, data):
        """Handle callbacks from the training controller"""
        if callback_type == 'training_status':
            # Real-time pitch and status data
            raw_pitch = data.get('pitch', 0)
            if raw_pitch > 0:
                # Apply smoothing for display
                self.current_pitch = self._smooth_pitch(raw_pitch)
                # Store smoothed pitch for in-range calculation (sync with display)
                if self.current_pitch > 0:
                    self.pitch_readings.append(self.current_pitch)

        elif callback_type == 'noise_feedback':
            message = data.get('message', '')
            self._safe_update_status(message, "color: #FFC107;")

        elif callback_type == 'status_update':
            message = data.get('message', '')
            self._safe_update_status(message, "color: #888;")

        elif callback_type == 'safety_warning':
            # Show safety warning in dedicated widget
            if self.safety_coordinator:
                self.safety_coordinator.handle_safety_warning(data, 'training')
            else:
                # Fallback to status label
                message = data.get('message', 'Safety warning')
                self._safe_update_status(f"⚠️ {message}", "color: #ff5722;")

    def update_display(self):
        """Update real-time display with current voice data"""
        if not self.training_active:
            return

        try:
            # Use the real-time current_pitch from callback
            current_pitch = getattr(self, 'current_pitch', 0)

            # Update pitch meter with real-time data (with safety checks)
            if hasattr(self, 'pitch_meter') and self.pitch_meter is not None:
                try:
                    self.pitch_meter.set_current_pitch(current_pitch)
                except RuntimeError:
                    # Widget deleted, stop trying to update it
                    return

            # Calculate session stats
            session_time = time.time() - self.session_start_time

            # Calculate in-range percentage with human-feeling analysis
            if hasattr(self, 'pitch_meter') and self.pitch_meter is not None:
                try:
                    target_range = [self.pitch_meter.target_min, self.pitch_meter.target_max]
                    in_range_pct = self._calculate_human_range_percentage(target_range)

                    # Get resonance data from audio analyzer
                    resonance_data = None
                    try:
                        if hasattr(self, 'audio_analyzer') and self.audio_analyzer is not None:
                            resonance_data = getattr(self.audio_analyzer, 'current_resonance', None)
                    except (AttributeError, RuntimeError):
                        # Audio analyzer not available or deleted
                        pass

                    # Update stats display (with safety checks)
                    if hasattr(self, 'stats_widget') and self.stats_widget is not None:
                        try:
                            self.stats_widget.update_stats(session_time, current_pitch, target_range, in_range_pct, resonance_data)
                        except RuntimeError:
                            # Widget deleted
                            pass
                except (RuntimeError, AttributeError):
                    # Widget deleted or attributes not available
                    pass

        except Exception as e:
            # Use proper error handling instead of silent pass
            from utils.error_handler import log_error
            log_error(e, "TrainingScreen.update_display")

    def handle_break_request(self):
        """Handle break request from safety widget"""
        if self.training_active:
            self.stop_training()

        # Show break message with safe update
        self._safe_update_status(
            "Training paused for voice break. Take a few minutes to rest your voice.",
            "color: #2196F3; font-weight: bold;"
        )

    def cleanup(self):
        """Clean up resources when leaving screen with interrupt-safe operations"""
        try:
            # Stop training first to halt callbacks - handle interrupts gracefully
            if self.training_active:
                try:
                    self.stop_training()
                except KeyboardInterrupt:
                    # Force essential cleanup even if interrupted
                    self.training_active = False
                    if hasattr(self, 'update_timer') and self.update_timer:
                        self.update_timer.stop()

            # Stop update timer - critical for preventing crashes
            if hasattr(self, 'update_timer') and self.update_timer is not None:
                self.update_timer.stop()

            # Clear safety warnings (non-critical, can be interrupted)
            try:
                if hasattr(self, 'safety_coordinator') and self.safety_coordinator:
                    self.safety_coordinator.clear_all_warnings()
            except KeyboardInterrupt:
                pass  # Skip if interrupted

            # Mark training as inactive to prevent any remaining callbacks
            self.training_active = False

        except KeyboardInterrupt:
            # Ensure critical cleanup happens even during interrupt, please...
            self.training_active = False
            if hasattr(self, 'update_timer') and self.update_timer:
                self.update_timer.stop()
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "TrainingScreen.cleanup")