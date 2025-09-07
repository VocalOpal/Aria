"""
Voice Trainer - Lightweight orchestrator for voice training components
Refactored from monolithic 1700+ line class to clean, modular architecture
"""

import sys
import builtins

# Fix Unicode encoding issues on Windows
def safe_print(*args, **kwargs):
    """Print function that handles Unicode encoding gracefully"""
    try:
        builtins.__print__(*args, **kwargs)
    except UnicodeEncodeError:
        # Convert args to ASCII-friendly versions
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                # Replace common emoji with ASCII equivalents
                arg = (arg.replace('🎉', '[CELEBRATION]')
                        .replace('🌱', '[SEEDLING]')  
                        .replace('🎯', '[TARGET]')
                        .replace('⏰', '[TIME]')
                        .replace('🔔', '[BELL]')
                        .replace('⏱️', '[TIMER]')
                        .replace('💭', '[THOUGHT]')
                        .replace('🎤', '[MIC]')
                        .replace('💪', '[STRONG]')
                        .replace('🔥', '[FIRE]')
                        .replace('⭐', '[STAR]')
                        .replace('🕐', '[CLOCK]')
                        .replace('📅', '[CALENDAR]')
                        .replace('📊', '[CHART]')
                        .replace('✅', '[CHECK]')
                        .replace('🏆', '[TROPHY]')
                        .replace('❌', '[X]')
                        .replace('⚠️', '[WARNING]')
                        .replace('🚨', '[ALERT]')
                        .replace('✨', '[SPARKLES]')
                        .replace('📚', '[BOOKS]')
                        .replace('🎙️', '[STUDIO_MIC]')
                        .replace('🔊', '[SPEAKER]')
                        .replace('💡', '[BULB]')
                        .replace('🛡️', '[SHIELD]')
                        .replace('📱', '[PHONE]')
                        .replace('🎧', '[HEADPHONES]')
                        .replace('↑', '^')
                        .replace('↓', 'v'))
            safe_args.append(arg)
        builtins.__print__(*safe_args, **kwargs)

# Store original print function and replace it
builtins.__print__ = builtins.print
builtins.print = safe_print

from utils.component_factory import get_component_factory, cleanup_all_components
from core.session_manager import VoiceSessionManager
from core.training_controller import VoiceTrainingController
from core.configuration_manager import VoiceConfigurationManager
from core.audio_coordinator import VoiceAudioAnalyzerCoordinator
from core.safety_coordinator import VoiceSafetyCoordinator
from core.menu_coordinator import VoiceMenuCoordinator
from voice_ui import TerminalUI, MenuSystem


class VoiceTrainer:
    """Lightweight orchestrator for voice training components"""
    
    def __init__(self, config_file="data/voice_config.json"):
        # Initialize component factory
        self.factory = get_component_factory(config_file)
        
        # Core UI components (always needed)
        self.ui = TerminalUI()
        self.menu_system = MenuSystem(self.ui)
        
        # Core managers
        self.config_manager = VoiceConfigurationManager(config_file)
        self.session_manager = VoiceSessionManager(config_file)
        
        # Controllers
        self.training_controller = VoiceTrainingController()
        self.audio_coordinator = VoiceAudioAnalyzerCoordinator(config_file)
        self.safety_coordinator = VoiceSafetyCoordinator()
        self.menu_coordinator = VoiceMenuCoordinator()
        
        # Wire up dependencies
        self._initialize_dependencies()
        
    def _initialize_dependencies(self):
        """Initialize and wire up all component dependencies"""
        
        # Get lazy-loaded components from factory
        analyzer = self.factory.get_component('voice_analyzer')
        audio_manager = self.factory.get_component('audio_manager')
        alert_system = self.factory.get_component('alert_system')
        voice_exercises = self.factory.get_component('voice_exercises')
        progress_tracker = self.factory.get_component('progress_tracker')
        audio_file_analyzer = self.factory.get_component('audio_file_analyzer')
        pitch_goal_manager = self.factory.get_component('pitch_goal_manager')
        safety_monitor = self.factory.get_component('safety_monitor')
        warmup_routines = self.factory.get_component('warmup_routines')
        vocal_education = self.factory.get_component('vocal_education')
        
        # Wire training controller dependencies
        self.training_controller.set_dependencies(
            session_manager=self.session_manager,
            audio_manager=audio_manager,
            safety_monitor=safety_monitor,
            progress_tracker=progress_tracker,
            analyzer=analyzer,
            alert_system=alert_system
        )
        
        # Wire audio coordinator dependencies
        self.audio_coordinator.set_dependencies(
            audio_file_analyzer=audio_file_analyzer,
            pitch_goal_manager=pitch_goal_manager,
            ui=self.ui,
            config_manager=self.config_manager
        )
        
        # Wire safety coordinator dependencies
        self.safety_coordinator.set_dependencies(
            safety_monitor=safety_monitor,
            warmup_routines=warmup_routines,
            vocal_education=vocal_education,
            ui=self.ui,
            config_manager=self.config_manager
        )
        
        # Wire menu coordinator dependencies
        self.menu_coordinator.set_dependencies(
            ui=self.ui,
            menu_system=self.menu_system,
            config_manager=self.config_manager,
            session_manager=self.session_manager,
            training_controller=self.training_controller,
            audio_coordinator=self.audio_coordinator,
            safety_coordinator=self.safety_coordinator
        )
    
    def run(self):
        """Main application entry point"""
        try:
            # Check onboarding if needed
            self._check_onboarding()
            
            # Update current goal based on progress
            self.config_manager.update_current_goal(self.session_manager)
            
            # Run main menu loop
            result = self.menu_coordinator.show_main_menu_loop()
            
            if result == 'quit':
                print("Thank you for using Aria Voice Studio!")
            elif result == 'error':
                print("An error occurred. Please check your configuration.")
                
        except KeyboardInterrupt:
            print("\n\nExiting Aria Voice Studio...")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            self.cleanup()
    
    def _check_onboarding(self):
        """Check and run onboarding if needed"""
        if self.config_manager.is_onboarding_needed():
            try:
                onboarding = self.factory.get_component('onboarding')
                if onboarding.is_first_time_user():
                    initial_config = onboarding.start_onboarding()
                    if initial_config:
                        self.config_manager.update_config(initial_config)
                        self.config_manager.mark_onboarding_complete()
                        onboarding.show_post_onboarding_tips()
            except Exception as e:
                print(f"Onboarding error: {e}")
                # Continue with default configuration
                self.config_manager.mark_onboarding_complete()
    
    def get_status_summary(self):
        """Get application status summary"""
        config_summary = self.config_manager.get_config_summary()
        progress_trends = self.session_manager.get_progress_trends()
        training_status = self.training_controller.get_training_status()
        
        return {
            'config': config_summary,
            'progress': progress_trends,
            'training': training_status,
            'is_setup_complete': config_summary['setup_completed'],
            'total_sessions': len(self.session_manager.weekly_sessions)
        }
    
    def cleanup(self):
        """Cleanup all resources"""
        try:
            # Cleanup training controller
            if self.training_controller:
                self.training_controller.cleanup()
            
            # Cleanup lazy-loaded components via factory
            self.factory.cleanup_all()
            
            # Cleanup global factory
            cleanup_all_components()
            
        except Exception as e:
            print(f"Cleanup error: {e}")


# Backward compatibility functions for existing code
def lazy_init(func):
    """Backward compatibility decorator"""
    from utils.lazy_loader import lazy_property
    return lazy_property(func)


if __name__ == "__main__":
    trainer = VoiceTrainer()
    trainer.run()