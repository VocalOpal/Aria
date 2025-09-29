from .base_exercise import BaseExercise


class ResonanceShiftExercise(BaseExercise):
    """Resonance shift exercise for forward placement training"""

    def __init__(self):
        super().__init__()
        self.name = 'Forward Resonance Training'
        self.duration = 75  # 1 minute 15 seconds
        self.instructions = 'Say "me-may-my-mo-moo" focusing sound in nasal cavity/face'
        self.target_range = (170, 250)  # Mid-high range for resonance work
        self.breathing_focus = False
        self.purpose = "Develop forward resonance placement and nasal/facial awareness"
        self.benefits = "Improves resonance placement, reduces throat tension, enhances vocal brightness"
        self.metrics_relevant = ['pitch', 'resonance']

        self.tips = [
            'Feel vibrations in nose and face',
            'Avoid chest resonance',
            'Exaggerate the nasal quality initially',
            'Practice slowly, then gradually speed up'
        ]

    def get_exercise_data(self):
        """Return exercise configuration dictionary"""
        return {
            'name': self.name,
            'duration': self.duration,
            'instructions': self.instructions,
            'target_range': self.target_range,
            'breathing_focus': self.breathing_focus,
            'purpose': self.purpose,
            'benefits': self.benefits,
            'metrics_relevant': self.metrics_relevant,
            'tips': self.tips,
            'safety_notes': [
                'Start with exaggerated nasal quality, then normalize',
                'Keep throat relaxed throughout',
                'Focus on feeling, not just hearing the sound'
            ],
            'exercise_info': {
                'vocal_technique': 'Vowel sequence with nasal consonants',
                'resonance_focus': 'Forward/nasal resonance',
                'breathing_pattern': 'Natural speech breathing',
                'difficulty': 'Intermediate to Advanced'
            }
        }