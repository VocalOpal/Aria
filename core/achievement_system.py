
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class VoiceAchievementSystem:
    """Handles all achievement and streak tracking functionality"""
    
    def __init__(self):
        self.rarity_icons = {
            'common': '🥉',
            'uncommon': '🥈', 
            'rare': '🥇',
            'epic': '💜',
            'legendary': '💎'
        }
    
    def calculate_streaks(self, sessions: List[Dict]) -> Dict[str, Any]:
        """Calculate current and best training streaks"""
        if not sessions:
            return {'current_streak': 0, 'best_streak': 0, 'streak_days': []}
        
        # Convert session dates to datetime objects and sort
        session_dates = []
        for session in sessions:
            try:
                date_str = session.get('date', '')
                if date_str:
                    # Handle both ISO format and simple date format
                    if 'T' in date_str:
                        date = datetime.fromisoformat(date_str.replace('Z', '')).date()
                    else:
                        date = datetime.fromisoformat(date_str).date()
                    session_dates.append(date)
            except (ValueError, AttributeError, TypeError):
                continue  # Skip invalid date entries
        
        if not session_dates:
            return {'current_streak': 0, 'best_streak': 0, 'streak_days': []}
        
        # Get unique dates and sort
        unique_dates = sorted(set(session_dates), reverse=True)
        
        # Calculate current streak
        current_streak = 0
        today = datetime.now().date()
        
        # Start from today or yesterday (allow for today not being trained yet)
        check_date = today
        if unique_dates and unique_dates[0] == today:
            current_streak = 1
            check_date = today - timedelta(days=1)
        elif unique_dates and unique_dates[0] == today - timedelta(days=1):
            current_streak = 1
            check_date = today - timedelta(days=2)
        else:
            current_streak = 0
        
        # Count consecutive days
        for date in unique_dates[current_streak:]:
            if date == check_date:
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                break
        
        # Calculate best streak
        best_streak = 0
        temp_streak = 0
        
        for i, date in enumerate(reversed(unique_dates)):
            if i == 0:
                temp_streak = 1
            else:
                prev_date = list(reversed(unique_dates))[i-1]
                if (date - prev_date).days == 1:
                    temp_streak += 1
                else:
                    best_streak = max(best_streak, temp_streak)
                    temp_streak = 1
        
        best_streak = max(best_streak, temp_streak, current_streak)
        
        return {
            'current_streak': current_streak,
            'best_streak': best_streak,
            'streak_days': unique_dates
        }
    
    def calculate_pitch_achievements(self, sessions: List[Dict]) -> Dict[str, Any]:
        """Calculate pitch-related achievement data"""
        if not sessions:
            return {}
        
        # Get pitch data from recent sessions
        recent_sessions = sessions[-10:] if len(sessions) >= 10 else sessions
        all_sessions = sessions
        
        pitch_data = {
            'recent_avg': sum(s.get('avg_pitch', 0) for s in recent_sessions) / len(recent_sessions) if recent_sessions else 0,
            'all_time_avg': sum(s.get('avg_pitch', 0) for s in all_sessions) / len(all_sessions) if all_sessions else 0,
            'best_session': max((s.get('avg_pitch', 0) for s in all_sessions), default=0),
            'total_goal_time': sum(s.get('time_in_range', 0) for s in all_sessions),
            'longest_goal_streak': self._calculate_longest_goal_streak(all_sessions),
            'improvement_trend': self._calculate_improvement_trend(all_sessions)
        }
        
        return pitch_data
    
    def _calculate_longest_goal_streak(self, sessions: List[Dict]) -> int:
        """Calculate longest consecutive time hitting goal in recent sessions"""
        if not sessions:
            return 0
        
        recent_sessions = sessions[-5:] if len(sessions) >= 5 else sessions
        goal_rates = [s.get('goal_achievement_percent', 0) for s in recent_sessions]
        
        # Find longest consecutive streak of high goal achievement (>70%)
        longest = 0
        current = 0
        for rate in goal_rates:
            if rate > 0.7:  # 70% goal achievement
                current += 1
                longest = max(longest, current)
            else:
                current = 0
        
        return longest * 10  # Approximate seconds (very rough estimate)
    
    def _calculate_improvement_trend(self, sessions: List[Dict]) -> float:
        """Calculate pitch improvement over time"""
        if len(sessions) < 4:
            return 0
        
        # Compare first quarter to last quarter of sessions
        quarter_size = max(2, len(sessions) // 4)
        early_sessions = sessions[:quarter_size]
        recent_sessions = sessions[-quarter_size:]
        
        early_avg = sum(s.get('avg_pitch', 0) for s in early_sessions) / len(early_sessions)
        recent_avg = sum(s.get('avg_pitch', 0) for s in recent_sessions) / len(recent_sessions)
        
        return recent_avg - early_avg
    
    def get_all_achievements(self, total_sessions: int, total_time: float, 
                           streak_info: Dict, pitch_data: Dict, sessions: List[Dict]) -> List[Dict]:
        """Get list of all achievements with earned status"""
        achievements = []
        
        # Session count achievements
        session_milestones = [
            (1, "🎤 First Steps", "Completed your first training session", "common"),
            (3, "🌱 Getting Started", "Completed 3 training sessions", "common"), 
            (5, "💪 Building Habits", "Completed 5 training sessions", "common"),
            (10, "🔥 Building Momentum", "Completed 10 training sessions", "uncommon"),
            (20, "🎯 Dedicated Learner", "Completed 20 training sessions", "uncommon"),
            (50, "⭐ Voice Warrior", "Completed 50 training sessions", "rare"),
            (100, "🏆 Voice Master", "Completed 100 training sessions", "epic"),
            (200, "💎 Voice Legend", "Completed 200 training sessions", "legendary")
        ]
        
        for count, name, desc, rarity in session_milestones:
            achievements.append({
                'name': name,
                'description': desc,
                'rarity': rarity,
                'earned': total_sessions >= count,
                'progress_percent': min(100, (total_sessions / count) * 100)
            })
        
        # Time-based achievements
        time_milestones = [
            (30, "⏰ Dedicated Trainer", "Practiced for 30+ minutes total", "common"),
            (120, "🕐 Marathon Trainer", "Practiced for 2+ hours total", "uncommon"),
            (300, "⏳ Time Master", "Practiced for 5+ hours total", "rare"),
            (600, "⏰ Training Veteran", "Practiced for 10+ hours total", "epic"),
            (1200, "🏅 Time Champion", "Practiced for 20+ hours total", "legendary")
        ]
        
        for minutes, name, desc, rarity in time_milestones:
            achievements.append({
                'name': name,
                'description': desc,
                'rarity': rarity,
                'earned': total_time >= minutes,
                'progress_percent': min(100, (total_time / minutes) * 100)
            })
        
        # Streak achievements
        current_streak = streak_info.get('current_streak', 0)
        best_streak = streak_info.get('best_streak', 0)
        
        streak_milestones = [
            (3, "🔥 Streak Starter", "Maintained a 3-day training streak", "common"),
            (7, "📅 Week Warrior", "Maintained a 7-day training streak", "uncommon"),
            (14, "💪 Two Week Champion", "Maintained a 14-day training streak", "rare"),
            (30, "🏆 Month Master", "Maintained a 30-day training streak", "epic"),
            (100, "💎 Century Streaker", "Maintained a 100-day training streak", "legendary")
        ]
        
        for days, name, desc, rarity in streak_milestones:
            achievements.append({
                'name': name,
                'description': desc,
                'rarity': rarity,
                'earned': best_streak >= days,
                'progress_percent': min(100, (best_streak / days) * 100)
            })
        
        # Pitch and performance achievements
        if pitch_data:
            goal_time = pitch_data.get('total_goal_time', 0)
            improvement = pitch_data.get('improvement_trend', 0)
            
            # Goal achievement time
            goal_milestones = [
                (30, "🎯 Goal Getter", "Hit target pitch for 30+ seconds total", "common"),
                (300, "🎪 Goal Master", "Hit target pitch for 5+ minutes total", "uncommon"),
                (1800, "🏹 Sharpshooter", "Hit target pitch for 30+ minutes total", "rare"),
                (3600, "🎯 Perfect Aim", "Hit target pitch for 1+ hour total", "epic")
            ]
            
            for seconds, name, desc, rarity in goal_milestones:
                achievements.append({
                    'name': name,
                    'description': desc,
                    'rarity': rarity,
                    'earned': goal_time >= seconds,
                    'progress_percent': min(100, (goal_time / seconds) * 100)
                })
            
            # Improvement achievements
            improvement_milestones = [
                (5, "📈 Voice Progress", "Improved average pitch by 5Hz", "common"),
                (15, "🚀 Rising Star", "Improved average pitch by 15Hz", "uncommon"),
                (30, "⬆️ Sky Climber", "Improved average pitch by 30Hz", "rare"),
                (50, "🌟 Voice Transformer", "Improved average pitch by 50Hz", "epic")
            ]
            
            for hz, name, desc, rarity in improvement_milestones:
                achievements.append({
                    'name': name,
                    'description': desc,
                    'rarity': rarity,
                    'earned': improvement >= hz,
                    'progress_percent': min(100, max(0, improvement / hz) * 100)
                })
        
        # Special consistency achievements
        if len(sessions) >= 7:
            recent_week = sessions[-7:]
            week_count = len(recent_week)
            achievements.append({
                'name': "📅 Weekly Warrior", 
                'description': "Completed 5+ sessions this week",
                'rarity': 'uncommon',
                'earned': week_count >= 5,
                'progress_percent': min(100, (week_count / 5) * 100)
            })
        
        if len(sessions) >= 30:
            recent_month = sessions[-30:]
            month_count = len(recent_month)
            achievements.append({
                'name': "📆 Monthly Champion",
                'description': "Completed 20+ sessions this month", 
                'rarity': 'rare',
                'earned': month_count >= 20,
                'progress_percent': min(100, (month_count / 20) * 100)
            })
        
        return achievements
    
    def check_for_new_achievements(self, sessions: List[Dict], previous_earned_count: int = 0) -> List[Dict]:
        """Check if any new achievements were earned this session"""
        if not sessions:
            return []
        
        # Get current achievements
        total_sessions = len(sessions)
        total_time = sum(s.get('duration_minutes', 0) for s in sessions)
        
        streak_info = self.calculate_streaks(sessions)
        pitch_achievements = self.calculate_pitch_achievements(sessions)
        
        current_achievements = self.get_all_achievements(total_sessions, total_time, streak_info, pitch_achievements, sessions)
        current_earned = [a for a in current_achievements if a['earned']]
        
        # Return new achievements since previous count
        new_achievements = current_earned[previous_earned_count:]
        return new_achievements
    
    def show_achievement_notification(self, achievement: Dict):
        """Show a celebratory achievement notification"""
        rarity_icon = self.rarity_icons.get(achievement['rarity'], '🏅')
        
        print("\n" + "=" * 60)
        print("🎉 NEW ACHIEVEMENT UNLOCKED! 🎉")
        print("=" * 60)
        print(f"{rarity_icon} {achievement['name']}")
        print(f"   {achievement['description']}")
        print("=" * 60)
        print("Great job! Keep up the amazing work!")
        print()
    
    def show_milestone_celebration(self, milestones: List[Dict]):
        """Show celebration for reaching multiple milestones"""
        if not milestones:
            return
            
        print("\n" + "🌟" * 20)
        print("🎊 AMAZING PROGRESS! 🎊")
        print("🌟" * 20)
        
        for achievement in milestones:
            rarity_icon = self.rarity_icons.get(achievement['rarity'], '🏅')
            print(f"✨ {rarity_icon} {achievement['name']}")
            print(f"   {achievement['description']}")
        
        print("🌟" * 20)
        print("You're doing fantastic! Your dedication is paying off!")
        print()
    
    def display_achievements_summary(self, sessions: List[Dict]):
        """Display achievements summary"""
        if not sessions:
            print("🌱 Start training to unlock achievements!")
            self._show_upcoming_achievements()
            return
        
        # Calculate overall statistics
        total_sessions = len(sessions)
        total_time = sum(s.get('duration_minutes', 0) for s in sessions)
        
        # Calculate streak information
        streak_info = self.calculate_streaks(sessions)
        
        # Calculate pitch achievements
        pitch_achievements = self.calculate_pitch_achievements(sessions)
        
        # Display current streak
        current_streak = streak_info['current_streak']
        best_streak = streak_info['best_streak']
        
        print(f"🔥 Current Streak: {current_streak} day{'s' if current_streak != 1 else ''}")
        print(f"⭐ Best Streak: {best_streak} day{'s' if best_streak != 1 else ''}")
        if current_streak >= 3:
            print("   Keep it up! Consistency is key for voice training!")
        print()
        
        # Get all achievements
        achievements = self.get_all_achievements(total_sessions, total_time, streak_info, pitch_achievements, sessions)
        
        # Separate earned and upcoming achievements
        earned = [a for a in achievements if a['earned']]
        upcoming = [a for a in achievements if not a['earned']]
        
        # Display earned achievements
        if earned:
            print("🏅 Earned Achievements:")
            for achievement in earned:
                rarity_icon = self.rarity_icons.get(achievement['rarity'], '🏅')
                print(f"✅ {rarity_icon} {achievement['name']} - {achievement['description']}")
            print()
        
        # Show next achievements to unlock
        if upcoming:
            next_achievements = sorted(upcoming, key=lambda x: x.get('progress_percent', 0))[-3:]
            print("🎯 Next Goals:")
            for achievement in next_achievements:
                progress = achievement.get('progress_percent', 0)
                rarity_icon = self.rarity_icons.get(achievement['rarity'], '🏅')
                progress_bar = self._create_progress_bar(progress, 10)
                print(f"🔒 {rarity_icon} {achievement['name']} {progress_bar} {progress:.0f}%")
                print(f"   {achievement['description']}")
            print()
        
        # Summary statistics
        print("📊 Training Statistics:")
        print(f"   Total Sessions: {total_sessions}")
        print(f"   Total Practice Time: {total_time:.1f} minutes ({total_time/60:.1f} hours)")
        
        if total_sessions > 0:
            avg_session_time = total_time / total_sessions
            print(f"   Average Session: {avg_session_time:.1f} minutes")
            
            # Weekly activity
            recent_week_sessions = [s for s in sessions if self._is_within_days(s.get('date', ''), 7)]
            print(f"   This Week: {len(recent_week_sessions)} sessions")
        
        print()
    
    def _show_upcoming_achievements(self):
        """Show what achievements are available to unlock"""
        print("\n🎯 Achievements waiting to be unlocked:")
        print("   🎤 First Steps - Complete your first training session")
        print("   💪 Getting Started - Complete 5 training sessions") 
        print("   🔥 Streak Master - Maintain a 3-day training streak")
        print("   🎯 Goal Getter - Hit your target pitch for 30 seconds")
        print("   ⏰ Dedicated Trainer - Practice for 30+ minutes total")
        print("   📈 Voice Progress - Improve average pitch by 10Hz")
        print("   And many more!")
        print()
    
    def _create_progress_bar(self, percentage: float, width: int = 10) -> str:
        """Create a progress bar for achievements"""
        filled = int((percentage / 100.0) * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def _is_within_days(self, date_str: str, days: int) -> bool:
        """Check if date string is within specified days from today"""
        try:
            if not date_str:
                return False
            
            if 'T' in date_str:
                date = datetime.fromisoformat(date_str.replace('Z', '')).date()
            else:
                date = datetime.fromisoformat(date_str).date()
            
            return (datetime.now().date() - date).days <= days
        except (ValueError, AttributeError, TypeError):
            return False
