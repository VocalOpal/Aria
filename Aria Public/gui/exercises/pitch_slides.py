from .base_exercise import BaseExercise


class PitchSlidesExercise(BaseExercise):
    """Pitch glides exercise for pitch control and resonance development"""

    def __init__(self):
        super().__init__()
        self.name = 'Pitch Glides'
        self.duration = 90  # 1.5 minutes
        self.instructions = 'Slide from low to high pitch on "nee" sound, focus on head resonance'
        self.target_range = (140, 280)  # Extended range for glides
        self.breathing_focus = False
        self.purpose = "Develop precise pitch control and establish head resonance"
        self.benefits = "Builds pitch accuracy, strengthens head voice connection, improves vocal agility"
        self.metrics_relevant = ['pitch', 'resonance']

        self.tips = [
            'Use "nee" sound for forward resonance placement',
            'Start at comfortable low pitch',
            'Glide smoothly to highest comfortable pitch',
            'Focus resonance in face/head area, not throat'
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
                'Stop at your comfortable upper limit',
                'Keep the sound light and forward',
                'Avoid pushing or straining on high notes'
            ],
            'exercise_info': {
                'vocal_technique': 'Smooth pitch glides on vowel sound',
                'resonance_focus': 'Forward/head resonance',
                'breathing_pattern': 'Natural breath support',
                'difficulty': 'Intermediate'
            }
        }