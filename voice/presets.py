import json
import os
from typing import Dict, Any, Optional

class VoicePresets:
    """Voice training presets for different vocal goals"""

    def __init__(self):
        self.presets = {
            'mtf': {
                'name': 'MTF Voice Training',
                'description': 'Targets feminine speech patterns with gradual pitch elevation',
                'base_frequency': 165,
                'target_frequency': 200,
                'high_alert_threshold': 450,
                'goal_increment': 3,
                'dip_tolerance': 5.0,
                'sensitivity': 1.2,
                'exercises': ['humming_warmup', 'pitch_slides', 'resonance_shift'],
                'tips': [
                    'Focus on head resonance rather than just pitch',
                    'Practice speech patterns and intonation',
                    'Gradual training prevents vocal strain'
                ]
            },
            'ftm': {
                'name': 'FTM Voice Training',
                'description': 'Develops lower pitch range and chest resonance',
                'base_frequency': 155,
                'target_frequency': 125,
                'high_alert_threshold': 280,
                'goal_increment': -3,
                'dip_tolerance': 5.0,
                'sensitivity': 0.9,
                'exercises': ['breathing_control', 'humming_warmup', 'straw_phonation'],
                'tips': [
                    'Focus on chest resonance and lower pitch',
                    'Practice speaking from diaphragm',
                    'Avoid vocal strain - work gradually',
                    'Consistency in lower ranges is more important than extremes'
                ]
            },
            'nonbinary_higher': {
                'name': 'Non-Binary (Higher Range)',
                'description': 'Androgynous voice with slight elevation',
                'base_frequency': 165,
                'target_frequency': 190,
                'high_alert_threshold': 380,
                'goal_increment': 2,
                'dip_tolerance': 6.0,
                'sensitivity': 1.0,
                'exercises': ['humming_warmup', 'pitch_slides', 'resonance_shift'],
                'tips': [
                    'Balance between ranges for androgynous quality',
                    'Focus on consistent control rather than extremes',
                    'Experiment with different resonance placements'
                ]
            },
            'nonbinary_lower': {
                'name': 'Non-Binary (Lower Range)',
                'description': 'Androgynous voice with slight deepening',
                'base_frequency': 155,
                'target_frequency': 140,
                'high_alert_threshold': 300,
                'goal_increment': -2,
                'dip_tolerance': 6.0,
                'sensitivity': 0.95,
                'exercises': ['breathing_control', 'humming_warmup', 'straw_phonation'],
                'tips': [
                    'Subtle lower pitch while maintaining flexibility',
                    'Practice chest resonance without strain',
                    'Focus on breath support for consistent tone'
                ]
            },
            'nonbinary_neutral': {
                'name': 'Non-Binary (Neutral)',
                'description': 'Current range with improved control and consistency',
                'base_frequency': 160,
                'target_frequency': 160,
                'high_alert_threshold': 350,
                'goal_increment': 0,
                'dip_tolerance': 7.0,
                'sensitivity': 1.0,
                'exercises': ['humming_warmup', 'breathing_control', 'resonance_shift'],
                'tips': [
                    'Focus on vocal control and consistency',
                    'Develop flexibility across your current range',
                    'Work on clarity and vocal health'
                ]
            },
            'custom': {
                'name': 'Custom Configuration',
                'description': 'Manually configured settings',
                'base_frequency': 165,
                'target_frequency': 165,
                'high_alert_threshold': 400,
                'goal_increment': 0,
                'dip_tolerance': 6.0,
                'sensitivity': 1.0,
                'exercises': ['humming_warmup', 'breathing_control'],
                'tips': [
                    'Customize your settings in the Settings menu',
                    'Start with gentle exercises',
                    'Adjust parameters based on your comfort level'
                ]
            }
        }

    def get_preset(self, preset_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific preset by name"""
        return self.presets.get(preset_name)

    def get_all_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get all available presets"""
        return self.presets

    def get_preset_list(self) -> Dict[str, str]:
        """Get list of preset names and descriptions"""
        return {name: preset['description'] for name, preset in self.presets.items()}

    def apply_preset_to_config(self, preset_name: str, current_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a preset to existing configuration"""
        preset = self.get_preset(preset_name)
        if not preset:
            return current_config

        # Create updated config with preset values
        updated_config = current_config.copy()
        updated_config.update({
            'base_goal': preset['base_frequency'],
            'current_goal': preset['target_frequency'],
            'goal_increment': preset['goal_increment'],
            'high_pitch_threshold': preset['high_alert_threshold'],
            'dip_tolerance_duration': preset['dip_tolerance'],
            'sensitivity': preset['sensitivity'],
            'current_preset': preset_name,
            'preset_applied_date': json.dumps(str(os.path.getmtime(__file__)))
        })

        return updated_config


# CLI setup classes removed - GUI handles onboarding through OnboardingWidget
# The FirstTimeUserSetup class contained CLI-only methods and has been removed to clean up the codebase