from .base_exercise import BaseExercise


class StrawPhonationExercise(BaseExercise):
    """Straw phonation exercise for vocal efficiency and tension reduction"""

    def __init__(self):
        super().__init__()
        self.name = 'Straw Phonation'
        self.duration = 120  # 2 minutes
        self.instructions = 'Hum through imaginary straw, creates efficient phonation'
        self.target_range = (165, 220)  # Mid-range focus
        self.breathing_focus = True
        self.purpose = "Improve vocal efficiency and reduce laryngeal tension"
        self.benefits = "Reduces vocal fatigue, improves vocal fold coordination, enhances breath efficiency"
        self.metrics_relevant = ['pitch', 'breathing']

        self.tips = [
            'Purse lips as if drinking through a straw',
            'Hum any comfortable pitch',
            'Focus on smooth, controlled sound',
            'This exercise improves vocal efficiency and reduces strain'
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
                'Keep lips gently pursed, not tightly squeezed',
                'Maintain steady, gentle airflow',
                'Should feel easy and effortless'
            ],
            'exercise_info': {
                'vocal_technique': 'Semi-occluded vocal tract exercise',
                'resonance_focus': 'Balanced oral-pharyngeal resonance',
                'breathing_pattern': 'Controlled, efficient airflow',
                'difficulty': 'Beginner to Advanced'
            }
        }