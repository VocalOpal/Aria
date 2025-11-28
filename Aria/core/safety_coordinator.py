"""
Safety Coordinator - Handles safety monitoring and warnings for GUI integration
Cleaned of CLI artifacts - GUI handles all safety UI interactions
"""

from typing import Dict, Any, List, Optional
from utils.emoji_handler import safe_print, convert_emoji_text, get_status_indicator


class VoiceSafetyCoordinator:
    """Coordinates voice safety monitoring and wellness features for GUI"""

    def __init__(self):
        # Components (will be injected)
        self.safety_monitor = None
        self.warmup_routines = None
        self.vocal_education = None
        self.config_manager = None

    def set_dependencies(self, safety_monitor, warmup_routines, vocal_education, ui, config_manager):
        """Inject dependencies"""
        self.safety_monitor = safety_monitor
        self.warmup_routines = warmup_routines
        self.vocal_education = vocal_education
        # ui parameter kept for compatibility but not used in GUI mode
        self.config_manager = config_manager

    def handle_safety_warning(self, warning: Dict[str, Any]):
        """Handle voice safety warnings from the monitoring system"""
        # This method is kept for compatibility but warnings are now handled by GUI components
        # The actual warning display is managed by VoiceSafetyGUICoordinator in GUI mode
        warning_type = warning.get('type', 'unknown')
        message = warning.get('message', '')
        suggestion = warning.get('suggestion', '')

        # Log warning for debugging purposes
        from utils.error_handler import log_error
        log_error(None, f"Safety warning: {warning_type} - {message} - {suggestion}", "VoiceSafetyCoordinator.handle_safety_warning")

    def show_safety_summary(self, session_duration: float):
        """Generate post-session safety summary data"""
        if not self._validate_dependencies():
            return None

        # Return summary data instead of printing (GUI handles display)
        summary_data = {
            'session_duration': session_duration,
            'safety_summary': None,
            'daily_tip': None
        }

        if self.safety_monitor:
            summary_data['safety_summary'] = self.safety_monitor.get_session_safety_summary()

        if self.vocal_education:
            summary_data['daily_tip'] = self.vocal_education.get_daily_tip()

        return summary_data

    def get_safety_settings_summary(self) -> Optional[Dict[str, Any]]:
        """Get safety settings for GUI display"""
        if not self.safety_monitor:
            return None

        try:
            return self.safety_monitor.get_safety_settings()
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "VoiceSafetyCoordinator.get_safety_settings_summary")
            return None

    def run_guided_warmup(self, routine_name: str = 'gentle_warmup') -> bool:
        """Get warmup routine data for GUI to handle"""
        if not self.warmup_routines:
            return False

        try:
            routine = self.warmup_routines.get_routine(routine_name)
            if not routine:
                return False

            # Return routine data for GUI to handle
            return True

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "VoiceSafetyCoordinator.run_guided_warmup")
            return False

    def get_warmup_routines(self) -> List[Dict[str, Any]]:
        """Get list of available warmup routines"""
        if not self.warmup_routines:
            return []

        try:
            return self.warmup_routines.get_routine_list()
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "VoiceSafetyCoordinator.get_warmup_routines")
            return []

    def get_warmup_routine(self, routine_id: str) -> Optional[Dict[str, Any]]:
        """Get specific warmup routine by ID"""
        if not self.warmup_routines:
            return None

        try:
            return self.warmup_routines.get_routine(routine_id)
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "VoiceSafetyCoordinator.get_warmup_routine")
            return None

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

        return safety_check

    def get_daily_health_tip(self) -> str:
        """Get daily vocal health tip"""
        if not self.vocal_education:
            return "Practice good vocal hygiene by staying hydrated and warming up before training."

        try:
            return self.vocal_education.get_daily_tip()
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "VoiceSafetyCoordinator.get_daily_health_tip")
            return "Practice good vocal hygiene by staying hydrated and warming up before training."

    def get_vocal_education_topics(self) -> List[Dict[str, Any]]:
        """Get available vocal education topics"""
        if not self.vocal_education:
            return []

        try:
            return self.vocal_education.get_education_topics()
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "VoiceSafetyCoordinator.get_vocal_education_topics")
            return []

    def _validate_dependencies(self) -> bool:
        """Validate that required components are available"""
        return (self.safety_monitor is not None and
                self.warmup_routines is not None and
                self.vocal_education is not None and
                self.config_manager is not None)