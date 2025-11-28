"""
Aria Voice Studio - Public Beta (v5) - Visual Breathing Guide Component
Animated circular breathing guide with pulsing animation for exercises
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QSequentialAnimationGroup
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from ..design_system import AriaColors, AriaTypography


class BreathingCircle(QWidget):
    """Animated breathing circle that pulses to guide breathing rhythm"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(250, 250)
        
        # Breathing parameters (in milliseconds)
        self.inhale_duration = 4000  # 4 seconds
        self.hold_duration = 2000     # 2 seconds
        self.exhale_duration = 4000   # 4 seconds
        
        # Animation state
        self._circle_size = 100
        self._phase = "INHALE"
        self._is_active = False
        
        # Animation group
        self.animation_group = QSequentialAnimationGroup()
        self.animation_group.finished.connect(self._restart_cycle)
        
        self._setup_animations()
        
    def _setup_animations(self):
        """Setup the breathing animation cycle"""
        # INHALE: Expand from 100px to 200px
        self.inhale_anim = QPropertyAnimation(self, b"circle_size")
        self.inhale_anim.setDuration(self.inhale_duration)
        self.inhale_anim.setStartValue(100)
        self.inhale_anim.setEndValue(200)
        self.inhale_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.inhale_anim.valueChanged.connect(lambda: self._set_phase("INHALE"))
        
        # HOLD: Stay at 200px
        self.hold_anim = QPropertyAnimation(self, b"circle_size")
        self.hold_anim.setDuration(self.hold_duration)
        self.hold_anim.setStartValue(200)
        self.hold_anim.setEndValue(200)
        self.hold_anim.valueChanged.connect(lambda: self._set_phase("HOLD"))
        
        # EXHALE: Contract from 200px to 100px
        self.exhale_anim = QPropertyAnimation(self, b"circle_size")
        self.exhale_anim.setDuration(self.exhale_duration)
        self.exhale_anim.setStartValue(200)
        self.exhale_anim.setEndValue(100)
        self.exhale_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.exhale_anim.valueChanged.connect(lambda: self._set_phase("EXHALE"))
        
        # Add to sequential group
        self.animation_group.addAnimation(self.inhale_anim)
        self.animation_group.addAnimation(self.hold_anim)
        self.animation_group.addAnimation(self.exhale_anim)
    
    def _set_phase(self, phase):
        """Update the current breathing phase"""
        if self._phase != phase:
            self._phase = phase
            self.update()
    
    def _restart_cycle(self):
        """Restart the breathing cycle if still active"""
        if self._is_active:
            self.animation_group.start()
    
    @pyqtProperty(int)
    def circle_size(self):
        return self._circle_size
    
    @circle_size.setter
    def circle_size(self, value):
        self._circle_size = value
        self.update()
    
    def start(self):
        """Start the breathing animation"""
        self._is_active = True
        self._circle_size = 100
        self._phase = "INHALE"
        self.animation_group.start()
    
    def stop(self):
        """Stop the breathing animation"""
        self._is_active = False
        self.animation_group.stop()
        self._circle_size = 100
        self._phase = "INHALE"
        self.update()
    
    def set_timing(self, inhale_ms, hold_ms, exhale_ms):
        """Configure breathing timing
        
        Args:
            inhale_ms (int): Inhale duration in milliseconds
            hold_ms (int): Hold duration in milliseconds
            exhale_ms (int): Exhale duration in milliseconds
        """
        self.inhale_duration = inhale_ms
        self.hold_duration = hold_ms
        self.exhale_duration = exhale_ms
        
        # Recreate animations with new timing
        was_active = self._is_active
        if was_active:
            self.stop()
        
        self.animation_group.clear()
        self._setup_animations()
        
        if was_active:
            self.start()
    
    def paintEvent(self, event):
        """Paint the breathing circle"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # Draw circle with teal color
        painter.setPen(QPen(QColor(AriaColors.TEAL), 4))
        painter.setBrush(QColor(AriaColors.TEAL))
        
        radius = self._circle_size // 2
        painter.drawEllipse(
            center_x - radius,
            center_y - radius,
            self._circle_size,
            self._circle_size
        )
        
        # Draw phase text in center
        painter.setPen(QColor(AriaColors.WHITE))
        font = QFont(AriaTypography.FAMILY, 16, QFont.Weight.Bold)
        painter.setFont(font)
        
        text_map = {
            "INHALE": "Breathe In",
            "HOLD": "Hold",
            "EXHALE": "Breathe Out"
        }
        text = text_map.get(self._phase, "Ready")
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text)


class BreathingGuideWidget(QWidget):
    """Complete breathing guide widget with circle and instructions"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.breathing_circle = BreathingCircle(self)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the widget UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Breathing Guide")
        title.setStyleSheet(f"""
            color: {AriaColors.WHITE_100};
            font-size: {AriaTypography.HEADING}px;
            font-weight: 700;
            background: transparent;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Breathing circle
        layout.addWidget(self.breathing_circle, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Instructions
        instructions = QLabel("Follow the circle's rhythm with your breathing")
        instructions.setStyleSheet(f"""
            color: {AriaColors.WHITE_70};
            font-size: {AriaTypography.BODY_SMALL}px;
            background: transparent;
        """)
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
    
    def start(self):
        """Start the breathing guide animation"""
        self.breathing_circle.start()
    
    def stop(self):
        """Stop the breathing guide animation"""
        self.breathing_circle.stop()
    
    def set_timing(self, inhale_ms, hold_ms, exhale_ms):
        """Configure breathing timing
        
        Args:
            inhale_ms (int): Inhale duration in milliseconds
            hold_ms (int): Hold duration in milliseconds
            exhale_ms (int): Exhale duration in milliseconds
        """
        self.breathing_circle.set_timing(inhale_ms, hold_ms, exhale_ms)
