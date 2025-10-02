"""
Aria Voice Studio - Public Beta (v5) - Screens Module
All application screens with consistent design language
"""

from .training import TrainingScreen
from .onboarding import OnboardingScreen
from .settings import SettingsScreen
from .exercises import ExercisesScreen
from .audio_analysis import AudioAnalysisScreen
from .progress import ProgressScreen

__all__ = [
    'TrainingScreen',
    'OnboardingScreen',
    'SettingsScreen',
    'ExercisesScreen',
    'AudioAnalysisScreen',
    'ProgressScreen'
]
