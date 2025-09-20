"""
Component factory for managing voice training components with dependency injection
"""

from typing import Any, Dict, Optional, Callable, List
from utils.lazy_loader import LazyLoader
from utils.file_operations import get_logger


class ComponentFactory:
    """Factory for creating and managing voice training components"""
    
    def __init__(self, config_file: str = "data/voice_config.json"):
        self.config_file = config_file
        self._lazy_loader = LazyLoader()
        self._component_registry: Dict[str, Dict[str, Any]] = {}
        self._singletons: Dict[str, Any] = {}
        self._dependency_graph: Dict[str, List[str]] = {}
        self.logger = get_logger()

        # Register core components
        self._register_core_components()
    
    def _register_core_components(self):
        """Register all core voice training components"""
        
        # Core voice analysis components
        self.register_component(
            'voice_analyzer',
            factory=lambda: self._create_voice_analyzer(),
            singleton=True,
            cleanup=lambda x: None
        )
        
        self.register_component(
            'audio_manager', 
            factory=lambda: self._create_audio_manager(),
            singleton=True,
            cleanup=lambda x: x.stop_processing(),
            dependencies=['voice_analyzer']
        )
        
        self.register_component(
            'alert_system',
            factory=lambda: self._create_alert_system(),
            singleton=True,
            cleanup=lambda x: x.cleanup()
        )
        
        # Exercise and training components
        self.register_component(
            'voice_exercises',
            factory=lambda: self._create_voice_exercises(),
            singleton=True
        )
        
        self.register_component(
            'progress_tracker',
            factory=lambda: self._create_progress_tracker(),
            singleton=True
        )
        
        # Audio analysis components
        self.register_component(
            'audio_file_analyzer',
            factory=lambda: self._create_audio_file_analyzer(),
            singleton=True
        )
        
        self.register_component(
            'pitch_goal_manager',
            factory=lambda: self._create_pitch_goal_manager(),
            singleton=True
        )
        
        # Safety components
        self.register_component(
            'safety_monitor',
            factory=lambda: self._create_safety_monitor(),
            singleton=True
        )
        
        self.register_component(
            'warmup_routines',
            factory=lambda: self._create_warmup_routines(),
            singleton=True
        )
        
        self.register_component(
            'vocal_education',
            factory=lambda: self._create_vocal_education(),
            singleton=True
        )
        
        # Onboarding component
        self.register_component(
            'onboarding',
            factory=lambda: self._create_onboarding(),
            singleton=True
        )
    
    def register_component(self, name: str, factory: Callable[[], Any], 
                         singleton: bool = False, cleanup: Optional[Callable[[Any], None]] = None,
                         dependencies: Optional[list] = None):
        """Register a component with the factory"""
        self._component_registry[name] = {
            'factory': factory,
            'singleton': singleton,
            'cleanup': cleanup,
            'dependencies': dependencies or []
        }

    def _validate_dependencies(self, component_name: str, dependencies: List[str]):
        """Validate that all dependencies are registered and check for circular dependencies"""
        for dep_name in dependencies:
            if dep_name not in self._component_registry:
                raise ValueError(f"Dependency '{dep_name}' for component '{component_name}' is not registered")

        # Simple circular dependency check
        self._check_circular_dependencies(component_name, dependencies, set())

    def _check_circular_dependencies(self, component_name: str, dependencies: List[str], visited: set):
        """Check for circular dependencies in the dependency graph"""
        if component_name in visited:
            raise ValueError(f"Circular dependency detected involving component '{component_name}'")

        visited.add(component_name)
        for dep_name in dependencies:
            dep_config = self._component_registry.get(dep_name, {})
            dep_dependencies = dep_config.get('dependencies', [])
            self._check_circular_dependencies(dep_name, dep_dependencies, visited.copy())

    def get_component(self, name: str) -> Any:
        """Get a component instance, creating it if necessary with proper error handling"""
        if name not in self._component_registry:
            self.logger.error(f"Component '{name}' not registered")
            raise ValueError(f"Component '{name}' not registered")

        config = self._component_registry[name]

        # Check if singleton and already created
        if config['singleton'] and name in self._singletons:
            return self._singletons[name]

        try:
            # Validate dependencies before creation
            self._validate_dependencies(name, config['dependencies'])

            # Create dependencies first
            dependencies = {}
            for dep_name in config['dependencies']:
                try:
                    dependencies[dep_name] = self.get_component(dep_name)
                except Exception as e:
                    self.logger.error(f"Failed to create dependency '{dep_name}' for '{name}': {e}")
                    raise

            # Create component
            self.logger.debug(f"Creating component '{name}'")
            component = config['factory']()

            if component is None:
                self.logger.error(f"Factory for '{name}' returned None")
                raise RuntimeError(f"Failed to create component '{name}'")

            # Store singleton
            if config['singleton']:
                self._singletons[name] = component

            self.logger.info(f"Successfully created component '{name}'")
            return component

        except Exception as e:
            self.logger.error(f"Error creating component '{name}': {e}")
            raise RuntimeError(f"Failed to create component '{name}': {e}") from e
    
    def cleanup_component(self, name: str):
        """Cleanup a specific component"""
        if name in self._singletons:
            component = self._singletons[name]
            config = self._component_registry.get(name, {})

            if config.get('cleanup'):
                try:
                    config['cleanup'](component)
                    self.logger.debug(f"Successfully cleaned up component '{name}'")
                except Exception as e:
                    # Log but don't raise - we still want to remove from singletons
                    self.logger.warning(f"Cleanup failed for component '{name}': {e}")

            del self._singletons[name]
    
    def cleanup_all(self):
        """Cleanup all managed components"""
        for name in list(self._singletons.keys()):
            self.cleanup_component(name)
    
    # Component factory methods
    def _create_voice_analyzer(self):
        """Create VoiceAnalyzer instance"""
        from voice_core import VoiceAnalyzer
        return VoiceAnalyzer()
    
    def _create_audio_manager(self):
        """Create AudioManager instance"""
        from voice_core import AudioManager
        analyzer = self.get_component('voice_analyzer')
        return AudioManager(analyzer)
    
    def _create_alert_system(self):
        """Create AlertSystem instance"""
        from voice_core import AlertSystem
        return AlertSystem()
    
    def _create_voice_exercises(self):
        """Create VoiceExercises instance"""
        from voice_exercises import VoiceExercises
        return VoiceExercises()
    
    def _create_progress_tracker(self):
        """Create ProgressTracker instance"""
        from voice_exercises import ProgressTracker
        return ProgressTracker()
    
    def _create_audio_file_analyzer(self):
        """Create AudioFileAnalyzer instance"""
        from voice_pitch_analyzer import AudioFileAnalyzer
        return AudioFileAnalyzer()
    
    def _create_pitch_goal_manager(self):
        """Create PitchGoalManager instance"""
        from voice_pitch_analyzer import PitchGoalManager
        return PitchGoalManager(self.config_file)
    
    def _create_safety_monitor(self):
        """Create VoiceSafetyMonitor instance"""
        from voice_safety import VoiceSafetyMonitor
        return VoiceSafetyMonitor()
    
    def _create_warmup_routines(self):
        """Create VoiceWarmupRoutines instance"""
        from voice_safety import VoiceWarmupRoutines
        return VoiceWarmupRoutines()
    
    def _create_vocal_education(self):
        """Create VocalHealthEducation instance"""
        from voice_safety import VocalHealthEducation
        return VocalHealthEducation()
    
    def _create_onboarding(self):
        """Create OnboardingWizard instance"""
        from voice_onboarding import OnboardingWizard
        from voice_ui import TerminalUI
        ui = TerminalUI()  # Simple dependency for now
        return OnboardingWizard(ui, self.config_file)


# Global factory instance
_global_factory: Optional[ComponentFactory] = None


def get_component_factory(config_file: str = "data/voice_config.json") -> ComponentFactory:
    """Get the global component factory instance"""
    global _global_factory
    if _global_factory is None:
        _global_factory = ComponentFactory(config_file)
    return _global_factory


def create_component(name: str, config_file: str = "data/voice_config.json") -> Any:
    """Helper function to create components via global factory"""
    factory = get_component_factory(config_file)
    return factory.get_component(name)


def cleanup_all_components():
    """Cleanup all components in the global factory"""
    global _global_factory
    if _global_factory:
        _global_factory.cleanup_all()
        _global_factory = None