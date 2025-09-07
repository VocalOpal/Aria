import json
import os
from datetime import datetime

class OnboardingWizard:
    """Guide new users through initial setup with beginner-friendly onboarding"""
    
    def __init__(self, ui, config_file="data/voice_config.json"):
        self.ui = ui
        self.config_file = config_file
        self.onboarding_complete = False
        
        # Onboarding state
        self.user_responses = {}
        self.recommended_preset = None
        self.skip_audio_test = False
        
    def is_first_time_user(self):
        """Check if this is a first-time user"""
        if not os.path.exists(self.config_file):
            return True
            
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return not config.get('onboarding_completed', False)
        except:
            return True
            
    def start_onboarding(self):
        """Start the complete onboarding process"""
        if not self.is_first_time_user():
            return None
            
        self.ui.clear_screen()
        self._show_welcome_screen()
        
        # Step 1: Welcome and overview
        if not self._get_user_consent():
            return None
            
        # Step 2: Voice goals assessment
        self._assess_voice_goals()
        
        # Step 3: Experience level
        self._assess_experience_level()
        
        # Step 4: Audio equipment check (optional)
        if not self.skip_audio_test:
            self._audio_equipment_check()
            
        # Step 5: Generate recommendations
        config = self._generate_initial_config()
        
        # Step 6: Preview and confirm
        if self._preview_and_confirm_config(config):
            return config
        else:
            return None
            
    def _show_welcome_screen(self):
        """Show welcoming introduction screen"""
        self.ui.clear_screen()
        print("🎉 Welcome to Aria Voice Studio! 🎉")
        print("=" * 60)
        print()
        print("We're excited to help you on your voice training journey!")
        print()
        print("This quick setup will help us personalize your experience:")
        print("• Understand your voice training goals")
        print("• Set appropriate target ranges for your practice")
        print("• Configure audio settings for your setup")
        print("• Recommend the best features for your needs")
        print()
        print("✨ This takes about 2-3 minutes and makes training much more effective!")
        print()
        print("💡 You can always change these settings later in the Settings menu.")
        
    def _get_user_consent(self):
        """Get user consent to continue with onboarding"""
        print()
        choice = input("Ready to get started? (Y/n): ").strip().lower()
        
        if choice in ['n', 'no']:
            print()
            print("No problem! You can run this setup anytime from Settings.")
            print("For now, we'll use default settings that work for most users.")
            return False
            
        return True
        
    def _assess_voice_goals(self):
        """Assess user's voice training goals"""
        self.ui.clear_screen()
        print("🎯 Voice Training Goals")
        print("=" * 30)
        print()
        print("What's your primary voice training goal?")
        print()
        print("1. Feminine voice development (MTF)")
        print("2. Masculine voice development (FTM)")  
        print("3. Androgynous/Non-binary (higher range)")
        print("4. Androgynous/Non-binary (lower range)")
        print("5. Androgynous/Non-binary (neutral)")
        print("6. General voice improvement")
        print("7. I'm not sure yet")
        print()
        
        while True:
            choice = input("Your choice (1-7): ").strip()
            
            if choice == '1':
                self.user_responses['voice_goal'] = 'mtf'
                self.user_responses['goal_description'] = 'Feminine voice development'
                break
            elif choice == '2':
                self.user_responses['voice_goal'] = 'ftm'
                self.user_responses['goal_description'] = 'Masculine voice development'
                break
            elif choice == '3':
                self.user_responses['voice_goal'] = 'nonbinary_higher'
                self.user_responses['goal_description'] = 'Androgynous (higher range)'
                break
            elif choice == '4':
                self.user_responses['voice_goal'] = 'nonbinary_lower'
                self.user_responses['goal_description'] = 'Androgynous (lower range)'
                break
            elif choice == '5':
                self.user_responses['voice_goal'] = 'nonbinary_neutral'
                self.user_responses['goal_description'] = 'Androgynous (neutral)'
                break
            elif choice == '6':
                self.user_responses['voice_goal'] = 'general'
                self.user_responses['goal_description'] = 'General voice improvement'
                break
            elif choice == '7':
                self.user_responses['voice_goal'] = 'unsure'
                self.user_responses['goal_description'] = 'Exploring options'
                break
            else:
                print("Please enter a number from 1-7.")
                continue
                
        print(f"\\n✅ Goal set: {self.user_responses['goal_description']}")
        
    def _assess_experience_level(self):
        """Assess user's experience with voice training"""
        self.ui.clear_screen()
        print("📚 Experience Level")
        print("=" * 25)
        print()
        print("How would you describe your voice training experience?")
        print()
        print("1. Complete beginner - I'm new to voice training")
        print("2. Some experience - I've tried voice training before")
        print("3. Intermediate - I have regular voice training practice")
        print("4. Advanced - I'm experienced with voice techniques")
        print()
        
        while True:
            choice = input("Your experience level (1-4): ").strip()
            
            if choice == '1':
                self.user_responses['experience'] = 'beginner'
                self.user_responses['experience_description'] = 'Complete beginner'
                break
            elif choice == '2':
                self.user_responses['experience'] = 'some'
                self.user_responses['experience_description'] = 'Some experience'
                break
            elif choice == '3':
                self.user_responses['experience'] = 'intermediate'
                self.user_responses['experience_description'] = 'Intermediate'
                break
            elif choice == '4':
                self.user_responses['experience'] = 'advanced'
                self.user_responses['experience_description'] = 'Advanced'
                break
            else:
                print("Please enter a number from 1-4.")
                continue
                
        print(f"\\n✅ Experience: {self.user_responses['experience_description']}")
        
        # Show beginner-specific information
        if self.user_responses['experience'] == 'beginner':
            print()
            print("💡 Great! Here are some beginner tips:")
            print("   • Start with short 10-15 minute sessions")
            print("   • Try the warm-up exercises first")
            print("   • Be patient - voice changes take time")
            print("   • The app will guide you with gentle feedback")
            
        input("\\nPress Enter to continue...")
        
    def _audio_equipment_check(self):
        """Optional audio equipment check"""
        self.ui.clear_screen()
        print("🎤 Audio Equipment Check")
        print("=" * 30)
        print()
        print("Let's make sure your microphone is working well!")
        print()
        print("What type of microphone are you using?")
        print()
        print("1. Built-in laptop/computer microphone")
        print("2. USB headset or gaming headset")
        print("3. External USB microphone")
        print("4. Professional audio interface")
        print("5. I'm not sure")
        print("6. Skip audio test for now")
        print()
        
        while True:
            choice = input("Your setup (1-6): ").strip()
            
            if choice == '1':
                self.user_responses['mic_type'] = 'builtin'
                self._show_builtin_mic_tips()
                break
            elif choice == '2':
                self.user_responses['mic_type'] = 'headset'
                self._show_headset_tips()
                break
            elif choice == '3':
                self.user_responses['mic_type'] = 'usb_mic'
                self._show_usb_mic_tips()
                break
            elif choice == '4':
                self.user_responses['mic_type'] = 'professional'
                self._show_professional_tips()
                break
            elif choice == '5':
                self.user_responses['mic_type'] = 'unknown'
                self._show_general_audio_tips()
                break
            elif choice == '6':
                self.skip_audio_test = True
                return
            else:
                print("Please enter a number from 1-6.")
                continue
                
    def _show_builtin_mic_tips(self):
        """Show tips for built-in microphone users"""
        print()
        print("📱 Built-in Microphone Tips:")
        print("   • Find a quiet environment for best results")
        print("   • Speak clearly and at a consistent distance")
        print("   • Consider a headset for better audio quality")
        print("   • The app will adjust sensitivity automatically")
        input("\\nPress Enter to continue...")
        
    def _show_headset_tips(self):
        """Show tips for headset users"""
        print()
        print("🎧 Headset Tips:")
        print("   • Position the mic close to your mouth")
        print("   • Avoid breathing directly into the microphone")
        print("   • Great choice for consistent audio quality!")
        input("\\nPress Enter to continue...")
        
    def _show_usb_mic_tips(self):
        """Show tips for USB microphone users"""
        print()
        print("🎙️ USB Microphone Tips:")
        print("   • Excellent choice for voice training!")
        print("   • Position 6-12 inches from your mouth")
        print("   • Use a pop filter if available")
        print("   • You should get very accurate pitch detection")
        input("\\nPress Enter to continue...")
        
    def _show_professional_tips(self):
        """Show tips for professional audio interface users"""
        print()
        print("🔊 Professional Setup Tips:")
        print("   • Perfect for precise voice training!")
        print("   • Make sure your interface is properly configured")
        print("   • Consider enabling phantom power if using condenser mics")
        print("   • Your setup should provide excellent results")
        input("\\nPress Enter to continue...")
        
    def _show_general_audio_tips(self):
        """Show general audio tips"""
        print()
        print("🔊 General Audio Tips:")
        print("   • Find the quietest space available")
        print("   • Test different microphone positions")
        print("   • The app will adapt to your setup")
        print("   • You can adjust sensitivity in Settings if needed")
        input("\\nPress Enter to continue...")
        
    def _generate_initial_config(self):
        """Generate initial configuration based on user responses"""
        # Import voice presets
        from voice_presets import VoicePresets
        presets = VoicePresets()
        
        # Get base configuration from voice goal
        voice_goal = self.user_responses.get('voice_goal', 'general')
        
        if voice_goal in ['mtf', 'ftm', 'nonbinary_higher', 'nonbinary_lower', 'nonbinary_neutral']:
            preset = presets.get_preset(voice_goal)
            config = presets.apply_preset_to_config(voice_goal, {})
        else:
            # Default configuration for general/unsure users
            config = {
                'threshold_hz': 165,
                'base_goal': 165,
                'goal_increment': 3,
                'sensitivity': 1.0,
                'vad_threshold': 0.01,
                'noise_threshold': 0.02,
                'dip_tolerance_duration': 6.0,
                'high_pitch_threshold': 400
            }
            
        # Adjust settings based on experience level
        experience = self.user_responses.get('experience', 'beginner')
        
        if experience == 'beginner':
            # More forgiving settings for beginners
            config['dip_tolerance_duration'] = max(config.get('dip_tolerance_duration', 6.0), 7.0)
            config['goal_increment'] = min(config.get('goal_increment', 3), 2)  # Smaller steps
        elif experience == 'advanced':
            # More precise settings for advanced users
            config['dip_tolerance_duration'] = min(config.get('dip_tolerance_duration', 6.0), 4.0)
            
        # Adjust for microphone type
        mic_type = self.user_responses.get('mic_type', 'unknown')
        
        if mic_type == 'builtin':
            # Higher noise threshold for built-in mics
            config['noise_threshold'] = max(config.get('noise_threshold', 0.02), 0.03)
            config['sensitivity'] = 1.2  # Slightly higher sensitivity
        elif mic_type in ['usb_mic', 'professional']:
            # Lower noise threshold for good mics
            config['noise_threshold'] = min(config.get('noise_threshold', 0.02), 0.015)
            config['sensitivity'] = 0.9  # Slightly lower sensitivity
            
        # Mark onboarding as completed
        config['onboarding_completed'] = True
        config['onboarding_date'] = datetime.now().isoformat()
        config['setup_completed'] = True
        
        return config
        
    def _preview_and_confirm_config(self, config):
        """Preview configuration and confirm with user"""
        self.ui.clear_screen()
        print("🔧 Your Personalized Setup")
        print("=" * 35)
        print()
        print("Based on your responses, here's your personalized configuration:")
        print()
        
        # Show user-friendly summary
        goal_desc = self.user_responses.get('goal_description', 'General improvement')
        experience_desc = self.user_responses.get('experience_description', 'Beginner')
        
        print(f"🎯 Voice Goal: {goal_desc}")
        print(f"📚 Experience: {experience_desc}")
        print(f"🎤 Target Frequency: {config['threshold_hz']} Hz")
        print(f"📈 Progression: {config['goal_increment']} Hz steps")
        
        if self.user_responses.get('mic_type'):
            mic_friendly_names = {
                'builtin': 'Built-in microphone',
                'headset': 'USB/Gaming headset', 
                'usb_mic': 'USB microphone',
                'professional': 'Professional audio interface',
                'unknown': 'General setup'
            }
            mic_name = mic_friendly_names.get(self.user_responses['mic_type'], 'Unknown')
            print(f"🎙️ Audio Setup: {mic_name}")
            
        print()
        print("💡 These settings are optimized for your goals and can be adjusted anytime!")
        print()
        
        # Get confirmation
        while True:
            choice = input("Does this look good? (Y/n): ").strip().lower()
            
            if choice in ['', 'y', 'yes']:
                print()
                print("🎉 Perfect! Your setup is complete!")
                print()
                print("📋 Quick Start Recommendations:")
                
                if self.user_responses.get('experience') == 'beginner':
                    print("   1. Start with Settings → Voice Exercises → Warm-up Routine")
                    print("   2. Try Live Training for 10-15 minutes")
                    print("   3. Check your Progress & Statistics to see improvement")
                else:
                    print("   1. Try Live Voice Training to test your settings")
                    print("   2. Experiment with Voice Exercises")  
                    print("   3. Use Audio File Analysis for detailed feedback")
                    
                print()
                print("🛡️ Remember: Voice training should never hurt!")
                print("   Take breaks and stop if you feel any discomfort.")
                
                input("\\nPress Enter to start using Aria Voice Studio...")
                return True
                
            elif choice in ['n', 'no']:
                print()
                print("No problem! Let's go through the setup again.")
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
                
    def get_beginner_tips(self):
        """Get contextual tips for beginners"""
        experience = self.user_responses.get('experience', 'beginner')
        voice_goal = self.user_responses.get('voice_goal', 'general')
        
        tips = []
        
        if experience == 'beginner':
            tips.extend([
                "Start with 10-15 minute sessions to avoid vocal fatigue",
                "Try the warm-up exercises before intensive training",
                "Be patient - significant voice changes take weeks or months",
                "Focus on consistency rather than dramatic changes"
            ])
            
        if voice_goal == 'mtf':
            tips.extend([
                "Focus on breath support and resonance, not just pitch",
                "Practice speaking from your chest/head voice blend",
                "Record yourself regularly to track progress objectively"
            ])
        elif voice_goal == 'ftm':
            tips.extend([
                "Work on lowering resonance and chest voice development", 
                "Practice sustainable techniques to protect your voice",
                "Consistency in lower ranges is more important than extremes"
            ])
            
        return tips[:4]  # Return max 4 tips
        
    def show_post_onboarding_tips(self):
        """Show helpful tips after onboarding completion"""
        tips = self.get_beginner_tips()
        
        if tips:
            self.ui.clear_screen()
            print("💡 Personalized Tips for Success")
            print("=" * 40)
            print()
            for i, tip in enumerate(tips, 1):
                print(f"{i}. {tip}")
            print()
            print("🌟 You can always find more guidance in Settings → Voice Safety & Wellness")
            input("\\nPress Enter to continue...")