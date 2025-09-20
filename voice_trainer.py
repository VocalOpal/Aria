"""
Voice Trainer - Main coordinator for voice training components
Refactored from monolithic 1700+ line class to clean, modular architecture
"""

import sys
import builtins

# Safe emoji handler to prevent crashes on different terminals
from utils.emoji_handler import safe_print

# Store original print function and replace it globally
builtins.__print__ = builtins.print
builtins.print = safe_print

from utils.component_factory import get_component_factory, cleanup_all_components
from core.session_manager import VoiceSessionManager
from core.training_controller import VoiceTrainingController
from core.configuration_manager import VoiceConfigurationManager
from core.audio_coordinator import VoiceAudioAnalyzerCoordinator
from core.safety_coordinator import VoiceSafetyCoordinator
from core.menu_coordinator import VoiceMenuCoordinator
from core.error_handler import log_error
from voice_ui import TerminalUI, MenuSystem


class VoiceTrainer:
    """Main coordinator for voice training components"""
    
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

        # Validate all dependencies are properly wired
        self._validate_system_integrity()
        
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

    def _validate_system_integrity(self):
        """Validate that all critical components are properly initialized and connected"""
        from utils.file_operations import get_logger
        logger = get_logger()

        # Check core components
        critical_components = [
            ('ui', self.ui),
            ('menu_system', self.menu_system),
            ('config_manager', self.config_manager),
            ('session_manager', self.session_manager),
            ('training_controller', self.training_controller),
            ('audio_coordinator', self.audio_coordinator),
            ('safety_coordinator', self.safety_coordinator),
            ('menu_coordinator', self.menu_coordinator),
            ('factory', self.factory)
        ]

        missing_components = []
        for name, component in critical_components:
            if component is None:
                missing_components.append(name)

        if missing_components:
            error_msg = f"Critical components not initialized: {', '.join(missing_components)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # Test component factory dependencies
        try:
            test_components = ['voice_analyzer', 'audio_manager', 'alert_system']
            for comp_name in test_components:
                component = self.factory.get_component(comp_name)
                if component is None:
                    raise RuntimeError(f"Factory failed to create {comp_name}")
            logger.info("System integrity validation passed")
        except Exception as e:
            logger.error(f"System integrity validation failed: {e}")
            raise RuntimeError(f"System integrity validation failed: {e}") from e

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
        except RuntimeError as e:
            # System integrity or critical component errors
            print(f"System error: {e}")
            print("The application cannot continue. Please check your installation.")
        except Exception as e:
            from utils.file_operations import get_logger
            logger = get_logger()
            logger.error(f"Unexpected error in main application: {e}")
            print(f"Unexpected error: {e}")
            print("Please check the log files for more details.")
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


# Backward compatibility removed - use utils.lazy_loader directly


if __name__ == "__main__":
    trainer = VoiceTrainer()
    trainer.run()