"""
Session Templates - Predefined training configurations for quick start
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SessionTemplate:
    """Template for quick-start training sessions"""
    
    name: str
    description: str
    duration_minutes: int
    goal_range: tuple
    exercises: List[str]
    intensity: str = "medium"
    icon: str = "⚡"
    
    def get_duration_display(self) -> str:
        """Format duration for display"""
        if self.duration_minutes < 60:
            return f"{self.duration_minutes}min"
        else:
            hours = self.duration_minutes // 60
            mins = self.duration_minutes % 60
            if mins == 0:
                return f"{hours}h"
            return f"{hours}h {mins}m"


def get_5min_warmup() -> SessionTemplate:
    """5-minute warmup session - basic exercises, low intensity"""
    return SessionTemplate(
        name="5-Min Warmup",
        description="Quick warmup with basic exercises",
        duration_minutes=5,
        goal_range=(165, 220),
        exercises=["breathing", "humming"],
        intensity="low",
        icon="🔥"
    )


def get_full_training() -> SessionTemplate:
    """30-minute full training - all exercises, target range"""
    return SessionTemplate(
        name="Full Training",
        description="Complete training session with all exercises",
        duration_minutes=30,
        goal_range=(165, 220),
        exercises=["breathing", "humming", "pitch_slides", "lip_trills", "resonance_shift", "straw_phonation"],
        intensity="medium",
        icon="💪"
    )


def get_focus_resonance() -> SessionTemplate:
    """15-minute resonance focus - resonance exercises only"""
    return SessionTemplate(
        name="Focus on Resonance",
        description="Targeted resonance training",
        duration_minutes=15,
        goal_range=(165, 220),
        exercises=["humming", "resonance_shift"],
        intensity="medium",
        icon="🎯"
    )


def get_quick_practice() -> SessionTemplate:
    """10-minute quick practice - pitch stability focus"""
    return SessionTemplate(
        name="Quick Practice",
        description="Short session focused on pitch stability",
        duration_minutes=10,
        goal_range=(165, 220),
        exercises=["breathing", "pitch_slides", "humming"],
        intensity="low",
        icon="⚡"
    )


def get_all_templates() -> List[SessionTemplate]:
    """Get all available session templates"""
    return [
        get_5min_warmup(),
        get_full_training(),
        get_focus_resonance(),
        get_quick_practice()
    ]


def get_template(name: str) -> Optional[SessionTemplate]:
    """Get a specific template by name"""
    templates = {
        "5-Min Warmup": get_5min_warmup(),
        "Full Training": get_full_training(),
        "Focus on Resonance": get_focus_resonance(),
        "Quick Practice": get_quick_practice()
    }
    return templates.get(name)


def get_adaptive_template(session_history: List = None, time_of_day: str = None) -> SessionTemplate:
    """Get adaptive template based on recent session performance and time
    
    Args:
        session_history: List of recent session data
        time_of_day: Time period (morning/afternoon/evening/night)
        
    Returns:
        SessionTemplate adjusted for user's current situation
    """
    from datetime import datetime
    import statistics
    
    # Determine time of day if not provided
    if time_of_day is None:
        hour = datetime.now().hour
        if 5 <= hour < 12:
            time_of_day = 'morning'
        elif 12 <= hour < 17:
            time_of_day = 'afternoon'
        elif 17 <= hour < 22:
            time_of_day = 'evening'
        else:
            time_of_day = 'night'
    
    # Base template selection by time
    if time_of_day == 'morning':
        base_template = get_5min_warmup()
        base_template.duration_minutes = 15
    elif time_of_day == 'afternoon':
        base_template = get_full_training()
    elif time_of_day == 'evening':
        base_template = get_quick_practice()
        base_template.duration_minutes = 20
    else:  # night
        base_template = get_5min_warmup()
    
    # Adjust based on session history
    if session_history and len(session_history) >= 3:
        recent_sessions = session_history[-5:]
        
        # Check for high strain in recent sessions
        avg_strain = statistics.mean([s.get('strain_events', 0) for s in recent_sessions])
        avg_quality = [s.get('voice_quality', 'good') for s in recent_sessions]
        poor_quality_count = sum(1 for q in avg_quality if q in ['fair', 'needs_improvement'])
        
        if avg_strain > 8 or poor_quality_count >= 2:
            # Scale down difficulty
            base_template.duration_minutes = max(10, base_template.duration_minutes - 10)
            base_template.intensity = 'light'
            base_template.exercises = ['breathing', 'gentle_humming']
            base_template.name = "Recovery Session"
            base_template.description = "Light exercises for vocal recovery"
            base_template.icon = "🌿"
        
        # Check for consistent good performance
        elif avg_strain < 3 and poor_quality_count == 0:
            # User doing well - can increase challenge slightly
            if time_of_day == 'afternoon':
                base_template.duration_minutes = min(45, base_template.duration_minutes + 5)
                base_template.intensity = 'medium-high'
        
        # Adjust based on typical session duration
        typical_duration = statistics.mean([s.get('duration_minutes', 15) for s in recent_sessions])
        if typical_duration < base_template.duration_minutes - 10:
            # User typically does shorter sessions
            base_template.duration_minutes = round((base_template.duration_minutes + typical_duration) / 2)
    
    return base_template


def scale_template_difficulty(template: SessionTemplate, difficulty: str) -> SessionTemplate:
    """Scale template difficulty
    
    Args:
        template: Base template to scale
        difficulty: 'easier', 'normal', or 'harder'
        
    Returns:
        Modified template
    """
    if difficulty == 'easier':
        template.duration_minutes = max(5, template.duration_minutes - 10)
        template.intensity = 'light'
        template.exercises = template.exercises[:2]  # Fewer exercises
    elif difficulty == 'harder':
        template.duration_minutes = min(45, template.duration_minutes + 10)
        if template.intensity == 'low':
            template.intensity = 'medium'
        elif template.intensity == 'medium':
            template.intensity = 'high'
    
    return template
