"""
Safety Coordinator - Handles safety monitoring and warnings
Extracted from voice_trainer.py lines 1455-1696 (safety functionality)
"""

from typing import Dict, Any, List, Optional, Callable


class VoiceSafetyCoordinator:
    """Coordinates voice safety monitoring and wellness features"""
    
    def __init__(self):
        # Components (will be injected)
        self.safety_monitor = None
        self.warmup_routines = None
        self.vocal_education = None
        self.ui = None
        self.config_manager = None
    
    def set_dependencies(self, safety_monitor, warmup_routines, vocal_education, ui, config_manager):
        """Inject dependencies"""
        self.safety_monitor = safety_monitor
        self.warmup_routines = warmup_routines
        self.vocal_education = vocal_education
        self.ui = ui
        self.config_manager = config_manager
    
    def handle_safety_warning(self, warning: Dict[str, Any]):
        """Handle voice safety warnings from the monitoring system"""
        warning_type = warning.get('type', 'unknown')
        message = warning.get('message', '')
        suggestion = warning.get('suggestion', '')
        
        # Display warning based on type
        if warning_type == 'break_reminder':
            print(f"\n{message}")
            print(f"💡 {suggestion}")
        elif warning_type in ['max_session', 'daily_limit']:
            print(f"\n{message}")
            print(f"⚠️ {suggestion}")
        elif warning_type in ['high_pitch_strain', 'excessive_force']:
            print(f"\r{message} - {suggestion}")
    
    def show_safety_summary(self, session_duration: float):
        """Show post-session safety summary"""
        if not self._validate_dependencies():
            return
        
        print("\n[ Voice Safety Summary ]")
        print(f"Session Duration: {session_duration:.1f} minutes")
        
        summary = self.safety_monitor.get_session_safety_summary()
        if summary:
            daily_total = summary['daily_total_minutes']
            status = summary['session_safety_status']
            
            print(f"Daily Total: {daily_total:.1f} minutes")
            
            if status == 'good':
                print("✅ Great session! Your voice usage was within healthy limits")
            elif status == 'break_suggested':
                print("💧 Good session! Remember to take breaks during longer practices")
            elif status == 'caution':
                print("⚠️ Long session completed. Consider shorter sessions tomorrow")
                
            if summary.get('recommendations'):
                print("\nRecommendations:")
                for rec in summary['recommendations']:
                    print(f"  • {rec}")
                    
        # Daily vocal health tip
        if self.vocal_education:
            daily_tip = self.vocal_education.get_daily_tip()
            print(f"\n💡 Daily Vocal Health Tip: {daily_tip}")
        print()
    
    def show_voice_safety_menu(self, menu_system):
        """Handle voice safety settings menu"""
        if not self._validate_dependencies():
            return
        
        while True:
            self.ui.clear_screen()
            print("[ Voice Safety & Wellness ]")
            
            settings = self.safety_monitor.get_safety_settings()
            
            options = {
                '1': f'Session Length Limits (Current: {settings["max_continuous_session"]} min)',
                '2': f'Break Reminders (Every {settings["break_interval"]} min)', 
                '3': f'Strain Detection (Threshold: {settings["strain_pitch_threshold"]} Hz)',
                '4': f'Daily Practice Limit (Current: {settings["max_daily_practice"]} min)',
                '5': 'Voice Warm-up Routines',
                '6': 'Vocal Health Education',
                'toggle': 'Toggle Safety Warnings On/Off',
                '0': 'Back to Settings'
            }
            
            self.ui.print_menu("Voice Safety Settings", options)
            choice = input("Select option: ").strip().lower()
            
            if choice == '0':
                break
            elif choice == '1':
                self._adjust_session_limits()
            elif choice == '2':
                self._adjust_break_reminders()
            elif choice == '3':
                self._adjust_strain_detection()
            elif choice == '4':
                self._adjust_daily_limits()
            elif choice == '5':
                self._show_warmup_routines()
            elif choice == '6':
                self._show_vocal_health_education()
            elif choice == 'toggle':
                self._toggle_safety_warnings()
    
    def _adjust_session_limits(self):
        """Adjust maximum session length"""
        if not self.safety_monitor:
            return
        
        self.ui.clear_screen()
        settings = self.safety_monitor.get_safety_settings()
        current = settings['max_continuous_session']
        
        print("[ Session Length Limits ]")
        print(f"Current limit: {current} minutes")
        print("Recommended: 20-30 minutes for voice training")
        print("Professional advice: Longer sessions can cause vocal fatigue")
        
        try:
            new_limit = input(f"\nEnter new limit (minutes) or press Enter to keep {current}: ").strip()
            if new_limit:
                new_value = int(new_limit)
                if 10 <= new_value <= 60:
                    settings['max_continuous_session'] = new_value
                    self.safety_monitor.update_safety_settings(settings)
                    print(f"Session limit updated to {new_value} minutes")
                else:
                    print("Please enter a value between 10 and 60 minutes")
        except ValueError:
            print("Invalid input")
            
        self.ui.wait_for_enter()
    
    def _adjust_break_reminders(self):
        """Adjust break reminder intervals"""
        if not self.safety_monitor:
            return
        
        self.ui.clear_screen()
        settings = self.safety_monitor.get_safety_settings()
        current = settings['break_interval']
        
        print("[ Break Reminder Settings ]")
        print(f"Current interval: {current} minutes")
        print("Regular breaks help prevent vocal fatigue")
        
        try:
            new_interval = input(f"\nEnter new interval (minutes) or press Enter to keep {current}: ").strip()
            if new_interval:
                new_value = int(new_interval)
                if 5 <= new_value <= 30:
                    settings['break_interval'] = new_value
                    self.safety_monitor.update_safety_settings(settings)
                    print(f"Break reminder interval updated to {new_value} minutes")
                else:
                    print("Please enter a value between 5 and 30 minutes")
        except ValueError:
            print("Invalid input")
            
        self.ui.wait_for_enter()
    
    def _adjust_strain_detection(self):
        """Adjust vocal strain detection settings"""
        if not self.safety_monitor:
            return
        
        self.ui.clear_screen()
        settings = self.safety_monitor.get_safety_settings()
        current_threshold = settings['strain_pitch_threshold']
        current_duration = settings['high_pitch_duration_limit']
        
        print("[ Vocal Strain Detection ]")
        print(f"Current high pitch threshold: {current_threshold} Hz")
        print(f"Current duration limit: {current_duration} seconds")
        print("These settings help detect potentially harmful vocal strain")
        
        print(f"\nStrain detection is {'enabled' if settings['strain_detection_active'] else 'disabled'}")
        
        toggle = input("Toggle strain detection on/off? (y/n): ").strip().lower()
        if toggle in ['y', 'yes']:
            settings['strain_detection_active'] = not settings['strain_detection_active']
            self.safety_monitor.update_safety_settings(settings)
            state = "enabled" if settings['strain_detection_active'] else "disabled"
            print(f"Strain detection {state}")
            
        self.ui.wait_for_enter()
    
    def _adjust_daily_limits(self):
        """Adjust daily practice time limits"""
        if not self.safety_monitor:
            return
        
        self.ui.clear_screen()
        settings = self.safety_monitor.get_safety_settings()
        current = settings['max_daily_practice']
        
        print("[ Daily Practice Limits ]")
        print(f"Current limit: {current} minutes")
        print("Daily limits help prevent overuse and vocal fatigue")
        print("Professional singers typically limit intensive practice")
        
        try:
            new_limit = input(f"\nEnter new daily limit (minutes) or press Enter to keep {current}: ").strip()
            if new_limit:
                new_value = int(new_limit)
                if 30 <= new_value <= 300:  # 30 minutes to 5 hours
                    settings['max_daily_practice'] = new_value
                    self.safety_monitor.update_safety_settings(settings)
                    print(f"Daily practice limit updated to {new_value} minutes")
                else:
                    print("Please enter a value between 30 and 300 minutes")
        except ValueError:
            print("Invalid input")
            
        self.ui.wait_for_enter()
    
    def _show_warmup_routines(self):
        """Show available voice warmup routines"""
        if not self.warmup_routines:
            return
        
        self.ui.clear_screen()
        print("[ Voice Warm-up Routines ]")
        print("These routines help prepare your voice safely for training:")
        print()
        
        gentle_warmup = self.warmup_routines.get_routine('gentle_warmup')
        cooldown = self.warmup_routines.get_routine('cooldown')
        strain_relief = self.warmup_routines.get_routine('strain_relief')
        
        print("1. Gentle Warm-up (3 minutes)")
        print("   • Prepares your voice for practice")
        print("   • Reduces risk of vocal strain")
        print()
        print("2. Voice Cool-down (2 minutes)")
        print("   • Helps your voice relax after practice")
        print("   • Important for vocal health")
        print()
        print("3. Strain Relief Routine (4 minutes)")
        print("   • Use if you feel vocal tension")
        print("   • Includes complete vocal rest")
        print()
        print("💡 Tip: Always warm up before intensive practice!")
        print("⚠️  Stop any routine if you feel pain or discomfort")
        
        self.ui.wait_for_enter()
    
    def _show_vocal_health_education(self):
        """Show vocal health education content"""
        if not self.vocal_education:
            return
        
        self.ui.clear_screen()
        print("[ Vocal Health Education ]")
        print("Essential knowledge for safe voice training:")
        print()
        
        for category, tips in self.vocal_education.get_all_tips().items():
            category_name = category.replace('_', ' ').title()
            print(f"🔹 {category_name}:")
            for tip in tips:
                print(f"   • {tip}")
            print()
            
        print("📚 Remember: This app provides general guidance.")
        print("🩺 Consult a speech-language pathologist for persistent voice problems.")
        
        self.ui.wait_for_enter()
    
    def _toggle_safety_warnings(self):
        """Toggle safety warning system on/off"""
        if not self.safety_monitor:
            return
        
        settings = self.safety_monitor.get_safety_settings()
        current_state = settings['warnings_active']
        
        settings['warnings_active'] = not current_state
        self.safety_monitor.update_safety_settings(settings)
        
        state_text = "enabled" if settings['warnings_active'] else "disabled"
        print(f"\nSafety warnings {state_text}")
        self.ui.wait_for_enter()
    
    def get_safety_settings_summary(self) -> Optional[Dict[str, Any]]:
        """Get safety settings summary for external use"""
        if not self.safety_monitor:
            return None
        
        return self.safety_monitor.get_safety_settings()
    
    def run_guided_warmup(self, routine_name: str = 'gentle_warmup') -> bool:
        """Run a guided warmup routine"""
        if not self.warmup_routines or not self.ui:
            return False
        
        routine = self.warmup_routines.get_routine(routine_name)
        if not routine:
            self.ui.print_error(f"Warmup routine '{routine_name}' not found")
            return False
        
        self.ui.clear_screen()
        print(f"[ {routine['name']} ]")
        print(f"Duration: {routine['duration'] // 60} minutes {routine['duration'] % 60} seconds")
        print()
        
        self.ui.wait_for_enter("Press Enter to begin warmup routine...")
        
        # Guide through each step
        for step in routine['steps']:
            time_marker = step['time']
            instruction = step['instruction']
            pitch_range = step.get('pitch_range')
            
            self.ui.clear_screen()
            print(f"[ Step - {time_marker}s ]")
            print(f"Instruction: {instruction}")
            
            if pitch_range:
                print(f"Pitch range: {pitch_range[0]}-{pitch_range[1]} Hz")
            
            print(f"\nFollow this instruction for the designated time.")
            print("Press Enter when ready for next step...")
            input()
        
        self.ui.clear_screen()
        print("🎉 Warmup routine completed!")
        print("Your voice is now prepared for training.")
        self.ui.wait_for_enter()
        
        return True
    
    def check_session_safety(self, session_duration: float) -> Dict[str, Any]:
        """Check if session duration is safe"""
        if not self.safety_monitor:
            return {'status': 'unknown', 'message': 'Safety monitor not available'}
        
        summary = self.safety_monitor.get_session_safety_summary()
        if not summary:
            return {'status': 'unknown', 'message': 'No session data available'}
        
        status = summary.get('session_safety_status', 'unknown')
        
        safety_check = {
            'status': status,
            'session_duration': session_duration,
            'daily_total': summary.get('daily_total_minutes', 0),
            'recommendations': summary.get('recommendations', [])
        }
        
        if status == 'good':
            safety_check['message'] = 'Session duration is within safe limits'
        elif status == 'break_suggested':
            safety_check['message'] = 'Consider taking breaks during longer sessions'
        elif status == 'caution':
            safety_check['message'] = 'Session was quite long - consider shorter sessions'
        else:
            safety_check['message'] = 'Unable to assess session safety'
        
        return safety_check
    
    def get_daily_health_tip(self) -> str:
        """Get daily vocal health tip"""
        if not self.vocal_education:
            return "Stay hydrated and take breaks during voice training!"
        
        return self.vocal_education.get_daily_tip()
    
    def _validate_dependencies(self) -> bool:
        """Validate that required dependencies are available"""
        return (self.safety_monitor is not None and 
                self.ui is not None)