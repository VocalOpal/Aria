"""Streak calendar heatmap component showing practice consistency."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor
from datetime import datetime, timedelta


class StreakCalendar(QDialog):
    """Calendar heatmap showing practice history"""
    
    def __init__(self, session_manager, parent=None):
        super().__init__(parent)
        self.session_manager = session_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Practice Calendar")
        self.setModal(True)
        self.setMinimumSize(700, 500)
        
        # Main background
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5A7A95,
                    stop:1 #C88AA8
                );
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Practice Calendar")
        header.setStyleSheet("""
            color: white;
            font-size: 28px;
            font-weight: 600;
            background: transparent;
        """)
        layout.addWidget(header)
        
        # Streak info
        streak_data = self.session_manager.get_current_streak()
        streak_info = self._create_streak_info(streak_data)
        layout.addWidget(streak_info)
        
        # Calendar heatmap
        calendar_widget = self._create_calendar_heatmap()
        layout.addWidget(calendar_widget)
        
        # Legend
        legend = self._create_legend()
        layout.addWidget(legend)
        
        layout.addStretch()
        
    def _create_streak_info(self, streak_data):
        """Create streak information card"""
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(8)
        
        # Streak message
        message = QLabel(streak_data['message'])
        message.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-weight: 600;
            background: transparent;
        """)
        layout.addWidget(message)
        
        # Additional info
        if streak_data['status'] == 'active':
            info_text = f"Keep it up! You've practiced {streak_data['streak_count']} days in a row."
        elif streak_data['status'] == 'at_risk':
            grace_msg = " (1 grace day available this week)" if streak_data.get('grace_available') else ""
            info_text = f"Current streak: {streak_data['streak_count']} days{grace_msg}"
        else:
            info_text = "Practice any session to count toward your streak"
            
        info = QLabel(info_text)
        info.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
            background: transparent;
        """)
        layout.addWidget(info)
        
        return container
        
    def _create_calendar_heatmap(self):
        """Create calendar heatmap grid"""
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout(container)
        layout.setSpacing(10)
        
        # Get last 30 days of data
        calendar_data = self.session_manager.get_practice_calendar_data(30)
        
        # Create grid
        grid = QGridLayout()
        grid.setSpacing(6)
        
        # Day labels
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            label = QLabel(day)
            label.setStyleSheet("""
                color: rgba(255, 255, 255, 0.6);
                font-size: 12px;
                font-weight: 500;
                background: transparent;
            """)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(label, 0, i)
        
        # Calendar cells (4 weeks + partial)
        row = 1
        col = 0
        
        # Start from the appropriate day of week
        if calendar_data:
            first_date = datetime.fromisoformat(calendar_data[0]['date'])
            col = first_date.weekday()
        
        for day_data in calendar_data:
            cell = self._create_day_cell(day_data)
            grid.addWidget(cell, row, col)
            
            col += 1
            if col > 6:
                col = 0
                row += 1
                
        layout.addLayout(grid)
        return container
        
    def _create_day_cell(self, day_data):
        """Create a single day cell with hover tooltip"""
        minutes = day_data['minutes']
        
        # Calculate color intensity based on practice time
        if minutes == 0:
            color = "rgba(255, 255, 255, 0.1)"
        elif minutes < 10:
            color = "rgba(144, 238, 144, 0.3)"  # Light green
        elif minutes < 20:
            color = "rgba(50, 205, 50, 0.5)"    # Medium green
        elif minutes < 30:
            color = "rgba(34, 139, 34, 0.7)"    # Dark green
        else:
            color = "rgba(0, 100, 0, 0.9)"      # Very dark green
            
        cell = QLabel(str(day_data['day_number']))
        cell.setFixedSize(50, 50)
        cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cell.setStyleSheet(f"""
            QLabel {{
                background: {color};
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: 500;
            }}
            QLabel:hover {{
                border: 2px solid rgba(255, 255, 255, 0.5);
            }}
        """)
        
        # Tooltip
        date_obj = datetime.fromisoformat(day_data['date'])
        date_str = date_obj.strftime('%B %d')
        if minutes > 0:
            tooltip = f"{date_str}: {int(minutes)} minutes"
        else:
            tooltip = f"{date_str}: No practice"
        cell.setToolTip(tooltip)
        
        return cell
        
    def _create_legend(self):
        """Create color legend"""
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(container)
        layout.setSpacing(10)
        
        label = QLabel("Less")
        label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.6);
            font-size: 12px;
            background: transparent;
        """)
        layout.addWidget(label)
        
        # Color boxes
        colors = [
            "rgba(255, 255, 255, 0.1)",
            "rgba(144, 238, 144, 0.3)",
            "rgba(50, 205, 50, 0.5)",
            "rgba(34, 139, 34, 0.7)",
            "rgba(0, 100, 0, 0.9)"
        ]
        
        for color in colors:
            box = QLabel()
            box.setFixedSize(20, 20)
            box.setStyleSheet(f"""
                background: {color};
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
            """)
            layout.addWidget(box)
            
        label = QLabel("More")
        label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.6);
            font-size: 12px;
            background: transparent;
        """)
        layout.addWidget(label)
        
        layout.addStretch()
        return container


class StreakBadge(QWidget):
    """Modern streak badge for sidebar"""
    
    def __init__(self, session_manager, parent=None):
        super().__init__(parent)
        self.session_manager = session_manager
        self.setMinimumHeight(85)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)
        
        self.message_label = None
        self.subtitle_label = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize modern UI"""
        # Get streak data
        streak_data = self.session_manager.get_current_streak()
        
        # Modern gradient style
        self.setStyleSheet(f"""
            StreakBadge {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(111, 162, 200, 0.25),
                    stop:1 rgba(232, 151, 189, 0.25)
                );
                border-radius: 14px;
                border: none;
            }}
            StreakBadge:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(111, 162, 200, 0.35),
                    stop:1 rgba(232, 151, 189, 0.35)
                );
            }}
        """)
        
        # Clear ALL existing widgets and layouts
        layout = self.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                while child.layout().count():
                    subchild = child.layout().takeAt(0)
                    if subchild.widget():
                        subchild.widget().deleteLater()
        
        # Reset references
        self.message_label = None
        self.subtitle_label = None
        
        # Header row
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        header_label = QLabel("DAILY STREAK")
        header_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.5);
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 1px;
            background: transparent;
        """)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        # Status icon
        if streak_data['status'] == 'active':
            status_icon = "🔥"
        elif streak_data['status'] == 'at_risk':
            status_icon = "⚠️"
        else:
            status_icon = "📅"
        
        icon_label = QLabel(status_icon)
        icon_label.setStyleSheet("background: transparent; font-size: 16px;")
        header_layout.addWidget(icon_label)
        
        layout.addLayout(header_layout)
        
        # Streak count or message
        if streak_data['status'] != 'no_streak':
            count_label = QLabel(f"{streak_data['streak_count']} days")
            count_label.setStyleSheet("""
                color: white;
                font-size: 20px;
                font-weight: 700;
                background: transparent;
            """)
            layout.addWidget(count_label)
            
            self.subtitle_label = QLabel("Tap to view history")
            self.subtitle_label.setStyleSheet("""
                color: rgba(255, 255, 255, 0.65);
                font-size: 12px;
                font-weight: 500;
                background: transparent;
            """)
            layout.addWidget(self.subtitle_label)
        else:
            self.message_label = QLabel("Start today!")
            self.message_label.setStyleSheet("""
                color: white;
                font-size: 15px;
                font-weight: 600;
                background: transparent;
            """)
            layout.addWidget(self.message_label)
            
            self.subtitle_label = QLabel("Begin your training streak")
            self.subtitle_label.setStyleSheet("""
                color: rgba(255, 255, 255, 0.65);
                font-size: 12px;
                font-weight: 500;
                background: transparent;
            """)
            layout.addWidget(self.subtitle_label)
            
    def mousePressEvent(self, event):
        """Handle click to open calendar"""
        if event.button() == Qt.MouseButton.LeftButton:
            calendar = StreakCalendar(self.session_manager, self)
            calendar.exec()
            
    def refresh(self):
        """Refresh the badge display"""
        self.init_ui()
