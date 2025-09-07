import time
from datetime import datetime, timedelta
from collections import deque
import numpy as np

class VoiceSafetyMonitor:
    """Monitor voice usage and prevent vocal strain/injury"""
    
    def __init__(self):
        # Session duration limits (in minutes)
        self.max_continuous_session = 30  # Maximum continuous session
        self.max_daily_practice = 120     # Maximum daily practice time
        self.recommended_break_interval = 15  # Break reminder interval
        
        # Vocal strain detection
        self.high_pitch_duration_limit = 60  # Max seconds in high pitch range
        self.strain_pitch_threshold = 300    # Hz above which we monitor strain
        self.excessive_force_threshold = 0.7  # Energy threshold for excessive force
        
        # Session tracking
        self.session_start_time = None
        self.daily_practice_time = 0
        self.last_break_reminder = None
        self.continuous_high_pitch_start = None
        self.high_pitch_duration = 0
        
        # Energy monitoring for strain detection
        self.recent_energy_levels = deque(maxlen=50)  # Last 50 measurements
        self.strain_warnings_given = 0
        
        # Safety state
        self.safety_warnings_active = True
        self.break_reminders_active = True
        self.strain_detection_active = True
        
    def start_session(self):
        """Start a new practice session"""
        self.session_start_time = datetime.now()
        self.last_break_reminder = self.session_start_time
        self.continuous_high_pitch_start = None
        self.high_pitch_duration = 0
        self.strain_warnings_given = 0
        self.recent_energy_levels.clear()
        
    def end_session(self):
        """End current session and update daily totals"""
        if self.session_start_time:
            session_duration = (datetime.now() - self.session_start_time).total_seconds() / 60
            self.daily_practice_time += session_duration
            self.session_start_time = None
            return session_duration
        return 0
        
    def update_voice_data(self, pitch, energy_level, audio_data):
        """Update voice monitoring with current data"""
        if not self.session_start_time:
            return []
            
        warnings = []
        current_time = datetime.now()
        
        # Track energy levels for strain detection
        self.recent_energy_levels.append(energy_level)
        
        # Check session duration limits
        session_duration_minutes = (current_time - self.session_start_time).total_seconds() / 60
        
        # Break reminders
        if (self.break_reminders_active and 
            self.last_break_reminder and
            (current_time - self.last_break_reminder).total_seconds() >= self.recommended_break_interval * 60):
            warnings.append({
                'type': 'break_reminder',
                'message': f"💧 Break reminder: You've been practicing for {session_duration_minutes:.0f} minutes",
                'suggestion': "Take a 2-3 minute break to rest your voice"
            })
            self.last_break_reminder = current_time
            
        # Maximum session duration warning
        if session_duration_minutes >= self.max_continuous_session:
            warnings.append({
                'type': 'max_session',
                'message': f"⚠️ Long session: {session_duration_minutes:.0f} minutes of continuous practice",
                'suggestion': "Consider ending this session to prevent vocal fatigue"
            })
            
        # High pitch duration monitoring
        if pitch > self.strain_pitch_threshold:
            if not self.continuous_high_pitch_start:
                self.continuous_high_pitch_start = current_time
            else:
                high_pitch_duration = (current_time - self.continuous_high_pitch_start).total_seconds()
                if high_pitch_duration >= self.high_pitch_duration_limit:
                    warnings.append({
                        'type': 'high_pitch_strain',
                        'message': f"🔊 High pitch warning: {high_pitch_duration:.0f}s in strain range",
                        'suggestion': "Lower your pitch or take a break to prevent vocal cord strain"
                    })
                    self.continuous_high_pitch_start = current_time  # Reset timer
        else:
            self.continuous_high_pitch_start = None
            
        # Excessive vocal force detection
        if len(self.recent_energy_levels) >= 10:
            recent_avg_energy = np.mean(list(self.recent_energy_levels)[-10:])
            if recent_avg_energy > self.excessive_force_threshold:
                warnings.append({
                    'type': 'excessive_force',
                    'message': "💪 Vocal force warning: Speaking/singing too forcefully",
                    'suggestion': "Relax your throat and use gentler airflow"
                })
                
        # Daily practice limit
        if self.daily_practice_time >= self.max_daily_practice:
            warnings.append({
                'type': 'daily_limit',
                'message': f"📅 Daily limit: {self.daily_practice_time:.0f} minutes practiced today",
                'suggestion': "You've had a great practice day! Consider resting until tomorrow"
            })
            
        return warnings
        
    def get_session_safety_summary(self):
        """Get safety summary for current session"""
        if not self.session_start_time:
            return None
            
        current_time = datetime.now()
        session_duration = (current_time - self.session_start_time).total_seconds() / 60
        
        summary = {
            'session_duration_minutes': session_duration,
            'daily_total_minutes': self.daily_practice_time + session_duration,
            'session_safety_status': 'good',
            'recommendations': []
        }
        
        # Determine safety status
        if session_duration >= self.max_continuous_session:
            summary['session_safety_status'] = 'caution'
            summary['recommendations'].append("Consider ending session due to length")
        elif session_duration >= self.recommended_break_interval:
            summary['session_safety_status'] = 'break_suggested'
            summary['recommendations'].append("Break recommended for voice rest")
            
        if self.daily_practice_time + session_duration >= self.max_daily_practice * 0.8:
            summary['recommendations'].append("Approaching daily practice limit")
            
        return summary
        
    def get_safety_settings(self):
        """Get current safety settings for configuration"""
        return {
            'max_continuous_session': self.max_continuous_session,
            'max_daily_practice': self.max_daily_practice,
            'break_interval': self.recommended_break_interval,
            'strain_pitch_threshold': self.strain_pitch_threshold,
            'high_pitch_duration_limit': self.high_pitch_duration_limit,
            'warnings_active': self.safety_warnings_active,
            'break_reminders_active': self.break_reminders_active,
            'strain_detection_active': self.strain_detection_active
        }
        
    def update_safety_settings(self, settings):
        """Update safety settings from configuration"""
        self.max_continuous_session = settings.get('max_continuous_session', self.max_continuous_session)
        self.max_daily_practice = settings.get('max_daily_practice', self.max_daily_practice)
        self.recommended_break_interval = settings.get('break_interval', self.recommended_break_interval)
        self.strain_pitch_threshold = settings.get('strain_pitch_threshold', self.strain_pitch_threshold)
        self.high_pitch_duration_limit = settings.get('high_pitch_duration_limit', self.high_pitch_duration_limit)
        self.safety_warnings_active = settings.get('warnings_active', self.safety_warnings_active)
        self.break_reminders_active = settings.get('break_reminders_active', self.break_reminders_active)
        self.strain_detection_active = settings.get('strain_detection_active', self.strain_detection_active)
        
    def should_suggest_session_end(self):
        """Check if we should suggest ending the current session"""
        if not self.session_start_time:
            return False
            
        session_duration = (datetime.now() - self.session_start_time).total_seconds() / 60
        daily_total = self.daily_practice_time + session_duration
        
        return (session_duration >= self.max_continuous_session or 
                daily_total >= self.max_daily_practice)
                
    def reset_daily_totals(self):
        """Reset daily practice totals (call this at start of new day)"""
        self.daily_practice_time = 0


class VoiceWarmupRoutines:
    """Provide safe voice warm-up and cool-down routines"""
    
    def __init__(self):
        self.routines = {
            'gentle_warmup': {
                'name': 'Gentle Voice Warm-up',
                'duration': 180,  # 3 minutes
                'steps': [
                    {'time': 30, 'instruction': 'Deep breathing: Breathe slowly and deeply', 'pitch_range': None},
                    {'time': 60, 'instruction': 'Gentle humming: Start very soft and low', 'pitch_range': (100, 150)},
                    {'time': 90, 'instruction': 'Lip trills: Relaxed lip buzzing', 'pitch_range': (120, 180)},
                    {'time': 180, 'instruction': 'Easy vowels: "Ah" sounds, comfortable pitch', 'pitch_range': (140, 200)}
                ]
            },
            'cooldown': {
                'name': 'Voice Cool-down',
                'duration': 120,  # 2 minutes
                'steps': [
                    {'time': 60, 'instruction': 'Gentle descending slides: High to low', 'pitch_range': (200, 100)},
                    {'time': 120, 'instruction': 'Relaxed sighs: Let your voice naturally fall', 'pitch_range': None}
                ]
            },
            'strain_relief': {
                'name': 'Vocal Strain Relief',
                'duration': 240,  # 4 minutes  
                'steps': [
                    {'time': 60, 'instruction': 'Complete vocal rest: Silence, breathe through nose', 'pitch_range': None},
                    {'time': 120, 'instruction': 'Gentle throat massage: Use fingertips on neck', 'pitch_range': None},
                    {'time': 180, 'instruction': 'Silent yawns: Open mouth wide, no sound', 'pitch_range': None},
                    {'time': 240, 'instruction': 'Very quiet humming: Barely audible', 'pitch_range': (80, 120)}
                ]
            }
        }
        
    def get_routine(self, routine_name):
        """Get a specific routine"""
        return self.routines.get(routine_name)
        
    def get_recommended_warmup(self, user_experience_level='beginner'):
        """Get recommended warmup based on experience"""
        if user_experience_level == 'beginner':
            return self.get_routine('gentle_warmup')
        else:
            return self.get_routine('gentle_warmup')  # Same for now, can expand
            
    def get_strain_relief_routine(self):
        """Get routine specifically for vocal strain relief"""
        return self.get_routine('strain_relief')


class VocalHealthEducation:
    """Provide educational content about vocal health"""
    
    def __init__(self):
        self.tips = {
            'hydration': [
                "Stay hydrated: Drink room temperature water throughout the day",
                "Avoid excessive caffeine and alcohol as they can dehydrate",
                "Humidify dry environments when possible"
            ],
            'technique': [
                "Use proper breath support from your diaphragm",
                "Avoid speaking/singing from your throat alone",
                "Keep your neck and shoulders relaxed while practicing"
            ],
            'rest': [
                "Take regular breaks during practice sessions",
                "Get adequate sleep for vocal cord recovery",
                "Use vocal rest periods when you feel strain"
            ],
            'warning_signs': [
                "Stop if you experience pain, scratchiness, or loss of voice",
                "Hoarseness lasting more than 2 weeks needs medical attention",
                "Persistent throat pain or difficulty swallowing requires evaluation"
            ]
        }
        
    def get_daily_tip(self):
        """Get a random daily vocal health tip"""
        import random
        category = random.choice(list(self.tips.keys()))
        return random.choice(self.tips[category])
        
    def get_tips_by_category(self, category):
        """Get all tips for a specific category"""
        return self.tips.get(category, [])
        
    def get_all_tips(self):
        """Get all vocal health tips organized by category"""
        return self.tips