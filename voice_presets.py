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
                'dip_tolerance': 5.0,
                'sensitivity': 1.0,
                'exercises': ['humming_warmup', 'lip_trills', 'pitch_slides'],
                'tips': [
                    'Aim for androgynous, versatile vocal range',
                    'Practice both higher and lower registers',
                    'Focus on clear articulation',
                    'Balance is key - neither too high nor too low'
                ]
            },
            'nonbinary_lower': {
                'name': 'Non-Binary (Lower Range)',
                'description': 'Androgynous voice with slight deepening',
                'base_frequency': 165,
                'target_frequency': 145,
                'high_alert_threshold': 320,
                'goal_increment': -2,
                'dip_tolerance': 5.0,
                'sensitivity': 0.95,
                'exercises': ['breathing_control', 'humming_warmup', 'straw_phonation'],
                'tips': [
                    'Develop comfortable lower register',
                    'Maintain clarity while deepening voice',
                    'Practice varied intonation patterns',
                    'Subtle changes create natural androgynous tone'
                ]
            },
            'nonbinary_neutral': {
                'name': 'Non-Binary (Neutral)',
                'description': 'Maintains current range with improved control',
                'base_frequency': 165,
                'target_frequency': 165,
                'high_alert_threshold': 380,
                'goal_increment': 1,
                'dip_tolerance': 6.0,
                'sensitivity': 1.0,
                'exercises': ['breathing_control', 'resonance_shift', 'pitch_slides'],
                'tips': [
                    'Focus on vocal control and stability',
                    'Develop consistent, clear voice',
                    'Practice expressive intonation',
                    'Flexibility and range are your strengths'
                ]
            },
            'custom': {
                'name': 'Custom Configuration',
                'description': 'Manually configured settings',
                'base_frequency': 165,
                'target_frequency': 165,
                'high_alert_threshold': 400,
                'goal_increment': 3,
                'dip_tolerance': 5.0,
                'sensitivity': 1.0,
                'exercises': ['humming_warmup', 'pitch_slides'],
                'tips': ['Customize these settings in the configuration menu']
            }
        }
    
    def get_preset(self, preset_name: str) -> Optional[Dict[str, Any]]:
        """Get preset configuration by name"""
        return self.presets.get(preset_name)
    
    def get_all_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get all available presets"""
        return self.presets
    
    def get_preset_list(self) -> Dict[str, str]:
        """Get simplified list of presets for menu display"""
        return {key: preset['name'] for key, preset in self.presets.items()}
    
    def apply_preset_to_config(self, preset_name: str, current_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply preset to current configuration"""
        preset = self.get_preset(preset_name)
        if not preset:
            return current_config
        
        updated_config = current_config.copy()
        updated_config.update({
            'current_goal': preset['base_frequency'],
            'base_goal': preset['base_frequency'], 
            'target_goal': preset['target_frequency'],
            'goal_increment': preset['goal_increment'],
            'dip_tolerance_duration': preset['dip_tolerance'],
            'sensitivity': preset['sensitivity'],
            'high_pitch_threshold': preset['high_alert_threshold'],
            'preset_name': preset_name,
            'recommended_exercises': preset['exercises']
        })
        
        return updated_config

class FirstTimeUserSetup:
    """Handle first-time user setup and preset selection"""
    
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.presets = VoicePresets()
    
    def is_first_time_user(self) -> bool:
        """Check if this is a first-time user"""
        if not os.path.exists(self.config_file):
            return True
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return not config.get('setup_completed', False)
        except Exception:
            return True
    
    def show_welcome_screen(self) -> str:
        """Display welcome message and get user preference"""
        print("=" * 80)
        print("            Welcome to Aria Voice Studio v4.0")
        print("        Your voice, your journey, your authentic self")
        print("=" * 80)
        print()
        print("🎯 First-Time Setup")
        print()
        print("This voice training application helps you achieve your vocal goals")
        print("with scientifically-based exercises and real-time feedback.")
        print()
        print("Let's start by selecting a preset that matches your goals:")
        print()
        
        options = {
            '1': 'MTF - Feminine voice training with pitch elevation',
            '2': 'FTM - Masculine voice development with lower pitch',
            '3': 'Non-Binary (Higher) - Androgynous with slight elevation',
            '4': 'Non-Binary (Lower) - Androgynous with slight deepening', 
            '5': 'Non-Binary (Neutral) - Maintain current range with better control',
            '6': 'Custom - I\'ll configure manually later'
        }
        
        for key, desc in options.items():
            print(f"  {key}. {desc}")
        
        print()
        print("Choose the option that best describes your vocal goals.")
        print("You can always change these settings later in the configuration menu.")
        print()
        
        while True:
            choice = input("Select option (1-6): ").strip()
            if choice in options:
                return choice
            print("Please enter a number between 1 and 6.")
    
    def get_preset_from_choice(self, choice: str) -> str:
        """Convert user choice to preset name"""
        choice_to_preset = {
            '1': 'mtf',
            '2': 'ftm', 
            '3': 'nonbinary_higher',
            '4': 'nonbinary_lower',
            '5': 'nonbinary_neutral',
            '6': 'custom'
        }
        return choice_to_preset.get(choice, 'custom')
    
    def show_preset_details(self, preset_name: str) -> bool:
        """Show preset details and confirm selection"""
        preset = self.presets.get_preset(preset_name)
        if not preset:
            return False
        
        print("\n" + "=" * 60)
        print(f"Selected: {preset['name']}")
        print("=" * 60)
        print(f"Description: {preset['description']}")
        print(f"Starting frequency: {preset['base_frequency']} Hz")
        print(f"Target frequency: {preset['target_frequency']} Hz")
        print()
        print("Key features of this preset:")
        for tip in preset['tips']:
            print(f"  • {tip}")
        
        print(f"\nRecommended exercises: {', '.join(preset['exercises'])}")
        print()
        
        while True:
            confirm = input("Does this look right for your goals? (y/n): ").strip().lower()
            if confirm in ['y', 'yes']:
                return True
            elif confirm in ['n', 'no']:
                return False
            print("Please enter 'y' for yes or 'n' for no.")
    
    def create_initial_config(self, preset_name: str) -> Dict[str, Any]:
        """Create initial configuration with selected preset"""
        base_config = {
            'current_goal': 165,
            'sensitivity': 1.0,
            'vad_threshold': 0.01,
            'noise_threshold': 0.02,
            'alert_volume': 0.7,
            'alert_cooldown': 2.0,
            'setup_completed': True
        }
        
        return self.presets.apply_preset_to_config(preset_name, base_config)
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def run_setup(self) -> Optional[Dict[str, Any]]:
        """Run complete first-time setup process"""
        if not self.is_first_time_user():
            return None
        
        while True:
            choice = self.show_welcome_screen()
            preset_name = self.get_preset_from_choice(choice)
            
            if self.show_preset_details(preset_name):
                config = self.create_initial_config(preset_name)
                
                if self.save_config(config):
                    print("\n✅ Configuration saved successfully!")
                    print("\nYou're all set to start voice training!")
                    print("Remember: Consistent practice is key to achieving your vocal goals.")
                    print("\nPress Enter to continue to the main application...")
                    input()
                    return config
                else:
                    print("❌ Error saving configuration. Please try again.")
                    input("Press Enter to retry...")
            else:
                print("\nLet's try a different option...")
                input("Press Enter to continue...")
        
        return None
