import sys
import builtins

from utils.emoji_handler import safe_print

builtins.__print__ = builtins.print
builtins.print = safe_print

from core.component_factory import get_component_factory, cleanup_all_components
from core.session_manager import VoiceSessionManager
from core.training_controller import VoiceTrainingController
from core.configuration_manager import VoiceConfigurationManager
from core.audio_coordinator import VoiceAudioAnalyzerCoordinator
from core.safety_coordinator import VoiceSafetyCoordinator

from utils.error_handler import log_error

class VoiceTrainer:
    """Main coordinator for voice training components"""

    def __init__(self, config_file="data/voice_config.json"):

        self.factory = get_component_factory(config_file)


        self.config_manager = VoiceConfigurationManager(config_file)
        self.session_manager = VoiceSessionManager(config_file)

        self.training_controller = VoiceTrainingController()
        self.audio_coordinator = VoiceAudioAnalyzerCoordinator(config_file)
        self.safety_coordinator = VoiceSafetyCoordinator()

        self._initialize_dependencies()

        self._validate_system_integrity()

    def _initialize_dependencies(self):
        """Initialize and wire up all component dependencies"""

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

        self.training_controller.set_dependencies(
            session_manager=self.session_manager,
            audio_manager=audio_manager,
            safety_monitor=safety_monitor,
            progress_tracker=progress_tracker,
            analyzer=analyzer,
            alert_system=alert_system
        )

        self.audio_coordinator.set_dependencies(
            audio_file_analyzer=audio_file_analyzer,
            pitch_goal_manager=pitch_goal_manager,
            ui=None,
            config_manager=self.config_manager
        )

        self.safety_coordinator.set_dependencies(
            safety_monitor=safety_monitor,
            warmup_routines=warmup_routines,
            vocal_education=vocal_education,
            ui=None,
            config_manager=self.config_manager
        )

    def _validate_system_integrity(self):
        """Validate that all critical components are properly initialized and connected"""
        from utils.file_operations import get_logger
        logger = get_logger()

        critical_components = [
            ('config_manager', self.config_manager),
            ('session_manager', self.session_manager),
            ('training_controller', self.training_controller),
            ('audio_coordinator', self.audio_coordinator),
            ('safety_coordinator', self.safety_coordinator),
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

    def is_onboarding_needed(self):
        """Check if onboarding is needed"""
        return self.config_manager.is_onboarding_needed()

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

            if self.training_controller:
                self.training_controller.cleanup()

            self.factory.cleanup_all()

            cleanup_all_components()

        except Exception as e:
            from utils.file_operations import get_logger
            get_logger().error(f"Cleanup error: {e}")