"""
Aria Voice Studio - Public Beta (v5) - Audio Analysis Screen
Full backend integration with real librosa pitch analysis
NO MOCK DATA - All results from voice.pitch_analyzer
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QFileDialog, QMessageBox,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from ..design_system import (
    AriaColors, AriaTypography, AriaSpacing, AriaRadius,
    InfoCard, PrimaryButton, SecondaryButton, create_gradient_background,
    TitleLabel, BodyLabel, CaptionLabel, StatCard, create_styled_progress_bar
)


class AudioAnalysisWorker(QThread):
    """Worker thread for audio analysis - prevents GUI freezing"""

    analysis_progress = pyqtSignal(str)      # Progress messages
    analysis_complete = pyqtSignal(dict)     # Results from backend
    analysis_error = pyqtSignal(str)         # Error messages

    def __init__(self, file_path, analyzer):
        super().__init__()
        self.file_path = file_path
        self.analyzer = analyzer

    def run(self):
        """Run analysis in background thread"""
        try:
            import os
            self.analysis_progress.emit("Loading audio file...")

            # Validate file
            if not self.analyzer.is_supported_file(self.file_path):
                self.analysis_error.emit(f"Unsupported format. Supported: {self.analyzer.supported_formats}")
                return

            if not os.path.exists(self.file_path):
                self.analysis_error.emit("Audio file not found")
                return

            self.analysis_progress.emit("Analyzing pitch characteristics...")

            # Call real backend analysis
            results = self.analyzer.full_analysis(self.file_path)

            self.analysis_progress.emit("Analysis complete!")
            self.analysis_complete.emit(results)

        except Exception as e:
            self.analysis_error.emit(f"Analysis failed: {str(e)}")


class AudioAnalysisScreen(QWidget):
    """Audio analysis screen with REAL backend integration"""

    def __init__(self, voice_trainer):
        super().__init__()
        self.voice_trainer = voice_trainer

        # Import real backend analyzer
        from voice.pitch_analyzer import AudioFileAnalyzer, PitchGoalManager
        self.analyzer = AudioFileAnalyzer()
        self.goal_manager = PitchGoalManager()

        self.current_results = None
        self.worker_thread = None

        self.init_ui()

    def init_ui(self):
        """Initialize audio analysis UI"""
        # Gradient background
        content = QFrame()
        content.setStyleSheet(create_gradient_background())

        layout = QVBoxLayout(content)
        layout.setContentsMargins(AriaSpacing.GIANT, AriaSpacing.GIANT, AriaSpacing.GIANT, AriaSpacing.GIANT)
        layout.setSpacing(AriaSpacing.XL)

        # Title
        layout.addWidget(TitleLabel("📊 Audio File Analysis"))

        # Upload card
        upload_card = InfoCard("📁 Upload Your Recording", min_height=240)

        info_label = QLabel(
            "Upload a voice recording to analyze pitch characteristics.\n\n"
            f"Supported formats: {', '.join(self.analyzer.supported_formats)}"
        )
        info_label.setStyleSheet(f"color: {AriaColors.WHITE_85}; font-size: {AriaTypography.BODY}px; background: transparent;")
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_card.content_layout.addWidget(info_label)

        # File path label
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.BODY_SMALL}px; background: transparent; font-style: italic;")
        self.file_path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_path_label.setWordWrap(True)
        upload_card.content_layout.addWidget(self.file_path_label)

        upload_btn = PrimaryButton("Select Audio File")
        upload_btn.clicked.connect(self.select_file)
        upload_card.content_layout.addWidget(upload_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(upload_card)

        # Progress bar (hidden by default)
        self.progress_card = InfoCard("Analysis Progress", min_height=100)
        self.progress_bar = create_styled_progress_bar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_card.content_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("Initializing...")
        self.progress_label.setStyleSheet(f"color: white; font-size: {AriaTypography.BODY}px; background: transparent;")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_card.content_layout.addWidget(self.progress_label)

        self.progress_card.setVisible(False)
        layout.addWidget(self.progress_card)

        # Results section (hidden until analysis complete)
        self.results_frame = QFrame()
        results_layout = QVBoxLayout(self.results_frame)
        results_layout.setSpacing(AriaSpacing.LG)

        results_title = QLabel("Analysis Results")
        results_title.setStyleSheet(f"color: white; font-size: {AriaTypography.HEADING}px; font-weight: bold; background: transparent;")
        results_layout.addWidget(results_title)

        # Results grid - responsive layout
        results_grid = QHBoxLayout()
        results_grid.setSpacing(AriaSpacing.MD)

        # Average Pitch
        avg_card = InfoCard("Average Pitch", min_height=180)
        avg_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.avg_pitch_label = QLabel("-- Hz")
        self.avg_pitch_label.setStyleSheet("color: white; font-size: 28px; font-weight: bold; background: transparent;")
        self.avg_pitch_label.setWordWrap(True)
        avg_card.content_layout.addWidget(self.avg_pitch_label, alignment=Qt.AlignmentFlag.AlignCenter)
        results_grid.addWidget(avg_card)

        # Pitch Range
        range_card = InfoCard("Pitch Range", min_height=180)
        range_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.range_label = QLabel("-- to -- Hz")
        self.range_label.setStyleSheet(f"color: white; font-size: {AriaTypography.SUBHEADING}px; font-weight: 600; background: transparent;")
        self.range_label.setWordWrap(True)
        range_card.content_layout.addWidget(self.range_label, alignment=Qt.AlignmentFlag.AlignCenter)
        results_grid.addWidget(range_card)

        # Stability
        stability_card = InfoCard("Stability", min_height=180)
        stability_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.stability_label = QLabel("--%")
        self.stability_label.setStyleSheet("color: white; font-size: 28px; font-weight: bold; background: transparent;")
        self.stability_label.setWordWrap(True)
        stability_card.content_layout.addWidget(self.stability_label, alignment=Qt.AlignmentFlag.AlignCenter)
        results_grid.addWidget(stability_card)

        results_layout.addLayout(results_grid)

        # Additional metrics card with scrolling
        self.metrics_card = InfoCard("Detailed Metrics", min_height=140)
        self.metrics_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        # Scrollable metrics text
        metrics_scroll = QScrollArea()
        metrics_scroll.setWidgetResizable(True)
        metrics_scroll.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background: transparent; 
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
            }
        """)
        metrics_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        metrics_scroll.setMaximumHeight(200)
        
        metrics_content = QWidget()
        metrics_content.setStyleSheet("background: transparent;")
        metrics_layout = QVBoxLayout(metrics_content)
        metrics_layout.setContentsMargins(0, 0, 8, 0)
        
        self.metrics_text = QLabel()
        self.metrics_text.setStyleSheet(f"color: {AriaColors.WHITE_85}; font-size: {AriaTypography.BODY_SMALL}px; background: transparent; line-height: 1.6;")
        self.metrics_text.setWordWrap(True)
        self.metrics_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.metrics_text.setTextFormat(Qt.TextFormat.RichText)
        metrics_layout.addWidget(self.metrics_text)
        metrics_layout.addStretch()
        
        metrics_scroll.setWidget(metrics_content)
        self.metrics_card.content_layout.addWidget(metrics_scroll)
        results_layout.addWidget(self.metrics_card)

        # Export button
        export_btn_layout = QHBoxLayout()
        export_btn_layout.addStretch()
        self.export_btn = SecondaryButton("Export Results")
        self.export_btn.clicked.connect(self.export_results)
        export_btn_layout.addWidget(self.export_btn)
        export_btn_layout.addStretch()
        results_layout.addLayout(export_btn_layout)

        self.results_frame.setVisible(False)
        layout.addWidget(self.results_frame)

        layout.addStretch()

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(content)

    def select_file(self):
        """Open file dialog to select audio file"""
        formats_filter = "Audio Files (" + " ".join([f"*{fmt}" for fmt in self.analyzer.supported_formats]) + ")"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            f"{formats_filter};;All Files (*)"
        )

        if file_path:
            import os
            self.file_path_label.setText(f"Selected: {os.path.basename(file_path)}")
            self.analyze_file(file_path)

    def analyze_file(self, file_path):
        """Analyze selected audio file using REAL backend"""
        try:
            # Hide results from previous analysis
            self.results_frame.setVisible(False)

            # Show progress
            self.progress_card.setVisible(True)
            self.progress_label.setText("Initializing analysis...")

            # Create worker thread
            self.worker_thread = AudioAnalysisWorker(file_path, self.analyzer)
            self.worker_thread.analysis_progress.connect(self.update_progress)
            self.worker_thread.analysis_complete.connect(self.display_results)
            self.worker_thread.analysis_error.connect(self.handle_error)
            self.worker_thread.finished.connect(self.on_analysis_finished)

            # Start analysis
            self.worker_thread.start()

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AudioAnalysisScreen.analyze_file")
            QMessageBox.critical(self, "Analysis Error", f"Failed to start analysis: {str(e)}")

    def update_progress(self, message):
        """Update progress label"""
        self.progress_label.setText(message)

    def display_results(self, results):
        """Display analysis results"""
        try:
            self.current_results = results

            # Extract pitch data
            pitch_data = results.get('pitch_analysis', {})

            # Display average pitch
            mean_pitch = pitch_data.get('mean_pitch', 0)
            self.avg_pitch_label.setText(f"{mean_pitch:.1f} Hz")

            # Display pitch range
            min_pitch = pitch_data.get('min_pitch', 0)
            max_pitch = pitch_data.get('max_pitch', 0)
            self.range_label.setText(f"{min_pitch:.0f} to {max_pitch:.0f} Hz")

            # Display stability (convert 0-1 to percentage)
            stability = pitch_data.get('pitch_stability', 0)
            self.stability_label.setText(f"{stability * 100:.0f}%")

            # Display detailed metrics
            voiced_pct = pitch_data.get('voiced_percentage', 0)
            std_pitch = pitch_data.get('std_pitch', 0)
            pitch_range = pitch_data.get('pitch_range', 0)

            metrics_html = f"""
            <p><b>Voiced Percentage:</b> {voiced_pct:.1f}%</p>
            <p><b>Pitch Variability:</b> ±{std_pitch:.1f} Hz</p>
            <p><b>Total Range:</b> {pitch_range:.1f} Hz</p>
            <p><b>Analysis Method:</b> {pitch_data.get('analysis_method', 'Unknown')}</p>
            """

            # Add spectral data if available
            spectral_data = results.get('spectral_analysis', {})
            if spectral_data:
                centroid = spectral_data.get('spectral_centroid_mean', 0)
                metrics_html += f"<p><b>Spectral Centroid:</b> {centroid:.0f} Hz</p>"

            self.metrics_text.setText(metrics_html)

            # Show results
            self.results_frame.setVisible(True)

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AudioAnalysisScreen.display_results")
            QMessageBox.warning(self, "Display Error", f"Failed to display results: {str(e)}")

    def handle_error(self, error_msg):
        """Handle analysis error"""
        QMessageBox.critical(self, "Analysis Failed", error_msg)
        from utils.error_handler import log_error
        log_error(RuntimeError(error_msg), "AudioAnalysisScreen.handle_error")

    def on_analysis_finished(self):
        """Called when analysis thread finishes"""
        self.progress_card.setVisible(False)

    def export_results(self):
        """Export results to JSON file"""
        if not self.current_results:
            QMessageBox.warning(self, "No Results", "No analysis results to export")
            return

        try:
            import json
            from datetime import datetime

            # Get save location
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Analysis Results",
                f"voice_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json);;All Files (*)"
            )

            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(self.current_results, f, indent=2)

                QMessageBox.information(self, "Export Successful", f"Results exported to:\n{file_path}")

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AudioAnalysisScreen.export_results")
            QMessageBox.critical(self, "Export Failed", f"Failed to export results: {str(e)}")

    def cleanup(self):
        """Cleanup resources"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
