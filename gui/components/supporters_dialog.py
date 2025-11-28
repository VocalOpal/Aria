"""
Supporters Dialog - Shows donor leaderboard and thanks
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QScrollArea, QWidget, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from gui.design_system import AriaColors, AriaSpacing


class SupportersDialog(QDialog):
    """Dialog showing supporters leaderboard with gamification"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Our Amazing Supporters 💝")
        self.setModal(True)
        self.setMinimumSize(500, 600)
        self.setup_ui()
    
    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(AriaSpacing.LG)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header section
        header = QWidget()
        header.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {AriaColors.GRADIENT_BLUE},
                    stop:1 {AriaColors.GRADIENT_PINK});
                border: none;
            }}
        """)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(AriaSpacing.XL, AriaSpacing.LG, AriaSpacing.XL, AriaSpacing.LG)
        header_layout.setSpacing(AriaSpacing.SM)
        
        title = QLabel("💝 Hall of Heroes")
        title.setStyleSheet(f"""
            color: {AriaColors.WHITE};
            font-size: 24px;
            font-weight: 700;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        subtitle = QLabel("Thank you for keeping Aria free and open-source!")
        subtitle.setStyleSheet(f"""
            color: {AriaColors.WHITE_90};
            font-size: 14px;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)
        
        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #2A3441; }")
        
        content = QWidget()
        content.setStyleSheet("background: #2A3441;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(AriaSpacing.XL, AriaSpacing.LG, AriaSpacing.XL, AriaSpacing.LG)
        content_layout.setSpacing(AriaSpacing.MD)
        
        # Supporter tiers with gamification
        self.add_tier(content_layout, "🌟 Legendary Hero", "$20+", [
            # Add real donor names here
            {"name": "Be the first!", "amount": "$20+", "message": "You're making a huge impact!"}
        ], "#FFD700")
        
        self.add_tier(content_layout, "💎 Super Supporter", "$10-19", [
            {"name": "Your name here!", "amount": "$10+", "message": "Thank you so much!"}
        ], "#B9F2FF")
        
        self.add_tier(content_layout, "⭐ Gold Friend", "$5-9", [
            {"name": "Your name here!", "amount": "$5+", "message": "Every bit helps!"}
        ], "#FFA500")
        
        self.add_tier(content_layout, "☕ Coffee Supporter", "$3-4", [
            {"name": "Your name here!", "amount": "$3+", "message": "You're awesome!"}
        ], "#FF9B71")
        
        self.add_tier(content_layout, "💝 Kind Soul", "$1-2", [
            {"name": "Every dollar counts!", "amount": "$1+", "message": "You rock!"}
        ], "#E897BD")
        
        content_layout.addStretch()
        
        # Bottom message
        thanks_msg = QLabel("Your support makes Aria possible for everyone")
        thanks_msg.setStyleSheet(f"""
            color: {AriaColors.WHITE_70};
            font-size: 13px;
            font-style: italic;
            padding: {AriaSpacing.LG}px;
        """)
        thanks_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thanks_msg.setWordWrap(True)
        content_layout.addWidget(thanks_msg)
        
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
    
    def add_tier(self, layout, tier_name, amount_range, supporters, color):
        """Add a supporter tier section"""
        tier_frame = QFrame()
        tier_frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(255, 255, 255, 0.05);
                border-left: 4px solid {color};
                border-radius: 8px;
            }}
        """)
        
        tier_layout = QVBoxLayout(tier_frame)
        tier_layout.setContentsMargins(AriaSpacing.MD, AriaSpacing.SM, AriaSpacing.MD, AriaSpacing.SM)
        tier_layout.setSpacing(AriaSpacing.XS)
        
        # Tier header
        header_layout = QHBoxLayout()
        tier_title = QLabel(tier_name)
        tier_title.setStyleSheet(f"""
            color: {color};
            font-size: 15px;
            font-weight: 600;
        """)
        header_layout.addWidget(tier_title)
        
        tier_amount = QLabel(amount_range)
        tier_amount.setStyleSheet(f"""
            color: {AriaColors.WHITE_70};
            font-size: 12px;
        """)
        header_layout.addStretch()
        header_layout.addWidget(tier_amount)
        
        tier_layout.addLayout(header_layout)
        
        # Supporters in this tier
        for supporter in supporters:
            supporter_layout = QHBoxLayout()
            supporter_layout.setSpacing(AriaSpacing.SM)
            
            name = QLabel(f"• {supporter['name']}")
            name.setStyleSheet(f"""
                color: {AriaColors.WHITE_85};
                font-size: 13px;
            """)
            supporter_layout.addWidget(name)
            
            if supporter.get('message'):
                message = QLabel(f"— {supporter['message']}")
                message.setStyleSheet(f"""
                    color: {AriaColors.WHITE_45};
                    font-size: 11px;
                    font-style: italic;
                """)
                supporter_layout.addWidget(message)
            
            supporter_layout.addStretch()
            tier_layout.addLayout(supporter_layout)
        
        layout.addWidget(tier_frame)
