from .base_exercise import BaseExercise


class BreathingControlExercise(BaseExercise):
    """Breathing control exercise for foundational breath support"""

    def __init__(self):
        super().__init__()
        self.name = 'Diaphragmatic Breathing'
        self.duration = 90  # 1.5 minutes
        self.instructions = 'Deep belly breathing, hand on chest should not move'
        self.target_range = (0, 0)  # No pitch target - breathing only
        self.breathing_focus = True
        self.purpose = "Establish proper diaphragmatic breathing foundation for voice control"
        self.benefits = "Builds breath support, reduces shoulder tension, improves vocal stamina"
        self.metrics_relevant = ['breathing']  # Only breathing matters

        self.tips = [
            'Place one hand on chest, one on belly',
            'Breathe so only belly hand moves',
            'Chest should remain relatively still',
            'This builds the foundation for all voice control'
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
                'Breathe naturally - do not force',
                'If you feel dizzy, breathe normally for a moment',
                'Focus on expansion of lower ribs, not just belly'
            ],
            'exercise_info': {
                'vocal_technique': 'Silent breathing exercise',
                'resonance_focus': 'No vocal sound required',
                'breathing_pattern': 'Deep diaphragmatic breathing',
                'difficulty': 'Beginner'
            }
        }