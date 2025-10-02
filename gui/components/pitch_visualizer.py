"""Modern full-width pitch visualizer for training screen."""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QPen, QLinearGradient, QBrush, QPainterPath, QFont
import math
from ..design_system import AriaColors


class ModernPitchVisualizer(QWidget):
    """Full-width pitch visualizer with waveform and pitch bar"""

    def __init__(self):
        super().__init__()
        self.pitch = 0
        self.target_pitch = 165
        self.phase = 0
        self.is_animating = False
        self._animated_pitch = 0

        self.setMinimumHeight(280)  # Reduced to fit better in default window size

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        
        # Pitch animation
        self.pitch_animation = QPropertyAnimation(self, b"animated_pitch")
        self.pitch_animation.setDuration(300)
        self.pitch_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    @pyqtProperty(float)
    def animated_pitch(self):
        return self._animated_pitch

    @animated_pitch.setter
    def animated_pitch(self, value):
        self._animated_pitch = value
        self.update()

    def start_animation(self):
        """Start visualizer animation"""
        self.is_animating = True
        self.timer.start(16)

    def stop_animation(self):
        """Stop visualizer animation"""
        self.is_animating = False
        self.timer.stop()

    def set_pitch(self, pitch_value):
        """Update pitch value with smooth animation"""
        if pitch_value != self.pitch:
            self.pitch = pitch_value
            self.pitch_animation.stop()
            self.pitch_animation.setStartValue(self._animated_pitch)
            self.pitch_animation.setEndValue(pitch_value)
            self.pitch_animation.start()

    def animate(self):
        """Animation step"""
        self.phase += 0.08
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        
        # Waveform visualization at top
        self._draw_waveform(painter, width, height)
        
        # Pitch bar at bottom
        self._draw_pitch_bar(painter, width, height)
        
        # Large pitch display in center
        self._draw_pitch_display(painter, width, height)

    def _draw_waveform(self, painter, width, height):
        """Draw animated waveform"""
        waveform_height = height * 0.3
        center_y = waveform_height / 2
        
        # Draw waveform path
        painter.setPen(QPen(QColor(255, 255, 255, 100), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        path = QPainterPath()
        
        num_points = 200
        amplitude = 20 if self._animated_pitch > 0 else 5
        
        for i in range(num_points):
            x = (width * i) / num_points
            y = center_y + amplitude * math.sin(i * 0.1 + self.phase)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        
        painter.drawPath(path)

    def _draw_pitch_bar(self, painter, width, height):
        """Draw horizontal pitch bar showing target vs current"""
        bar_height = 50
        # Position at 65% to ensure visibility with proper bottom margin
        bar_y = height * 0.65
        # Ensure bar doesn't go beyond bounds
        if bar_y + bar_height > height - 15:
            bar_y = height - bar_height - 15
        
        # Background track
        painter.setBrush(QColor(255, 255, 255, 30))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, int(bar_y), width, bar_height, 8, 8)
        
        # Target indicator line
        if self.target_pitch > 0:
            target_x = self._pitch_to_position(self.target_pitch, width)
            painter.setPen(QPen(QColor(255, 255, 255, 150), 3, Qt.PenStyle.DashLine))
            painter.drawLine(int(target_x), int(bar_y), int(target_x), int(bar_y + bar_height))
        
        # Current pitch fill
        if self._animated_pitch > 0:
            current_x = self._pitch_to_position(self._animated_pitch, width)
            
            # Gradient fill based on pitch
            gradient = QLinearGradient(0, bar_y, current_x, bar_y)
            gradient.setColorAt(0, QColor(AriaColors.GRADIENT_BLUE))
            gradient.setColorAt(1, QColor(AriaColors.GRADIENT_PINK))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(0, int(bar_y), int(current_x), bar_height, 8, 8)

    def _draw_pitch_display(self, painter, width, height):
        """Draw large pitch value in center"""
        if self._animated_pitch > 0:
            pitch_text = f"{int(self._animated_pitch)} Hz"
        else:
            pitch_text = "---"
        
        # Center position
        center_y = height * 0.45
        
        # Background
        text_width = 200
        text_height = 80
        text_x = (width - text_width) / 2
        text_y = center_y - text_height / 2
        
        painter.setBrush(QColor(AriaColors.SIDEBAR_DARK).darker(110))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(int(text_x), int(text_y), text_width, text_height, 12, 12)
        
        # Pitch text
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Arial", 42, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(int(text_x), int(text_y), text_width, text_height,
                        Qt.AlignmentFlag.AlignCenter, pitch_text)
        
        # "Current Pitch" label
        if self._animated_pitch > 0:
            label_y = text_y + text_height + 10
            painter.setPen(QColor(255, 255, 255, 180))
            font = QFont("Arial", 13, QFont.Weight.Normal)
            painter.setFont(font)
            painter.drawText(int(text_x), int(label_y), text_width, 30,
                            Qt.AlignmentFlag.AlignCenter, "Current Pitch")

    def _pitch_to_position(self, pitch, width):
        """Convert pitch (Hz) to x position on bar"""
        min_pitch = 80
        max_pitch = 350
        
        if pitch < min_pitch:
            pitch = min_pitch
        elif pitch > max_pitch:
            pitch = max_pitch
        
        normalized = (pitch - min_pitch) / (max_pitch - min_pitch)
        return width * normalized
