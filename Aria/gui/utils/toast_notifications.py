"""
Centralized toast notification utility for consistent UI feedback across the application.
"""

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QTimer
from gui.design_system import AriaColors, AriaTypography, AriaSpacing, AriaRadius


class ToastNotification:
    """Centralized toast notification system to avoid code duplication."""
    
    @staticmethod
    def show_toast(parent, message: str, duration: int = 2000, error: bool = False, icon: str = ""):
        """Show a temporary toast notification.
        
        Args:
            parent: Parent widget to attach the toast to
            message: Message text to display
            duration: Duration in milliseconds (default 2000)
            error: Whether this is an error message (changes color)
            icon: Optional icon to prepend to message
        """
        try:
            # Prepare message with optional icon
            display_message = f"{icon} {message}" if icon else message
            
            # Create toast label
            toast = QLabel(display_message, parent)
            
            # Determine background color
            bg_color = AriaColors.RED if error else AriaColors.GREEN
            
            toast.setStyleSheet(f"""
                QLabel {{
                    background-color: {bg_color};
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.25);
                    border-radius: {AriaRadius.MD}px;
                    padding: {AriaSpacing.MD}px {AriaSpacing.XL}px;
                    font-size: {AriaTypography.BODY}px;
                    font-weight: 600;
                }}
            """)
            toast.setAlignment(Qt.AlignmentFlag.AlignCenter)
            toast.adjustSize()
            
            # Position at bottom center
            x = (parent.width() - toast.width()) // 2
            y = parent.height() - toast.height() - 60
            toast.move(x, y)
            
            toast.show()
            
            # Auto-hide after duration
            QTimer.singleShot(duration, toast.deleteLater)
            
        except Exception:
            # Silently fail for toast notifications - they're not critical
            pass
