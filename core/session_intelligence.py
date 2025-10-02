"""
Session Intelligence - Smart recommendations based on time and user patterns
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import statistics
from utils.error_handler import log_error


class SessionIntelligence:
    """Provides intelligent session recommendations based on time and patterns"""
    
    def __init__(self):
        self.time_zones = {
            'morning': (5, 12),    # 5 AM - 12 PM
            'afternoon': (12, 17), # 12 PM - 5 PM
            'evening': (17, 22),   # 5 PM - 10 PM
            'night': (22, 5)       # 10 PM - 5 AM
        }
    
    def get_session_recommendations(self, session_history: List[Dict] = None) -> Dict[str, Any]:
        """Get smart session recommendations based on time of day and patterns
        
        Args:
            session_history: Optional list of recent session data for personalization
            
        Returns:
            dict with recommended_duration, exercises, intensity, and reasoning
        """
        try:
            current_hour = datetime.now().hour
            time_period = self._get_time_period(current_hour)
        
        # Base recommendations by time of day
        if time_period == 'morning':
            recommendations = {
                'recommended_duration': 15,  # minutes
                'min_duration': 10,
                'max_duration': 25,
                'exercises': ['breathing', 'gentle_humming', 'pitch_slides'],
                'intensity': 'light',
                'reasoning': 'Morning sessions should be gentle to warm up vocal cords',
                'notes': [
                    'Voice may be lower after sleep',
                    'Start with gentle breathing exercises',
                    'Avoid pushing for high pitches immediately'
                ]
            }
        elif time_period == 'afternoon':
            recommendations = {
                'recommended_duration': 30,
                'min_duration': 20,
                'max_duration': 45,
                'exercises': ['breathing', 'humming', 'pitch_slides', 'resonance_shift', 'lip_trills'],
                'intensity': 'medium',
                'reasoning': 'Afternoon is optimal for full training sessions',
                'notes': [
                    'Voice is warmed up from daily use',
                    'Ideal time for challenging exercises',
                    'Energy levels typically good'
                ]
            }
        elif time_period == 'evening':
            recommendations = {
                'recommended_duration': 20,
                'min_duration': 10,
                'max_duration': 30,
                'exercises': ['breathing', 'humming', 'gentle_resonance'],
                'intensity': 'light-medium',
                'reasoning': 'Evening sessions should avoid strain, focus on relaxation',
                'notes': [
                    'Vocal cords may be fatigued from daily use',
                    'Avoid high-intensity exercises',
                    'Focus on maintaining gains, not pushing limits'
                ]
            }
        else:  # night
            recommendations = {
                'recommended_duration': 10,
                'min_duration': 5,
                'max_duration': 15,
                'exercises': ['breathing', 'gentle_humming'],
                'intensity': 'very_light',
                'reasoning': 'Late night practice not recommended - rest is important',
                'notes': [
                    'Vocal rest is crucial for progress',
                    'Consider practicing earlier tomorrow',
                    'Only gentle exercises if needed'
                ]
            }
        
        # Adjust based on user history
        if session_history and len(session_history) > 0:
            recommendations = self._personalize_recommendations(
                recommendations, 
                session_history, 
                time_period
            )
        
            recommendations['time_period'] = time_period
            recommendations['current_hour'] = current_hour
            
            return recommendations
        except Exception as e:
            log_error(e, "SessionIntelligence.get_session_recommendations")
            return {
                'recommended_duration': 15,
                'exercises': ['breathing'],
                'intensity': 'light',
                'reasoning': 'Error getting recommendations - using defaults',
                'time_period': 'unknown',
                'current_hour': 0
            }
    
    def _get_time_period(self, hour: int) -> str:
        """Determine time period from hour"""
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 22:
            return 'evening'
        else:
            return 'night'
    
    def _personalize_recommendations(self, base_recs: Dict, history: List[Dict], 
                                    time_period: str) -> Dict:
        """Personalize recommendations based on user history
        
        Args:
            base_recs: Base recommendations dict
            history: List of recent sessions
            time_period: Current time period
            
        Returns:
            Modified recommendations dict
        """
        try:
            if not history:
                return base_recs
        
        # Analyze typical session duration
        recent_durations = [s.get('duration_minutes', 15) for s in history[-10:]]
        avg_duration = statistics.mean(recent_durations) if recent_durations else 15
        
        # Adjust recommended duration based on user's typical patterns
        if avg_duration > base_recs['recommended_duration']:
            # User typically does longer sessions
            adjustment = min(10, (avg_duration - base_recs['recommended_duration']) * 0.5)
            base_recs['recommended_duration'] = min(
                base_recs['max_duration'],
                base_recs['recommended_duration'] + adjustment
            )
        
        # Check for recent fatigue indicators
        recent_sessions = history[-3:] if len(history) >= 3 else history
        high_strain = any(
            s.get('strain_events', 0) > 10 or 
            s.get('voice_quality', 'good') in ['fair', 'needs_improvement']
            for s in recent_sessions
        )
        
        if high_strain:
            # Reduce intensity if recent strain detected
            base_recs['intensity'] = 'light'
            base_recs['recommended_duration'] = max(
                base_recs['min_duration'],
                base_recs['recommended_duration'] - 5
            )
                base_recs['notes'].insert(0, '⚠️ Recent strain detected - taking it easy today')
            
            return base_recs
        except Exception as e:
            log_error(e, "SessionIntelligence._personalize_recommendations")
            return base_recs
    
    def get_time_based_motivation(self) -> str:
        """Get motivational message based on time of day"""
        try:
            current_hour = datetime.now().hour
            time_period = self._get_time_period(current_hour)
            
            messages = {
                'morning': "Good morning! 🌅 Start your day with gentle practice",
                'afternoon': "Perfect timing! ☀️ Your voice is ready for training",
                'evening': "Evening practice! 🌆 Keep it light and relaxed",
                'night': "Late practice! 🌙 Consider resting - tomorrow is better"
            }
            
            return messages.get(time_period, "Ready to practice!")
        except Exception as e:
            log_error(e, "SessionIntelligence.get_time_based_motivation")
            return "Ready to practice!"
    
    def should_recommend_break(self, session_duration_minutes: int, 
                               time_period: str = None) -> bool:
        """Determine if a break should be recommended
        
        Args:
            session_duration_minutes: Current session duration
            time_period: Current time period (optional)
            
        Returns:
            True if break recommended
        """
        try:
            if time_period is None:
                time_period = self._get_time_period(datetime.now().hour)
            
            # Break thresholds by time of day
            break_thresholds = {
                'morning': 20,      # Every 20 minutes in morning
                'afternoon': 30,    # Every 30 minutes in afternoon
                'evening': 15,      # Every 15 minutes in evening
                'night': 10         # Every 10 minutes at night
            }
            
            threshold = break_thresholds.get(time_period, 25)
            return session_duration_minutes >= threshold
        except Exception as e:
            log_error(e, "SessionIntelligence.should_recommend_break")
            return session_duration_minutes >= 25
