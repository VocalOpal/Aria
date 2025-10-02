"""
Aria Voice Studio - Easter Eggs & Hidden Features
For the curious and the dedicated 🎉

Created with love by the Aria Team (HopefulOpal)
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QKeySequence
import random

from gui.design_system import (
    AriaColors, AriaTypography, AriaSpacing, AriaRadius,
    TitleLabel, HeadingLabel, BodyLabel
)


class SecretAboutDialog(QDialog):
    """Secret credits and fun facts dialog - triggered by logo clicks"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Aria Voice Studio")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        
        # Prevent transparency
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setAutoFillBackground(True)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the secret about dialog"""
        self.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {AriaColors.GRADIENT_BLUE_DARK},
                    stop:1 {AriaColors.GRADIENT_PINK}
                );
            }}
            QLabel {{
                background: transparent;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        
        header = QLabel("About Aria Voice Studio")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(f"""
            color: white;
            font-size: 28px;
            font-weight: bold;
            background: transparent;
        """)
        layout.addWidget(header)

        about_card = QFrame()
        about_card.setStyleSheet(f"""
            QFrame {{
                background: rgba(255, 255, 255, 0.15);
                border-radius: {AriaRadius.LG}px;
                padding: 24px;
            }}
        """)
        about_layout = QVBoxLayout(about_card)
        about_layout.setSpacing(16)

        title = QLabel("Aria Voice Studio")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold; background: transparent;")
        about_layout.addWidget(title)

        version = QLabel("Public Beta v5.0")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet(f"color: {AriaColors.WHITE_85}; font-size: 14px; background: transparent;")
        about_layout.addWidget(version)

        dev_story = QLabel(
            "Created by HopefulOpal\n\n"
            "I'm also in vocal training, and this app was born from my own journey. "
            "Everything here comes from personal research, experimentation, and "
            "learning what works through trial and error."
        )
        dev_story.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dev_story.setWordWrap(True)
        dev_story.setStyleSheet(f"color: {AriaColors.WHITE_85}; font-size: 14px; background: transparent;")
        about_layout.addWidget(dev_story)

        layout.addWidget(about_card)

        disclaimer_card = QFrame()
        disclaimer_card.setStyleSheet(f"""
            QFrame {{
                background: rgba(255, 100, 100, 0.2);
                border-radius: {AriaRadius.LG}px;
                padding: 20px;
                border: 1px solid rgba(255, 100, 100, 0.3);
            }}
        """)
        disclaimer_layout = QVBoxLayout(disclaimer_card)
        disclaimer_layout.setSpacing(12)

        disclaimer_title = QLabel("Important Disclaimer")
        disclaimer_title.setStyleSheet("color: white; font-size: 16px; font-weight: bold; background: transparent;")
        disclaimer_layout.addWidget(disclaimer_title)

        disclaimer_text = QLabel(
            "This is NOT medical advice. I'm not a speech therapist or medical professional.\n\n"
            "Voice training carries real risks. Vocal strain, fatigue, and injury can occur. "
            "Please consult a qualified speech-language pathologist for professional guidance.\n\n"
            "Use this tool as a supplement to professional care, not a replacement."
        )
        disclaimer_text.setWordWrap(True)
        disclaimer_text.setStyleSheet(f"color: {AriaColors.WHITE_85}; font-size: 13px; background: transparent;")
        disclaimer_layout.addWidget(disclaimer_text)

        layout.addWidget(disclaimer_card)

        tech_label = QLabel("Built with: Python • PyQt6 • NumPy • SciPy • Librosa")
        tech_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tech_label.setStyleSheet(f"color: {AriaColors.WHITE_70}; font-size: 12px; background: transparent;")
        layout.addWidget(tech_label)
        
        layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setMinimumHeight(48)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaColors.TEAL};
                color: white;
                border: none;
                border-radius: {AriaRadius.MD}px;
                font-size: 15px;
                font-weight: 600;
                padding: 12px;
            }}
            QPushButton:hover {{
                background-color: {AriaColors.TEAL_HOVER};
            }}
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class KonamiCodeDetector:
    """Detect the legendary Konami Code: ↑↑↓↓←→←→BA"""
    
    konami_triggered = pyqtSignal()
    
    def __init__(self):
        self.sequence = []
        self.konami_code = [
            Qt.Key.Key_Up, Qt.Key.Key_Up,
            Qt.Key.Key_Down, Qt.Key.Key_Down,
            Qt.Key.Key_Left, Qt.Key.Key_Right,
            Qt.Key.Key_Left, Qt.Key.Key_Right,
            Qt.Key.Key_B, Qt.Key.Key_A
        ]
        self.reset_timer = QTimer()
        self.reset_timer.setSingleShot(True)
        self.reset_timer.timeout.connect(self.reset)
    
    def key_pressed(self, key):
        """Track key presses for konami code"""
        self.sequence.append(key)
        
        # Keep only last 10 keys
        if len(self.sequence) > 10:
            self.sequence.pop(0)
        
        # Check if konami code matched
        if self.sequence == self.konami_code:
            self.sequence = []
            return True
        
        # Reset after 3 seconds of inactivity
        self.reset_timer.start(3000)
        return False
    
    def reset(self):
        """Reset the sequence"""
        self.sequence = []


class SecretMessageToast:
    """Show random secret messages"""
    
    MESSAGES = [
        "Your voice is valid",
        "Practice makes progress, not perfection",
        "Every session counts",
        "Consistency > Perfection",
        "Your voice, your journey",
        "Small steps, big changes",
        "Progress over perfection",
        "Keep that streak going",
        "Believe in your voice",
    ]
    
    @staticmethod
    def get_random_message():
        """Get a random encouraging message"""
        return random.choice(SecretMessageToast.MESSAGES)


class DeveloperModeDialog(QDialog):
    """Secret developer mode - triggered by Konami code"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎮 Developer Mode Unlocked!")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setAutoFillBackground(True)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize developer mode dialog"""
        self.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e,
                    stop:1 #16213e
                );
            }}
            QLabel {{
                background: transparent;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("🎮 KONAMI CODE DETECTED! 🎮")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("""
            color: #00ff41;
            font-size: 28px;
            font-weight: bold;
            background: transparent;
            font-family: 'Courier New';
        """)
        layout.addWidget(header)
        
        # Achievement
        achievement = QLabel("🏆 Achievement Unlocked:\n\"The Konami Chronicles\"")
        achievement.setAlignment(Qt.AlignmentFlag.AlignCenter)
        achievement.setStyleSheet("""
            color: #ffd700;
            font-size: 18px;
            font-weight: 600;
            background: transparent;
        """)
        layout.addWidget(achievement)
        
        # Stats card
        stats_card = QFrame()
        stats_card.setStyleSheet("""
            QFrame {
                background: rgba(0, 255, 65, 0.1);
                border: 2px solid #00ff41;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        stats_layout = QVBoxLayout(stats_card)
        
        stats = [
            "👾 You're one of the elite",
            "🎯 Easter Egg Hunter: Level 99",
            "Unlocked: Secret Respect",
            "The Aria Team salutes you",
            "Keep being curious",
        ]
        
        for stat in stats:
            label = QLabel(stat)
            label.setStyleSheet("""
                color: #00ff41;
                font-size: 14px;
                background: transparent;
                font-family: 'Courier New';
            """)
            stats_layout.addWidget(label)
        
        layout.addWidget(stats_card)
        
        # Message
        msg = QLabel("You've discovered a piece of gaming history.\nThe Aria Team (HopefulOpal) honors your dedication!")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        msg.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            font-size: 13px;
            background: transparent;
            margin-top: 16px;
        """)
        layout.addWidget(msg)
        
        layout.addStretch()
        
        # Close
        close_btn = QPushButton("LEVEL COMPLETE")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setMinimumHeight(44)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #00ff41;
                color: #1a1a2e;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Courier New';
            }
            QPushButton:hover {
                background: #00dd35;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class LogoClickDetector:
    """Detect multiple clicks on the logo to reveal secrets"""
    
    def __init__(self, click_threshold=7):
        self.click_count = 0
        self.click_threshold = click_threshold
        self.reset_timer = QTimer()
        self.reset_timer.setSingleShot(True)
        self.reset_timer.timeout.connect(self.reset)
    
    def click(self):
        """Register a logo click"""
        self.click_count += 1
        
        # Reset after 3 seconds
        self.reset_timer.start(3000)
        
        # Check if threshold reached
        if self.click_count >= self.click_threshold:
            self.reset()
            return True
        
        return False
    
    def reset(self):
        """Reset the click counter"""
        self.click_count = 0


def get_motivational_quote():
    """Get a random motivational quote for loading screens or transitions"""
    quotes = [
        "Your voice is uniquely yours",
        "Progress, not perfection",
        "Every practice session matters",
        "You're stronger than you think",
        "Consistency is key",
        "Small steps lead to big changes",
        "Believe in your journey",
        "Your voice, your story",
        "Keep pushing forward",
        "You've got this",
    ]
    return random.choice(quotes)


def trigger_sparkle_effect(widget):
    """Add a sparkle effect to any widget (for special moments)"""
    # This could be implemented with QPropertyAnimation
    # For now, it's a placeholder for future enhancement
    pass
