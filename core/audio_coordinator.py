import os
from typing import Dict, Any, List
from utils.emoji_handler import safe_print, convert_emoji_text, get_status_indicator


class VoiceAudioAnalyzerCoordinator:
    """Coordinates audio file analysis features for GUI integration"""

    def __init__(self, config_file="data/voice_config.json"):
        self.config_file = config_file

        # Components (will be injected)
        self.audio_file_analyzer = None
        self.pitch_goal_manager = None
        self.config_manager = None
        # Analyzer for GUI access
        self.analyzer = None

    def set_dependencies(self, audio_file_analyzer, pitch_goal_manager, ui, config_manager):
        """Inject dependencies"""
        self.audio_file_analyzer = audio_file_analyzer
        self.pitch_goal_manager = pitch_goal_manager
        self.config_manager = config_manager
        # Set analyzer reference for GUI
        self.analyzer = audio_file_analyzer

    def analyze_audio_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze an audio file and return results"""
        if not self._validate_dependencies():
            return {}

        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Check if file format is supported
            if not self.audio_file_analyzer.is_supported_file(file_path):
                supported_formats = ", ".join(self.audio_file_analyzer.supported_formats)
                raise ValueError(f"Unsupported file format. Supported formats: {supported_formats}")

            # Perform analysis
            analysis_result = self.audio_file_analyzer.full_analysis(file_path)

            if analysis_result:
                # Save to history
                self.pitch_goal_manager.add_analysis_result(analysis_result)
                return analysis_result
            else:
                raise RuntimeError("Analysis failed")

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AudioCoordinator.analyze_audio_file")
            return {}

    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get analysis history for GUI display"""
        if not self.pitch_goal_manager:
            return []

        try:
            return self.pitch_goal_manager.get_analysis_history()
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AudioCoordinator.get_analysis_history")
            return []

    def suggest_goal_from_analysis(self, analysis_result: Dict[str, Any]) -> tuple:
        """Get goal suggestion from analysis"""
        if not self.pitch_goal_manager:
            return (None, None)

        try:
            return self.pitch_goal_manager.suggest_goal_from_analysis(analysis_result)
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AudioCoordinator.suggest_goal_from_analysis")
            return (None, None)

    def set_goal_from_analysis(self, analysis_result: Dict[str, Any]) -> tuple:
        """Set training goal from analysis result"""
        if not self.pitch_goal_manager:
            return (None, None)

        try:
            low, high = self.pitch_goal_manager.set_goal_from_analysis(analysis_result)
            if low and high and self.config_manager:
                # Reload config to pick up changes
                self.config_manager.load_config()
            return (low, high)
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AudioCoordinator.set_goal_from_analysis")
            return (None, None)

    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of all analyses"""
        if not self.pitch_goal_manager:
            return {}

        try:
            history = self.pitch_goal_manager.get_analysis_history()
            if not history:
                return {'total_analyses': 0, 'message': 'No analyses found'}

            total = len(history)
            latest = history[-1] if history else None

            return {
                'total_analyses': total,
                'latest_analysis': latest,
                'has_data': total > 0
            }
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AudioCoordinator.get_analysis_summary")
            return {}

    def stop_audio(self):
        """Stop any audio processing - called during cleanup"""
        try:
            if self.audio_file_analyzer and hasattr(self.audio_file_analyzer, 'stop'):
                self.audio_file_analyzer.stop()
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "AudioCoordinator.stop_audio")

    def _validate_dependencies(self) -> bool:
        """Validate that required components are available"""
        return (self.audio_file_analyzer is not None and
                self.pitch_goal_manager is not None)