"""
Aria Voice Studio - Public Beta (v5) - Encouragement Engine
Context-aware motivational messaging system
"""

import random
from typing import Dict, List, Optional, Any
from datetime import datetime
from utils.emoji_handler import convert_emoji_text


class EncouragementEngine:
    """Generates context-aware encouragement and motivational messages"""
    
    def __init__(self):
        self.message_categories = {
            'motivational': self._get_motivational_messages(),
            'educational': self._get_educational_messages(),
            'celebratory': self._get_celebratory_messages(),
            'struggling': self._get_struggling_messages(),
            'milestone': self._get_milestone_messages()
        }
        
    def _get_motivational_messages(self) -> List[str]:
        """General motivational messages"""
        return [
            convert_emoji_text("Every voice is unique and beautiful 💜", "encouragement"),
            convert_emoji_text("You're doing amazing! Keep going! ✨", "encouragement"),
            convert_emoji_text("Small steps lead to big changes 🌟", "encouragement"),
            convert_emoji_text("Your dedication is inspiring! 💪", "encouragement"),
            convert_emoji_text("Believe in your voice journey 🎵", "encouragement"),
            convert_emoji_text("You've got this! 🌈", "encouragement"),
            convert_emoji_text("Every session brings you closer to your goals 🎯", "encouragement"),
            convert_emoji_text("Your progress is real, even when it's subtle 💙", "encouragement"),
            convert_emoji_text("Practice makes progress, not perfection 🌸", "encouragement"),
            convert_emoji_text("Be proud of every step forward! ⭐", "encouragement")
        ]
    
    def _get_educational_messages(self) -> List[str]:
        """Educational tips and reminders"""
        return [
            convert_emoji_text("💡 Tip: Stay hydrated! Water helps vocal cord flexibility", "tip"),
            convert_emoji_text("💡 Reminder: Warm up gently before intense practice", "tip"),
            convert_emoji_text("💡 Did you know? Voice changes take time - be patient with yourself", "tip"),
            convert_emoji_text("💡 Tip: Record yourself to track your amazing progress!", "tip"),
            convert_emoji_text("💡 Reminder: Rest is as important as practice", "tip"),
            convert_emoji_text("💡 Tip: Breath support is the foundation of voice control", "tip"),
            convert_emoji_text("💡 Did you know? Consistency beats intensity in voice training", "tip"),
            convert_emoji_text("💡 Reminder: Listen to your body - it knows best!", "tip"),
            convert_emoji_text("💡 Tip: Resonance exercises can help shape your voice", "tip"),
            convert_emoji_text("💡 Did you know? Relaxation is key to natural vocal production", "tip")
        ]
    
    def _get_celebratory_messages(self) -> List[str]:
        """Celebration messages for achievements"""
        return [
            convert_emoji_text("Incredible work! You're a superstar! 🌟", "celebration"),
            convert_emoji_text("Wow! Look at that progress! 🎉", "celebration"),
            convert_emoji_text("You absolutely crushed it! 🔥", "celebration"),
            convert_emoji_text("Outstanding performance! 🏆", "celebration"),
            convert_emoji_text("You're on fire today! 💫", "celebration"),
            convert_emoji_text("Phenomenal dedication! ⭐", "celebration"),
            convert_emoji_text("Your hard work is paying off! 🎊", "celebration"),
            convert_emoji_text("That's what we call excellence! 💎", "celebration"),
            convert_emoji_text("You're making magic happen! ✨", "celebration"),
            convert_emoji_text("Absolutely stellar session! 🌠", "celebration")
        ]
    
    def _get_struggling_messages(self) -> List[str]:
        """Supportive messages for difficult sessions"""
        return [
            convert_emoji_text("Progress isn't always linear. You're doing great! 💙", "support"),
            convert_emoji_text("Challenging days build resilience. Keep going! 🌱", "support"),
            convert_emoji_text("It's okay to have tough sessions - they're part of growth 🌿", "support"),
            convert_emoji_text("Your effort matters more than perfection 💜", "support"),
            convert_emoji_text("Every practice counts, even the difficult ones 🌟", "support"),
            convert_emoji_text("Be kind to yourself - you're learning something new 💙", "support"),
            convert_emoji_text("Struggles are temporary, but your progress is permanent ✨", "support"),
            convert_emoji_text("You're braver than you think! Keep pushing! 💪", "support"),
            convert_emoji_text("Difficult ≠ Impossible. You've got this! 🌈", "support"),
            convert_emoji_text("Rest when needed, but don't give up! 🌸", "support")
        ]
    
    def _get_milestone_messages(self) -> Dict[str, str]:
        """Specific milestone achievement messages"""
        return {
            'first_session': convert_emoji_text("🎉 Welcome to your voice journey! First step complete!", "milestone"),
            'session_3': convert_emoji_text("🌱 Three sessions done! You're building momentum!", "milestone"),
            'session_5': convert_emoji_text("💪 Five sessions! You're forming a real habit!", "milestone"),
            'session_10': convert_emoji_text("🔥 Ten sessions! You're committed to this journey!", "milestone"),
            'session_20': convert_emoji_text("⭐ Twenty sessions! Your dedication is incredible!", "milestone"),
            'session_50': convert_emoji_text("🏆 Fifty sessions! You're a voice training warrior!", "milestone"),
            'session_100': convert_emoji_text("💎 One hundred sessions! You're a true voice master!", "milestone"),
            'streak_3': convert_emoji_text("🔥 3-day streak! You're building consistency!", "milestone"),
            'streak_7': convert_emoji_text("📅 Week-long streak! Your dedication is inspiring!", "milestone"),
            'streak_14': convert_emoji_text("💪 Two weeks strong! You're unstoppable!", "milestone"),
            'streak_30': convert_emoji_text("🏅 30-day streak! You're a consistency champion!", "milestone"),
            'long_session': convert_emoji_text("⏰ Wow! {duration} minutes of practice - that's dedication!", "milestone"),
            'personal_best': convert_emoji_text("🎯 New personal record! You're getting stronger!", "milestone"),
            'perfect_session': convert_emoji_text("✨ Perfect session! Your voice control is amazing!", "milestone"),
        }
    
    def get_encouragement(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Get context-appropriate encouragement message
        
        Args:
            context: Dictionary containing:
                - session_count: Total number of sessions
                - session_duration: Current session duration in minutes
                - current_streak: Current training streak
                - performance: 'excellent'|'good'|'fair'|'struggling'
                - achievement_unlocked: Optional achievement name
                - is_milestone: Boolean for milestone sessions
                - session_stats: Optional dict with session performance data
        
        Returns:
            Encouragement message string or None
        """
        session_count = context.get('session_count', 0)
        duration = context.get('session_duration', 0)
        performance = context.get('performance', 'good')
        achievement = context.get('achievement_unlocked')
        is_milestone = context.get('is_milestone', False)
        current_streak = context.get('current_streak', 0)
        
        # Check for specific milestone messages
        if is_milestone:
            milestone_msg = self._get_milestone_message(session_count, duration, current_streak, achievement)
            if milestone_msg:
                return milestone_msg
        
        # Check for achievement celebration
        if achievement:
            return random.choice(self.message_categories['celebratory'])
        
        # Performance-based messages
        if performance == 'struggling':
            return random.choice(self.message_categories['struggling'])
        elif performance == 'excellent':
            return random.choice(self.message_categories['celebratory'])
        
        # Long session encouragement
        if duration >= 25:
            return self.message_categories['milestone']['long_session'].format(duration=int(duration))
        
        # Default: mix of motivational and educational
        if random.random() < 0.3:  # 30% chance for educational tip
            return random.choice(self.message_categories['educational'])
        else:
            return random.choice(self.message_categories['motivational'])
    
    def _get_milestone_message(self, session_count: int, duration: float, 
                               streak: int, achievement: Optional[str] = None) -> Optional[str]:
        """Get message for specific milestones"""
        milestones = self.message_categories['milestone']
        
        # Session count milestones
        if session_count == 1:
            return milestones['first_session']
        elif session_count == 3:
            return milestones['session_3']
        elif session_count == 5:
            return milestones['session_5']
        elif session_count == 10:
            return milestones['session_10']
        elif session_count == 20:
            return milestones['session_20']
        elif session_count == 50:
            return milestones['session_50']
        elif session_count == 100:
            return milestones['session_100']
        
        # Streak milestones
        if streak == 3:
            return milestones['streak_3']
        elif streak == 7:
            return milestones['streak_7']
        elif streak == 14:
            return milestones['streak_14']
        elif streak == 30:
            return milestones['streak_30']
        
        return None
    
    def get_session_end_message(self, context: Dict[str, Any]) -> str:
        """
        Get end-of-session summary message
        
        Args:
            context: Dictionary with session performance data
            
        Returns:
            Encouraging summary message
        """
        duration = context.get('session_duration', 0)
        performance = context.get('performance', 'good')
        goal_achievement = context.get('goal_achievement_percent', 0)
        new_achievements = context.get('new_achievements', [])
        
        # Build message
        parts = []
        
        # Session completion
        parts.append(convert_emoji_text(f"✨ Session Complete! {duration:.1f} minutes of practice", "summary"))
        
        # Performance feedback
        if performance == 'excellent':
            parts.append(convert_emoji_text("🌟 Excellent session! Your voice sounded confident today!", "feedback"))
        elif performance == 'good':
            parts.append(convert_emoji_text("💙 Great work! You're making steady progress!", "feedback"))
        elif performance == 'fair':
            parts.append(convert_emoji_text("🌱 Good effort! Keep practicing, you're improving!", "feedback"))
        else:
            parts.append(convert_emoji_text("💜 Every practice counts! You showed up and that matters!", "feedback"))
        
        # Goal achievement
        if goal_achievement >= 80:
            parts.append(convert_emoji_text(f"🎯 Amazing! {goal_achievement:.0f}% goal achievement!", "stat"))
        elif goal_achievement >= 50:
            parts.append(convert_emoji_text(f"📈 Good progress! {goal_achievement:.0f}% goal achievement!", "stat"))
        
        # New achievements
        if new_achievements:
            count = len(new_achievements)
            parts.append(convert_emoji_text(f"🏆 {count} new achievement{'s' if count > 1 else ''} unlocked!", "achievement"))
        
        return "\n".join(parts)
    
    def get_random_tip(self) -> str:
        """Get a random educational tip"""
        return random.choice(self.message_categories['educational'])
    
    def get_struggling_support(self) -> str:
        """Get a supportive message for difficult sessions"""
        return random.choice(self.message_categories['struggling'])
    
    def should_show_encouragement(self, context: Dict[str, Any]) -> bool:
        """
        Determine if encouragement should be shown during session
        
        Args:
            context: Dictionary with:
                - session_duration: Current duration in minutes
                - safety_warnings: Number of safety warnings
                - recent_performance: Recent pitch performance data
                
        Returns:
            Boolean indicating if encouragement should be displayed
        """
        duration = context.get('session_duration', 0)
        warnings = context.get('safety_warnings', 0)
        struggling = context.get('is_struggling', False)
        
        # Show encouragement:
        # - After 10 minutes of practice
        # - If multiple safety warnings (user might be frustrated)
        # - If detected struggling
        # - Randomly (5% chance per check for surprise motivation)
        
        if struggling or warnings >= 3:
            return True
        
        if duration >= 10 and random.random() < 0.15:  # 15% chance after 10 min
            return True
        
        if duration >= 20 and random.random() < 0.25:  # 25% chance after 20 min
            return True
        
        return False
