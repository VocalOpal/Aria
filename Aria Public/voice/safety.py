import time
from datetime import datetime
from collections import deque
import numpy as np
from utils.emoji_handler import safe_print, convert_emoji_text, get_status_indicator

class VoiceSafetyMonitor:
    """Monitor voice usage and prevent vocal strain/injury"""

    def __init__(self):
        # Duration limits
        self.max_continuous_session = 30
        self.max_daily_practice = 120
        self.recommended_break_interval = 15

        # Pitch-based limits
        self.high_pitch_duration_limit = 60
        self.strain_pitch_threshold = 300
        self.excessive_force_threshold = 0.7

        # Session state
        self.session_start_time = None
        self.daily_practice_time = 0
        self.last_break_reminder = None
        self.continuous_high_pitch_start = None
        self.high_pitch_duration = 0

        self.recent_energy_levels = deque(maxlen=50)
        self.strain_warnings_given = 0

        # Feature toggles
        self.safety_warnings_active = True
        self.break_reminders_active = True
        self.strain_detection_active = True

        # Vocal roughness tracking
        self.roughness_history = deque(maxlen=100)
        self.strain_event_count = 0
        self.last_roughness_warning = None
        self.roughness_warning_cooldown = 10.0

        # Multi-session baseline tracking
        self.baseline_metrics = {
            "hnr": {"mean": 18.0, "std": 3.0, "samples": 0},
            "jitter": {"mean": 0.8, "std": 0.3, "samples": 0},
            "shimmer": {"mean": 4.0, "std": 2.0, "samples": 0},
        }

        # Adaptive thresholds per preset
        self.adaptive_thresholds = {
            "mtf": {"strain_pitch": 350, "high_pitch_duration": 45},
            "ftm": {"strain_pitch": 280, "high_pitch_duration": 60},
            "nonbinary": {"strain_pitch": 320, "high_pitch_duration": 50},
            "custom": {"strain_pitch": 300, "high_pitch_duration": 60}
        }
        self.current_preset = "custom"

    def start_session(self):
        self.session_start_time = datetime.now()
        self.last_break_reminder = self.session_start_time
        self.continuous_high_pitch_start = None
        self.high_pitch_duration = 0
        self.strain_warnings_given = 0
        self.recent_energy_levels.clear()
        self.roughness_history.clear()
        self.strain_event_count = 0
        self.last_roughness_warning = None

    def end_session(self):
        """End current session and update daily totals"""
        if self.session_start_time:
            session_duration = (datetime.now() - self.session_start_time).total_seconds() / 60
            self.daily_practice_time += session_duration
            self.session_start_time = None
            return session_duration
        return 0

    def update_voice_data(self, pitch, energy_level, audio_data, roughness_metrics=None):
        """Update voice monitoring with current data

        Args:
            pitch: Current pitch in Hz
            energy_level: Current energy level (0.0-1.0)
            audio_data: Raw audio data for analysis
            roughness_metrics: Optional dict with jitter, shimmer, hnr from VoiceAnalyzer
        """
        if not self.session_start_time:
            return []

        warnings = []
        current_time = datetime.now()

        self.recent_energy_levels.append(energy_level)

        session_duration_minutes = (current_time - self.session_start_time).total_seconds() / 60

        # Duration-based warnings
        if (self.break_reminders_active and
            self.last_break_reminder and
            (current_time - self.last_break_reminder).total_seconds() >= self.recommended_break_interval * 60):
            warnings.append({
                'type': 'break_reminder',
                'severity': 'light',
                'message': f"{convert_emoji_text('💧', 'health')} Break reminder: You've been practicing for {session_duration_minutes:.0f} minutes",
                'suggestion': "Take a 2-3 minute break to rest your voice"
            })
            self.last_break_reminder = current_time

        if session_duration_minutes >= self.max_continuous_session:
            warnings.append({
                'type': 'max_session',
                'severity': 'strong',
                'message': f"{get_status_indicator('warning')} Long session: {session_duration_minutes:.0f} minutes of continuous practice",
                'suggestion': "Consider ending this session to prevent vocal fatigue"
            })

        # Pitch-based warnings
        effective_strain_threshold = self.adaptive_thresholds[self.current_preset]["strain_pitch"]
        effective_duration_limit = self.adaptive_thresholds[self.current_preset]["high_pitch_duration"]

        if pitch > effective_strain_threshold:
            if not self.continuous_high_pitch_start:
                self.continuous_high_pitch_start = current_time
            else:
                high_pitch_duration = (current_time - self.continuous_high_pitch_start).total_seconds()
                if high_pitch_duration >= effective_duration_limit:
                    warnings.append({
                        'type': 'high_pitch_strain',
                        'severity': 'strong',
                        'message': f"{convert_emoji_text('🔊', 'audio')} High pitch warning: {high_pitch_duration:.0f}s in strain range",
                        'suggestion': "Lower your pitch or take a break to prevent vocal cord strain"
                    })
                    self.continuous_high_pitch_start = current_time
        else:
            self.continuous_high_pitch_start = None

        # Energy-based warnings
        if len(self.recent_energy_levels) >= 10:
            recent_avg_energy = np.mean(list(self.recent_energy_levels)[-10:])
            if recent_avg_energy > self.excessive_force_threshold:
                warnings.append({
                    'type': 'excessive_force',
                    'severity': 'light',
                    'message': f"{convert_emoji_text('💪', 'achievement')} Vocal force warning: Speaking/singing too forcefully",
                    'suggestion': "Relax your throat and use gentler airflow"
                })

        # Vocal roughness warnings
        if roughness_metrics and self.strain_detection_active:
            roughness_warning = self._check_roughness_strain(roughness_metrics, current_time)
            if roughness_warning:
                warnings.append(roughness_warning)

        # Daily limit warning
        if self.daily_practice_time >= self.max_daily_practice:
            warnings.append({
                'type': 'daily_limit',
                'severity': 'critical',
                'message': f"{convert_emoji_text('📅', 'time')} Daily limit: {self.daily_practice_time:.0f} minutes practiced today",
                'suggestion': "You've had a great practice day! Consider resting until tomorrow"
            })

        return warnings

    def _check_roughness_strain(self, roughness_metrics, current_time):
        """Check for vocal strain based on roughness metrics"""
        self.roughness_history.append(roughness_metrics)

        # Update baseline with healthy samples (only if metrics are good)
        if not roughness_metrics.get("strain_detected", False):
            self._update_baseline_metrics(roughness_metrics)

        # Check cooldown
        if self.last_roughness_warning:
            time_since_warning = (current_time - self.last_roughness_warning).total_seconds()
            if time_since_warning < self.roughness_warning_cooldown:
                return None

        # Analyze recent trends (last 5 seconds ≈ 50 samples)
        recent_samples = list(self.roughness_history)[-50:]
        if len(recent_samples) < 10:
            return None

        strain_count = sum(1 for s in recent_samples if s.get("strain_detected", False))
        strain_rate = strain_count / len(recent_samples)

        # Get current metrics
        jitter = roughness_metrics.get("jitter", 0)
        shimmer = roughness_metrics.get("shimmer", 0)
        hnr = roughness_metrics.get("hnr", 20)

        # Determine severity and message
        if strain_rate > 0.7:  # 70% of recent samples show strain
            self.strain_event_count += 1
            self.last_roughness_warning = current_time

            # Critical strain - multiple indicators
            if jitter > 3.0 and shimmer > 15.0:
                return {
                    'type': 'vocal_roughness',
                    'severity': 'critical',
                    'message': f"{convert_emoji_text('⚠️', 'warning')} Critical vocal strain detected (Jitter: {jitter:.1f}%, Shimmer: {shimmer:.1f}%)",
                    'suggestion': "STOP immediately and rest your voice. High jitter and shimmer indicate significant strain."
                }
            elif hnr < 8.0:
                return {
                    'type': 'vocal_roughness',
                    'severity': 'strong',
                    'message': f"{convert_emoji_text('🔊', 'audio')} Voice quality degraded (HNR: {hnr:.1f}dB - raspiness detected)",
                    'suggestion': "Your voice sounds raspy/strained. Take a break and drink water."
                }
            elif jitter > 2.0:
                return {
                    'type': 'vocal_roughness',
                    'severity': 'strong',
                    'message': f"{convert_emoji_text('📊', 'stats')} Pitch instability detected (Jitter: {jitter:.1f}%)",
                    'suggestion': "Upper range strain detected. Consider lowering your pitch or pausing."
                }
            elif shimmer > 10.0:
                return {
                    'type': 'vocal_roughness',
                    'severity': 'light',
                    'message': f"{convert_emoji_text('📈', 'trend')} Amplitude variation high (Shimmer: {shimmer:.1f}%)",
                    'suggestion': "Resonance drifting - check your posture and breath support."
                }

        return None

    def _update_baseline_metrics(self, roughness_metrics):
        """Update baseline metrics with healthy voice samples"""
        for metric in ["jitter", "shimmer", "hnr"]:
            value = roughness_metrics.get(metric, 0)
            if value <= 0:
                continue

            baseline = self.baseline_metrics[metric]
            if baseline["samples"] == 0:
                baseline["mean"] = value
                baseline["samples"] = 1
            else:
                alpha = 0.02
                baseline["mean"] = alpha * value + (1 - alpha) * baseline["mean"]
                baseline["samples"] += 1

    def set_preset(self, preset_name):
        """Set adaptive thresholds based on voice preset

        Args:
            preset_name: One of 'mtf', 'ftm', 'nonbinary_higher', 'nonbinary_lower', 'nonbinary_neutral', 'custom'
        """
        # Map preset names to adaptive threshold keys
        preset_mapping = {
            'mtf': 'mtf',
            'ftm': 'ftm',
            'nonbinary_higher': 'nonbinary',
            'nonbinary_lower': 'nonbinary',
            'nonbinary_neutral': 'nonbinary',
            'custom': 'custom'
        }

        mapped_preset = preset_mapping.get(preset_name, 'custom')
        self.current_preset = mapped_preset

        # Update strain pitch threshold
        self.strain_pitch_threshold = self.adaptive_thresholds[mapped_preset]["strain_pitch"]
        self.high_pitch_duration_limit = self.adaptive_thresholds[mapped_preset]["high_pitch_duration"]

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
                'duration': 180,  
                'steps': [
                    {'time': 30, 'instruction': 'Deep breathing: Breathe slowly and deeply', 'pitch_range': None},
                    {'time': 60, 'instruction': 'Gentle humming: Start very soft and low', 'pitch_range': (100, 150)},
                    {'time': 90, 'instruction': 'Lip trills: Relaxed lip buzzing', 'pitch_range': (120, 180)},
                    {'time': 180, 'instruction': 'Easy vowels: "Ah" sounds, comfortable pitch', 'pitch_range': (140, 200)}
                ]
            },
            'cooldown': {
                'name': 'Voice Cool-down',
                'duration': 120,  
                'steps': [
                    {'time': 60, 'instruction': 'Gentle descending slides: High to low', 'pitch_range': (200, 100)},
                    {'time': 120, 'instruction': 'Relaxed sighs: Let your voice naturally fall', 'pitch_range': None}
                ]
            },
            'strain_relief': {
                'name': 'Vocal Strain Relief',
                'duration': 240,  
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
            return self.get_routine('gentle_warmup')  

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
        import random
        category = random.choice(list(self.tips.keys()))
        return random.choice(self.tips[category])

    def get_tips_by_category(self, category):
        """Get all tips for a specific category"""
        return self.tips.get(category, [])

    def get_all_tips(self):
        """Get all vocal health tips organized by category"""
        return self.tips