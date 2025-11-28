from .base_exercise import BaseExercise


class LipTrillsExercise(BaseExercise):
    """Lip trill exercise for breath control and pitch flexibility"""

    def __init__(self):
        super().__init__()
        self.name = 'Lip Trill Exercise'
        self.duration = 45  # 45 seconds
        self.instructions = 'Make "brrr" sound, glide pitch up and down smoothly'
        self.target_range = (150, 250)  # Wide range for pitch glides
        self.breathing_focus = True
        self.purpose = "Develop breath control, vocal flexibility, and smooth pitch transitions"
        self.benefits = "Improves breath support, reduces vocal tension, builds pitch control skills"
        self.metrics_relevant = ['pitch', 'breathing']

        self.tips = [
            'Keep lips relaxed and loose',
            'Use steady, consistent airflow',
            'Glide smoothly between pitches',
            'Let the lips "bubble" naturally with the airflow'
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
                'Stop if your lips become too dry',
                'Maintain gentle, consistent air pressure',
                'Avoid forcing the sound'
            ],
            'exercise_info': {
                'vocal_technique': 'Lip vibration with airflow',
                'resonance_focus': 'Natural oral resonance',
                'breathing_pattern': 'Sustained, controlled exhalation',
                'difficulty': 'Beginner to Intermediate'
            }
        }