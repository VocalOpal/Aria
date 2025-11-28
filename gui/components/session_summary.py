"""
Smart Session Summary Dialog
Displays comprehensive session analytics with celebration animations
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGraphicsOpacityEffect, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont, QPainter, QColor, QPen
import math

from ..design_system import (
    AriaColors, AriaTypography, AriaSpacing, AriaRadius,
    PrimaryButton, SecondaryButton
)
from core.recommendations_engine import SmartRecommendations


class ConfettiWidget(QFrame):
    """Animated confetti overlay for celebration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setStyleSheet("background: transparent;")
        
        self.confetti_pieces = []
        self.animation_step = 0
        
        # Generate confetti pieces
        import random
        for _ in range(30):
            self.confetti_pieces.append({
                'x': random.uniform(0, 1),
                'y': random.uniform(-0.2, 0),
                'vx': random.uniform(-0.02, 0.02),
                'vy': random.uniform(0.01, 0.03),
                'color': random.choice([
                    AriaColors.TEAL,
                    AriaColors.GREEN,
                    AriaColors.GRADIENT_PINK,
                    AriaColors.GRADIENT_BLUE
                ]),
                'size': random.uniform(4, 8)
            })
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_confetti)
        self.timer.start(33)  # ~30 FPS
        
    def update_confetti(self):
        """Update confetti positions"""
        self.animation_step += 1
        
        for piece in self.confetti_pieces:
            piece['y'] += piece['vy']
            piece['x'] += piece['vx']
            
            # Reset if fallen off screen
            if piece['y'] > 1.2:
                piece['y'] = -0.1
                import random
                piece['x'] = random.uniform(0, 1)
        
        self.update()
        
        # Stop after 5 seconds
        if self.animation_step > 150:
            self.timer.stop()
            self.hide()
    
    def paintEvent(self, event):
        """Draw confetti"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        for piece in self.confetti_pieces:
            x = piece['x'] * width
            y = piece['y'] * height
            
            painter.setBrush(QColor(piece['color']))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(x), int(y), int(piece['size']), int(piece['size']))


class SessionSummaryDialog(QDialog):
    """
    Smart Session Summary Dialog
    Shows session statistics, achievements, and personalized tips
    """
    
    def __init__(self, session_data, parent=None, all_sessions=None):
        super().__init__(parent)
        self.session_data = session_data
        self.all_sessions = all_sessions or []
        self.is_milestone = self._check_milestone()
        
        # Generate smart recommendations
        self.recommendations_engine = SmartRecommendations()
        if self.all_sessions:
            self.recommendations_engine.analyze_user_patterns(self.all_sessions)
        
        self.setWindowTitle("Session Summary")
        self.setMinimumSize(600, 700)
        self.setModal(True)
        
        self.init_ui()
        
        # Show confetti if milestone achieved
        if self.is_milestone:
            self.show_confetti()
    
    def _check_milestone(self):
        """Check if this session achieved a milestone"""
        if not self.session_data:
            return False
        
        # Check for milestones
        consistency = self.session_data.get('time_in_range_percent', 0)
        duration = self.session_data.get('duration_minutes', 0)
        
        # Milestones: 90%+ consistency, or 30+ min session
        return consistency >= 90 or duration >= 30
    
    def init_ui(self):
        """Initialize the dialog UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Gradient background
        self.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {AriaColors.GRADIENT_BLUE_DARK},
                    stop:1 {AriaColors.GRADIENT_PINK}
                );
            }}
            QLabel {{
                color: white;
                background: transparent;
            }}
        """)
        
        # Content container
        content = QFrame()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL)
        content_layout.setSpacing(AriaSpacing.LG)
        
        # Header with celebration emoji
        header_layout = QVBoxLayout()
        header_layout.setSpacing(AriaSpacing.SM)
        
        if self.is_milestone:
            celebration = QLabel("🎉")
            celebration.setAlignment(Qt.AlignmentFlag.AlignCenter)
            celebration.setStyleSheet("font-size: 64px; background: transparent;")
            header_layout.addWidget(celebration)
        
        title = QLabel("Session Complete!" if not self.is_milestone else "New Personal Record!")
        title.setFont(QFont(AriaTypography.FAMILY, AriaTypography.TITLE, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        subtitle = QLabel("Great work on your voice training!")
        subtitle.setFont(QFont(AriaTypography.FAMILY, AriaTypography.BODY))
        subtitle.setStyleSheet(f"color: {AriaColors.WHITE_85}; background: transparent;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)
        
        content_layout.addLayout(header_layout)
        content_layout.addSpacing(AriaSpacing.MD)
        
        # Stats grid
        stats_card = self._create_stats_card()
        content_layout.addWidget(stats_card)
        
        # Best pitch highlight
        best_pitch_card = self._create_best_pitch_card()
        content_layout.addWidget(best_pitch_card)
        
        # Smart recommendations (replaces old tip card)
        recommendations_card = self._create_recommendations_card()
        content_layout.addWidget(recommendations_card)
        
        content_layout.addStretch()
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(AriaSpacing.MD)
        
        share_btn = SecondaryButton("Share Progress")
        share_btn.clicked.connect(self._share_progress)
        button_layout.addWidget(share_btn)
        
        continue_btn = PrimaryButton("Continue Training")
        continue_btn.clicked.connect(self.accept)
        button_layout.addWidget(continue_btn)
        
        content_layout.addLayout(button_layout)
        
        main_layout.addWidget(content)
    
    def _create_stats_card(self):
        """Create the main statistics card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {AriaColors.CARD_BG};
                border-radius: {AriaRadius.LG}px;
                border: 1px solid {AriaColors.WHITE_25};
                padding: {AriaSpacing.LG}px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(AriaSpacing.MD)
        
        # Title
        title = QLabel("Session Statistics")
        title.setFont(QFont(AriaTypography.FAMILY, AriaTypography.HEADING, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Grid of stats
        grid = QVBoxLayout()
        grid.setSpacing(AriaSpacing.SM)
        
        # Duration
        duration = self.session_data.get('duration_minutes', 0)
        grid.addWidget(self._create_stat_row("⏱️", "Duration", f"{duration:.1f} min"))
        
        # Average pitch
        avg_pitch = self.session_data.get('avg_pitch', 0)
        grid.addWidget(self._create_stat_row("🎵", "Average Pitch", f"{avg_pitch:.0f} Hz"))
        
        # Consistency
        consistency = self.session_data.get('time_in_range_percent', 0)
        grid.addWidget(self._create_stat_row("🎯", "Consistency", f"{consistency:.0f}% in target range"))
        
        # Goal achievement
        goal_achievement = self.session_data.get('goal_achievement_percent', 0)
        grid.addWidget(self._create_stat_row("⭐", "Goal Achievement", f"{goal_achievement:.0f}%"))
        
        layout.addLayout(grid)
        
        return card
    
    def _create_stat_row(self, emoji, label, value):
        """Create a single stat row"""
        row = QFrame()
        row.setStyleSheet("background: transparent;")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(AriaSpacing.SM)
        
        # Emoji
        emoji_label = QLabel(emoji)
        emoji_label.setStyleSheet("font-size: 24px; background: transparent;")
        emoji_label.setFixedWidth(40)
        row_layout.addWidget(emoji_label)
        
        # Label
        label_widget = QLabel(label)
        label_widget.setFont(QFont(AriaTypography.FAMILY, AriaTypography.BODY))
        label_widget.setStyleSheet(f"color: {AriaColors.WHITE_85}; background: transparent;")
        row_layout.addWidget(label_widget)
        
        row_layout.addStretch()
        
        # Value
        value_widget = QLabel(value)
        value_widget.setFont(QFont(AriaTypography.FAMILY, AriaTypography.BODY, QFont.Weight.Bold))
        value_widget.setStyleSheet(f"color: {AriaColors.WHITE_100}; background: transparent;")
        row_layout.addWidget(value_widget)
        
        return row
    
    def _create_best_pitch_card(self):
        """Create best pitch highlight card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {AriaColors.CARD_BG_LIGHT};
                border-radius: {AriaRadius.LG}px;
                border: 1px solid {AriaColors.WHITE_45};
                padding: {AriaSpacing.LG}px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(AriaSpacing.SM)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title
        title = QLabel("Your Best Pitch Today")
        title.setFont(QFont(AriaTypography.FAMILY, AriaTypography.SUBHEADING))
        title.setStyleSheet(f"color: {AriaColors.WHITE_70}; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Best pitch value
        max_pitch = self.session_data.get('max_pitch', 0)
        pitch_label = QLabel(f"{max_pitch:.0f} Hz 🎯")
        pitch_label.setFont(QFont(AriaTypography.FAMILY, 42, QFont.Weight.Bold))
        pitch_label.setStyleSheet(f"color: {AriaColors.TEAL}; background: transparent;")
        pitch_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(pitch_label)
        
        return card
    
    def _create_tip_card(self):
        """Create smart tip card based on performance"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(68, 197, 230, 0.15);
                border-radius: {AriaRadius.LG}px;
                border: 1px solid {AriaColors.TEAL};
                padding: {AriaSpacing.LG}px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(AriaSpacing.SM)
        
        # Tip icon and title
        header = QHBoxLayout()
        icon = QLabel("💡")
        icon.setStyleSheet("font-size: 28px; background: transparent;")
        header.addWidget(icon)
        
        title = QLabel("Smart Tip")
        title.setFont(QFont(AriaTypography.FAMILY, AriaTypography.SUBHEADING, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {AriaColors.TEAL}; background: transparent;")
        header.addWidget(title)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Generate smart tip
        tip_text = self._generate_smart_tip()
        tip_label = QLabel(tip_text)
        tip_label.setWordWrap(True)
        tip_label.setFont(QFont(AriaTypography.FAMILY, AriaTypography.BODY))
        tip_label.setStyleSheet(f"color: {AriaColors.WHITE_95}; background: transparent;")
        layout.addWidget(tip_label)
        
        return card
    
    def _create_recommendations_card(self):
        """Create smart recommendations card using AI-powered analysis"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(68, 197, 230, 0.15);
                border-radius: {AriaRadius.LG}px;
                border: 1px solid {AriaColors.TEAL};
                padding: {AriaSpacing.LG}px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(AriaSpacing.MD)
        
        # Header
        header = QHBoxLayout()
        icon = QLabel("🎯")
        icon.setStyleSheet("font-size: 28px; background: transparent;")
        header.addWidget(icon)
        
        title = QLabel("Smart Recommendations")
        title.setFont(QFont(AriaTypography.FAMILY, AriaTypography.SUBHEADING, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {AriaColors.TEAL}; background: transparent;")
        header.addWidget(title)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Get recommendations
        recommendations = self.recommendations_engine.get_recommendations_text(max_count=3)
        
        # Display recommendations or fallback
        if recommendations:
            for rec_text in recommendations:
                rec_label = QLabel(f"• {rec_text}")
                rec_label.setWordWrap(True)
                rec_label.setFont(QFont(AriaTypography.FAMILY, AriaTypography.BODY))
                rec_label.setStyleSheet(f"color: {AriaColors.WHITE_95}; background: transparent; margin-left: 10px;")
                layout.addWidget(rec_label)
        else:
            # Fallback to simple tip
            fallback_label = QLabel(self._generate_fallback_tip())
            fallback_label.setWordWrap(True)
            fallback_label.setFont(QFont(AriaTypography.FAMILY, AriaTypography.BODY))
            fallback_label.setStyleSheet(f"color: {AriaColors.WHITE_95}; background: transparent;")
            layout.addWidget(fallback_label)
        
        return card
    
    def _generate_fallback_tip(self):
        """Generate simple fallback tip when no recommendations available"""
        consistency = self.session_data.get('time_in_range_percent', 0)
        
        if consistency >= 80:
            return "Excellent session! Keep up this consistency for best results."
        elif consistency >= 60:
            return "Good progress! Focus on steady breath support for better control."
        else:
            return "Keep practicing! Consistency is key to vocal development."
    
    def _share_progress(self):
        """Share progress (placeholder for future implementation)"""
        # TODO: Implement sharing functionality
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Share Progress",
            "Sharing functionality coming soon!\n\nYour progress has been saved locally."
        )
    
    def show_confetti(self):
        """Show celebration confetti animation"""
        self.confetti = ConfettiWidget(self)
        self.confetti.setGeometry(self.rect())
        self.confetti.show()
        self.confetti.raise_()
    
    def resizeEvent(self, event):
        """Handle window resize"""
        super().resizeEvent(event)
        if hasattr(self, 'confetti'):
            self.confetti.setGeometry(self.rect())
