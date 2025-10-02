from .base_exercise import BaseExercise


class HummingWarmupExercise(BaseExercise):
    """Humming exercise for resonance development and warm-up"""

    def __init__(self):
        super().__init__()
        self.name = 'Humming Resonance Warm-up'
        self.duration = 60  # 1 minute
        self.instructions = 'Hum at comfortable pitch, feel vibrations in face/head (not chest)'
        self.target_range = (160, 200)  # Comfortable lower-mid range
        self.breathing_focus = True
        self.purpose = "Develop head resonance awareness and prepare vocal cords for training"
        self.benefits = "Builds resonance awareness, warms up vocal cords safely, establishes proper breath support"
        self.metrics_relevant = ['pitch', 'resonance', 'breathing']

        self.tips = [
            'Place hand on chest - should feel minimal vibration',
            'Place hand on face/nose - should feel strong vibration',
            'Start low and gradually move higher',
            'Focus on the buzzing sensation in your face and head'
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
                'Keep volume comfortable - no straining',
                'Stop if you feel any throat tension',
                'This should feel relaxing and gentle'
            ],
            'exercise_info': {
                'vocal_technique': 'Humming with mouth closed',
                'resonance_focus': 'Head and facial resonance',
                'breathing_pattern': 'Steady, controlled airflow',
                'difficulty': 'Beginner'
            }
        }