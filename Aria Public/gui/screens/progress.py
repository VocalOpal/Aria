"""Progress screen displaying training statistics and achievements."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy, QScrollArea,
    QFileDialog, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QTimer

from ..design_system import (
    AriaColors, AriaTypography, AriaSpacing, AriaRadius,
    InfoCard, CircularProgress, create_gradient_background,
    TitleLabel, HeadingLabel, BodyLabel, CaptionLabel,
    StatCard, create_scroll_container, AchievementWidget,
    SecondaryButton
)

from ..components.pitch_heatmap import PitchHeatMapWidget
from ..utils.toast_notifications import ToastNotification
from core.export_manager import ExportManager


class ProgressScreen(QWidget):
    """Progress and statistics screen with REAL backend data"""

    def __init__(self, voice_trainer):
        super().__init__()
        self.voice_trainer = voice_trainer
        self.session_manager = voice_trainer.session_manager
        self.achievement_system = voice_trainer.achievement_system
        self.export_manager = ExportManager()

        # Refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_progress_data)

        self.init_ui()
        self.load_progress_data()

        # Auto-refresh every 30 seconds
        self.refresh_timer.start(30000)

    def init_ui(self):
        """Initialize progress UI"""
        # Gradient background
        content = QFrame()
        content.setStyleSheet(create_gradient_background())

        layout = QVBoxLayout(content)
        layout.setContentsMargins(AriaSpacing.GIANT, AriaSpacing.GIANT, AriaSpacing.GIANT, AriaSpacing.GIANT)
        layout.setSpacing(AriaSpacing.XL)

        # Title and Export buttons row
        title_row = QHBoxLayout()
        title_row.addWidget(TitleLabel("📈 Your Progress"))
        title_row.addStretch()

        json_export_btn = SecondaryButton("🎤 Discord")
        json_export_btn.setMaximumWidth(120)
        json_export_btn.setToolTip("Export for Discord Bot")
        json_export_btn.clicked.connect(self.export_to_json)
        title_row.addWidget(json_export_btn)

        csv_export_btn = SecondaryButton("📊 CSV")
        csv_export_btn.setMaximumWidth(100)
        csv_export_btn.setToolTip("Export to CSV")
        csv_export_btn.clicked.connect(self.export_to_csv_quick)
        title_row.addWidget(csv_export_btn)

        export_btn = SecondaryButton("📥 Options")
        export_btn.setMaximumWidth(120)
        export_btn.setToolTip("More Export Options")
        export_btn.clicked.connect(self.open_export_dialog)
        title_row.addWidget(export_btn)
        
        layout.addLayout(title_row)

        # Scroll area for content
        scroll = create_scroll_container()

        scroll_content = QWidget()
        scroll_content.setStyleSheet("QWidget { background: transparent; }")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(AriaSpacing.LG)

        # Stats grid (top row)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(AriaSpacing.LG)

        # Total Sessions
        self.sessions_card = StatCard("🎤 Total Sessions", "0", "Completed", min_height=220)
        self.sessions_label = self.sessions_card.value_label  # Keep reference for updates
        stats_layout.addWidget(self.sessions_card)

        # Total Time
        self.time_card = StatCard("Training Time", "0h 0m", "Total Practice", min_height=200, value_size=42)
        self.time_label = self.time_card.value_label  # Keep reference for updates
        stats_layout.addWidget(self.time_card)

        # Overall Progress
        self.progress_card = InfoCard("🎯 Overall Progress", min_height=220)
        self.progress_card.content_layout.addStretch()
        self.progress_widget = CircularProgress(percentage=0, size=110)
        self.progress_card.content_layout.addWidget(self.progress_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        self.progress_desc = QLabel("Goal Achievement")
        self.progress_desc.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.BODY_SMALL}px; background: transparent; margin-top: {AriaSpacing.SM}px;")
        self.progress_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_card.content_layout.addWidget(self.progress_desc)
        self.progress_card.content_layout.addStretch()
        stats_layout.addWidget(self.progress_card)

        scroll_layout.addLayout(stats_layout)

        # Recent Sessions Card
        self.recent_card = InfoCard("Recent Sessions", min_height=250)
        self.recent_sessions_text = CaptionLabel("No session data available.\nComplete training sessions to see progress.")
        self.recent_sessions_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.recent_sessions_text.setStyleSheet(f"""
            color: {AriaColors.WHITE_70};
            font-size: {AriaTypography.BODY}px;
            background: transparent;
            font-style: italic;
            padding: {AriaSpacing.LG}px;
        """)
        self.recent_card.content_layout.addWidget(self.recent_sessions_text)

        scroll_layout.addWidget(self.recent_card)

        # Performance Metrics Card
        self.metrics_card = InfoCard("Performance Metrics", min_height=200)

        metrics_grid = QHBoxLayout()
        metrics_grid.setSpacing(AriaSpacing.XXXL)

        # Average Pitch
        avg_pitch_layout = QVBoxLayout()
        avg_pitch_layout.setSpacing(AriaSpacing.SM)
        avg_pitch_label = QLabel("Avg Pitch")
        avg_pitch_label.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.BODY_SMALL}px; background: transparent;")
        avg_pitch_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avg_pitch_value = QLabel("-- Hz")
        self.avg_pitch_value.setStyleSheet(f"color: white; font-size: 32px; font-weight: bold; background: transparent; margin: {AriaSpacing.XS}px 0;")
        self.avg_pitch_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avg_pitch_layout.addStretch()
        avg_pitch_layout.addWidget(avg_pitch_label)
        avg_pitch_layout.addWidget(self.avg_pitch_value)
        avg_pitch_layout.addStretch()
        metrics_grid.addLayout(avg_pitch_layout)

        # Avg Accuracy
        accuracy_layout = QVBoxLayout()
        accuracy_layout.setSpacing(AriaSpacing.SM)
        accuracy_label = QLabel("Avg Accuracy")
        accuracy_label.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.BODY_SMALL}px; background: transparent;")
        accuracy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.accuracy_value = QLabel("--%")
        self.accuracy_value.setStyleSheet(f"color: white; font-size: 32px; font-weight: bold; background: transparent; margin: {AriaSpacing.XS}px 0;")
        self.accuracy_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        accuracy_layout.addStretch()
        accuracy_layout.addWidget(accuracy_label)
        accuracy_layout.addWidget(self.accuracy_value)
        accuracy_layout.addStretch()
        metrics_grid.addLayout(accuracy_layout)

        # Goal Achievement
        goal_layout = QVBoxLayout()
        goal_layout.setSpacing(AriaSpacing.SM)
        goal_label = QLabel("Goal Achievement")
        goal_label.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.BODY_SMALL}px; background: transparent;")
        goal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.goal_value = QLabel("--%")
        self.goal_value.setStyleSheet(f"color: white; font-size: 32px; font-weight: bold; background: transparent; margin: {AriaSpacing.XS}px 0;")
        self.goal_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        goal_layout.addStretch()
        goal_layout.addWidget(goal_label)
        goal_layout.addWidget(self.goal_value)
        goal_layout.addStretch()
        metrics_grid.addLayout(goal_layout)

        self.metrics_card.content_layout.addLayout(metrics_grid)

        scroll_layout.addWidget(self.metrics_card)

        # Weekly Summary Card
        self.weekly_card = InfoCard("This Week's Summary", min_height=240)
        self.weekly_card.content_layout.addStretch()
        self.weekly_text = QLabel("No sessions this week")
        self.weekly_text.setStyleSheet(f"color: {AriaColors.WHITE_85}; font-size: {AriaTypography.BODY}px; background: transparent; padding: {AriaSpacing.MD}px;")
        self.weekly_text.setWordWrap(True)
        self.weekly_card.content_layout.addWidget(self.weekly_text)
        self.weekly_card.content_layout.addStretch()

        scroll_layout.addWidget(self.weekly_card)

        # Streaks Card
        self.streaks_card = InfoCard("Training Streaks", min_height=200)
        streaks_grid = QHBoxLayout()
        streaks_grid.setSpacing(AriaSpacing.XXXL)

        # Current Streak
        current_streak_layout = QVBoxLayout()
        current_streak_layout.setSpacing(AriaSpacing.SM)
        current_streak_label = QLabel("Current Streak")
        current_streak_label.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.BODY_SMALL}px; background: transparent;")
        current_streak_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_streak_value = QLabel("0 days")
        self.current_streak_value.setStyleSheet(f"color: white; font-size: 32px; font-weight: bold; background: transparent; margin: {AriaSpacing.XS}px 0;")
        self.current_streak_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_streak_emoji = QLabel("🔥")
        self.current_streak_emoji.setStyleSheet("font-size: 40px; background: transparent;")
        self.current_streak_emoji.setAlignment(Qt.AlignmentFlag.AlignCenter)
        current_streak_layout.addStretch()
        current_streak_layout.addWidget(self.current_streak_emoji)
        current_streak_layout.addWidget(current_streak_label)
        current_streak_layout.addWidget(self.current_streak_value)
        current_streak_layout.addStretch()
        streaks_grid.addLayout(current_streak_layout)

        # Best Streak
        best_streak_layout = QVBoxLayout()
        best_streak_layout.setSpacing(AriaSpacing.SM)
        best_streak_label = QLabel("Best Streak")
        best_streak_label.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: {AriaTypography.BODY_SMALL}px; background: transparent;")
        best_streak_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.best_streak_value = QLabel("0 days")
        self.best_streak_value.setStyleSheet(f"color: white; font-size: 32px; font-weight: bold; background: transparent; margin: {AriaSpacing.XS}px 0;")
        self.best_streak_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.best_streak_emoji = QLabel("🏆")
        self.best_streak_emoji.setStyleSheet("font-size: 40px; background: transparent;")
        self.best_streak_emoji.setAlignment(Qt.AlignmentFlag.AlignCenter)
        best_streak_layout.addStretch()
        best_streak_layout.addWidget(self.best_streak_emoji)
        best_streak_layout.addWidget(best_streak_label)
        best_streak_layout.addWidget(self.best_streak_value)
        best_streak_layout.addStretch()
        streaks_grid.addLayout(best_streak_layout)

        self.streaks_card.content_layout.addLayout(streaks_grid)
        scroll_layout.addWidget(self.streaks_card)

        # Practice Patterns Card (Pitch Heatmap)
        self.patterns_card = InfoCard("Practice Patterns", min_height=500)
        self.heatmap_widget = PitchHeatMapWidget(self.session_manager)
        self.patterns_card.content_layout.addWidget(self.heatmap_widget)
        scroll_layout.addWidget(self.patterns_card)

        # Achievements Card
        self.achievements_card = InfoCard("Achievements", min_height=400)

        # Remove the stretch from the card's layout to allow content to expand
        while self.achievements_card.layout().count() > 0:
            item = self.achievements_card.layout().itemAt(self.achievements_card.layout().count() - 1)
            if item.spacerItem():
                self.achievements_card.layout().removeItem(item)
                break

        self.achievements_scroll = QScrollArea()
        self.achievements_scroll.setWidgetResizable(True)
        self.achievements_scroll.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.achievements_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.05);
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        self.achievements_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.achievements_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.achievements_content = QWidget()
        self.achievements_content.setStyleSheet("background: transparent;")
        self.achievements_content.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.achievements_layout = QVBoxLayout(self.achievements_content)
        self.achievements_layout.setSpacing(AriaSpacing.SM)
        self.achievements_layout.setContentsMargins(0, 0, 8, 0)

        self.achievements_text = QLabel("No achievements yet.\nComplete training sessions to earn achievements!")
        self.achievements_text.setStyleSheet(f"""
            color: {AriaColors.WHITE_70};
            font-size: {AriaTypography.BODY}px;
            background: transparent;
            font-style: italic;
            padding: {AriaSpacing.LG}px;
        """)
        self.achievements_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.achievements_text.setWordWrap(True)
        self.achievements_layout.addWidget(self.achievements_text)

        self.achievements_scroll.setWidget(self.achievements_content)
        self.achievements_card.content_layout.addWidget(self.achievements_scroll, stretch=1)
        scroll_layout.addWidget(self.achievements_card)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)

        layout.addWidget(scroll)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(content)

    def load_progress_data(self):
        """Load REAL progress data from session manager"""
        try:
            # Get session history from backend
            session_history = self.session_manager.get_session_history()

            if not session_history:
                # No data - show empty state
                self.sessions_label.setText("0")
                self.time_label.setText("0h 0m")
                self.progress_widget.set_percentage(0)
                self.recent_sessions_text.setText("No session data available.\nComplete training sessions to see progress.")
                self.avg_pitch_value.setText("-- Hz")
                self.accuracy_value.setText("--%")
                self.goal_value.setText("--%")
                self.weekly_text.setText("No sessions this week")
                self.current_streak_value.setText("0 days")
                self.best_streak_value.setText("0 days")
                return

            # Calculate total sessions
            total_sessions = len(session_history)
            self.sessions_label.setText(str(total_sessions))

            # Calculate total time
            total_minutes = sum(s.get('duration', 0) for s in session_history) / 60
            hours = int(total_minutes // 60)
            minutes = int(total_minutes % 60)
            self.time_label.setText(f"{hours}h {minutes}m")

            # Calculate overall progress (average of goal achievements)
            goal_achievements = [s.get('goal_achievement_percent', 0) for s in session_history if s.get('goal_achievement_percent', 0) > 0]
            if goal_achievements:
                avg_progress = sum(goal_achievements) / len(goal_achievements)
                self.progress_widget.set_percentage(avg_progress)
            else:
                self.progress_widget.set_percentage(0)

            # Display recent sessions
            recent_sessions = session_history[-5:]  # Last 5 sessions
            recent_text = "<table width='100%' cellspacing='6' style='margin-top: 4px;'>"
            recent_text += f"<tr style='color: rgba(255,255,255,0.65); font-size: {AriaTypography.BODY_SMALL}px; font-weight: 600;'>"
            recent_text += "<td style='padding: 6px 0;'>Date</td><td>Duration</td><td>Avg Pitch</td><td>Accuracy</td></tr>"

            for session in reversed(recent_sessions):  # Most recent first
                from datetime import datetime
                try:
                    date_str = datetime.fromisoformat(session['date'].replace('Z', '+00:00')).strftime('%m/%d %H:%M')
                except:
                    date_str = "Unknown"

                duration_min = int(session.get('duration', 0) / 60)
                avg_pitch = session.get('avg_pitch', 0)
                accuracy = session.get('time_in_range_percent', 0)

                recent_text += f"<tr style='color: rgba(255,255,255,0.95);'>"
                recent_text += f"<td style='padding: 8px 0;'>{date_str}</td>"
                recent_text += f"<td style='font-weight: 500;'>{duration_min}m</td>"
                recent_text += f"<td style='font-weight: 500;'>{avg_pitch:.0f} Hz</td>"
                recent_text += f"<td style='font-weight: 600;'>{accuracy:.0f}%</td>"
                recent_text += "</tr>"

            recent_text += "</table>"
            self.recent_sessions_text.setText(recent_text)
            self.recent_sessions_text.setStyleSheet(f"color: white; font-size: {AriaTypography.BODY_SMALL}px; background: transparent; padding: {AriaSpacing.SM}px;")

            # Calculate performance metrics
            avg_pitches = [s.get('avg_pitch', 0) for s in session_history if s.get('avg_pitch', 0) > 0]
            if avg_pitches:
                overall_avg_pitch = sum(avg_pitches) / len(avg_pitches)
                self.avg_pitch_value.setText(f"{overall_avg_pitch:.0f} Hz")
            else:
                self.avg_pitch_value.setText("-- Hz")

            accuracies = [s.get('time_in_range_percent', 0) for s in session_history]
            if accuracies:
                avg_accuracy = sum(accuracies) / len(accuracies)
                self.accuracy_value.setText(f"{avg_accuracy:.0f}%")
            else:
                self.accuracy_value.setText("--%")

            if goal_achievements:
                avg_goal = sum(goal_achievements) / len(goal_achievements)
                self.goal_value.setText(f"{avg_goal:.0f}%")
            else:
                self.goal_value.setText("--%")

            # Weekly summary
            from datetime import datetime, timedelta
            week_ago = datetime.now() - timedelta(days=7)

            weekly_sessions = [
                s for s in session_history
                if datetime.fromisoformat(s['date'].replace('Z', '+00:00')) >= week_ago
            ]

            if weekly_sessions:
                week_count = len(weekly_sessions)
                week_minutes = sum(s.get('duration', 0) for s in weekly_sessions) / 60
                week_hours = int(week_minutes // 60)
                week_mins = int(week_minutes % 60)

                week_avg_pitch = sum(s.get('avg_pitch', 0) for s in weekly_sessions) / week_count if week_count > 0 else 0

                weekly_summary = f"""
                <div style='line-height: 1.8;'>
                <p style='margin: {AriaSpacing.SM}px 0;'><span style='color: rgba(255,255,255,0.7); font-weight: 500;'>Sessions:</span> <span style='font-weight: 600; margin-left: 8px;'>{week_count}</span></p>
                <p style='margin: {AriaSpacing.SM}px 0;'><span style='color: rgba(255,255,255,0.7); font-weight: 500;'>Total Time:</span> <span style='font-weight: 600; margin-left: 8px;'>{week_hours}h {week_mins}m</span></p>
                <p style='margin: {AriaSpacing.SM}px 0;'><span style='color: rgba(255,255,255,0.7); font-weight: 500;'>Avg Pitch:</span> <span style='font-weight: 600; margin-left: 8px;'>{week_avg_pitch:.0f} Hz</span></p>
                </div>
                """
                self.weekly_text.setText(weekly_summary)
            else:
                self.weekly_text.setText("No sessions this week")

            # Calculate and display streaks
            streak_info = self.achievement_system.calculate_streaks(session_history)
            current_streak = streak_info.get('current_streak', 0)
            best_streak = streak_info.get('best_streak', 0)

            self.current_streak_value.setText(f"{current_streak} {'day' if current_streak == 1 else 'days'}")
            self.best_streak_value.setText(f"{best_streak} {'day' if best_streak == 1 else 'days'}")

            # Calculate and display achievements
            total_time = sum(s.get('duration', 0) for s in session_history) / 60  # in minutes
            pitch_data = self.achievement_system.calculate_pitch_achievements(session_history)
            all_achievements = self.achievement_system.get_all_achievements(
                total_sessions, total_time, streak_info, pitch_data, session_history
            )

            # Filter to show earned and nearly-earned achievements
            earned_achievements = [a for a in all_achievements if a['earned']]
            nearly_earned = [a for a in all_achievements if not a['earned'] and a['progress_percent'] >= 50]
            display_achievements = earned_achievements + nearly_earned[:3]  # Show earned + top 3 nearly-earned

            # Clear previous achievements
            while self.achievements_layout.count():
                item = self.achievements_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            if display_achievements:
                for achievement in display_achievements:
                    achievement_widget = AchievementWidget(achievement)
                    self.achievements_layout.addWidget(achievement_widget)
            else:
                self.achievements_text = QLabel("No achievements yet.\nComplete training sessions to earn achievements!")
                self.achievements_text.setStyleSheet(f"""
                    color: {AriaColors.WHITE_70};
                    font-size: {AriaTypography.BODY}px;
                    background: transparent;
                    font-style: italic;
                    padding: {AriaSpacing.LG}px;
                """)
                self.achievements_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.achievements_text.setWordWrap(True)
                self.achievements_layout.addWidget(self.achievements_text)

            # Refresh pitch heatmap
            if hasattr(self, 'heatmap_widget'):
                self.heatmap_widget.refresh()

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "ProgressScreen.load_progress_data")

            # Show error state
            self.recent_sessions_text.setText(f"Error loading progress data:\n{str(e)}")
            self.recent_sessions_text.setStyleSheet(f"color: {AriaColors.RED}; font-size: {AriaTypography.BODY_SMALL}px; background: transparent;")


    def showEvent(self, event):
        """Reload data when screen becomes visible"""
        super().showEvent(event)
        self.load_progress_data()

    def cleanup(self):
        """Cleanup resources"""
        if self.refresh_timer:
            self.refresh_timer.stop()
    
    def export_to_csv_quick(self):
        """Quick CSV export of all sessions with default filename"""
        from datetime import datetime
        
        session_history = self.session_manager.get_session_history()
        
        if not session_history:
            self.show_toast("No session data available to export", error=True)
            return
        
        default_filename = f"aria_sessions_{datetime.now().strftime('%Y%m%d')}.csv"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export All Sessions to CSV",
            default_filename,
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            success = self.export_manager.export_to_csv(session_history, file_path)
            
            if success:
                ToastNotification.show_toast(self, "CSV exported successfully!", icon="✓")
            else:
                ToastNotification.show_toast(self, "Failed to export CSV", error=True)
    
    def open_export_dialog(self):
        """Open dialog to choose export options"""
        session_history = self.session_manager.get_session_history()
        
        if not session_history:
            from gui.utils.toast_notifications import ToastNotification
            ToastNotification.show_toast(self, "No session data available to export", icon="❌", error=True)
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Export Session Data")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {AriaColors.GRADIENT_BLUE},
                    stop:1 {AriaColors.GRADIENT_PINK}
                );
            }}
            QLabel {{
                color: white;
                font-size: {AriaTypography.BODY}px;
            }}
            QPushButton {{
                background-color: {AriaColors.TEAL};
                color: white;
                border: none;
                border-radius: {AriaRadius.MD}px;
                font-size: {AriaTypography.BODY}px;
                font-weight: 600;
                padding: 10px 20px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {AriaColors.TEAL_HOVER};
            }}
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(AriaSpacing.LG)
        layout.setContentsMargins(AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL)
        
        title = QLabel("Choose Export Format:")
        title.setStyleSheet(f"font-size: {AriaTypography.HEADING}px; font-weight: bold;")
        layout.addWidget(title)
        
        info = QLabel(f"Total sessions available: {len(session_history)}")
        layout.addWidget(info)
        
        layout.addSpacing(AriaSpacing.MD)
        
        export_all_btn = SecondaryButton("Export All Sessions (CSV)")
        export_all_btn.clicked.connect(lambda: self.export_data(session_history, dialog))
        layout.addWidget(export_all_btn)
        
        recent_sessions = session_history[-10:] if len(session_history) > 10 else session_history
        export_recent_btn = SecondaryButton(f"Export Recent {len(recent_sessions)} Sessions (CSV)")
        export_recent_btn.clicked.connect(lambda: self.export_data(recent_sessions, dialog))
        layout.addWidget(export_recent_btn)
        
        layout.addStretch()
        
        close_btn = SecondaryButton("Cancel")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def export_data(self, sessions, dialog):
        """Export session data to CSV file"""
        from datetime import datetime
        
        default_filename = f"aria_sessions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Session Data",
            default_filename,
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            success = self.export_manager.export_to_csv(sessions, file_path)
            
            if success:
                ToastNotification.show_toast(self, "Data exported successfully!", icon="✓", duration=3000)
                dialog.close()
            else:
                ToastNotification.show_toast(self, "Failed to export data", error=True, duration=3000)
    
    def export_to_json(self):
        """Export complete data to JSON for Discord bot"""
        from datetime import datetime
        
        default_filename = f"aria_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data for Discord Bot",
            default_filename,
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            sessions = self.session_manager.weekly_sessions
            
            result = self.export_manager.export_to_json(
                sessions=sessions,
                achievement_manager=self.achievement_system,
                session_manager=self.session_manager,
                output_path=file_path
            )
            
            if result:
                ToastNotification.show_toast(
                    self, 
                    "✅ Data exported! Upload this file to Aria Discord Bot", 
                    icon="🎤", 
                    duration=5000
                )
            else:
                ToastNotification.show_toast(
                    self, 
                    "Failed to export JSON data", 
                    error=True, 
                    duration=3000
                )
