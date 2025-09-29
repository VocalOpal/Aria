from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,  # type: ignore
                            QLabel, QGroupBox, QGridLayout, QFrame, QScrollArea,
                            QProgressBar, QTableWidget, QTableWidgetItem, QTabWidget,
                            QMessageBox, QHeaderView, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal  # type: ignore
from PyQt6.QtGui import QFont, QPalette, QColor  # type: ignore
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime, timedelta
import numpy as np
from core.achievement_system import VoiceAchievementSystem
from ..design_system import AriaDesignSystem


class ProgressVisualizationWidget(QWidget):
    """Custom widget for progress visualization charts"""

    def __init__(self):
        super().__init__()
        self.figure = Figure(figsize=(10, 6), facecolor=AriaDesignSystem.COLORS['bg_primary'])
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet(f"background-color: {AriaDesignSystem.COLORS['bg_primary']};")

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot_progress_trends(self, sessions_data):
        """Plot pitch progress trends over time"""
        self.figure.clear()

        if not sessions_data:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No session data available\nComplete training sessions to see progress',
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=14, color=AriaDesignSystem.COLORS['text_muted'], style='italic')
            ax.set_facecolor(AriaDesignSystem.COLORS['bg_primary'])
            ax.tick_params(colors=AriaDesignSystem.COLORS['text_primary'])
            self.canvas.draw()
            return

        # Extract data
        dates = [datetime.fromisoformat(s['date'].replace('Z', '+00:00')) for s in sessions_data]
        avg_pitches = [s['avg_pitch'] for s in sessions_data]
        goals = [s.get('goal', 165) for s in sessions_data]

        # Main progress plot
        ax1 = self.figure.add_subplot(211)
        ax1.set_facecolor(AriaDesignSystem.COLORS['bg_primary'])

        # Plot average pitches
        ax1.plot(dates, avg_pitches, 'o-', color=AriaDesignSystem.COLORS['success'], linewidth=2, markersize=6, label='Average Pitch')

        # Plot goals if they vary
        if len(set(goals)) > 1:
            ax1.plot(dates, goals, '--', color=AriaDesignSystem.COLORS['warning'], linewidth=2, alpha=0.7, label='Goal')
        else:
            ax1.axhline(y=goals[0], color=AriaDesignSystem.COLORS['warning'], linestyle='--', alpha=0.7, label=f'Goal ({goals[0]} Hz)')

        ax1.set_ylabel('Pitch (Hz)', color=AriaDesignSystem.COLORS['text_primary'], fontsize=12)
        ax1.set_title('Voice Training Progress Over Time', color=AriaDesignSystem.COLORS['text_primary'], fontsize=14, fontweight='bold')
        ax1.legend(facecolor=AriaDesignSystem.COLORS['bg_secondary'], edgecolor=AriaDesignSystem.COLORS['border_subtle'], labelcolor=AriaDesignSystem.COLORS['text_primary'])
        ax1.tick_params(colors=AriaDesignSystem.COLORS['text_primary'])
        ax1.grid(True, alpha=0.3, color=AriaDesignSystem.COLORS['text_muted'])

        # Format dates on x-axis
        if len(dates) > 10:
            ax1.tick_params(axis='x', rotation=45)

        # Performance metrics plot
        ax2 = self.figure.add_subplot(212)
        ax2.set_facecolor(AriaDesignSystem.COLORS['bg_primary'])

        time_in_range = [s.get('time_in_range_percent', 0) for s in sessions_data]
        goal_achievement = [s.get('goal_achievement_percent', 0) for s in sessions_data]

        width = 0.35
        x = np.arange(len(dates))

        if len(dates) <= 20:  # Only show bars if not too many sessions
            ax2.bar(x - width/2, time_in_range, width, label='Time in Range %', color=AriaDesignSystem.COLORS['info'], alpha=0.8)
            ax2.bar(x + width/2, goal_achievement, width, label='Goal Achievement %', color=AriaDesignSystem.COLORS['warning'], alpha=0.8)
            ax2.set_xticks(x)
            ax2.set_xticklabels([d.strftime('%m/%d') for d in dates], rotation=45)
        else:
            # Line plot for many sessions
            ax2.plot(dates, time_in_range, 'o-', color=AriaDesignSystem.COLORS['info'], label='Time in Range %', alpha=0.8)
            ax2.plot(dates, goal_achievement, 'o-', color=AriaDesignSystem.COLORS['warning'], label='Goal Achievement %', alpha=0.8)

        ax2.set_ylabel('Percentage (%)', color=AriaDesignSystem.COLORS['text_primary'], fontsize=12)
        ax2.set_xlabel('Session Date', color=AriaDesignSystem.COLORS['text_primary'], fontsize=12)
        ax2.set_title('Training Performance Metrics', color=AriaDesignSystem.COLORS['text_primary'], fontsize=14, fontweight='bold')
        ax2.legend(facecolor=AriaDesignSystem.COLORS['bg_secondary'], edgecolor=AriaDesignSystem.COLORS['border_subtle'], labelcolor=AriaDesignSystem.COLORS['text_primary'])
        ax2.tick_params(colors=AriaDesignSystem.COLORS['text_primary'])
        ax2.grid(True, alpha=0.3, color=AriaDesignSystem.COLORS['text_muted'])
        ax2.set_ylim(0, 100)

        self.figure.tight_layout()
        self.canvas.draw()


class ProgressScreen(QWidget):
    """Progress tracking and statistics dashboard"""

    back_requested = pyqtSignal()

    def __init__(self, voice_trainer):
        super().__init__()
        self.voice_trainer = voice_trainer
        self.session_manager = voice_trainer.session_manager
        self.achievement_system = VoiceAchievementSystem()
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)

        self.init_ui()
        self.load_progress_data()

        # Refresh every 30 seconds when active
        self.refresh_timer.start(30000)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Header card
        header_frame = QFrame()
        header_frame.setProperty("style", "card")
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AriaDesignSystem.COLORS['bg_secondary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: {AriaDesignSystem.RADIUS['lg']};
                padding: 24px;
            }}
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setSpacing(16)

        back_button = QPushButton("← Back to Menu")
        back_button.clicked.connect(self.back_requested.emit)
        back_button.setProperty("style", "secondary")
        back_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_normal']};
                border-radius: {AriaDesignSystem.RADIUS['md']};
                padding: {AriaDesignSystem.SPACING['sm']} {AriaDesignSystem.SPACING['md']};
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-weight: 500;
                min-height: 36px;
                min-width: 140px;
            }}
            QPushButton:hover {{
                background-color: {AriaDesignSystem.COLORS['bg_accent']};
                border-color: {AriaDesignSystem.COLORS['border_strong']};
            }}
            QPushButton:pressed {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
            }}
        """)
        header_layout.addWidget(back_button)

        # Title section
        title_container = QVBoxLayout()
        title = QLabel("Progress & Statistics")
        title.setFont(QFont(AriaDesignSystem.FONTS['family_primary'], AriaDesignSystem.FONTS['xxl'], QFont.Weight.Bold))
        title.setProperty("style", "heading")
        title.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['xxl']}pt;
                font-weight: 600;
                background: transparent;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_container.addWidget(title)

        subtitle = QLabel("Track your voice training journey and achievements")
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_secondary']};
                font-size: {AriaDesignSystem.FONTS['md']}pt;
                background: transparent;
                margin-top: 4px;
            }}
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_container.addWidget(subtitle)

        header_layout.addLayout(title_container)
        header_layout.addStretch()

        layout.addWidget(header_frame)

        # Create tabs for different views
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                background-color: {AriaDesignSystem.COLORS['bg_primary']};
                border-radius: {AriaDesignSystem.RADIUS['lg']};
                padding: 16px;
            }}
            QTabBar::tab {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
                color: {AriaDesignSystem.COLORS['text_secondary']};
                padding: 12px 20px;
                margin-right: 2px;
                margin-bottom: 2px;
                border-top-left-radius: {AriaDesignSystem.RADIUS['md']};
                border-top-right-radius: {AriaDesignSystem.RADIUS['md']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-weight: 500;
                min-width: 100px;
            }}
            QTabBar::tab:selected {{
                background-color: {AriaDesignSystem.COLORS['primary']};
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-weight: 600;
            }}
            QTabBar::tab:hover {{
                background-color: {AriaDesignSystem.COLORS['bg_accent']};
                color: {AriaDesignSystem.COLORS['text_primary']};
            }}
            QTabBar::tab:!selected {{
                margin-top: 2px;
            }}
        """)

        # Overview tab
        overview_tab = self.create_overview_tab()
        tab_widget.addTab(overview_tab, "Overview")

        # Charts tab
        charts_tab = self.create_charts_tab()
        tab_widget.addTab(charts_tab, "Progress Charts")

        # Session history tab
        history_tab = self.create_history_tab()
        tab_widget.addTab(history_tab, "Session History")

        # Achievements tab
        achievements_tab = self.create_achievements_tab()
        tab_widget.addTab(achievements_tab, "Achievements")

        layout.addWidget(tab_widget)

        # Apply overall styling
        self.setStyleSheet(f"""
            ProgressScreen {{
                background-color: {AriaDesignSystem.COLORS['bg_primary']};
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-family: {AriaDesignSystem.FONTS['family_primary']};
            }}
            QGroupBox {{
                font-size: {AriaDesignSystem.FONTS['md']}pt;
                font-weight: 600;
                color: {AriaDesignSystem.COLORS['text_primary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: {AriaDesignSystem.RADIUS['md']};
                margin: 8px 0px;
                padding-top: 12px;
                background-color: {AriaDesignSystem.COLORS['bg_secondary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                background-color: {AriaDesignSystem.COLORS['bg_secondary']};
            }}
        """)

        self.setLayout(layout)

    def create_overview_tab(self):
        """Create overview statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Current session status
        current_group = QGroupBox("Current Session")
        current_layout = QVBoxLayout()

        self.current_session_label = QLabel("No active session")
        self.current_session_label.setStyleSheet(f"""
            QLabel {{
                font-size: {AriaDesignSystem.FONTS['md']}pt;
                color: {AriaDesignSystem.COLORS['text_muted']};
                font-style: italic;
                background: transparent;
            }}
        """)
        current_layout.addWidget(self.current_session_label)

        current_group.setLayout(current_layout)
        layout.addWidget(current_group)

        # Statistics grid
        stats_group = QGroupBox("Training Statistics")
        stats_layout = QGridLayout()

        # Create stat display pairs
        self.total_sessions_label = QLabel("0")
        self.total_training_time_label = QLabel("0 hours")
        self.avg_pitch_label = QLabel("No data")
        self.improvement_label = QLabel("No data")
        self.consistency_label = QLabel("No data")
        self.recent_goal_label = QLabel("No data")

        # Style stat labels
        for label in [self.total_sessions_label, self.total_training_time_label,
                     self.avg_pitch_label, self.improvement_label,
                     self.consistency_label, self.recent_goal_label]:
            label.setStyleSheet(f"""
                QLabel {{
                    font-weight: 600;
                    font-size: {AriaDesignSystem.FONTS['lg']}pt;
                    color: {AriaDesignSystem.COLORS['success']};
                    background: transparent;
                }}
            """)

        stats_layout.addWidget(QLabel("Total Sessions:"), 0, 0)
        stats_layout.addWidget(self.total_sessions_label, 0, 1)

        stats_layout.addWidget(QLabel("Total Training Time:"), 1, 0)
        stats_layout.addWidget(self.total_training_time_label, 1, 1)

        stats_layout.addWidget(QLabel("Recent Average Pitch:"), 2, 0)
        stats_layout.addWidget(self.avg_pitch_label, 2, 1)

        stats_layout.addWidget(QLabel("Progress Trend:"), 0, 2)
        stats_layout.addWidget(self.improvement_label, 0, 3)

        stats_layout.addWidget(QLabel("Goal Consistency:"), 1, 2)
        stats_layout.addWidget(self.consistency_label, 1, 3)

        stats_layout.addWidget(QLabel("Current Goal:"), 2, 2)
        stats_layout.addWidget(self.recent_goal_label, 2, 3)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Recent achievements
        achievements_group = QGroupBox("Recent Achievements")
        achievements_layout = QVBoxLayout()

        self.achievements_label = QLabel("Complete training sessions to unlock achievements!")
        self.achievements_label.setWordWrap(True)
        self.achievements_label.setStyleSheet(f"""
            QLabel {{
                color: {AriaDesignSystem.COLORS['text_muted']};
                font-style: italic;
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                background: transparent;
            }}
        """)
        achievements_layout.addWidget(self.achievements_label)

        achievements_group.setLayout(achievements_layout)
        layout.addWidget(achievements_group)

        # Actions
        actions_group = QGroupBox("Data Management")
        actions_layout = QHBoxLayout()

        refresh_button = QPushButton("Refresh Data")
        refresh_button.clicked.connect(self.refresh_data)
        refresh_button.setProperty("style", "info")
        refresh_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaDesignSystem.COLORS['info']};
                border: none;
                border-radius: {AriaDesignSystem.RADIUS['md']};
                padding: 8px 16px;
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-weight: 500;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: #2563eb;
            }}
            QPushButton:pressed {{
                background-color: #1d4ed8;
            }}
        """)

        export_button = QPushButton("Export Data")
        export_button.clicked.connect(self.export_data)
        export_button.setProperty("style", "warning")
        export_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaDesignSystem.COLORS['warning']};
                border: none;
                border-radius: {AriaDesignSystem.RADIUS['md']};
                padding: 8px 16px;
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-weight: 500;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: #d97706;
            }}
            QPushButton:pressed {{
                background-color: #b45309;
            }}
        """)

        clear_button = QPushButton("Clear All Data")
        clear_button.clicked.connect(self.clear_data)
        clear_button.setProperty("style", "danger")
        clear_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaDesignSystem.COLORS['error']};
                border: none;
                border-radius: {AriaDesignSystem.RADIUS['md']};
                padding: 8px 16px;
                color: {AriaDesignSystem.COLORS['text_primary']};
                font-size: {AriaDesignSystem.FONTS['sm']}pt;
                font-weight: 500;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: #dc2626;
            }}
            QPushButton:pressed {{
                background-color: #b91c1c;
            }}
        """)

        actions_layout.addWidget(refresh_button)
        actions_layout.addWidget(export_button)
        actions_layout.addWidget(clear_button)
        actions_layout.addStretch()

        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_charts_tab(self):
        """Create progress visualization tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Chart controls
        controls_layout = QHBoxLayout()

        time_filter_label = QLabel("Show last:")
        time_filter_combo = QPushButton("30 sessions")  # Simplified for now

        controls_layout.addWidget(time_filter_label)
        controls_layout.addWidget(time_filter_combo)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # Progress visualization
        self.progress_chart = ProgressVisualizationWidget()
        layout.addWidget(self.progress_chart)

        widget.setLayout(layout)
        return widget

    def create_history_tab(self):
        """Create session history tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Session history table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "Date", "Duration", "Avg Pitch", "Goal", "Time in Range", "Alerts", "Type"
        ])

        # Style the table
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                color: white;
                gridline-color: #666;
                selection-background-color: #4CAF50;
            }
            QHeaderView::section {
                background-color: #404040;
                color: white;
                padding: 8px;
                border: 1px solid #666;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #444;
            }
        """)

        # Auto-resize columns
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.history_table)

        widget.setLayout(layout)
        return widget

    def create_achievements_tab(self):
        """Create achievements display tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Achievements overview
        overview_group = QGroupBox("Achievement Summary")
        overview_layout = QGridLayout()

        self.total_earned_label = QLabel("0")
        self.total_earned_label.setStyleSheet(f"font-weight: bold; font-size: 24px; color: {AriaDesignSystem.COLORS['success']};")
        overview_layout.addWidget(QLabel("Achievements Earned:"), 0, 0)
        overview_layout.addWidget(self.total_earned_label, 0, 1)

        self.total_possible_label = QLabel("0")
        self.total_possible_label.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {AriaDesignSystem.COLORS['text_muted']};")
        overview_layout.addWidget(QLabel("Total Available:"), 1, 0)
        overview_layout.addWidget(self.total_possible_label, 1, 1)

        self.completion_progress = QProgressBar()
        self.completion_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                background-color: #333;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 6px;
            }
        """)
        overview_layout.addWidget(QLabel("Completion:"), 2, 0)
        overview_layout.addWidget(self.completion_progress, 2, 1)

        overview_group.setLayout(overview_layout)
        layout.addWidget(overview_group)

        # Filter buttons
        filter_group = QGroupBox("Filter by Category")
        filter_layout = QHBoxLayout()

        self.filter_all_btn = QPushButton("All")
        self.filter_earned_btn = QPushButton("Earned")
        self.filter_unearned_btn = QPushButton("Not Earned")
        self.filter_rarity_btn = QPushButton("By Rarity")

        for btn in [self.filter_all_btn, self.filter_earned_btn, self.filter_unearned_btn, self.filter_rarity_btn]:
            btn.setStyleSheet("padding: 6px 12px; margin: 2px;")
            btn.clicked.connect(self.update_achievements_display)
            filter_layout.addWidget(btn)

        filter_layout.addStretch()
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Achievements list
        self.achievements_list = QListWidget()
        self.achievements_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {AriaDesignSystem.COLORS['bg_secondary']};
                color: {AriaDesignSystem.COLORS['text_primary']};
                border: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                border-radius: 8px;
                font-family: {AriaDesignSystem.FONTS['family_primary']};
            }}
            QListWidget::item {{
                padding: 16px;
                border-bottom: 1px solid {AriaDesignSystem.COLORS['border_subtle']};
                margin: 0px;
                border-radius: 4px;
            }}
            QListWidget::item:hover {{
                background-color: {AriaDesignSystem.COLORS['bg_tertiary']};
            }}
            QListWidget::item:selected {{
                background-color: {AriaDesignSystem.COLORS['primary']};
                color: white;
            }}
        """)
        layout.addWidget(self.achievements_list)

        widget.setLayout(layout)
        return widget

    def load_progress_data(self):
        """Load and display progress data"""
        try:
            # Get session history
            sessions = self.session_manager.get_session_history(limit=50)

            # Update overview statistics
            self.update_overview_stats(sessions)

            # Update charts
            self.progress_chart.plot_progress_trends(sessions)

            # Update history table
            self.update_history_table(sessions)

            # Check current session
            self.update_current_session_status()

        except Exception as e:
            self.show_error(f"Error loading progress data: {str(e)}")

    def update_overview_stats(self, sessions):
        """Update overview statistics display"""
        if not sessions:
            return

        # Basic counts
        total_sessions = len(sessions)
        self.total_sessions_label.setText(str(total_sessions))

        # Total training time
        total_minutes = sum(s.get('duration_minutes', 0) for s in sessions)
        total_hours = total_minutes / 60
        self.total_training_time_label.setText(f"{total_hours:.1f} hours")

        # Recent average pitch
        recent_sessions = sessions[-7:] if len(sessions) >= 7 else sessions
        if recent_sessions:
            recent_avg = sum(s['avg_pitch'] for s in recent_sessions) / len(recent_sessions)
            self.avg_pitch_label.setText(f"{recent_avg:.1f} Hz")

            # Current goal
            latest_goal = recent_sessions[-1].get('goal', 165)
            self.recent_goal_label.setText(f"{latest_goal} Hz")
        else:
            self.avg_pitch_label.setText("No data")
            self.recent_goal_label.setText("No data")

        # Progress trends
        trends = self.session_manager.get_progress_trends()
        trend_text = trends.get('trend', 'unknown')

        if trend_text == 'improving':
            improvement_hz = trends.get('improvement_hz', 0)
            self.improvement_label.setText(f"Improving (+{improvement_hz:.1f} Hz)")
            self.improvement_label.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {AriaDesignSystem.COLORS['success']};")
        elif trend_text == 'stable':
            self.improvement_label.setText("Stable")
            self.improvement_label.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {AriaDesignSystem.COLORS['warning']};")
        elif trend_text == 'declining':
            improvement_hz = trends.get('improvement_hz', 0)
            self.improvement_label.setText(f"Declining ({improvement_hz:.1f} Hz)")
            self.improvement_label.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {AriaDesignSystem.COLORS['error']};")
        else:
            self.improvement_label.setText("New user")
            self.improvement_label.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {AriaDesignSystem.COLORS['info']};")

        # Consistency
        consistency = trends.get('consistency_percent', 0)
        self.consistency_label.setText(f"{consistency:.0f}%")

        if consistency >= 70:
            self.consistency_label.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {AriaDesignSystem.COLORS['success']};")
        elif consistency >= 50:
            self.consistency_label.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {AriaDesignSystem.COLORS['warning']};")
        else:
            self.consistency_label.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {AriaDesignSystem.COLORS['error']};")

        # Update achievements using the real achievement system
        self.update_achievements_data(sessions)

    def update_achievements_data(self, sessions):
        """Update achievements using the real achievement system"""
        if not sessions:
            return

        # Calculate achievement data
        total_sessions = len(sessions)
        total_time = sum(s.get('duration_minutes', 0) for s in sessions)
        streak_info = self.achievement_system.calculate_streaks(sessions)
        pitch_data = self.achievement_system.calculate_pitch_achievements(sessions)

        # Get all achievements
        all_achievements = self.achievement_system.get_all_achievements(
            total_sessions, total_time, streak_info, pitch_data, sessions)

        # Store for the achievements tab
        self.current_achievements = all_achievements

        # Update achievements tab if it exists
        if hasattr(self, 'achievements_list'):
            self.update_achievements_display()

        # Update simple overview achievements display (for overview tab)
        earned_achievements = [a for a in all_achievements if a['earned']]
        recent_earned = earned_achievements[-3:] if len(earned_achievements) > 3 else earned_achievements

        if recent_earned:
            achievements_text = "  ".join([f"• {a['name']}" for a in recent_earned])
            if len(earned_achievements) > 3:
                achievements_text += f"  (+{len(earned_achievements) - 3} more)"
            self.achievements_label.setText(achievements_text)
            self.achievements_label.setStyleSheet(f"color: {AriaDesignSystem.COLORS['success']}; font-weight: bold;")
        else:
            self.achievements_label.setText("Complete training sessions to unlock achievements!")
            self.achievements_label.setStyleSheet(f"color: {AriaDesignSystem.COLORS['text_muted']}; font-style: italic;")

    def update_achievements_display(self):
        """Update the achievements list display with filtering"""
        if not hasattr(self, 'current_achievements') or not hasattr(self, 'achievements_list'):
            return

        achievements = self.current_achievements
        sender = self.sender()

        # Apply filters
        if sender == self.filter_earned_btn:
            achievements = [a for a in achievements if a['earned']]
        elif sender == self.filter_unearned_btn:
            achievements = [a for a in achievements if not a['earned']]
        elif sender == self.filter_rarity_btn:
            # Sort by rarity (legendary first)
            rarity_order = {'legendary': 0, 'epic': 1, 'rare': 2, 'uncommon': 3, 'common': 4}
            achievements = sorted(achievements, key=lambda x: rarity_order.get(x['rarity'], 5))

        # Clear and populate list
        self.achievements_list.clear()

        for achievement in achievements:
            item = QListWidgetItem()

            # Create achievement display text
            name = achievement['name']
            description = achievement['description']
            rarity = achievement['rarity'].title()
            progress = achievement.get('progress_percent', 0)
            earned = achievement['earned']

            # Create rich text
            if earned:
                text = f"✅ {name}\n{description}\n[{rarity}] - EARNED!"
                item.setBackground(QColor(AriaDesignSystem.COLORS['success']))  # Green for earned
            else:
                text = f"⏳ {name}\n{description}\n[{rarity}] - Progress: {progress:.0f}%"
                item.setBackground(QColor(AriaDesignSystem.COLORS['bg_tertiary']))  # Gray for unearned

            item.setText(text)
            self.achievements_list.addItem(item)

        # Update overview
        total_achievements = len(self.current_achievements)
        earned_count = len([a for a in self.current_achievements if a['earned']])
        completion_percent = (earned_count / total_achievements * 100) if total_achievements > 0 else 0

        if hasattr(self, 'total_earned_label'):
            self.total_earned_label.setText(str(earned_count))
            self.total_possible_label.setText(str(total_achievements))
            self.completion_progress.setValue(int(completion_percent))

    def update_history_table(self, sessions):
        """Update session history table"""
        self.history_table.setRowCount(len(sessions))

        for row, session in enumerate(sessions):
            # Date
            date_str = session.get('date', 'Unknown')
            try:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime('%m/%d/%y %H:%M')
            except (ValueError, AttributeError) as e:
                from utils.error_handler import log_error
                log_error(e, "ProgressScreen.populate_session_history - date parsing")
                formatted_date = date_str[:10] if len(date_str) > 10 else date_str

            self.history_table.setItem(row, 0, QTableWidgetItem(formatted_date))

            # Duration
            duration = session.get('duration_minutes', 0)
            duration_text = f"{duration:.1f} min"
            self.history_table.setItem(row, 1, QTableWidgetItem(duration_text))

            # Average pitch
            avg_pitch = session.get('avg_pitch', 0)
            pitch_text = f"{avg_pitch:.1f} Hz"
            self.history_table.setItem(row, 2, QTableWidgetItem(pitch_text))

            # Goal
            goal = session.get('goal', 165)
            goal_text = f"{goal} Hz"
            self.history_table.setItem(row, 3, QTableWidgetItem(goal_text))

            # Time in range
            time_in_range = session.get('time_in_range_percent', 0)
            range_text = f"{time_in_range:.1f}%"
            self.history_table.setItem(row, 4, QTableWidgetItem(range_text))

            # Alerts
            alerts = session.get('total_alerts', 0)
            self.history_table.setItem(row, 5, QTableWidgetItem(str(alerts)))

            # Type
            session_type = session.get('session_type', 'training').title()
            self.history_table.setItem(row, 6, QTableWidgetItem(session_type))

    def update_current_session_status(self):
        """Update current session status display"""
        current_session = self.session_manager.current_session

        if current_session:
            start_time = current_session.get('start_time')
            if start_time:
                elapsed = datetime.now() - start_time
                elapsed_minutes = elapsed.total_seconds() / 60
                session_type = current_session.get('type', 'training')
                goal = current_session.get('goal', 165)

                status_text = f"Active {session_type} session: {elapsed_minutes:.1f} minutes (Goal: {goal} Hz)"
                self.current_session_label.setText(status_text)
                self.current_session_label.setStyleSheet(f"font-size: 14px; color: {AriaDesignSystem.COLORS['success']}; font-weight: bold;")
            else:
                self.current_session_label.setText("Session active (time unknown)")
                self.current_session_label.setStyleSheet(f"font-size: 14px; color: {AriaDesignSystem.COLORS['warning']};")
        else:
            self.current_session_label.setText("No active session")
            self.current_session_label.setStyleSheet(f"font-size: 14px; color: {AriaDesignSystem.COLORS['text_muted']}; font-style: italic;")

    def refresh_data(self):
        """Refresh all progress data"""
        self.load_progress_data()

    def export_data(self):
        """Export progress data"""
        try:
            sessions = self.session_manager.get_session_history(limit=1000)

            if not sessions:
                QMessageBox.information(self, "Export Data", "No session data to export.")
                return

            # Simple export to text format for now
            export_text = "Aria Voice Studio - Training Data Export\n"
            export_text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            export_text += f"Total Sessions: {len(sessions)}\n\n"

            export_text += "Session History:\n"
            export_text += "Date\tDuration(min)\tAvg Pitch(Hz)\tGoal(Hz)\tTime in Range(%)\tAlerts\tType\n"

            for session in sessions:
                date_str = session.get('date', 'Unknown')[:19]  # Trim to datetime
                duration = session.get('duration_minutes', 0)
                avg_pitch = session.get('avg_pitch', 0)
                goal = session.get('goal', 165)
                time_in_range = session.get('time_in_range_percent', 0)
                alerts = session.get('total_alerts', 0)
                session_type = session.get('session_type', 'training')

                export_text += f"{date_str}\t{duration:.1f}\t{avg_pitch:.1f}\t{goal}\t{time_in_range:.1f}\t{alerts}\t{session_type}\n"

            # For now, show in a message box (could be enhanced to save to file)
            QMessageBox.information(
                self,
                "Export Data",
                f"Export ready! ({len(sessions)} sessions)\n\nData could be saved to file in future version."
            )

        except Exception as e:
            self.show_error(f"Export failed: {str(e)}")

    def clear_data(self):
        """Clear all progress data with confirmation"""
        reply = QMessageBox.question(
            self,
            "Clear All Data",
            "Are you sure you want to clear all training progress data?\n\n"
            "This action cannot be undone and will delete:\n"
            "• All session history\n"
            "• Progress statistics\n"
            "• Achievement progress\n\n"
            "Your configuration settings will be preserved.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.session_manager.clear_all_data()
                if success:
                    QMessageBox.information(self, "Data Cleared", "All progress data has been cleared successfully.")
                    self.load_progress_data()  # Refresh display
                else:
                    QMessageBox.warning(self, "Clear Failed", "Could not clear all data. Some files may be in use.")
            except Exception as e:
                self.show_error(f"Failed to clear data: {str(e)}")

    def show_error(self, message):
        """Show error message"""
        QMessageBox.critical(self, "Error", message)

    def closeEvent(self, event):
        """Clean up when widget is closed"""
        if self.refresh_timer.isActive():
            self.refresh_timer.stop()
        event.accept()