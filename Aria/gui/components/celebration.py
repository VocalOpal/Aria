"""
Aria Voice Studio - Public Beta (v5) - Celebration Component
Animated celebration effects for achievements and milestones
"""

import random
import math
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, 
    QPoint, QRect, pyqtSignal, QParallelAnimationGroup, QSequentialAnimationGroup
)
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from typing import List, Tuple

from ..design_system import AriaColors, AriaTypography, AriaSpacing, AriaRadius


class ConfettiParticle:
    """Individual confetti particle with physics"""
    
    def __init__(self, x: int, y: int, color: QColor):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-8, -3)
        self.gravity = 0.2
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-10, 10)
        self.color = color
        self.size = random.randint(6, 12)
        self.opacity = 1.0
        self.lifetime = random.uniform(2.0, 3.5)
        self.age = 0.0
        
    def update(self, dt: float):
        """Update particle physics"""
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rotation_speed
        self.age += dt
        
        # Fade out near end of lifetime
        if self.age > self.lifetime * 0.7:
            self.opacity = 1.0 - ((self.age - self.lifetime * 0.7) / (self.lifetime * 0.3))
        
    def is_alive(self) -> bool:
        """Check if particle is still visible"""
        return self.age < self.lifetime and self.opacity > 0


class ConfettiWidget(QWidget):
    """Widget that displays animated confetti effect"""
    
    animation_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles: List[ConfettiParticle] = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_particles)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Confetti colors matching Aria theme
        self.confetti_colors = [
            QColor(119, 93, 208),   # Purple
            QColor(241, 76, 76),    # Red/Pink
            QColor(255, 183, 77),   # Gold
            QColor(129, 199, 132),  # Green
            QColor(100, 181, 246),  # Blue
            QColor(255, 138, 101),  # Orange
        ]
        
    def start_celebration(self, duration_ms: int = 3000):
        """Start confetti animation"""
        self.particles.clear()
        
        # Create bursts of confetti
        for burst in range(3):
            QTimer.singleShot(burst * 200, self.create_confetti_burst)
        
        # Start animation timer
        self.timer.start(16)  # ~60 FPS
        
        # Stop after duration
        QTimer.singleShot(duration_ms, self.stop_celebration)
        
    def create_confetti_burst(self):
        """Create a burst of confetti particles"""
        center_x = self.width() // 2
        center_y = self.height() // 3
        
        # Create particles in a burst pattern
        for _ in range(30):
            color = random.choice(self.confetti_colors)
            # Add some randomness to spawn position
            x = center_x + random.randint(-50, 50)
            y = center_y + random.randint(-20, 20)
            self.particles.append(ConfettiParticle(x, y, color))
            
    def update_particles(self):
        """Update all particles"""
        dt = 0.016  # Assuming 60 FPS
        
        # Update and remove dead particles
        self.particles = [p for p in self.particles if p.is_alive()]
        
        for particle in self.particles:
            particle.update(dt)
        
        # Stop if no particles left
        if not self.particles and not self.timer.isActive():
            self.animation_finished.emit()
            
        self.update()  # Trigger repaint
        
    def stop_celebration(self):
        """Stop the celebration animation"""
        self.timer.stop()
        
    def paintEvent(self, event):
        """Paint confetti particles"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        for particle in self.particles:
            painter.save()
            
            # Apply opacity
            color = QColor(particle.color)
            color.setAlphaF(particle.opacity)
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            
            # Draw rotated rectangle
            painter.translate(particle.x, particle.y)
            painter.rotate(particle.rotation)
            
            half_size = particle.size // 2
            painter.drawRect(-half_size, -half_size, particle.size, particle.size)
            
            painter.restore()


class CelebrationToast(QWidget):
    """Toast notification for quick celebrations"""
    
    closed = pyqtSignal()
    
    def __init__(self, message: str, icon: str = "🎉", parent=None):
        super().__init__(parent)
        self.message = message
        self.icon = icon
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.init_ui()
        
    def init_ui(self):
        """Initialize toast UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(AriaSpacing.LG, AriaSpacing.MD, AriaSpacing.LG, AriaSpacing.MD)
        layout.setSpacing(AriaSpacing.MD)
        
        # Container with gradient background
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {AriaColors.GRADIENT_BLUE_DARK},
                    stop:1 {AriaColors.GRADIENT_PINK}
                );
                border-radius: {AriaRadius.LG}px;
                border: 2px solid {AriaColors.WHITE_25};
            }}
            QLabel {{
                background: transparent;
                color: white;
            }}
        """)
        
        # Icon
        icon_label = QLabel(self.icon)
        icon_label.setFont(QFont(AriaTypography.FAMILY, 24))
        layout.addWidget(icon_label)
        
        # Message
        message_label = QLabel(self.message)
        message_label.setFont(QFont(AriaTypography.FAMILY, AriaTypography.BODY))
        message_label.setWordWrap(True)
        layout.addWidget(message_label, stretch=1)
        
    def show_animated(self, duration_ms: int = 3000):
        """Show toast with slide-in animation"""
        self.show()
        
        # Calculate position (top-right of parent)
        if self.parent():
            parent_rect = self.parent().rect()
            start_x = parent_rect.width()
            end_x = parent_rect.width() - self.width() - 20
            y_pos = 20
            
            self.move(start_x, y_pos)
            
            # Slide in animation
            self.slide_in_anim = QPropertyAnimation(self, b"pos")
            self.slide_in_anim.setDuration(300)
            self.slide_in_anim.setStartValue(QPoint(start_x, y_pos))
            self.slide_in_anim.setEndValue(QPoint(end_x, y_pos))
            self.slide_in_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.slide_in_anim.start()
            
            # Auto-hide after duration
            QTimer.singleShot(duration_ms, self.hide_animated)
            
    def hide_animated(self):
        """Hide toast with slide-out animation"""
        if self.parent():
            parent_rect = self.parent().rect()
            current_pos = self.pos()
            end_x = parent_rect.width()
            
            # Slide out animation
            self.slide_out_anim = QPropertyAnimation(self, b"pos")
            self.slide_out_anim.setDuration(300)
            self.slide_out_anim.setStartValue(current_pos)
            self.slide_out_anim.setEndValue(QPoint(end_x, current_pos.y()))
            self.slide_out_anim.setEasingCurve(QEasingCurve.Type.InCubic)
            self.slide_out_anim.finished.connect(self.close)
            self.slide_out_anim.finished.connect(self.closed.emit)
            self.slide_out_anim.start()


class CelebrationOverlay(QWidget):
    """Full-screen celebration overlay for major achievements"""
    
    dismissed = pyqtSignal()
    
    def __init__(self, achievement_data: dict, parent=None):
        super().__init__(parent)
        self.achievement_data = achievement_data
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.init_ui()
        
        # Confetti widget
        self.confetti = ConfettiWidget(self)
        self.confetti.setGeometry(self.rect())
        
    def init_ui(self):
        """Initialize celebration overlay UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL, AriaSpacing.XXL)
        
        # Semi-transparent background
        self.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(10, 13, 30, 0.85);
            }}
        """)
        
        # Achievement card
        card = QWidget()
        card.setMaximumWidth(500)
        card.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {AriaColors.GRADIENT_BLUE_DARK},
                    stop:1 {AriaColors.GRADIENT_PINK}
                );
                border-radius: {AriaRadius.XL}px;
                border: 3px solid {AriaColors.WHITE_25};
                padding: {AriaSpacing.XXL}px;
            }}
            QLabel {{
                background: transparent;
                color: white;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(AriaSpacing.LG)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Achievement unlocked text
        unlocked_label = QLabel("🎉 ACHIEVEMENT UNLOCKED! 🎉")
        unlocked_label.setFont(QFont(AriaTypography.FAMILY, AriaTypography.HEADING, QFont.Weight.Bold))
        unlocked_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(unlocked_label)
        
        # Achievement icon/rarity
        rarity = self.achievement_data.get('rarity', 'common')
        rarity_icons = {
            'common': '🥉',
            'uncommon': '🥈', 
            'rare': '🥇',
            'epic': '💜',
            'legendary': '💎'
        }
        icon_label = QLabel(rarity_icons.get(rarity, '⭐'))
        icon_label.setFont(QFont(AriaTypography.FAMILY, 72))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(icon_label)
        
        # Achievement name
        name_label = QLabel(self.achievement_data.get('name', 'Achievement'))
        name_label.setFont(QFont(AriaTypography.FAMILY, AriaTypography.TITLE, QFont.Weight.Bold))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        card_layout.addWidget(name_label)
        
        # Achievement description
        desc_label = QLabel(self.achievement_data.get('description', ''))
        desc_label.setFont(QFont(AriaTypography.FAMILY, AriaTypography.BODY))
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"color: {AriaColors.WHITE_85};")
        card_layout.addWidget(desc_label)
        
        # Dismiss hint
        hint_label = QLabel("Click anywhere to continue")
        hint_label.setFont(QFont(AriaTypography.FAMILY, AriaTypography.BODY_SMALL))
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setStyleSheet(f"color: {AriaColors.WHITE_65};")
        card_layout.addWidget(hint_label)
        
        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        
    def show_celebration(self):
        """Show celebration with animations"""
        self.show()
        self.raise_()
        
        # Start confetti
        self.confetti.start_celebration(duration_ms=4000)
        
        # Pulse animation for the widget
        self.setGraphicsEffect(None)  # Clear any existing effects
        
    def mousePressEvent(self, event):
        """Dismiss on click"""
        self.confetti.stop_celebration()
        self.hide()
        self.dismissed.emit()
        
    def resizeEvent(self, event):
        """Resize confetti widget with parent"""
        super().resizeEvent(event)
        if hasattr(self, 'confetti'):
            self.confetti.setGeometry(self.rect())


class CelebrationManager:
    """Manages celebration animations and displays"""
    
    def __init__(self, parent_widget: QWidget):
        self.parent = parent_widget
        self.active_toasts: List[CelebrationToast] = []
        self.overlay: Optional[CelebrationOverlay] = None
        
    def show_toast(self, message: str, icon: str = "🎉", duration_ms: int = 3000):
        """Show a toast notification"""
        toast = CelebrationToast(message, icon, self.parent)
        toast.setMinimumWidth(300)
        toast.adjustSize()
        
        # Stack toasts vertically
        y_offset = 20 + len(self.active_toasts) * (toast.height() + 10)
        
        toast.closed.connect(lambda: self._remove_toast(toast))
        self.active_toasts.append(toast)
        
        toast.show_animated(duration_ms)
        
    def show_achievement_celebration(self, achievement_data: dict):
        """Show full-screen achievement celebration"""
        if self.overlay:
            self.overlay.close()
            
        self.overlay = CelebrationOverlay(achievement_data, self.parent)
        self.overlay.setGeometry(self.parent.rect())
        self.overlay.dismissed.connect(self._clear_overlay)
        self.overlay.show_celebration()
        
    def show_milestone_celebration(self, milestone_name: str, message: str):
        """Show celebration for milestones"""
        # For milestones, show a prominent toast
        self.show_toast(f"{milestone_name}\n{message}", "🌟", duration_ms=4000)
        
    def _remove_toast(self, toast: CelebrationToast):
        """Remove toast from active list"""
        if toast in self.active_toasts:
            self.active_toasts.remove(toast)
            
    def _clear_overlay(self):
        """Clear celebration overlay"""
        self.overlay = None
        
    def clear_all(self):
        """Clear all active celebrations"""
        for toast in self.active_toasts[:]:
            toast.close()
        self.active_toasts.clear()
        
        if self.overlay:
            self.overlay.close()
            self.overlay = None
