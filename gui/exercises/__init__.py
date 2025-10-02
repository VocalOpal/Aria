"""
Exercises module - Voice training exercises and warm-ups
Backward compatibility for old component_factory.py
"""

# Exercise spec for new GUI
from . import exercise_spec

# Backward compatibility imports for component_factory
try:
    from .base_exercise import BaseExercise, ExerciseSession, BreathingTracker, ProgressTracker
    from .humming_warmup import HummingWarmupExercise
    from .lip_trills import LipTrillsExercise
    from .pitch_slides import PitchSlidesExercise
    from .straw_phonation import StrawPhonationExercise
    from .resonance_shift import ResonanceShiftExercise
    from .breathing_control import BreathingControlExercise

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
        'exercise_spec',
        'BaseExercise', 'ExerciseSession', 'BreathingTracker', 'ProgressTracker',
        'HummingWarmupExercise', 'LipTrillsExercise', 'PitchSlidesExercise',
        'StrawPhonationExercise', 'ResonanceShiftExercise', 'BreathingControlExercise',
        'EXERCISE_REGISTRY', 'get_exercise', 'get_all_exercises', 'get_warmup_sequence'
    ]

except ImportError as e:
    # If old exercise classes fail to import, provide minimal compatibility
    print(f"Warning: Some exercise classes could not be imported: {e}")

    def get_exercise(name):
        return None

    def get_all_exercises():
        return {}

    def get_warmup_sequence():
        return []

    EXERCISE_REGISTRY = {}

    __all__ = ['exercise_spec', 'get_exercise', 'get_all_exercises', 'get_warmup_sequence', 'EXERCISE_REGISTRY']