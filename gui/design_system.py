def safe_apply_stylesheet(widget, stylesheet):
    """Safely apply stylesheet to widget if it still exists

    This helper function prevents crashes when applying styles to widgets
    that may have been deleted during navigation or cleanup.
    """
    try:
        # Check if widget exists and is valid
        if widget is None:
            return False

        # Try to access a basic property to check if widget is still alive
        if hasattr(widget, 'setStyleSheet') and hasattr(widget, 'isVisible'):
            # Only apply if widget is visible (to avoid styling hidden/deleted widgets)
            if widget.isVisible():
                widget.setStyleSheet(stylesheet)
            return True
        return False
    except (RuntimeError, AttributeError):
        # Widget has been deleted or is no longer valid
        return False

class AriaDesignSystem:
    """Centralized design system for consistent UI styling"""

    # Color Palette - Modern Dark Theme
    COLORS = {
        # Primary colors
        'primary': '#6366f1',        # Indigo - main brand color
        'primary_hover': '#4f46e5',  # Darker indigo for hover states
        'primary_light': '#818cf8',  # Lighter indigo for accents

        # Background colors
        'bg_primary': '#0f0f23',     # Deep dark blue - main background
        'bg_secondary': '#1a1a2e',   # Slightly lighter - cards/panels
        'bg_tertiary': '#16213e',    # Medium - input fields/sections
        'bg_accent': '#162447',      # Lighter - hover states

        # Text colors
        'text_primary': '#f8fafc',   # Almost white - primary text
        'text_secondary': '#cbd5e1',  # Light gray - secondary text
        'text_muted': '#94a3b8',     # Muted gray - captions/hints
        'text_accent': '#818cf8',    # Indigo - links/accents

        # Semantic colors
        'success': '#10b981',        # Green - success states
        'success_hover': '#059669',  # Darker green for hover states
        'success_bg': '#064e3b',     # Dark green background
        'warning': '#f59e0b',        # Amber - warning states
        'warning_hover': '#d97706',  # Darker amber for hover states
        'warning_bg': '#451a03',     # Dark amber background
        'error': '#ef4444',          # Red - error states
        'error_hover': '#dc2626',    # Darker red for hover states
        'error_bg': '#450a0a',       # Dark red background
        'info': '#3b82f6',           # Blue - info states
        'info_hover': '#2563eb',     # Darker blue for hover states
        'info_bg': '#172554',        # Dark blue background

        # Border colors
        'border_subtle': '#334155',   # Subtle borders
        'border_normal': '#475569',   # Normal borders
        'border_strong': '#64748b',   # Strong borders
        'border_accent': '#6366f1',   # Accent borders

        # Component specific
        'pitch_good': '#10b981',      # Green for in-range pitch
        'pitch_warning': '#f59e0b',   # Amber for close to range
        'pitch_error': '#ef4444',     # Red for out of range
        'resonance_color': '#a855f7', # Purple for resonance
    }

    # Typography Scale
    FONTS = {
        'family_primary': '"Segoe UI", -apple-system, BlinkMacSystemFont, "Roboto", sans-serif',
        'family_mono': '"SF Mono", "Monaco", "Consolas", monospace',

        # Font sizes (in pt for PyQt6)
        'xs': 10,   # Small captions
        'sm': 11,   # Body text, buttons
        'md': 12,   # Default body
        'lg': 14,   # Subheadings
        'xl': 16,   # Headings
        'xxl': 20,  # Large headings
        'xxxl': 24, # Page titles
    }

    # Spacing Scale (8px grid system)
    SPACING = {
        'xs': '4px',    # 0.5 units
        'sm': '8px',    # 1 unit
        'md': '16px',   # 2 units
        'lg': '24px',   # 3 units
        'xl': '32px',   # 4 units
        'xxl': '48px',  # 6 units
        'xxxl': '64px', # 8 units
    }

    # Border Radius
    RADIUS = {
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
        'full': '9999px',
    }

    # Shadows
    SHADOWS = {
        'sm': '0 1px 2px rgba(0, 0, 0, 0.3)',
        'md': '0 4px 6px rgba(0, 0, 0, 0.3)',
        'lg': '0 10px 15px rgba(0, 0, 0, 0.4)',
        'inner': 'inset 0 2px 4px rgba(0, 0, 0, 0.3)',
    }

    @classmethod
    def get_base_stylesheet(cls):
        """Get the base application stylesheet"""
        return f"""
        /* Base Application Styles */
        QMainWindow {{
            background-color: {cls.COLORS['bg_primary']};
            color: {cls.COLORS['text_primary']};
        }}

        QWidget {{
            background-color: {cls.COLORS['bg_primary']};
            color: {cls.COLORS['text_primary']};
            font-family: {cls.FONTS['family_primary']};
            font-size: {cls.FONTS['md']}pt;
        }}

        /* Scrollbars */
        QScrollBar:vertical {{
            background-color: {cls.COLORS['bg_secondary']};
            border: none;
            width: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {cls.COLORS['border_normal']};
            min-height: 20px;
            border-radius: 6px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {cls.COLORS['border_strong']};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}

        /* Selection Colors */
        QWidget::selection {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['text_primary']};
        }}
        """

    @classmethod
    def get_button_styles(cls):
        """Get consistent button styling"""
        return f"""
        /* Primary Button */
        QPushButton {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['text_primary']};
            border: none;
            border-radius: {cls.RADIUS['md']};
            padding: {cls.SPACING['sm']} {cls.SPACING['md']};
            font-size: {cls.FONTS['sm']}pt;
            font-weight: 500;
            min-height: 32px;
        }}

        QPushButton:hover {{
            background-color: {cls.COLORS['primary_hover']};
        }}

        QPushButton:pressed {{
            background-color: {cls.COLORS['primary_hover']};
        }}

        QPushButton:disabled {{
            background-color: {cls.COLORS['bg_tertiary']};
            color: {cls.COLORS['text_muted']};
        }}

        /* Secondary Button */
        QPushButton[style="secondary"] {{
            background-color: {cls.COLORS['bg_secondary']};
            border: 1px solid {cls.COLORS['border_normal']};
            color: {cls.COLORS['text_primary']};
        }}

        QPushButton[style="secondary"]:hover {{
            background-color: {cls.COLORS['bg_tertiary']};
            border-color: {cls.COLORS['border_strong']};
        }}

        /* Success Button */
        QPushButton[style="success"] {{
            background-color: {cls.COLORS['success']};
            color: {cls.COLORS['text_primary']};
        }}

        QPushButton[style="success"]:hover {{
            background-color: {cls.COLORS['success_hover']};
        }}

        /* Warning Button */
        QPushButton[style="warning"] {{
            background-color: {cls.COLORS['warning']};
            color: {cls.COLORS['text_primary']};
        }}

        QPushButton[style="warning"]:hover {{
            background-color: {cls.COLORS['warning_hover']};
        }}

        /* Danger Button */
        QPushButton[style="danger"] {{
            background-color: {cls.COLORS['error']};
            color: {cls.COLORS['text_primary']};
        }}

        QPushButton[style="danger"]:hover {{
            background-color: {cls.COLORS['error_hover']};
        }}
        """

    @classmethod
    def get_input_styles(cls):
        """Get input field styling"""
        return f"""
        /* Input Fields */
        QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {{
            background-color: {cls.COLORS['bg_tertiary']};
            border: 1px solid {cls.COLORS['border_subtle']};
            border-radius: {cls.RADIUS['md']};
            padding: {cls.SPACING['sm']};
            color: {cls.COLORS['text_primary']};
            font-size: {cls.FONTS['sm']}pt;
            min-height: 24px;
        }}

        QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {cls.COLORS['primary']};
            outline: none;
        }}

        QLineEdit:disabled, QTextEdit:disabled {{
            background-color: {cls.COLORS['bg_secondary']};
            color: {cls.COLORS['text_muted']};
            border-color: {cls.COLORS['border_subtle']};
        }}

        /* Combo Boxes */
        QComboBox {{
            background-color: {cls.COLORS['bg_tertiary']};
            border: 1px solid {cls.COLORS['border_subtle']};
            border-radius: {cls.RADIUS['md']};
            padding: {cls.SPACING['sm']};
            color: {cls.COLORS['text_primary']};
            min-height: 24px;
        }}

        QComboBox:hover {{
            border-color: {cls.COLORS['border_normal']};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}

        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid {cls.COLORS['text_secondary']};
            margin-right: 8px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {cls.COLORS['bg_secondary']};
            border: 1px solid {cls.COLORS['border_normal']};
            border-radius: {cls.RADIUS['md']};
            color: {cls.COLORS['text_primary']};
            selection-background-color: {cls.COLORS['primary']};
        }}
        """

    @classmethod
    def get_card_styles(cls):
        """Get card/panel styling"""
        return f"""
        /* Cards and Panels */
        QFrame[style="card"] {{
            background-color: {cls.COLORS['bg_secondary']};
            border: 1px solid {cls.COLORS['border_subtle']};
            border-radius: {cls.RADIUS['lg']};
            padding: {cls.SPACING['md']};
        }}

        QFrame[style="card_elevated"] {{
            background-color: {cls.COLORS['bg_secondary']};
            border: 1px solid {cls.COLORS['border_subtle']};
            border-radius: {cls.RADIUS['lg']};
            padding: {cls.SPACING['md']};
        }}

        /* Headers */
        QLabel[style="heading"] {{
            font-size: {cls.FONTS['xl']}pt;
            font-weight: 600;
            color: {cls.COLORS['text_primary']};
            margin-bottom: {cls.SPACING['sm']};
        }}

        QLabel[style="subheading"] {{
            font-size: {cls.FONTS['lg']}pt;
            font-weight: 500;
            color: {cls.COLORS['text_secondary']};
            margin-bottom: {cls.SPACING['xs']};
        }}

        QLabel[style="caption"] {{
            font-size: {cls.FONTS['xs']}pt;
            color: {cls.COLORS['text_muted']};
        }}

        /* Success/Error States */
        QLabel[style="success"] {{
            color: {cls.COLORS['success']};
            font-weight: 500;
        }}

        QLabel[style="warning"] {{
            color: {cls.COLORS['warning']};
            font-weight: 500;
        }}

        QLabel[style="error"] {{
            color: {cls.COLORS['error']};
            font-weight: 500;
        }}
        """

    @classmethod
    def get_complete_stylesheet(cls):
        """Get the complete application stylesheet"""
        return (
            cls.get_base_stylesheet() + "\n" +
            cls.get_button_styles() + "\n" +
            cls.get_input_styles() + "\n" +
            cls.get_card_styles()
        )