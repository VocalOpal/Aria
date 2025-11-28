"""Vocal Health Dashboard - Weekly vocal health report and recommendations."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy, QPushButton, QButtonGroup
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta

from ..design_system import (
    AriaColors, AriaTypography, AriaSpacing, AriaRadius,
    InfoCard, create_gradient_background, TitleLabel, HeadingLabel, 
    BodyLabel, CaptionLabel, StatCard, create_scroll_container
)
from core.health_analyzer import VocalHealthAnalyzer


class HealthDashboardScreen(QWidget):
    """Vocal Health Dashboard displaying weekly health grade and trends"""

    def __init__(self, voice_trainer):
        super().__init__()
        self.voice_trainer = voice_trainer
        self.session_manager = voice_trainer.session_manager
        self.health_analyzer = VocalHealthAnalyzer()
        
        # Current timeframe (today, week, month, year)
        self.current_timeframe = 'today'  # Default to 'today' for immediate feedback

        # Refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_health_data)

        self.init_ui()
        self.load_health_data()

        # Auto-refresh every 30 seconds
        self.refresh_timer.start(30000)

    def init_ui(self):
        """Initialize health dashboard UI"""
        content = QFrame()
        content.setStyleSheet(create_gradient_background())

        layout = QVBoxLayout(content)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(32)

        # Title and timeframe selector
        header_layout = QHBoxLayout()
        header_layout.addWidget(TitleLabel("❤️ Vocal Health Dashboard"))
        header_layout.addStretch()
        
        # Timeframe selector
        timeframe_layout = QHBoxLayout()
        timeframe_layout.setSpacing(AriaSpacing.SM)

        self.timeframe_buttons = QButtonGroup()
        self.today_btn = self._create_timeframe_button("Today", "today")
        self.week_btn = self._create_timeframe_button("Week", "week")
        self.month_btn = self._create_timeframe_button("Month", "month")
        self.year_btn = self._create_timeframe_button("Year", "year")

        self.timeframe_buttons.addButton(self.today_btn, 0)
        self.timeframe_buttons.addButton(self.week_btn, 1)
        self.timeframe_buttons.addButton(self.month_btn, 2)
        self.timeframe_buttons.addButton(self.year_btn, 3)

        timeframe_layout.addWidget(self.today_btn)
        timeframe_layout.addWidget(self.week_btn)
        timeframe_layout.addWidget(self.month_btn)
        timeframe_layout.addWidget(self.year_btn)
        
        header_layout.addLayout(timeframe_layout)
        layout.addLayout(header_layout)

        # Scroll area for content
        scroll = create_scroll_container()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(8, 8, AriaSpacing.LG + 8, 8)  # Add padding for shadows
        scroll_layout.setSpacing(AriaSpacing.XL)

        # Grade Display Card
        self.grade_card = self._create_grade_card()
        scroll_layout.addWidget(self.grade_card)

        # Comparison Row (This Week vs Last Week)
        comparison_row = QHBoxLayout()
        comparison_row.setSpacing(AriaSpacing.LG)

        self.this_week_card = StatCard("This Week", "N/A", "No data", min_height=180, value_size=48)
        self.last_week_card = StatCard("Last Week", "N/A", "No data", min_height=180, value_size=48)

        comparison_row.addWidget(self.this_week_card)
        comparison_row.addWidget(self.last_week_card)
        scroll_layout.addLayout(comparison_row)

        # Trend Metrics Row (using plain language names)
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(AriaSpacing.LG)

        self.jitter_card = self._create_metric_card("Voice Steadiness", "0.0%")
        self.shimmer_card = self._create_metric_card("Voice Consistency", "0.0%")
        self.hnr_card = self._create_metric_card("Voice Clarity", "0.0")
        self.strain_card = self._create_metric_card("Strain Alerts", "0")

        metrics_row.addWidget(self.jitter_card)
        metrics_row.addWidget(self.shimmer_card)
        metrics_row.addWidget(self.hnr_card)
        metrics_row.addWidget(self.strain_card)
        scroll_layout.addLayout(metrics_row)

        # Recommendations Card
        self.recommendations_card = self._create_recommendations_card()
        scroll_layout.addWidget(self.recommendations_card)

        # Weekly Summary Card
        self.summary_card = self._create_summary_card()
        scroll_layout.addWidget(self.summary_card)

        # Advanced Safety Metrics Row
        advanced_row = QHBoxLayout()
        advanced_row.setSpacing(AriaSpacing.LG)

        self.fatigue_card = self._create_metric_card("Fatigue Score", "0/100")
        self.rest_card = self._create_metric_card("Rest Needed", "0h")
        self.recovery_card = self._create_metric_card("Recovery Score", "100/100")

        advanced_row.addWidget(self.fatigue_card)
        advanced_row.addWidget(self.rest_card)
        advanced_row.addWidget(self.recovery_card)
        scroll_layout.addLayout(advanced_row)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Set main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(content)
    
    def _create_timeframe_button(self, text: str, timeframe: str) -> QPushButton:
        """Create a timeframe selector button"""
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(timeframe == 'today')  # Today is default
        btn.clicked.connect(lambda: self._on_timeframe_changed(timeframe))
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255, 255, 255, 0.1);
                color: {AriaColors.WHITE_85};
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: {AriaRadius.MD}px;
                padding: {AriaSpacing.SM}px {AriaSpacing.MD}px;
                font-size: {AriaTypography.BODY}px;
                font-weight: 600;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.15);
                border-color: {AriaColors.TEAL};
            }}
            QPushButton:checked {{
                background: {AriaColors.TEAL};
                color: white;
                border-color: {AriaColors.TEAL};
            }}
        """)
        
        return btn
    
    def _on_timeframe_changed(self, timeframe: str):
        """Handle timeframe change"""
        self.current_timeframe = timeframe
        self.load_health_data()

    def _create_grade_card(self):
        """Create the main grade display card"""
        card = InfoCard("", min_height=220)

        # Large grade display
        self.grade_label = QLabel("N/A")
        self.grade_label.setStyleSheet(f"""
            color: white;
            font-size: 96px;
            font-weight: 900;
            background: transparent;
            letter-spacing: -2px;
        """)
        self.grade_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card.content_layout.addWidget(self.grade_label)

        # Score display
        self.score_label = CaptionLabel("Score: 0/100")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_label.setStyleSheet(f"""
            color: {AriaColors.WHITE_85};
            font-size: {AriaTypography.HEADING}px;
            font-weight: 600;
            background: transparent;
        """)
        card.content_layout.addWidget(self.score_label)

        # Status message
        self.status_label = CaptionLabel("Weekly Vocal Health Grade")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card.content_layout.addWidget(self.status_label)

        return card

    def _create_metric_card(self, title, value):
        """Create a small metric display card"""
        card = InfoCard("", min_height=140)  # Empty title, we'll set it manually

        # Title label (stored for plain language updates)
        title_label = HeadingLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card.content_layout.addWidget(title_label)
        card.title_label = title_label

        # Value label
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            color: white;
            font-size: 36px;
            font-weight: 700;
            background: transparent;
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card.content_layout.addWidget(value_label)

        # Store reference for updates
        card.value_label = value_label

        return card

    def _create_recommendations_card(self):
        """Create recommendations panel"""
        card = InfoCard("💡 Personalized Recommendations", min_height=200)

        self.recommendations_layout = QVBoxLayout()
        self.recommendations_layout.setSpacing(AriaSpacing.SM)
        card.content_layout.addLayout(self.recommendations_layout)

        return card

    def _create_summary_card(self):
        """Create weekly summary card"""
        card = InfoCard("📊 Weekly Summary", min_height=240)

        self.summary_label = BodyLabel("Loading health data...")
        card.content_layout.addWidget(self.summary_label)

        return card

    def load_health_data(self):
        """Load and display health data based on selected timeframe"""
        try:
            # Get all sessions
            all_sessions = getattr(self.session_manager, 'weekly_sessions', [])

            if not all_sessions:
                self._show_no_data()
                return

            # Load data based on timeframe
            if self.current_timeframe == 'today':
                self._load_today_data(all_sessions)
            elif self.current_timeframe == 'week':
                self._load_weekly_data(all_sessions)
            elif self.current_timeframe == 'month':
                self._load_monthly_data(all_sessions)
            elif self.current_timeframe == 'year':
                self._load_yearly_data(all_sessions)

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "HealthDashboardScreen.load_health_data")
            # Show no data instead of error for empty sessions
            if "weekly_sessions" in str(e) or not hasattr(self.session_manager, 'weekly_sessions'):
                self._show_no_data()
            else:
                self._show_error()
    
    def _load_today_data(self, all_sessions):
        """Load today's health data for immediate feedback"""
        from datetime import datetime

        # Filter sessions from today
        today = datetime.now().date()
        today_sessions = [
            s for s in all_sessions
            if datetime.fromisoformat(s['date']).date() == today
        ]

        if not today_sessions:
            self._show_no_data_today()
            return

        # Calculate health grade from today's sessions
        grade_data = self.health_analyzer.calculate_health_grade(today_sessions)

        # Get user's total session count for contextual messaging
        user_session_count = len(all_sessions)

        # Get dashboard display data with plain language
        display_data = self.health_analyzer.get_dashboard_display_data(
            grade_data,
            user_session_count
        )

        # Update grade display
        self._update_grade_display_enhanced(display_data)

        # Update comparison cards (Today vs Yesterday)
        yesterday = today - timedelta(days=1)
        yesterday_sessions = [
            s for s in all_sessions
            if datetime.fromisoformat(s['date']).date() == yesterday
        ]

        if yesterday_sessions:
            yesterday_grade = self.health_analyzer.calculate_health_grade(yesterday_sessions)
            self.this_week_card.set_value(grade_data.get('grade', 'N/A'))
            self.this_week_card.set_description(
                f"Today | {len(today_sessions)} session{'s' if len(today_sessions) != 1 else ''}\nScore: {grade_data.get('score', 0)}/100"
            )
            self.last_week_card.set_value(yesterday_grade.get('grade', 'N/A'))
            self.last_week_card.set_description(
                f"Yesterday | {len(yesterday_sessions)} session{'s' if len(yesterday_sessions) != 1 else ''}\nScore: {yesterday_grade.get('score', 0)}/100"
            )
        else:
            self.this_week_card.set_value(grade_data.get('grade', 'N/A'))
            self.this_week_card.set_description(
                f"Today | {len(today_sessions)} session{'s' if len(today_sessions) != 1 else ''}\nScore: {grade_data.get('score', 0)}/100"
            )
            self.last_week_card.set_value("N/A")
            self.last_week_card.set_description("Yesterday\nNo sessions")

        # Update metric cards with plain language
        self._update_metric_cards_enhanced(display_data)

        # Generate recommendations
        recommendations = self.health_analyzer.generate_recommendations(grade_data, {'trends': {}})
        self._update_recommendations(recommendations)

        # Update summary
        self._update_summary_today(display_data, len(today_sessions))

        # Update advanced metrics
        self._update_advanced_metrics(all_sessions)

    def _load_weekly_data(self, all_sessions):
        """Load weekly health data"""
        # Get health trends
        trend_data = self.health_analyzer.get_health_trends(all_sessions)

        if not trend_data:
            self._show_no_data()
            return

        this_week = trend_data.get('this_week', {})
        last_week = trend_data.get('last_week', {})
        trends = trend_data.get('trends', {})
        session_counts = trend_data.get('session_counts', {'this_week': 0, 'last_week': 0})

        # Get user's total session count for contextual messaging
        user_session_count = len(all_sessions)

        # Get dashboard display data with plain language (NEW)
        display_data = self.health_analyzer.get_dashboard_display_data(
            this_week,
            user_session_count
        )

        # Update grade display with enhanced method
        self._update_grade_display_enhanced(display_data)

        # Update comparison cards
        self._update_comparison_cards(this_week, last_week, session_counts)

        # Update metric cards with enhanced method
        self._update_metric_cards_enhanced(display_data)

        # Update recommendations
        recommendations = self.health_analyzer.generate_recommendations(this_week, trend_data)
        self._update_recommendations(recommendations)

        # Update summary
        self._update_summary(this_week, session_counts)

        # Update advanced safety metrics
        self._update_advanced_metrics(all_sessions)
    
    def _load_monthly_data(self, all_sessions):
        """Load monthly health trends"""
        monthly_data = self.health_analyzer.get_monthly_health_trends(all_sessions, months=6)
        
        if not monthly_data or not monthly_data.get('months'):
            self._show_no_data()
            return
        
        # Get current and previous month data
        months = monthly_data['months']
        current_month_key = months[-1]
        previous_month_key = months[-2] if len(months) >= 2 else None
        
        current_month = monthly_data['monthly_data'][current_month_key]
        previous_month = monthly_data['monthly_data'][previous_month_key] if previous_month_key else {}
        
        # Create grade data structure
        current_grade = {
            'grade': current_month['health_grade'],
            'score': current_month['health_score'],
            'metrics': {
                'avg_jitter': current_month['avg_jitter'],
                'avg_shimmer': current_month['avg_shimmer'],
                'avg_hnr': current_month['avg_hnr'],
                'strain_events': current_month['total_strain']
            },
            'details': {}
        }
        
        previous_grade = {
            'grade': previous_month.get('health_grade', 'N/A'),
            'score': previous_month.get('health_score', 0),
            'metrics': previous_month
        }
        
        # Update displays
        self._update_grade_display(current_grade)
        
        # Update comparison cards with month names
        self.this_week_card.set_value(current_grade['grade'])
        self.this_week_card.set_description(
            f"Score: {current_grade['score']} | {current_month['session_count']} sessions\n{current_month['month_name']}"
        )
        
        if previous_month:
            self.last_week_card.set_value(previous_grade['grade'])
            self.last_week_card.set_description(
                f"Score: {previous_grade['score']} | {previous_month['session_count']} sessions\n{previous_month['month_name']}"
            )
        else:
            self.last_week_card.set_value("N/A")
            self.last_week_card.set_description("No previous month data")
        
        # Update metric cards with trends
        trends = monthly_data.get('trends', {})
        self._update_metric_cards(current_grade, trends)
        
        # Update summary for monthly view
        summary_text = f"Monthly Overview: {current_month['month_name']}\n\n"
        summary_text += f"Completed {current_month['session_count']} sessions with grade {current_grade['grade']}. "
        
        if trends:
            if 'overall_health' in trends:
                health_trend = trends['overall_health']
                change = health_trend['change_percent']
                direction = "improved" if change > 0 else "declined"
                summary_text += f"Health {direction} by {abs(change):.1f}% over the tracked period."
        
        self.summary_label.setText(summary_text)
        
        # Update advanced metrics
        self._update_advanced_metrics(all_sessions)
    
    def _load_yearly_data(self, all_sessions):
        """Load yearly health overview"""
        yearly_data = self.health_analyzer.get_yearly_health_overview(all_sessions)
        
        if not yearly_data or not yearly_data.get('years'):
            self._show_no_data()
            return
        
        # Get current and previous year data
        years = yearly_data['years']
        current_year_key = years[-1]
        previous_year_key = years[-2] if len(years) >= 2 else None
        
        current_year = yearly_data['yearly_data'][current_year_key]
        previous_year = yearly_data['yearly_data'][previous_year_key] if previous_year_key else {}
        
        # Create grade data structure
        current_grade = {
            'grade': current_year['health_grade'],
            'score': current_year['health_score'],
            'metrics': {
                'avg_jitter': current_year['avg_jitter'],
                'avg_shimmer': current_year['avg_shimmer'],
                'avg_hnr': current_year['avg_hnr'],
                'strain_events': current_year['total_strain']
            },
            'details': {}
        }
        
        # Update displays
        self._update_grade_display(current_grade)
        
        # Update comparison cards
        self.this_week_card.set_value(current_grade['grade'])
        self.this_week_card.set_description(
            f"Year {current_year_key}\nScore: {current_grade['score']} | {current_year['total_sessions']} sessions"
        )
        
        if previous_year:
            self.last_week_card.set_value(previous_year['health_grade'])
            self.last_week_card.set_description(
                f"Year {previous_year_key}\nScore: {previous_year['health_score']} | {previous_year['total_sessions']} sessions"
            )
        else:
            self.last_week_card.set_value("N/A")
            self.last_week_card.set_description("No previous year data")
        
        # Update metric cards (no trends for yearly view, just display values)
        self.jitter_card.value_label.setText(f"{current_year['avg_jitter']:.2f}%")
        self.shimmer_card.value_label.setText(f"{current_year['avg_shimmer']:.2f}%")
        self.hnr_card.value_label.setText(f"{current_year['avg_hnr']:.1f}")
        self.strain_card.value_label.setText(str(int(current_year['total_strain'])))
        
        # Update summary for yearly view
        summary_text = f"Yearly Overview: {current_year_key}\n\n"
        summary_text += f"Completed {current_year['total_sessions']} sessions with an overall grade of {current_grade['grade']}. "
        summary_text += f"Most active month: {current_year['most_active_month']}. "
        
        if yearly_data.get('best_year'):
            summary_text += f"\n\nBest year: {yearly_data['best_year']} (Score: {yearly_data['best_score']}). "
        
        if yearly_data.get('improvement_rate'):
            rate = yearly_data['improvement_rate']
            direction = "improved" if rate > 0 else "declined"
            summary_text += f"Overall health has {direction} by {abs(rate):.1f}% since starting."
        
        self.summary_label.setText(summary_text)
        
        # Update advanced metrics
        self._update_advanced_metrics(all_sessions)

    def _update_grade_display(self, grade_data):
        """Update the main grade display"""
        grade = grade_data.get('grade', 'N/A')
        score = grade_data.get('score', 0)

        self.grade_label.setText(grade)
        self.score_label.setText(f"Score: {score}/100")

        # Color-code the grade
        color = self._get_grade_color(grade)
        self.grade_label.setStyleSheet(f"""
            color: {color};
            font-size: 96px;
            font-weight: 900;
            background: transparent;
            letter-spacing: -2px;
        """)

        if grade in ['A+', 'A']:
            self.status_label.setText("Outstanding Vocal Health")
        elif grade == 'B':
            self.status_label.setText("Good Vocal Health")
        elif grade == 'C':
            self.status_label.setText("Fair - Room for Improvement")
        elif grade in ['D', 'F']:
            self.status_label.setText("Needs Attention")
        else:
            self.status_label.setText("Weekly Vocal Health Grade")

    def _get_grade_color(self, grade):
        """Get color based on grade"""
        if grade in ['A+', 'A']:
            return AriaColors.GREEN
        elif grade == 'B':
            return AriaColors.TEAL
        elif grade == 'C':
            return "#FFC107"  # Yellow
        elif grade in ['D', 'F']:
            return AriaColors.RED
        return AriaColors.WHITE

    def _update_comparison_cards(self, this_week, last_week, session_counts):
        """Update this week vs last week cards"""
        this_grade = this_week.get('grade', 'N/A')
        this_score = this_week.get('score', 0)
        this_count = session_counts.get('this_week', 0)

        last_grade = last_week.get('grade', 'N/A')
        last_score = last_week.get('score', 0)
        last_count = session_counts.get('last_week', 0)

        self.this_week_card.set_value(this_grade)
        self.this_week_card.set_description(f"Score: {this_score} | {this_count} sessions")

        self.last_week_card.set_value(last_grade)
        self.last_week_card.set_description(f"Score: {last_score} | {last_count} sessions")

    def _update_metric_cards(self, grade_data, trends):
        """Update individual metric cards"""
        details = grade_data.get('details', {})
        metrics = grade_data.get('metrics', {})

        # Jitter
        jitter_val = metrics.get('avg_jitter', 0)
        jitter_change = trends.get('jitter_change', 0)
        jitter_text = f"{jitter_val:.2f}%"
        if jitter_change != 0:
            arrow = "↑" if jitter_change > 0 else "↓"
            jitter_text += f" {arrow}{abs(jitter_change):.1f}%"
        self.jitter_card.value_label.setText(jitter_text)

        # Shimmer
        shimmer_val = metrics.get('avg_shimmer', 0)
        shimmer_change = trends.get('shimmer_change', 0)
        shimmer_text = f"{shimmer_val:.2f}%"
        if shimmer_change != 0:
            arrow = "↑" if shimmer_change > 0 else "↓"
            shimmer_text += f" {arrow}{abs(shimmer_change):.1f}%"
        self.shimmer_card.value_label.setText(shimmer_text)

        # HNR
        hnr_val = metrics.get('avg_hnr', 0)
        hnr_change = trends.get('hnr_change', 0)
        hnr_text = f"{hnr_val:.1f}"
        if hnr_change != 0:
            arrow = "↑" if hnr_change > 0 else "↓"
            hnr_text += f" {arrow}{abs(hnr_change):.1f}%"
        self.hnr_card.value_label.setText(hnr_text)

        # Strain Events
        strain_val = metrics.get('strain_events', 0)
        self.strain_card.value_label.setText(str(int(strain_val)))

    def _update_recommendations(self, recommendations):
        """Update recommendations panel"""
        # Clear existing recommendations
        while self.recommendations_layout.count():
            child = self.recommendations_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Add new recommendations
        if recommendations:
            for rec in recommendations:
                rec_label = BodyLabel(rec)
                rec_label.setStyleSheet(f"""
                    color: {AriaColors.WHITE_95};
                    font-size: {AriaTypography.BODY}px;
                    background: rgba(255, 255, 255, 0.1);
                    padding: {AriaSpacing.SM}px;
                    border-radius: {AriaRadius.SM}px;
                    border-left: 3px solid {AriaColors.TEAL};
                """)
                self.recommendations_layout.addWidget(rec_label)
        else:
            no_rec = BodyLabel("Keep up the good work")
            self.recommendations_layout.addWidget(no_rec)

    def _update_summary(self, grade_data, session_counts):
        """Update weekly summary text"""
        this_count = session_counts.get('this_week', 0)
        grade = grade_data.get('grade', 'N/A')
        score = grade_data.get('score', 0)

        summary_text = f"You completed {this_count} training session{'s' if this_count != 1 else ''} this week "
        summary_text += f"with an overall vocal health grade of {grade} ({score}/100). "

        details = grade_data.get('details', {})
        excellent_metrics = [k for k, v in details.items() if isinstance(v, dict) and v.get('status') == 'excellent']
        
        if excellent_metrics:
            summary_text += f"Excellent performance in: {', '.join(excellent_metrics)}. "
        
        if grade in ['A+', 'A']:
            summary_text += "You're maintaining outstanding vocal health!"
        elif grade == 'B':
            summary_text += "Your vocal health is good, with room for minor improvements."
        elif grade == 'C':
            summary_text += "Focus on the recommendations to improve your vocal health."
        else:
            summary_text += "Consider reviewing your training approach and consulting a specialist."

        self.summary_label.setText(summary_text)

    def _show_no_data_today(self):
        """Show no data state for today view"""
        self.grade_label.setText("N/A")
        self.score_label.setText("No sessions today")
        self.status_label.setText("Start training to see today's vocal health metrics!")

        self.this_week_card.set_value("N/A")
        self.this_week_card.set_description("Today\nNo sessions yet")
        self.last_week_card.set_value("N/A")
        self.last_week_card.set_description("Yesterday\nNo sessions")

        self.jitter_card.value_label.setText("--")
        self.shimmer_card.value_label.setText("--")
        self.hnr_card.value_label.setText("--")
        self.strain_card.value_label.setText("--")

        self.fatigue_card.value_label.setText("--")
        self.rest_card.value_label.setText("--")
        self.recovery_card.value_label.setText("--")

        # Clear recommendations and show today's message
        while self.recommendations_layout.count():
            child = self.recommendations_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        today_rec = BodyLabel("Complete your first session today to see real-time vocal health metrics.")
        today_rec.setStyleSheet(f"""
            color: {AriaColors.WHITE_95};
            font-size: {AriaTypography.BODY}px;
            background: rgba(255, 255, 255, 0.1);
            padding: {AriaSpacing.MD}px;
            border-radius: {AriaRadius.SM}px;
            border-left: 3px solid {AriaColors.TEAL};
        """)
        self.recommendations_layout.addWidget(today_rec)

        self.summary_label.setText("Complete a training session to see today's vocal health analysis.")

    def _show_no_data(self):
        """Show no data state"""
        self.grade_label.setText("N/A")
        self.score_label.setText("No sessions this week")
        self.status_label.setText("Start training to see your vocal health grade!")
        
        self.this_week_card.set_value("N/A")
        self.this_week_card.set_description("No sessions")
        self.last_week_card.set_value("N/A")
        self.last_week_card.set_description("No sessions")
        
        self.jitter_card.value_label.setText("--")
        self.shimmer_card.value_label.setText("--")
        self.hnr_card.value_label.setText("--")
        self.strain_card.value_label.setText("--")
        
        self.fatigue_card.value_label.setText("--")
        self.rest_card.value_label.setText("--")
        self.recovery_card.value_label.setText("--")
        
        # Clear recommendations and show welcome message
        while self.recommendations_layout.count():
            child = self.recommendations_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        welcome_rec = BodyLabel("Welcome! Complete your first training session to receive personalized vocal health recommendations.")
        welcome_rec.setStyleSheet(f"""
            color: {AriaColors.WHITE_95};
            font-size: {AriaTypography.BODY}px;
            background: rgba(255, 255, 255, 0.1);
            padding: {AriaSpacing.MD}px;
            border-radius: {AriaRadius.SM}px;
            border-left: 3px solid {AriaColors.TEAL};
        """)
        self.recommendations_layout.addWidget(welcome_rec)
        
        self.summary_label.setText("Complete your first training session to see your vocal health metrics and personalized recommendations.")

    def _show_error(self):
        """Show error state"""
        self.grade_label.setText("Error")
        self.score_label.setText("Unable to load health data")
        self.status_label.setText("Please try again later")

    def _update_grade_display_enhanced(self, display_data: dict):
        """Update grade display with enhanced contextual data"""
        grade = display_data['grade']
        grade_emoji = display_data['grade_emoji']
        grade_title = display_data['grade_title']

        # Display grade with emoji
        self.grade_label.setText(f"{grade_emoji} {grade}")
        self.score_label.setText(f"{display_data['score']}/{display_data['score_max']} points")
        self.status_label.setText(f"{grade_title} | {display_data['context_message']}")

        # Color-code the grade
        color = self._get_grade_color(grade)
        self.grade_label.setStyleSheet(f"""
            color: {color};
            font-size: 96px;
            font-weight: 900;
            background: transparent;
            letter-spacing: -2px;
        """)

    def _update_metric_cards_enhanced(self, display_data: dict):
        """Update metric cards with plain language from display_data"""
        metrics = display_data.get('metrics', {})

        # Update each metric card with plain language
        for metric_key in ['jitter', 'shimmer', 'hnr', 'strain_events']:
            if metric_key not in metrics:
                continue

            metric_data = metrics[metric_key]

            # Format value
            if metric_key == 'jitter' or metric_key == 'shimmer':
                value_text = f"{metric_data['value']:.2f}%"
            elif metric_key == 'hnr':
                value_text = f"{metric_data['value']:.1f} dB"
            else:  # strain_events
                value_text = str(int(metric_data['value']))

            # Add status emoji
            value_text = f"{metric_data['emoji']} {value_text}"

            # Update the corresponding card
            if metric_key == 'jitter':
                self.jitter_card.value_label.setText(value_text)
                # Update title to plain language
                if hasattr(self.jitter_card, 'title_label'):
                    self.jitter_card.title_label.setText(metric_data['display_name'])
            elif metric_key == 'shimmer':
                self.shimmer_card.value_label.setText(value_text)
                if hasattr(self.shimmer_card, 'title_label'):
                    self.shimmer_card.title_label.setText(metric_data['display_name'])
            elif metric_key == 'hnr':
                self.hnr_card.value_label.setText(value_text)
                if hasattr(self.hnr_card, 'title_label'):
                    self.hnr_card.title_label.setText(metric_data['display_name'])
            elif metric_key == 'strain_events':
                self.strain_card.value_label.setText(value_text)
                if hasattr(self.strain_card, 'title_label'):
                    self.strain_card.title_label.setText(metric_data['display_name'])

    def _update_summary_today(self, display_data: dict, session_count: int):
        """Update summary text for today's view"""
        grade = display_data['grade']
        score = display_data['score']

        summary_text = f"Today: Completed {session_count} session{'s' if session_count != 1 else ''} "
        summary_text += f"with a vocal health grade of {grade} ({score}/100 points).\n\n"

        # Add context message
        summary_text += display_data['context_message'] + "\n\n"

        # Add action message
        summary_text += display_data['action_message']

        self.summary_label.setText(summary_text)

    def _update_advanced_metrics(self, all_sessions):
        """Update advanced safety metrics: fatigue, rest, recovery"""
        try:
            # Get fatigue trend
            fatigue_trend = self.session_manager.get_fatigue_trend(days=7)
            current_fatigue = fatigue_trend.get('current_fatigue', 0)
            fatigue_trend_status = fatigue_trend.get('trend', 'no_data')
            
            # Update fatigue card
            fatigue_text = f"{current_fatigue:.0f}/100"
            if fatigue_trend_status == 'worsening':
                fatigue_text += " ↑"
            elif fatigue_trend_status == 'improving':
                fatigue_text += " ↓"
            self.fatigue_card.value_label.setText(fatigue_text)
            
            # Color code fatigue
            if current_fatigue > 70:
                color = AriaColors.RED
            elif current_fatigue > 50:
                color = "#FFC107"  # Yellow
            else:
                color = AriaColors.GREEN
            self.fatigue_card.value_label.setStyleSheet(f"""
                color: {color};
                font-size: 36px;
                font-weight: 700;
                background: transparent;
            """)
            
            # Calculate recommended rest
            rest_data = self.health_analyzer.calculate_recommended_rest(all_sessions, fatigue_trend)
            hours_needed = rest_data.get('hours_until_ready', 0)
            rest_status = rest_data.get('status', 'ready')
            
            # Update rest card
            if hours_needed == 0:
                rest_text = "Ready ✓"
                rest_color = AriaColors.GREEN
            elif hours_needed >= 24:
                days = hours_needed // 24
                rest_text = f"{days}d rest"
                rest_color = AriaColors.RED
            else:
                rest_text = f"{hours_needed}h rest"
                rest_color = "#FFC107" if hours_needed < 12 else AriaColors.RED
            
            self.rest_card.value_label.setText(rest_text)
            self.rest_card.value_label.setStyleSheet(f"""
                color: {rest_color};
                font-size: 36px;
                font-weight: 700;
                background: transparent;
            """)
            
            # Calculate recovery score (compare last 2 sessions)
            if len(all_sessions) >= 2:
                previous_session = all_sessions[-2]
                current_session = all_sessions[-1]
                
                current_metrics = {
                    'avg_jitter': current_session.get('avg_jitter', 0),
                    'avg_shimmer': current_session.get('avg_shimmer', 0),
                    'avg_hnr': current_session.get('avg_hnr', 20),
                    'strain_events': current_session.get('strain_events', 0)
                }
                
                recovery_data = self.health_analyzer.calculate_recovery_score(previous_session, current_metrics)
                recovery_score = recovery_data.get('score', 100)
                recovery_status = recovery_data.get('status', 'no_baseline')
                
                # Update recovery card
                recovery_text = f"{recovery_score:.0f}/100"
                
                if recovery_score >= 90:
                    recovery_color = AriaColors.GREEN
                elif recovery_score >= 75:
                    recovery_color = AriaColors.TEAL
                elif recovery_score >= 60:
                    recovery_color = "#FFC107"
                else:
                    recovery_color = AriaColors.RED
                
                self.recovery_card.value_label.setText(recovery_text)
                self.recovery_card.value_label.setStyleSheet(f"""
                    color: {recovery_color};
                    font-size: 36px;
                    font-weight: 700;
                    background: transparent;
                """)
            else:
                self.recovery_card.value_label.setText("N/A")
                self.recovery_card.value_label.setStyleSheet(f"""
                    color: {AriaColors.WHITE_85};
                    font-size: 36px;
                    font-weight: 700;
                    background: transparent;
                """)
                
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "HealthDashboardScreen._update_advanced_metrics")
            self.fatigue_card.value_label.setText("--")
            self.rest_card.value_label.setText("--")
            self.recovery_card.value_label.setText("--")
