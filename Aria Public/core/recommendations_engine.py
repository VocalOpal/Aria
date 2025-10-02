"""
Smart Recommendations Engine
Analyzes user patterns from session data and provides personalized, actionable insights
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from utils.emoji_handler import convert_emoji_text


class Recommendation:
    """Represents a single recommendation"""
    
    def __init__(self, category: str, message: str, priority: int, data: Optional[Dict] = None):
        self.category = category
        self.message = message
        self.priority = priority
        self.data = data or {}
    
    def __repr__(self):
        return f"Recommendation({self.category}, priority={self.priority})"


class SmartRecommendations:
    """
    Analyzes user session patterns and generates intelligent recommendations
    
    Categories:
    - exercise: Exercise suggestions based on weak areas
    - timing: Performance timing optimization
    - progression: Advancement suggestions
    - warning: Pattern warnings
    - encouragement: Achievement recognition
    """
    
    def __init__(self):
        self.recommendations = []
        
        # Pattern thresholds
        self.STRAIN_THRESHOLD_HZ = 280  # Hz above which frequent strain is detected
        self.MASTERY_THRESHOLD = 0.85  # 85% consistency = mastered
        self.DECLINE_THRESHOLD = 0.20  # 20% decline triggers warning
        self.IMPROVEMENT_THRESHOLD = 0.15  # 15% improvement triggers encouragement
        self.MIN_SESSIONS_FOR_PATTERNS = 3  # Minimum sessions needed for pattern detection
    
    def analyze_user_patterns(self, sessions: List[Dict[str, Any]]) -> None:
        """
        Analyze session data to detect patterns
        
        Args:
            sessions: List of session dictionaries (most recent first)
        """
        self.recommendations = []
        
        if not sessions:
            return
        
        # Need minimum sessions for meaningful patterns
        if len(sessions) < self.MIN_SESSIONS_FOR_PATTERNS:
            self._add_early_user_recommendations(len(sessions))
            return
        
        # Run all pattern detectors
        self._detect_strain_patterns(sessions)
        self._detect_best_performance_time(sessions)
        self._detect_mastered_exercises(sessions)
        self._detect_declining_metrics(sessions)
        self._detect_improving_metrics(sessions)
        self._detect_consistency_patterns(sessions)
        self._detect_vocal_health_patterns(sessions)
        self._detect_progression_readiness(sessions)
        
        # Sort by priority (higher = more important)
        self.recommendations.sort(key=lambda r: r.priority, reverse=True)
    
    def get_recommendations(self, max_count: int = 3) -> List[Recommendation]:
        """
        Get top recommendations
        
        Args:
            max_count: Maximum number of recommendations to return
            
        Returns:
            List of top recommendations
        """
        return self.recommendations[:max_count]
    
    def get_recommendations_text(self, max_count: int = 3) -> List[str]:
        """Get recommendation messages as formatted strings"""
        return [rec.message for rec in self.get_recommendations(max_count)]
    
    # Pattern Detection Methods
    
    def _detect_strain_patterns(self, sessions: List[Dict]) -> None:
        """Detect frequent strain above certain frequencies"""
        recent_sessions = sessions[:7]  # Last 7 sessions
        
        strain_events = []
        high_pitch_sessions = []
        
        for session in recent_sessions:
            max_pitch = session.get('max_pitch', 0)
            strain = session.get('strain_events', 0)
            
            if max_pitch > self.STRAIN_THRESHOLD_HZ:
                high_pitch_sessions.append(max_pitch)
            
            if strain > 2:  # More than 2 strain events
                strain_events.append(strain)
        
        # Frequent strain in high range
        if len(strain_events) >= 3:
            avg_strain = statistics.mean(strain_events)
            message = convert_emoji_text(
                f"⚠️ You often experience strain above {self.STRAIN_THRESHOLD_HZ}Hz. "
                f"Try gentler exercises like Humming or Sirens to build strength safely.",
                "warning"
            )
            self.recommendations.append(
                Recommendation('warning', message, priority=9, 
                             data={'avg_strain': avg_strain})
            )
        
        # Pushing too high consistently
        elif len(high_pitch_sessions) >= 4:
            avg_high = statistics.mean(high_pitch_sessions)
            message = convert_emoji_text(
                f"💡 Your range peaks around {avg_high:.0f}Hz. "
                f"Focus on stabilizing this range before pushing higher.",
                "exercise"
            )
            self.recommendations.append(
                Recommendation('exercise', message, priority=6,
                             data={'avg_peak': avg_high})
            )
    
    def _detect_best_performance_time(self, sessions: List[Dict]) -> None:
        """Identify when user performs best"""
        if len(sessions) < 5:
            return
        
        # Group sessions by hour of day
        time_performance = defaultdict(list)
        
        for session in sessions[:14]:  # Last 2 weeks
            try:
                session_time = datetime.fromisoformat(session['date'])
                hour = session_time.hour
                consistency = session.get('time_in_range_percent', 0)
                
                time_performance[hour].append(consistency)
            except (ValueError, KeyError):
                continue
        
        # Find best performing hour
        if time_performance:
            avg_by_hour = {hour: statistics.mean(scores) 
                          for hour, scores in time_performance.items() 
                          if len(scores) >= 2}
            
            if avg_by_hour:
                best_hour = max(avg_by_hour.items(), key=lambda x: x[1])
                hour_12 = best_hour[0] % 12 or 12
                period = "PM" if best_hour[0] >= 12 else "AM"
                
                # Only recommend if difference is significant (>10%)
                hour_scores = list(avg_by_hour.values())
                if max(hour_scores) - min(hour_scores) > 10:
                    message = convert_emoji_text(
                        f"🕐 Your best sessions are around {hour_12} {period} "
                        f"(avg {best_hour[1]:.0f}% consistency). Try training then!",
                        "timing"
                    )
                    self.recommendations.append(
                        Recommendation('timing', message, priority=5,
                                     data={'best_hour': best_hour[0], 'score': best_hour[1]})
                    )
    
    def _detect_mastered_exercises(self, sessions: List[Dict]) -> None:
        """Detect exercises that have been mastered"""
        if len(sessions) < 5:
            return
        
        recent_sessions = sessions[:5]
        consistencies = [s.get('time_in_range_percent', 0) for s in recent_sessions]
        
        if not consistencies:
            return
        
        avg_consistency = statistics.mean(consistencies)
        
        # Mastered current level
        if avg_consistency >= self.MASTERY_THRESHOLD * 100:
            session_type = sessions[0].get('session_type', 'training')
            
            # Suggest progression
            suggestions = {
                'training': 'Resonance Shift or Breath Control exercises',
                'free_practice': 'structured Training Sessions with specific goals',
                'warmup': 'longer Training Sessions'
            }
            
            suggestion = suggestions.get(session_type, 'more advanced exercises')
            
            message = convert_emoji_text(
                f"You've mastered this level ({avg_consistency:.0f}% consistency). "
                f"Ready to try {suggestion}?",
                "progression"
            )
            self.recommendations.append(
                Recommendation('progression', message, priority=8,
                             data={'consistency': avg_consistency, 'type': session_type})
            )
    
    def _detect_declining_metrics(self, sessions: List[Dict]) -> None:
        """Detect declining performance metrics"""
        if len(sessions) < 6:
            return
        
        # Compare recent 3 vs previous 3
        recent = sessions[:3]
        previous = sessions[3:6]
        
        recent_consistency = statistics.mean([s.get('time_in_range_percent', 0) for s in recent])
        prev_consistency = statistics.mean([s.get('time_in_range_percent', 0) for s in previous])
        
        if prev_consistency == 0:
            return
        
        decline = (prev_consistency - recent_consistency) / prev_consistency
        
        # Significant decline detected
        if decline >= self.DECLINE_THRESHOLD:
            message = convert_emoji_text(
                f"💙 Your consistency has dipped {decline*100:.0f}%. "
                f"This is normal! Try going back to basics with gentle warmups.",
                "warning"
            )
            self.recommendations.append(
                Recommendation('warning', message, priority=7,
                             data={'decline_percent': decline * 100})
            )
    
    def _detect_improving_metrics(self, sessions: List[Dict]) -> None:
        """Recognize and celebrate improvements"""
        if len(sessions) < 6:
            return
        
        # Compare recent 3 vs previous 3
        recent = sessions[:3]
        previous = sessions[3:6]
        
        recent_consistency = statistics.mean([s.get('time_in_range_percent', 0) for s in recent])
        prev_consistency = statistics.mean([s.get('time_in_range_percent', 0) for s in previous])
        
        if prev_consistency == 0:
            return
        
        improvement = (recent_consistency - prev_consistency) / prev_consistency
        
        # Significant improvement
        if improvement >= self.IMPROVEMENT_THRESHOLD:
            message = convert_emoji_text(
                f"Great progress! Your consistency improved {improvement*100:.0f}%. "
                f"Your hard work is paying off.",
                "encouragement"
            )
            self.recommendations.append(
                Recommendation('encouragement', message, priority=8,
                             data={'improvement_percent': improvement * 100})
            )
    
    def _detect_consistency_patterns(self, sessions: List[Dict]) -> None:
        """Analyze session frequency and regularity"""
        if len(sessions) < 4:
            return
        
        # Check session frequency (last 14 days)
        recent_sessions = []
        cutoff_date = datetime.now() - timedelta(days=14)
        
        for session in sessions:
            try:
                session_date = datetime.fromisoformat(session['date'])
                if session_date >= cutoff_date:
                    recent_sessions.append(session_date)
            except (ValueError, KeyError):
                continue
        
        sessions_per_week = len(recent_sessions) / 2.0  # Over 2 weeks
        
        # Low frequency warning
        if sessions_per_week < 2:
            message = convert_emoji_text(
                "💡 Training 3-4 times per week yields better results than occasional long sessions. "
                "Try shorter, more frequent practice!",
                "timing"
            )
            self.recommendations.append(
                Recommendation('timing', message, priority=6,
                             data={'sessions_per_week': sessions_per_week})
            )
        
        # High consistency praise
        elif sessions_per_week >= 4:
            message = convert_emoji_text(
                f"Strong dedication! You're training {sessions_per_week:.1f}x per week. "
                f"This consistency will bring results.",
                "encouragement"
            )
            self.recommendations.append(
                Recommendation('encouragement', message, priority=4,
                             data={'sessions_per_week': sessions_per_week})
            )
    
    def _detect_vocal_health_patterns(self, sessions: List[Dict]) -> None:
        """Monitor vocal health indicators"""
        recent_sessions = sessions[:5]
        
        # Check for concerning vocal health metrics
        high_jitter_count = 0
        low_hnr_count = 0
        
        for session in recent_sessions:
            jitter = session.get('avg_jitter', 0)
            hnr = session.get('avg_hnr', 20)  # Default healthy HNR
            
            if jitter > 0.015:  # High jitter (roughness)
                high_jitter_count += 1
            
            if hnr < 10:  # Low HNR (noisy voice)
                low_hnr_count += 1
        
        # Multiple sessions with rough voice quality
        if high_jitter_count >= 3:
            message = convert_emoji_text(
                "💙 Your voice quality shows roughness recently. "
                "Take a rest day, stay hydrated, and focus on gentle warmups.",
                "warning"
            )
            self.recommendations.append(
                Recommendation('warning', message, priority=9,
                             data={'high_jitter_sessions': high_jitter_count})
            )
        
        # Good vocal health
        elif high_jitter_count == 0 and low_hnr_count == 0:
            message = convert_emoji_text(
                "Your vocal health metrics look good. "
                "Keep up the technique.",
                "encouragement"
            )
            self.recommendations.append(
                Recommendation('encouragement', message, priority=3,
                             data={'vocal_health': 'excellent'})
            )
    
    def _detect_progression_readiness(self, sessions: List[Dict]) -> None:
        """Determine if user is ready for more challenging exercises"""
        if len(sessions) < 7:
            return
        
        recent = sessions[:7]
        
        # Calculate stability metrics
        consistencies = [s.get('time_in_range_percent', 0) for s in recent]
        avg_consistency = statistics.mean(consistencies)
        consistency_variance = statistics.stdev(consistencies) if len(consistencies) > 1 else 0
        
        avg_duration = statistics.mean([s.get('duration_minutes', 0) for s in recent])
        
        # Ready for progression: high consistency, low variance, decent duration
        if (avg_consistency >= 75 and 
            consistency_variance < 10 and 
            avg_duration >= 8):
            
            message = convert_emoji_text(
                f"🚀 You're showing stable performance ({avg_consistency:.0f}% ± {consistency_variance:.0f}%). "
                f"Consider increasing session duration or trying advanced exercises!",
                "progression"
            )
            self.recommendations.append(
                Recommendation('progression', message, priority=7,
                             data={
                                 'consistency': avg_consistency,
                                 'variance': consistency_variance,
                                 'avg_duration': avg_duration
                             })
            )
    
    def _add_early_user_recommendations(self, session_count: int) -> None:
        """Special recommendations for new users with few sessions"""
        if session_count == 1:
            message = convert_emoji_text(
                "🎯 Great start! Try to practice 3-4 times this week for best results. "
                "Consistency is more important than session length!",
                "timing"
            )
            self.recommendations.append(
                Recommendation('timing', message, priority=10,
                             data={'session_count': session_count})
            )
        
        elif session_count == 2:
            message = convert_emoji_text(
                "💪 You're building momentum! Focus on finding your comfortable range "
                "before pushing for higher pitches.",
                "exercise"
            )
            self.recommendations.append(
                Recommendation('exercise', message, priority=10,
                             data={'session_count': session_count})
            )
    
    # Helper methods
    
    def _add_recommendation(self, category: str, message: str, 
                          priority: int, data: Optional[Dict] = None) -> None:
        """Helper to add recommendation"""
        self.recommendations.append(
            Recommendation(category, message, priority, data)
        )
