"""
Aria Voice Studio - Public Beta (v5) - Encouragement Integration Helper
Integration between encouragement engine, celebrations, and training system
"""

from typing import Dict, Any, Optional, List
from .encouragement_engine import EncouragementEngine
from .achievement_system import VoiceAchievementSystem


class EncouragementIntegration:
    """
    Helper class to integrate encouragement and celebration systems
    with the existing training workflow
    """
    
    def __init__(self, session_manager, achievement_system: VoiceAchievementSystem = None):
        """
        Initialize encouragement integration
        
        Args:
            session_manager: VoiceSessionManager instance
            achievement_system: VoiceAchievementSystem instance (optional)
        """
        self.session_manager = session_manager
        self.achievement_system = achievement_system or VoiceAchievementSystem()
        self.encouragement_engine = EncouragementEngine()
        
        # Track previous state for detecting new achievements
        self.previous_achievement_count = 0
        self.last_encouragement_time = 0
        self.encouragement_cooldown = 600  # 10 minutes between random encouragement
        
    def get_session_context(self) -> Dict[str, Any]:
        """
        Build context for encouragement system from current session state
        
        Returns:
            Dictionary with session context data
        """
        import time
        
        # Get session summary
        summary = self.session_manager.get_session_summary()
        if not summary:
            return {}
        
        # Get session history
        sessions = self.session_manager.weekly_sessions
        session_count = len(sessions)
        
        # Calculate streak
        streak_info = self.achievement_system.calculate_streaks(sessions)
        current_streak = streak_info.get('current_streak', 0)
        
        # Assess performance
        stats = summary.get('stats', {})
        voice_quality = self._assess_performance(stats)
        
        # Calculate session duration
        duration_seconds = summary.get('active_training_seconds', 0)
        duration_minutes = duration_seconds / 60
        
        # Check for new achievements
        total_time = sum(s.get('duration_minutes', 0) for s in sessions)
        pitch_data = self.achievement_system.calculate_pitch_achievements(sessions)
        all_achievements = self.achievement_system.get_all_achievements(
            session_count, total_time, streak_info, pitch_data, sessions
        )
        earned_achievements = [a for a in all_achievements if a['earned']]
        new_achievement = len(earned_achievements) > self.previous_achievement_count
        
        # Determine if this is a milestone session
        is_milestone = self._is_milestone_session(session_count, current_streak)
        
        context = {
            'session_count': session_count,
            'session_duration': duration_minutes,
            'current_streak': current_streak,
            'performance': voice_quality,
            'achievement_unlocked': earned_achievements[-1] if new_achievement else None,
            'is_milestone': is_milestone,
            'session_stats': stats,
            'goal_achievement_percent': self._get_goal_achievement_percent(stats),
            'new_achievements': earned_achievements[self.previous_achievement_count:] if new_achievement else []
        }
        
        # Update previous count
        self.previous_achievement_count = len(earned_achievements)
        
        return context
    
    def _assess_performance(self, stats: Dict[str, Any]) -> str:
        """
        Assess session performance level
        
        Args:
            stats: Session statistics dictionary
            
        Returns:
            Performance level: 'excellent', 'good', 'fair', or 'struggling'
        """
        # Check safety warnings
        safety_warnings = stats.get('safety_warnings', {})
        total_warnings = sum(safety_warnings.values())
        
        # Check voice quality metrics
        strain_events = stats.get('strain_events', 0)
        avg_hnr = stats.get('avg_hnr', 20)
        
        # Calculate goal achievement
        total_time = stats.get('total_time', 1)
        time_in_range = stats.get('time_in_range', 0)
        goal_percent = (time_in_range / total_time * 100) if total_time > 0 else 0
        
        # Assess performance
        if total_warnings > 5 or strain_events > 10 or avg_hnr < 10:
            return 'struggling'
        elif goal_percent >= 80 and strain_events < 3 and avg_hnr > 18:
            return 'excellent'
        elif goal_percent >= 50 and strain_events < 5:
            return 'good'
        else:
            return 'fair'
    
    def _get_goal_achievement_percent(self, stats: Dict[str, Any]) -> float:
        """Calculate goal achievement percentage"""
        total_time = stats.get('total_time', 1)
        time_in_range = stats.get('time_in_range', 0)
        return (time_in_range / total_time * 100) if total_time > 0 else 0
    
    def _is_milestone_session(self, session_count: int, streak: int) -> bool:
        """Check if current session is a milestone"""
        milestone_sessions = [1, 3, 5, 10, 20, 50, 100, 200]
        milestone_streaks = [3, 7, 14, 30, 100]
        
        return session_count in milestone_sessions or streak in milestone_streaks
    
    def should_show_during_session_encouragement(self) -> bool:
        """
        Check if encouragement should be shown during active session
        
        Returns:
            True if encouragement should be displayed
        """
        import time
        
        summary = self.session_manager.get_session_summary()
        if not summary:
            return False
        
        # Check cooldown
        current_time = time.time()
        if current_time - self.last_encouragement_time < self.encouragement_cooldown:
            return False
        
        stats = summary.get('stats', {})
        duration_seconds = summary.get('active_training_seconds', 0)
        duration_minutes = duration_seconds / 60
        
        # Build context
        safety_warnings = stats.get('safety_warnings', {})
        total_warnings = sum(safety_warnings.values())
        performance = self._assess_performance(stats)
        
        context = {
            'session_duration': duration_minutes,
            'safety_warnings': total_warnings,
            'is_struggling': performance == 'struggling'
        }
        
        should_show = self.encouragement_engine.should_show_encouragement(context)
        
        if should_show:
            self.last_encouragement_time = current_time
            
        return should_show
    
    def get_during_session_encouragement(self) -> Optional[str]:
        """Get encouragement message to show during active session"""
        if not self.should_show_during_session_encouragement():
            return None
        
        context = self.get_session_context()
        return self.encouragement_engine.get_encouragement(context)
    
    def get_session_end_summary(self) -> str:
        """
        Get comprehensive session end summary with encouragement
        
        Returns:
            Formatted summary message
        """
        context = self.get_session_context()
        return self.encouragement_engine.get_session_end_message(context)
    
    def get_new_achievements(self) -> List[Dict]:
        """Get list of newly earned achievements this session"""
        context = self.get_session_context()
        return context.get('new_achievements', [])
    
    def reset_session_tracking(self):
        """Reset tracking for new session"""
        self.last_encouragement_time = 0
        # Don't reset achievement count - it persists across sessions


# Example usage in training screen:
"""
# In TrainingScreen.__init__():
from core.encouragement_integration import EncouragementIntegration
from gui.components import CelebrationManager

self.encouragement = EncouragementIntegration(
    self.voice_trainer.session_manager,
    self.voice_trainer.factory.get_component('achievement_system')
)
self.celebration_manager = CelebrationManager(self)

# During active training (in update_stats or similar):
if self.encouragement.should_show_during_session_encouragement():
    message = self.encouragement.get_during_session_encouragement()
    if message:
        self.celebration_manager.show_toast(message, "💙", duration_ms=4000)

# In stop_training():
# Get new achievements
new_achievements = self.encouragement.get_new_achievements()

# Show achievement celebrations
for achievement in new_achievements:
    if achievement.get('rarity') in ['epic', 'legendary']:
        # Full-screen celebration for epic/legendary
        self.celebration_manager.show_achievement_celebration(achievement)
    else:
        # Toast for common/uncommon/rare
        self.celebration_manager.show_toast(
            f"{achievement['name']}\n{achievement['description']}",
            "🏆",
            duration_ms=5000
        )

# Show session summary
summary_message = self.encouragement.get_session_end_summary()
# Display summary_message in session summary dialog

# Reset for next session
self.encouragement.reset_session_tracking()
"""
