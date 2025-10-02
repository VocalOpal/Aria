"""
Aria Voice Studio - Public Beta (v5) - Components Module
Reusable UI components for the application
"""

from .celebration import (
    CelebrationManager,
    CelebrationToast,
    CelebrationOverlay,
    ConfettiWidget
)

from .session_summary import SessionSummaryDialog

from .shortcuts_help import (
    ShortcutsDialog,
    get_modifier_key,
    get_modifier_qt
)

from .pitch_heatmap import PitchHeatMapWidget

from .breathing_guide import (
    BreathingGuideWidget,
    BreathingCircle
)

from .profile_switcher import (
    ProfileDropdown,
    ProfileSelectorDialog,
    CreateProfileDialog
)

from .streak_calendar import (
    StreakCalendar,
    StreakBadge
)

from .spectrogram_widget import (
    SpectrogramWidget,
    CompactSpectrogramWidget
)

__all__ = [
    'CelebrationManager',
    'CelebrationToast',
    'CelebrationOverlay',
    'ConfettiWidget',
    'SessionSummaryDialog',
    'ShortcutsDialog',
    'get_modifier_key',
    'get_modifier_qt',
    'PitchHeatMapWidget',
    'BreathingGuideWidget',
    'BreathingCircle',
    'ProfileDropdown',
    'ProfileSelectorDialog',
    'CreateProfileDialog',
    'StreakCalendar',
    'StreakBadge',
    'SpectrogramWidget',
    'CompactSpectrogramWidget'
]
