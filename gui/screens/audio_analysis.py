from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,  # type: ignore
                            QLabel, QFileDialog, QTextEdit, QProgressBar, QGroupBox,
                            QGridLayout, QFrame, QScrollArea, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer  # type: ignore
from PyQt6.QtGui import QFont, QPalette, QColor  # type: ignore
import os
from voice.pitch_analyzer import AudioFileAnalyzer, PitchGoalManager
from ..design_system import AriaDesignSystem


class AudioAnalysisWorker(QThread):
    """Worker thread for audio analysis to prevent GUI freezing"""

    analysis_progress = pyqtSignal(str)  # Progress messages
    analysis_complete = pyqtSignal(dict)  # Results
    analysis_error = pyqtSignal(str)     # Error messages

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.analyzer = AudioFileAnalyzer()

    def run(self):
        try:
            self.analysis_progress.emit("Loading audio file...")

            # Validate file first
            if not self.analyzer.is_supported_file(self.file_path):
                self.analysis_error.emit(f"Unsupported file format. Supported: {self.analyzer.supported_formats}")
                return

            if not os.path.exists(self.file_path):
                self.analysis_error.emit("Audio file not found")
                return

            self.analysis_progress.emit("Analyzing pitch characteristics...")

            # Run the full analysis
            results = self.analyzer.full_analysis(self.file_path)

            self.analysis_progress.emit("Analysis complete!")
            self.analysis_complete.emit(results)

        except Exception as e:
            self.analysis_error.emit(f"Analysis failed: {str(e)}")


class AudioAnalysisScreen(QWidget):
    """Audio file analysis screen with real pitch analysis functionality"""

    back_requested = pyqtSignal()

    def __init__(self, voice_trainer):
        super().__init__()
        self.voice_trainer = voice_trainer
        self.analyzer = AudioFileAnalyzer()
        self.goal_manager = PitchGoalManager()
        self.current_results = None
        self.worker_thread = None

        self.init_ui()
        self.load_analysis_history()

    def init_ui(self):
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
            AudioAnalysisScreen {{
                background-color: {AriaDesignSystem.COLORS['bg_primary']};
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-family: {AriaDesignSystem.FONTS['family_primary']};
            }}
        """)

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
        header_layout.addWidget(nav_bar)

        # Title section (mirrors onboarding header)
        title_section = QWidget()
        title_layout = QVBoxLayout(title_section)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)

        # Main title
        self.title_label = QLabel("Audio File Analysis")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont(AriaDesignSystem.FONTS['family_primary'], 22, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"""
            color: {AriaDesignSystem.COLORS['primary']};
            margin-bottom: 8px;
        """)
        title_layout.addWidget(self.title_label)

        # Subtitle
        self.subtitle_label = QLabel("Analyze your voice recordings for pitch and quality insights")
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
                padding: 32px;
            }}
        """)

        # This will contain the file selection and analysis areas
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setSpacing(24)

        # File selection section
        self.create_file_selection_section(content_layout)

        # Analysis section (initially hidden)
        self.create_analysis_section(content_layout)

        layout.addWidget(self.content_frame)

    def create_file_selection_section(self, layout):
        """Create modern file selection section"""
        # File selection card
        file_card = QFrame()
        file_card.setStyleSheet(f"""
            QFrame {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: 8px;
                padding: 20px;
            }}
        """)
        file_layout = QVBoxLayout(file_card)
        file_layout.setSpacing(16)

        # Section title
        title_label = QLabel("Select Audio File")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['md']}pt;
                font-weight: 600;
                background: transparent;
            }}
        """)
        file_layout.addWidget(title_label)

        # Description
        info_label = QLabel("Upload an audio file to analyze your voice pitch and characteristics")
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_secondary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                background: transparent;
                line-height: 1.4;
            }}
        """)
        file_layout.addWidget(info_label)

        # File selection button and status
        button_layout = QHBoxLayout()
        button_layout.setSpacing(16)

        self.select_file_button = QPushButton("Choose Audio File")
        self.select_file_button.clicked.connect(self.select_audio_file)
        self.select_file_button.setStyleSheet(f"""
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
        button_layout.addWidget(self.select_file_button)

        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_muted']};
                font-style: italic;
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                background: transparent;
            }}
        """)
        button_layout.addWidget(self.file_path_label)
        button_layout.addStretch()
        file_layout.addLayout(button_layout)

        # Supported formats
        formats_label = QLabel(f"Supported formats: {', '.join(self.analyzer.supported_formats)}")
        formats_label.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_muted']};
                font-size: {AriaDesignSystem.FONTS['xs']}pt;
                background: transparent;
            }}
        """)
        file_layout.addWidget(formats_label)

        layout.addWidget(file_card)

    def create_analysis_section(self, layout):
        """Create modern analysis progress and results section"""
        # Progress card
        self.progress_card = QFrame()
        self.progress_card.setStyleSheet(f"""
            QFrame {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: 8px;
                padding: 20px;
            }}
        """)
        self.progress_card.setVisible(False)  # Initially hidden
        progress_layout = QVBoxLayout(self.progress_card)
        progress_layout.setSpacing(12)

        # Progress title
        progress_title = QLabel("Analysis Progress")
        progress_title.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['md']}pt;
                font-weight: 600;
                background: transparent;
            }}
        """)
        progress_layout.addWidget(progress_title)

        self.progress_label = QLabel("Ready to analyze")
        self.progress_label.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_secondary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                background: transparent;
            }}
        """)
        progress_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: 6px;
                text-align: center;
                font-weight: 500;
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                background-color: {AriaDesignSystem.COLORS['bg_primary']};
                color: {AriaDesignSystem.COLORS['text_primary']};
                min-height: 24px;
            }}
            QProgressBar::chunk {{
                background-color: {AriaDesignSystem.COLORS['primary']};
                border-radius: 5px;
            }}
        """)
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        layout.addWidget(self.progress_card)

        # Results area with modern styling
        self.results_card = QFrame()
        self.results_card.setStyleSheet(f"""
            QFrame {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: 8px;
                padding: 20px;
            }}
        """)
        results_layout = QVBoxLayout(self.results_card)
        results_layout.setSpacing(16)

        # Results title
        results_title = QLabel("Analysis Results")
        results_title.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['md']}pt;
                font-weight: 600;
                background: transparent;
            }}
        """)
        results_layout.addWidget(results_title)

        # Scrollable results area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {AriaDesignSystem.COLORS['bg_primary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: 6px;
            }}
        """)

        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setContentsMargins(16, 16, 16, 16)
        self.results_layout.setSpacing(12)

        # Initially show placeholder
        placeholder_label = QLabel("Analysis results will appear here after uploading and analyzing an audio file")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_muted']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-style: italic;
                background: transparent;
                padding: 40px;
            }}
        """)
        self.results_layout.addWidget(placeholder_label)

        scroll_area.setWidget(self.results_widget)
        results_layout.addWidget(scroll_area)
        layout.addWidget(self.results_card)

    def select_audio_file(self):
        """Open file dialog to select audio file"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.wav *.mp3 *.flac *.ogg *.m4a *.aac);;All Files (*)"
        )

        if file_path:
            self.file_path_label.setText(os.path.basename(file_path))
            self.start_analysis(file_path)

    def start_analysis(self, file_path):
        """Start audio analysis in background thread"""
        # Update UI for analysis state
        self.progress_card.setVisible(True)
        self.progress_label.setText("Starting analysis...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.select_file_button.setEnabled(False)

        # Clear previous results
        self.clear_results()

        # Start worker thread
        self.worker_thread = AudioAnalysisWorker(file_path)
        self.worker_thread.analysis_progress.connect(self.update_progress)
        self.worker_thread.analysis_complete.connect(self.show_results)
        self.worker_thread.analysis_error.connect(self.show_error)
        self.worker_thread.finished.connect(self.analysis_finished)
        self.worker_thread.start()

    def update_progress(self, message):
        """Update progress display"""
        self.progress_label.setText(message)

    def analysis_finished(self):
        """Clean up after analysis completes"""
        self.progress_bar.setVisible(False)
        self.select_file_button.setEnabled(True)
        if self.worker_thread:
            self.worker_thread.deleteLater()
            self.worker_thread = None

    def show_error(self, error_message):
        """Show analysis error"""
        self.progress_label.setText(f"Error: {error_message}")

        # Show error in results area
        self.clear_results()
        error_label = QLabel(f"Analysis Error: {error_message}")
        error_label.setProperty("style", "error")
        error_label.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['error']};
                font-size: {AriaDesignSystem.FONTS['md']}pt;
                font-weight: 600;
                padding: 20px;
                background-color: {AriaDesignSystem.COLORS['error_bg']};
                border: 1px solid {AriaDesignSystem.COLORS['error']};
                border-radius: {AriaDesignSystem.RADIUS['md']};
                margin: 8px;
            }}
        """)
        error_label.setWordWrap(True)
        self.results_layout.addWidget(error_label)

    def show_results(self, results):
        """Display analysis results"""
        self.current_results = results
        self.progress_label.setText("Analysis complete!")

        # Clear previous results
        self.clear_results()

        # File info section
        file_info = results.get('file_info', {})
        self.add_file_info_section(file_info)

        # Pitch analysis section
        pitch_analysis = results.get('pitch_analysis', {})
        self.add_pitch_analysis_section(pitch_analysis)

        # Voice quality section
        quality_analysis = results.get('voice_quality', {})
        self.add_voice_quality_section(quality_analysis)

        # Summary and recommendations
        summary = results.get('summary', {})
        self.add_summary_section(summary)

        # Goal setting section
        self.add_goal_setting_section(summary)

        # Save to history
        self.goal_manager.add_analysis_result(results, set_as_goal=False)

    def clear_results(self):
        """Clear all results from display"""
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def add_file_info_section(self, file_info):
        """Add file information section"""
        group = QGroupBox("File Information")
        layout = QGridLayout()
        layout.setSpacing(8)

        # Consistent label styling
        label_style = f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-weight: 500;
                background: transparent;
            }}
        """

        value_style = f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_secondary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                background: transparent;
            }}
        """

        name_label = QLabel("File Name:")
        name_label.setStyleSheet(label_style)
        layout.addWidget(name_label, 0, 0)
        name_value = QLabel(file_info.get('file_name', 'Unknown'))
        name_value.setStyleSheet(value_style)
        layout.addWidget(name_value, 0, 1)

        duration_label = QLabel("Duration:")
        duration_label.setStyleSheet(label_style)
        layout.addWidget(duration_label, 1, 0)
        duration = file_info.get('duration_seconds', 0)
        duration_text = f"{duration:.1f} seconds" if duration > 0 else "Unknown"
        duration_value = QLabel(duration_text)
        duration_value.setStyleSheet(value_style)
        layout.addWidget(duration_value, 1, 1)

        size_label = QLabel("File Size:")
        size_label.setStyleSheet(label_style)
        layout.addWidget(size_label, 2, 0)
        size_mb = file_info.get('file_size_mb', 0)
        size_text = f"{size_mb:.1f} MB" if size_mb > 0 else "Unknown"
        size_value = QLabel(size_text)
        size_value.setStyleSheet(value_style)
        layout.addWidget(size_value, 2, 1)

        rate_label = QLabel("Sample Rate:")
        rate_label.setStyleSheet(label_style)
        layout.addWidget(rate_label, 3, 0)
        rate_value = QLabel(f"{file_info.get('sample_rate', 0)} Hz")
        rate_value.setStyleSheet(value_style)
        layout.addWidget(rate_value, 3, 1)

        group.setLayout(layout)
        self.results_layout.addWidget(group)

    def add_pitch_analysis_section(self, pitch_analysis):
        """Add pitch analysis results section"""
        group = QGroupBox("Pitch Analysis")
        layout = QGridLayout()

        # Add consistent styling for all labels
        label_style = f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-weight: 500;
                background: transparent;
            }}
        """

        value_style = f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_secondary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                background: transparent;
            }}
        """

        mean_pitch = pitch_analysis.get('mean_pitch', 0)
        avg_label = QLabel("Average Pitch:")
        avg_label.setStyleSheet(label_style)
        layout.addWidget(avg_label, 0, 0)

        pitch_text = f"{mean_pitch:.1f} Hz" if mean_pitch > 0 else "No pitch detected"
        pitch_label = QLabel(pitch_text)
        if mean_pitch > 0:
            pitch_label.setStyleSheet(f"""
                QLabel {{
                    color: {AriaDesignSystem.COLORS['success']};
                    font-size: {AriaDesignSystem.FONTS['sm']}pt;
                    font-weight: 600;
                    background: transparent;
                }}
            """)
        else:
            pitch_label.setStyleSheet(value_style)
        layout.addWidget(pitch_label, 0, 1)

        range_label = QLabel("Pitch Range:")
        range_label.setStyleSheet(label_style)
        layout.addWidget(range_label, 1, 0)
        min_pitch = pitch_analysis.get('min_pitch', 0)
        max_pitch = pitch_analysis.get('max_pitch', 0)
        range_text = f"{min_pitch:.1f} - {max_pitch:.1f} Hz" if min_pitch > 0 else "Unknown"
        range_value = QLabel(range_text)
        range_value.setStyleSheet(value_style)
        layout.addWidget(range_value, 1, 1)

        stability_label = QLabel("Pitch Stability:")
        stability_label.setStyleSheet(label_style)
        layout.addWidget(stability_label, 2, 0)
        stability = pitch_analysis.get('pitch_stability', 0)
        stability_text = f"{stability:.1%}" if stability >= 0 else "Unknown"
        stability_value = QLabel(stability_text)
        stability_value.setStyleSheet(value_style)
        layout.addWidget(stability_value, 2, 1)

        voiced_label = QLabel("Voiced Speech:")
        voiced_label.setStyleSheet(label_style)
        layout.addWidget(voiced_label, 3, 0)
        voiced_pct = pitch_analysis.get('voiced_percentage', 0)
        voiced_text = f"{voiced_pct:.1f}%" if voiced_pct >= 0 else "Unknown"
        voiced_value = QLabel(voiced_text)
        voiced_value.setStyleSheet(value_style)
        layout.addWidget(voiced_value, 3, 1)

        group.setLayout(layout)
        self.results_layout.addWidget(group)

    def add_voice_quality_section(self, quality_analysis):
        """Add voice quality analysis section"""
        group = QGroupBox("Voice Quality")
        layout = QGridLayout()

        # Consistent label styling
        label_style = f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-weight: 500;
                background: transparent;
            }}
        """

        score_label = QLabel("Voice Quality Score:")
        score_label.setStyleSheet(label_style)
        layout.addWidget(score_label, 0, 0)

        quality_score = quality_analysis.get('voice_quality_score', 0)
        score_text = f"{quality_score:.1%}" if quality_score >= 0 else "Unknown"
        score_value = QLabel(score_text)

        # Use design system colors for quality indicators
        if quality_score > 0.7:
            score_value.setStyleSheet(f"""
                QLabel {{
                    color: {AriaDesignSystem.COLORS['success']};
                    font-size: {AriaDesignSystem.FONTS['sm']}pt;
                    font-weight: 600;
                    background: transparent;
                }}
            """)
        elif quality_score > 0.4:
            score_value.setStyleSheet(f"""
                QLabel {{
                    color: {AriaDesignSystem.COLORS['warning']};
                    font-size: {AriaDesignSystem.FONTS['sm']}pt;
                    font-weight: 600;
                    background: transparent;
                }}
            """)
        else:
            score_value.setStyleSheet(f"""
                QLabel {{
                    color: {AriaDesignSystem.COLORS['error']};
                    font-size: {AriaDesignSystem.FONTS['sm']}pt;
                    font-weight: 600;
                    background: transparent;
                }}
            """)
        layout.addWidget(score_value, 0, 1)

        energy_label = QLabel("Energy Consistency:")
        energy_label.setStyleSheet(label_style)
        layout.addWidget(energy_label, 1, 0)

        rms_mean = quality_analysis.get('rms_energy_mean', 0)
        rms_std = quality_analysis.get('rms_energy_std', 0)
        energy_text = "Good" if rms_std < rms_mean * 0.5 else "Variable"
        energy_value = QLabel(energy_text)
        energy_value.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_secondary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                background: transparent;
            }}
        """)
        layout.addWidget(energy_value, 1, 1)

        group.setLayout(layout)
        self.results_layout.addWidget(group)

    def add_summary_section(self, summary):
        """Add analysis summary and recommendations"""
        group = QGroupBox("Analysis Summary")
        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Overall assessment
        assessment = summary.get('pitch_assessment', 'No assessment available')
        assessment_label = QLabel(f"Assessment: {assessment}")
        assessment_label.setWordWrap(True)
        assessment_label.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['info']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-weight: 600;
                background: transparent;
                padding: 8px;
            }}
        """)
        layout.addWidget(assessment_label)

        # Goal suggestion
        suggestion = summary.get('goal_suggestion', 'No suggestions available')
        suggestion_label = QLabel(f"Recommendation: {suggestion}")
        suggestion_label.setWordWrap(True)
        suggestion_label.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                background: transparent;
                padding: 8px;
                line-height: 1.4;
            }}
        """)
        layout.addWidget(suggestion_label)

        # Target range
        target_low = summary.get('recommended_target_low', 0)
        target_high = summary.get('recommended_target_high', 0)
        if target_low > 0 and target_high > 0:
            target_label = QLabel(f"Suggested Training Range: {target_low} - {target_high} Hz")
            target_label.setStyleSheet(f"""
                QLabel {{
                    color: {AriaDesignSystem.COLORS['success']};
                    font-size: {AriaDesignSystem.FONTS['sm']}pt;
                    font-weight: 600;
                    background: transparent;
                    padding: 8px;
                }}
            """)
            layout.addWidget(target_label)

        group.setLayout(layout)
        self.results_layout.addWidget(group)

    def add_goal_setting_section(self, summary):
        """Add goal setting options"""
        group = QGroupBox("Training Goal Setup")
        layout = QVBoxLayout()
        layout.setSpacing(16)

        info_label = QLabel("Would you like to set a new training goal based on this analysis?")
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                background: transparent;
                margin-bottom: 8px;
            }}
        """)
        layout.addWidget(info_label)

        button_layout = QHBoxLayout()

        set_goal_button = QPushButton("Set as Training Goal")
        set_goal_button.clicked.connect(self.set_training_goal)

        target_low = summary.get('recommended_target_low', 0)
        target_high = summary.get('recommended_target_high', 0)
        if target_low > 0 and target_high > 0:
            set_goal_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AriaDesignSystem.COLORS['success']};
                    border: none;
                    border-radius: {AriaDesignSystem.RADIUS['md']};
                    padding: 12px 20px;
                    color: {AriaDesignSystem.COLORS['text_primary']};
                    font-size: {AriaDesignSystem.FONTS['sm']}pt;
                    font-weight: 600;
                    min-height: 40px;
                    min-width: 160px;
                }}
                QPushButton:hover {{
                    background-color: {AriaDesignSystem.COLORS['success_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {AriaDesignSystem.COLORS['success_hover']};
                }}
            """)

            goal_preview = QLabel(f"Goal will be set to {target_low} Hz")
            goal_preview.setStyleSheet(f"""
                QLabel {{
                    color: {AriaDesignSystem.COLORS['text_muted']};
                    font-style: italic;
                    font-size: {AriaDesignSystem.FONTS['sm']}pt;
                    background: transparent;
                    margin-left: 12px;
                }}
            """)
            button_layout.addWidget(set_goal_button)
            button_layout.addWidget(goal_preview)
        else:
            set_goal_button.setEnabled(False)
            set_goal_button.setText("No Valid Goal Available")
            set_goal_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                    border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                    border-radius: {AriaDesignSystem.RADIUS['md']};
                    padding: 12px 20px;
                    color: {AriaDesignSystem.COLORS['text_muted']};
                    font-size: {AriaDesignSystem.FONTS['sm']}pt;
                    font-weight: 500;
                    min-height: 40px;
                    min-width: 160px;
                }}
                QPushButton:disabled {{
                    opacity: 0.5;
                }}
            """)
            button_layout.addWidget(set_goal_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        group.setLayout(layout)
        self.results_layout.addWidget(group)

    def set_training_goal(self):
        """Set training goal based on analysis results"""
        if not self.current_results:
            return

        try:
            target_low, target_high = self.goal_manager.set_goal_from_analysis(self.current_results)

            if target_low and target_high:
                QMessageBox.information(
                    self,
                    "Goal Set Successfully",
                    f"Your training goal has been updated to {target_low} Hz.\n\n"
                    f"Target range: {target_low} - {target_high} Hz\n\n"
                    "You can now use this goal in your live training sessions!"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Goal Setting Failed",
                    "Could not set training goal. Please try again or set a manual goal in settings."
                )

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AudioAnalysisScreen.set_training_goal")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to set training goal: {str(e)}"
            )

    def load_analysis_history(self):
        """Load and display analysis history summary"""
        try:
            history_summary = self.goal_manager.get_analysis_history_summary()

            if history_summary.get('count', 0) > 0:
                # Update progress label to show history info
                recent_files = history_summary.get('recent_files', [])
                if recent_files:
                    recent_text = ", ".join(recent_files[-3:])  # Show last 3 files
                    self.progress_label.setText(f"Ready to analyze (Recent: {recent_text})")

        except Exception as e:
            # Log history loading errors but don't interrupt user flow
            from utils.error_handler import log_error
            log_error(e, "AudioAnalysisScreen.load_analysis_history")