"""
Voice Domain Layer
Core voice processing, analysis, and training functionality
"""

from .trainer import VoiceTrainer
from .core import VoiceAnalyzer, AudioManager, AlertSystem
from .pitch_analyzer import AudioFileAnalyzer, PitchGoalManager
from .presets import VoicePresets
from .safety import VoiceSafetyMonitor, VoiceWarmupRoutines, VocalHealthEducation

__all__ = [
    'VoiceTrainer',
    'VoiceAnalyzer',
    'AudioManager',
    'AlertSystem',
    'AudioFileAnalyzer',
    'PitchGoalManager',
    'VoicePresets',
    'VoiceSafetyMonitor',
    'VoiceWarmupRoutines',
    'VocalHealthEducation'
]
