"""
Aria Voice Studio v4.2 - Modern Design System
Gradient-driven aesthetic with consistent visual language across all screens
Based on app.py mock UI design
"""

from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGraphicsDropShadowEffect, QSizePolicy, QComboBox, QSpinBox,
    QDoubleSpinBox, QCheckBox, QScrollArea, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QLinearGradient, QBrush, QPainterPath,
    QFont
)
import math


class AriaColors:
    """Centralized color palette - gradient-driven aesthetic"""

    # Primary Gradients (Blue → Pink diagonal)
    GRADIENT_BLUE = "#6FA2C8"
    GRADIENT_PINK = "#E897BD"
    GRADIENT_BLUE_DARK = "#5593B8"
    
    # Aliases for template buttons
    PRIMARY = "#6FA2C8"  # Alias for GRADIENT_BLUE
    PINK = "#E897BD"      # Alias for GRADIENT_PINK

    # Sidebar Colors
    SIDEBAR_DARK = "#3A4A5C"
    SIDEBAR_MEDIUM = "#49596A"
    SIDEBAR_HOVER = "rgba(82, 98, 116, 0.5)"
    SIDEBAR_ACTIVE = "rgba(95, 147, 176, 0.7)"

    # Accent Colors
    TEAL = "#44C5E6"          # Active/interactive states
    TEAL_HOVER = "#4DD4F5"
    TEAL_PRESSED = "#38B5D8"

    GREEN = "#52C55A"         # Safe/success indicators
    YELLOW = "#FFA500"        # Warning/caution indicators
    ORANGE = "#FF8C42"        # Alert states
    RED = "#F14C4C"           # Warnings/record
    RED_HOVER = "#FF6B6B"

    # Typography
    WHITE = "#FFFFFF"
    WHITE_100 = "rgba(255, 255, 255, 1.0)"     # Primary text
    WHITE_95 = "rgba(255, 255, 255, 0.95)"     # Strong text
    WHITE_90 = "rgba(255, 255, 255, 0.90)"     # Body text
    WHITE_85 = "rgba(255, 255, 255, 0.85)"     # Key labels
    WHITE_70 = "rgba(255, 255, 255, 0.7)"      # Secondary text
    WHITE_45 = "rgba(255, 255, 255, 0.45)"     # Subtle elements
    WHITE_35 = "rgba(255, 255, 255, 0.35)"     # Hover states
    WHITE_25 = "rgba(255, 255, 255, 0.25)"     # Borders
    WHITE_15 = "rgba(255, 255, 255, 0.15)"     # Very subtle backgrounds

    # Card backgrounds
    CARD_BG = "rgba(111, 162, 200, 0.35)"        # Standard card (blue side)
    CARD_BG_LIGHT = "rgba(111, 162, 200, 0.4)"   # Elevated card (blue side)
    CARD_BG_PINK = "rgba(232, 151, 189, 0.35)"   # Card gradient (pink side)
    CARD_BG_PINK_LIGHT = "rgba(232, 151, 189, 0.4)" # Elevated card gradient (pink side)

    # Special
    PITCH_INDICATOR = "#44C5E6"
    LABEL_BG = "#36454F"


class AriaTypography:
    """Typography system with hierarchy - comfortable and readable"""

    FAMILY = "Arial"

    # Font sizes - increased for better readability
    LOGO = 45
    TITLE = 26
    HEADING = 18
    SUBHEADING = 16       # Increased from 15
    BODY = 15            # Increased from 14
    BODY_SMALL = 14      # Increased from 13
    CAPTION = 13         # Increased from 11
    TINY = 11            # Increased from 10

    # Weights
    LIGHT = QFont.Weight.Light
    NORMAL = QFont.Weight.Normal
    MEDIUM = QFont.Weight.Medium
    SEMIBOLD = 600
    BOLD = QFont.Weight.Bold


class AriaSpacing:
    """8px grid spacing system"""

    XS = 6
    SM = 12
    MD = 16
    LG = 24
    XL = 32
    XXL = 40
    XXXL = 48
    GIANT = 56


class AriaRadius:
    """Border radius values"""

    SM = 6
    MD = 13
    LG = 18
    XL = 26
    FULL = 9999


class CircularProgress(QWidget):
    """Circular progress indicator with smooth animation"""

    def __init__(self, percentage=0, size=120):
        super().__init__()
        self.setFixedSize(size, size)
        self._percentage = percentage
        self._animated_percentage = percentage
        self.animation = None

    def set_percentage(self, value, animated=True):
        """Set percentage with optional animation"""
        if animated and self._percentage != value:
            # Create smooth animation
            if self.animation:
                self.animation.stop()

            self.animation = QPropertyAnimation(self, b"animated_percentage")
            self.animation.setDuration(500)
            self.animation.setStartValue(self._animated_percentage)
            self.animation.setEndValue(value)
            self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.animation.start()
        else:
            self._animated_percentage = value
            self.update()

        self._percentage = value

    @pyqtProperty(float)
    def animated_percentage(self):
        return self._animated_percentage

    @animated_percentage.setter
    def animated_percentage(self, value):
        self._animated_percentage = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = self.width() // 2
        radius = center - 10
        pen_width = 7

        # Background circle
        painter.setPen(QPen(QColor(255, 255, 255, 45), pen_width))
        painter.drawEllipse(center - radius, center - radius, radius * 2, radius * 2)

        # Progress arc
        painter.setPen(QPen(QColor("#FFFFFF"), pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        span_angle = int(self._animated_percentage * 360 / 100)
        painter.drawArc(
            center - radius, center - radius, radius * 2, radius * 2,
            90 * 16, -span_angle * 16
        )

        # Center text
        font = QFont(AriaTypography.FAMILY, 26, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{int(self._animated_percentage)}%")


class CircularVisualizer(QWidget):
    """Circular gradient visualizer with animated waveform for pitch display"""

    def __init__(self):
        super().__init__()
        self.pitch = 165
        self.phase = 0
        self.is_animating = False

        # Set size policy for responsive layout
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)

    def sizeHint(self):
        """Suggest square aspect ratio"""
        size = min(self.width() if self.width() > 0 else 580,
                   self.height() if self.height() > 0 else 580)
        return QSize(size, size)

    def heightForWidth(self, width):
        """Maintain 1:1 aspect ratio"""
        return width

    def start_animation(self):
        """Start visualizer animation"""
        self.is_animating = True
        self.timer.start(16)  # 60fps

    def stop_animation(self):
        """Stop visualizer animation"""
        self.is_animating = False
        self.timer.stop()

    def set_pitch(self, pitch_value):
        """Update pitch value from external source"""
        self.pitch = pitch_value
        if not self.is_animating:
            self.update()

    def animate(self):
        """Animation step"""
        self.phase += 0.1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate dynamic size with proper padding
        side = min(self.width(), self.height())
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = int((side * 0.40))

        if radius < 100:
            radius = 100

        # Gradient fill (blue to pink diagonal)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(AriaColors.GRADIENT_BLUE))
        gradient.setColorAt(1, QColor(AriaColors.GRADIENT_PINK))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(center_x - radius), int(center_y - radius), int(radius * 2), int(radius * 2))

        # White border
        painter.setPen(QPen(QColor("#FFFFFF"), 4))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(int(center_x - radius), int(center_y - radius), int(radius * 2), int(radius * 2))

        # Waveform
        painter.setPen(QPen(QColor("#FFFFFF"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        path = QPainterPath()

        wave_length_factor = 0.7
        wave_amplitude_factor = 0.1

        wave_start_x = center_x - (radius * wave_length_factor)
        wave_end_x = center_x + (radius * wave_length_factor)

        num_points = 250
        for i in range(num_points):
            x = wave_start_x + (wave_end_x - wave_start_x) * i / num_points
            y = center_y + (radius * wave_amplitude_factor) * math.sin(i * 0.08 + self.phase)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        painter.drawPath(path)

        # Pitch indicator line
        painter.setPen(QPen(QColor(AriaColors.PITCH_INDICATOR), 2))
        painter.drawLine(int(wave_start_x), int(center_y), int(wave_end_x), int(center_y))

        # Pitch label with rounded background
        label_width = radius * 0.3
        label_height = radius * 0.12
        label_x = center_x - label_width // 2
        label_y = center_y - label_height // 2

        # Rounded rectangle background
        painter.setBrush(QColor(AriaColors.LABEL_BG))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(int(label_x), int(label_y), int(label_width), int(label_height), 6, 6)

        # Pitch text
        painter.setPen(QColor("#FFFFFF"))
        font_size = max(10, int(radius * 0.05))
        font = QFont(AriaTypography.FAMILY, font_size, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(int(label_x), int(label_y), int(label_width), int(label_height),
                        Qt.AlignmentFlag.AlignCenter, f"{int(self.pitch)} Hz")


class InfoCard(QFrame):
    """Reusable info card with gradient background and shadow"""

    def __init__(self, title="", min_height=200):
        super().__init__()
        self.setMinimumHeight(min_height)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {AriaColors.CARD_BG},
                    stop:1 {AriaColors.CARD_BG_PINK}
                );
                border-radius: 20px;
                border: none;
            }}
        """)

        # Enhanced shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)

        # Layout with more breathing room
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Title
        if title:
            self.title_label = QLabel(title)
            self.title_label.setStyleSheet(f"""
                color: {AriaColors.WHITE_100};
                font-size: {AriaTypography.HEADING}px;
                font-weight: 700;
                background: transparent;
            """)
            layout.addWidget(self.title_label)

        # Content layout for dynamic content
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(AriaSpacing.SM)
        layout.addLayout(self.content_layout)
        layout.addStretch()


class PrimaryButton(QPushButton):
    """Primary action button with teal accent"""

    def __init__(self, text="", icon=None):
        super().__init__(text)
        self.setMinimumSize(220, 60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {AriaColors.TEAL};
                color: white;
                border: none;
                border-radius: {AriaRadius.MD}px;
                font-size: 16px;
                font-weight: 600;
                padding: 12px 24px;
            }}
            QPushButton:hover {{
                background-color: {AriaColors.TEAL_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {AriaColors.TEAL_PRESSED};
            }}
            QPushButton:disabled {{
                background-color: {AriaColors.WHITE_45};
                color: {AriaColors.WHITE_70};
            }}
        """)


class SecondaryButton(QPushButton):
    """Secondary button with subtle styling"""

    def __init__(self, text=""):
        super().__init__(text)
        self.setMinimumHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {AriaColors.WHITE_100};
                border: 2px solid {AriaColors.WHITE_45};
                border-radius: {AriaRadius.MD}px;
                font-size: 15px;
                font-weight: 500;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: {AriaColors.WHITE_25};
                border-color: {AriaColors.WHITE_70};
            }}
            QPushButton:pressed {{
                background-color: {AriaColors.WHITE_45};
            }}
        """)


class RecordButton(QPushButton):
    """Circular record/stop button with red accent"""

    def __init__(self):
        super().__init__()
        self.setFixedSize(56, 56)
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 3px solid {AriaColors.RED};
                border-radius: 28px;
            }}
            QPushButton:hover {{
                background-color: rgba(241, 76, 76, 0.15);
                border: 3px solid {AriaColors.RED_HOVER};
            }}
            QPushButton:pressed {{
                background-color: rgba(241, 76, 76, 0.25);
            }}
        """)


class NavButton(QFrame):
    """Navigation button for sidebar"""

    def __init__(self, icon, text, active=False):
        super().__init__()
        self.active = active
        self.icon = icon
        self.text = text
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Cleaner, more spacious layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 18, 32, 18)
        layout.setSpacing(16)

        # Icon - slightly smaller, cleaner
        self.icon_label = QLabel(icon)
        self.icon_label.setStyleSheet("color: white; font-size: 20px; background: transparent;")
        self.icon_label.setFixedWidth(24)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Text - bolder, more impactful
        self.text_label = QLabel(text)
        self.text_label.setStyleSheet("""
            color: white; 
            font-size: 15px; 
            background: transparent; 
            font-weight: 600;
        """)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        layout.addStretch()

        # Apply initial styling
        self.update_style()

    def set_active(self, active):
        """Update active state"""
        self.active = active
        self.update_style()

    def update_style(self):
        """Update button styling based on active state"""
        if self.active:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(68, 197, 230, 0.2);
                    border: none;
                    border-radius: 0px;
                }}
                QFrame:hover {{
                    background-color: rgba(68, 197, 230, 0.28);
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background: transparent;
                    border: none;
                    border-radius: 0px;
                }}
                QFrame:hover {{
                    background-color: rgba(255, 255, 255, 0.08);
                }}
            """)

    def mousePressEvent(self, event):
        """Handle click"""
        if hasattr(self, 'clicked'):
            self.clicked.emit()
        super().mousePressEvent(event)


def create_gradient_background():
    """Create standard gradient background stylesheet"""
    return f"""
        QFrame {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 {AriaColors.GRADIENT_BLUE_DARK},
                stop:1 {AriaColors.GRADIENT_PINK}
            );
        }}
    """


def create_sidebar():
    """Create standard sidebar layout"""
    sidebar = QFrame()
    sidebar.setFixedWidth(300)
    sidebar.setStyleSheet(f"""
        QFrame {{
            background-color: {AriaColors.SIDEBAR_DARK};
            border: none;
        }}
    """)

    layout = QVBoxLayout(sidebar)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)

    # Header - with logo and text in clean vertical layout
    header = QFrame()
    header.setStyleSheet("background: transparent; border: none;")
    header_layout = QVBoxLayout(header)
    header_layout.setContentsMargins(0, 24, 0, 24)
    header_layout.setSpacing(12)
    header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # Load actual icon image
    import os
    from PyQt6.QtGui import QPixmap
    icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "edited-photo.png")
    
    # Logo - centered
    logo = QLabel()
    logo.setCursor(Qt.CursorShape.PointingHandCursor)
    logo.setObjectName("aria_logo")
    logo.setScaledContents(False)
    
    if os.path.exists(icon_path):
        pixmap = QPixmap(icon_path)
        # Scale to 80x80 while maintaining quality
        scaled_pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo.setPixmap(scaled_pixmap)
    else:
        # Fallback to music note if icon not found
        logo.setText("♫")
        logo.setStyleSheet("""
            QLabel {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6FA2C8,
                    stop:1 #E897BD
                );
                color: white;
                font-size: 48px;
                border-radius: 40px;
                font-weight: bold;
            }
        """)
    
    logo.setFixedSize(80, 80)
    logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    # Store logo reference for parent to connect click event
    sidebar.aria_logo = logo
    header_layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)
    
    # App title - centered below logo (hidden by default, shown when fullscreen)
    title = QLabel("Aria Voice Studio")
    title.setObjectName("sidebar_title")
    title.setStyleSheet("""
        color: white; 
        font-size: 20px; 
        font-weight: 700; 
        background: transparent;
        letter-spacing: -0.3px;
    """)
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setWordWrap(False)
    title.setVisible(False)  # Hidden by default
    sidebar.sidebar_title = title
    header_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

    # Version - centered below title (hidden by default, shown when fullscreen)
    version = QLabel("Public Beta (v5)")
    version.setObjectName("sidebar_version")
    version.setStyleSheet("""
        color: rgba(255, 255, 255, 0.5); 
        font-size: 11px; 
        font-weight: 500;
        background: transparent;
    """)
    version.setAlignment(Qt.AlignmentFlag.AlignCenter)
    version.setVisible(False)  # Hidden by default
    sidebar.sidebar_version = version
    header_layout.addWidget(version, alignment=Qt.AlignmentFlag.AlignCenter)
    
    layout.addWidget(header)

    return sidebar, layout


def add_card_shadow(widget):
    """Add standard shadow to a card widget"""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(22)
    shadow.setOffset(0, 5)
    shadow.setColor(QColor(0, 0, 0, 50))
    widget.setGraphicsEffect(shadow)


# ============================================================================
# STYLED FORM COMPONENTS
# ============================================================================

class StyledLabel(QLabel):
    """Label with consistent styling"""

    def __init__(self, text="", style="body"):
        super().__init__(text)
        self.apply_style(style)

    def apply_style(self, style):
        """Apply predefined style"""
        styles = {
            "body": f"color: {AriaColors.WHITE_90}; font-size: {AriaTypography.BODY}px; font-weight: 500; background: transparent;",
            "heading": f"color: white; font-size: {AriaTypography.HEADING}px; font-weight: 600; background: transparent;",
            "caption": f"color: {AriaColors.WHITE_85}; font-size: {AriaTypography.CAPTION}px; font-weight: 500; background: transparent;",
        }
        self.setStyleSheet(styles.get(style, styles["body"]))


class StyledComboBox(QComboBox):
    """ComboBox with consistent styling"""

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"""
            QComboBox {{
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid {AriaColors.WHITE_25};
                border-radius: {AriaRadius.MD}px;
                padding: {AriaSpacing.SM}px;
                color: white;
                font-size: {AriaTypography.BODY}px;
                min-height: 32px;
            }}
            QComboBox:hover {{
                border: 1px solid {AriaColors.WHITE_45};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {AriaColors.SIDEBAR_MEDIUM};
                border: 1px solid {AriaColors.WHITE_25};
                color: white;
                selection-background-color: {AriaColors.TEAL};
                padding: 4px;
            }}
        """)


class StyledSpinBox(QSpinBox):
    """SpinBox with consistent styling"""

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"""
            QSpinBox {{
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid {AriaColors.WHITE_25};
                border-radius: {AriaRadius.MD}px;
                padding: {AriaSpacing.SM}px;
                color: white;
                font-size: {AriaTypography.BODY}px;
                min-height: 32px;
            }}
            QSpinBox:hover {{
                border: 1px solid {AriaColors.WHITE_45};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background: transparent;
                border: none;
                width: 16px;
            }}
        """)

    def wheelEvent(self, event):
        """Ignore scroll wheel to prevent accidental changes while scrolling."""
        event.ignore()


class StyledDoubleSpinBox(QDoubleSpinBox):
    """DoubleSpinBox with consistent styling"""

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid {AriaColors.WHITE_25};
                border-radius: {AriaRadius.MD}px;
                padding: {AriaSpacing.SM}px;
                color: white;
                font-size: {AriaTypography.BODY}px;
                min-height: 32px;
            }}
            QDoubleSpinBox:hover {{
                border: 1px solid {AriaColors.WHITE_45};
            }}
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
                background: transparent;
                border: none;
                width: 16px;
            }}
        """)

    def wheelEvent(self, event):
        """Ignore scroll wheel to prevent accidental changes while scrolling."""
        event.ignore()


class StyledCheckBox(QCheckBox):
    """CheckBox with consistent styling"""

    def __init__(self, text=""):
        super().__init__(text)
        self.setStyleSheet(f"""
            QCheckBox {{
                color: white;
                font-size: {AriaTypography.BODY}px;
                background: transparent;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {AriaColors.WHITE_45};
                border-radius: 4px;
                background-color: transparent;
            }}
            QCheckBox::indicator:hover {{
                border-color: {AriaColors.TEAL};
            }}
            QCheckBox::indicator:checked {{
                background-color: {AriaColors.TEAL};
                border-color: {AriaColors.TEAL};
            }}
        """)


# ============================================================================
# TYPOGRAPHY LABELS (Pre-styled for consistency)
# ============================================================================

class TitleLabel(QLabel):
    """Large title label for screen headers.

    Pre-styled with white color, TITLE font size (26px), and bold weight.
    Used for main screen titles to ensure consistency across all screens.

    Args:
        text (str): The title text to display
    """

    def __init__(self, text=""):
        super().__init__(text)
        self.setStyleSheet(f"""
            color: {AriaColors.WHITE_100};
            font-size: {AriaTypography.TITLE}px;
            font-weight: 800;
            background: transparent;
            letter-spacing: -0.3px;
        """)


class HeadingLabel(QLabel):
    """Section heading label for subsections.

    Pre-styled with white color, HEADING font size (18px), and semibold weight.
    Automatically enables word wrapping for long text.

    Args:
        text (str): The heading text to display
    """

    def __init__(self, text=""):
        super().__init__(text)
        self.setStyleSheet(f"""
            color: {AriaColors.WHITE_100};
            font-size: {AriaTypography.HEADING}px;
            font-weight: 700;
            background: transparent;
        """)
        self.setWordWrap(True)


class BodyLabel(QLabel):
    """Standard body text label for general content.

    Pre-styled with WHITE_95 color and BODY font size (14px).
    Automatically enables word wrapping.

    Args:
        text (str): The body text to display
    """

    def __init__(self, text=""):
        super().__init__(text)
        self.setStyleSheet(f"""
            color: {AriaColors.WHITE_95};
            font-size: {AriaTypography.BODY}px;
            background: transparent;
        """)
        self.setWordWrap(True)


class CaptionLabel(QLabel):
    """Small caption/description label for secondary information.

    Pre-styled with WHITE_85 color (increased from 70), CAPTION font size, and medium weight.
    Ideal for hints, descriptions, and supplementary text.

    Args:
        text (str): The caption text to display
    """

    def __init__(self, text=""):
        super().__init__(text)
        self.setStyleSheet(f"""
            color: {AriaColors.WHITE_85};
            font-size: {AriaTypography.CAPTION}px;
            font-weight: 500;
            background: transparent;
        """)
        self.setWordWrap(True)


# ============================================================================
# STAT & METRIC COMPONENTS
# ============================================================================

class StatCard(InfoCard):
    """Card displaying a large statistic value with description.

    Extends InfoCard to provide a centered vertical layout with a large
    value display and descriptive text. Commonly used for dashboard stats
    like "Total Sessions: 42".

    Args:
        title (str): Card title shown at the top
        value (str): Large value to display (e.g., "42", "15h 30m")
        description (str): Description text below the value
        min_height (int): Minimum card height in pixels (default: 200)
        value_size (int): Font size for the value in pixels (default: 56)

    Example:
        card = StatCard("Total Sessions", "42", "Completed", min_height=200)
        card.set_value("43")  # Update the value dynamically
    """

    def __init__(self, title="", value="", description="", min_height=200, value_size=56):
        super().__init__(title, min_height)

        # Clear existing content_layout stretch
        while self.content_layout.count() > 0:
            item = self.content_layout.takeAt(0)
            if item.spacerItem():
                break

        self.content_layout.addStretch()

        # Large value display
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"""
            color: white;
            font-size: {value_size}px;
            font-weight: bold;
            background: transparent;
            margin: {AriaSpacing.SM}px 0;
        """)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.value_label)

        self.desc_label = QLabel(description)
        self.desc_label.setStyleSheet(f"""
            color: {AriaColors.WHITE_70};
            font-size: {AriaTypography.BODY}px;
            background: transparent;
        """)
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_label.setWordWrap(True)
        self.content_layout.addWidget(self.desc_label)

        self.content_layout.addStretch()

    def set_value(self, value):
        """Update the displayed value"""
        self.value_label.setText(str(value))

    def set_description(self, description):
        """Update the description text"""
        self.desc_label.setText(description)


class MetricRow(QWidget):
    """Horizontal row displaying label: value pair.

    Creates a consistent label-value layout with proper spacing and styling.
    Used for displaying metrics like "Duration: 00:05:30" or "Avg Pitch: 185 Hz".

    Args:
        label_text (str): The label text (e.g., "Duration:")
        value_text (str): The initial value text (e.g., "00:00:00")
        parent (QWidget, optional): Parent widget

    Example:
        metric = MetricRow("Duration:", "00:00:00")
        metric.set_value("00:05:30")  # Update the value
    """

    def __init__(self, label_text="", value_text="", parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(AriaSpacing.SM)

        # Label
        self.label = QLabel(label_text)
        self.label.setStyleSheet(f"""
            color: {AriaColors.WHITE_85};
            font-size: {AriaTypography.BODY_SMALL}px;
            background: transparent;
        """)
        layout.addWidget(self.label)

        # Value
        self.value = QLabel(value_text)
        self.value.setStyleSheet(f"""
            color: white;
            font-weight: 600;
            font-size: {AriaTypography.BODY_SMALL}px;
            background: transparent;
        """)
        layout.addWidget(self.value)

        layout.addStretch()

    def set_value(self, value_text):
        """Update the value display"""
        self.value.setText(str(value_text))


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_screen_title(text):
    """Create a standard screen title label.

    Args:
        text (str): The title text

    Returns:
        TitleLabel: A pre-styled title label
    """
    return TitleLabel(text)


def create_scroll_container():
    """Create a standard scroll area with consistent styling.

    Configures a QScrollArea with transparent background, no border,
    vertical scrolling enabled, and horizontal scrolling disabled.

    Returns:
        QScrollArea: Fully configured scroll container
    """
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    return scroll


def create_styled_progress_bar():
    """Create a standard styled progress bar.

    Applies consistent Aria design system styling with teal accent color,
    rounded corners, and proper contrast.

    Returns:
        QProgressBar: Fully styled progress bar widget
    """
    progress_bar = QProgressBar()
    progress_bar.setStyleSheet(f"""
        QProgressBar {{
            border: 1px solid {AriaColors.WHITE_25};
            border-radius: {AriaRadius.SM}px;
            background-color: rgba(255, 255, 255, 0.1);
            color: white;
            text-align: center;
            height: 24px;
        }}
        QProgressBar::chunk {{
            background-color: {AriaColors.TEAL};
            border-radius: {AriaRadius.SM}px;
        }}
    """)
    return progress_bar


class AchievementWidget(QFrame):
    """Display widget for a single achievement.

    Renders achievement status with rarity indicator, name, description,
    and optional progress bar for nearly-earned achievements.

    Args:
        achievement (dict): Achievement data with keys:
            - name (str): Achievement name
            - description (str): Achievement description
            - earned (bool): Whether achievement is earned
            - rarity (str): Rarity level (common, uncommon, rare, epic, legendary)
            - progress_percent (float): Progress towards achievement (0-100)

    Example:
        achievement_data = {
            'name': 'First Steps',
            'description': 'Complete 5 training sessions',
            'earned': True,
            'rarity': 'common',
            'progress_percent': 100
        }
        widget = AchievementWidget(achievement_data)
    """

    RARITY_COLORS = {
        'common': AriaColors.WHITE_70,
        'uncommon': '#5ECC7F',
        'rare': '#4F9FFF',
        'epic': '#B34FFF',
        'legendary': '#FFD700'
    }

    def __init__(self, achievement):
        super().__init__()
        self.achievement = achievement
        self.init_ui()

    def init_ui(self):
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setStyleSheet(f"""
            QFrame {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: {AriaRadius.SM}px;
                margin: 4px 0;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setSpacing(AriaSpacing.SM)
        layout.setContentsMargins(AriaSpacing.MD, AriaSpacing.SM, AriaSpacing.MD, AriaSpacing.SM)

        rarity_color = self.RARITY_COLORS.get(self.achievement.get('rarity', 'common'), AriaColors.WHITE_70)
        if not self.achievement['earned']:
            rarity_color = AriaColors.WHITE_25

        icon = self.achievement.get('icon', '🏆')
        icon_label = QLabel(icon)
        icon_label.setFixedWidth(24)
        icon_label.setStyleSheet(f"""
            color: {rarity_color if self.achievement['earned'] else AriaColors.WHITE_45};
            font-size: 18px;
            background: transparent;
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        name_label = QLabel(self.achievement['name'])
        name_label.setStyleSheet(f"""
            color: {'white' if self.achievement['earned'] else AriaColors.WHITE_45};
            font-size: {AriaTypography.BODY_SMALL}px;
            font-weight: 600;
            background: transparent;
        """)
        name_label.setWordWrap(True)
        info_layout.addWidget(name_label)

        desc_label = QLabel(self.achievement['description'])
        desc_label.setStyleSheet(f"""
            color: {AriaColors.WHITE_70 if self.achievement['earned'] else AriaColors.WHITE_45};
            font-size: {AriaTypography.CAPTION}px;
            background: transparent;
        """)
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)

        if not self.achievement['earned'] and self.achievement.get('progress_percent', 0) > 0:
            progress_bar = QFrame()
            progress_bar.setFixedHeight(3)
            progress_bar.setStyleSheet(f"""
                QFrame {{
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 2px;
                }}
            """)
            info_layout.addWidget(progress_bar)

            progress_text = QLabel(f"{self.achievement['progress_percent']:.0f}%")
            progress_text.setStyleSheet(f"""
                color: {AriaColors.WHITE_45};
                font-size: {AriaTypography.TINY}px;
                background: transparent;
            """)
            info_layout.addWidget(progress_text)

        layout.addLayout(info_layout, stretch=1)
