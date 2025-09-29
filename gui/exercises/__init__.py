"""
Exercises module - Voice training exercises and warm-ups
"""

from .exercises_manager import ExercisesManager

# Keep existing imports for backward compatibility
from .base_exercise import BaseExercise, ExerciseSession, BreathingTracker, ProgressTracker
from .humming_warmup import HummingWarmupExercise
from .lip_trills import LipTrillsExercise
from .pitch_slides import PitchSlidesExercise
from .straw_phonation import StrawPhonationExercise
from .resonance_shift import ResonanceShiftExercise
from .breathing_control import BreathingControlExercise
from .exercises_screen import ExercisesScreen

# Exercise registry for easy access
EXERCISE_REGISTRY = {
    'humming_warmup': HummingWarmupExercise,
    'lip_trills': LipTrillsExercise,
    'pitch_slides': PitchSlidesExercise,
    'straw_phonation': StrawPhonationExercise,
    'resonance_shift': ResonanceShiftExercise,
    'breathing_control': BreathingControlExercise
}

def get_exercise(name):
    """Get exercise class by name"""
    return EXERCISE_REGISTRY.get(name)

def get_all_exercises():
    """Get all available exercise classes"""
    return {name: cls() for name, cls in EXERCISE_REGISTRY.items()}

def get_warmup_sequence():
    """Get recommended warm-up sequence"""
    return ['breathing_control', 'humming_warmup', 'lip_trills', 'pitch_slides']

__all__ = [
    'ExercisesManager',
    'BaseExercise', 'ExerciseSession', 'BreathingTracker', 'ProgressTracker',
    'HummingWarmupExercise', 'LipTrillsExercise', 'PitchSlidesExercise',
    'StrawPhonationExercise', 'ResonanceShiftExercise', 'BreathingControlExercise',
    'ExercisesScreen', 'EXERCISE_REGISTRY', 'get_exercise', 'get_all_exercises',
    'get_warmup_sequence'
]