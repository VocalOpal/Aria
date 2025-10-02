"""
Session Manager - Handles session lifecycle, statistics, and progress tracking
Extracted from voice_trainer.py lines 184-317, 538-671, 803-825
"""

import numpy as np
import time
import json
import os
from pathlib import Path
from collections import deque
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import statistics
from utils.file_operations import safe_save_config, safe_load_config, get_logger


class VoiceSessionManager:
    """Manages voice training session lifecycle, stats, and progress"""
    
    def __init__(self, config_file="data/voice_config.json"):
        self.config_file = config_file
        self.progress_file = config_file.replace('.json', '_progress.json')
        self.recovery_file = config_file.replace('.json', '_recovery.tmp.json')
        
        # Session state
        self.current_session = None
        self.current_exercise = None
        self.session_stats = self._create_empty_stats()
        self.weekly_sessions = []
        
        # Session tracking
        self.pitch_buffer = deque(maxlen=20)
        self.dip_start_time = None
        self.in_dip = False
        self.session_range_low = float('inf')
        self.session_range_high = 0.0
        
        # Noise handling
        self.timer_paused_for_noise = False
        self.noise_pause_start_time = None
        self.total_noise_pause_time = 0.0
        
        # Auto-save
        self.auto_save_interval = 30
        self.last_auto_save = time.time()
        
        # Streak tracking
        self.streak_count = 0
        self.last_practice_date = None
        self.grace_period_used = None
        
        # Practice calendar for heatmap (date -> minutes)
        self.practice_calendar = {}
        
        # Multi-day fatigue tracking (date -> fatigue_score 0-100)
        self.fatigue_history = {}
        
        # Break pattern learning
        self.user_break_preferences = {
            'typical_break_intervals': [],  # Minutes between breaks
            'preferred_break_duration': 2,   # Default 2 minutes
            'last_break_time': None
        }
        
        # Check for recovery file on startup
        self._check_for_recovery()
        
        # Load existing progress data
        self.load_progress_data()
    
    def _create_empty_stats(self):
        """Create empty session statistics structure"""
        return {
            'start_time': datetime.now(),
            'total_alerts': 0,
            'avg_pitch': 0.0,
            'min_pitch': float('inf'),
            'max_pitch': 0.0,
            'time_in_range': 0,
            'total_time': 0,
            'goal_achievements': 0,
            'dip_count': 0,
            'dip_recovery_time': 0.0,
            'high_alerts': 0,
            'last_update': time.time(),
            'avg_jitter': 0.0,
            'avg_shimmer': 0.0,
            'avg_hnr': 0.0,
            'strain_events': 0,
            'roughness_samples': 0,
            'avg_resonance': 0.0,
            'resonance_shift': 0.0,
            'resonance_samples': 0,
            'safety_warnings': {
                'vocal_roughness': 0,
                'high_pitch_strain': 0,
                'excessive_force': 0,
                'break_reminder': 0
            },
            'voice_quality_metrics': {
                'avg_breathiness': 0.0,
                'avg_nasality': 0.0,
                'breathiness_samples': 0,
                'nasality_samples': 0
            }
        }
    
    def start_session(self, session_type="training", current_goal=165):
        self.session_stats = self._create_empty_stats()
        self.current_session = {
            'type': session_type,
            'goal': current_goal,
            'start_time': datetime.now()
        }
        self.total_noise_pause_time = 0.0
        self.pitch_buffer.clear()
        self.session_range_low = float('inf')
        self.session_range_high = 0.0
        self.in_dip = False
        self.dip_start_time = None
        self.timer_paused_for_noise = False
        self.noise_pause_start_time = None
        return True
    
    def end_session(self):
        """End current session and save data"""
        try:
            if self.current_session:
                self.save_session_data()
                self.current_session = None
                
                # Clean up recovery file on successful session end
                try:
                    if os.path.exists(self.recovery_file):
                        os.remove(self.recovery_file)
                except:
                    pass
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "SessionManager.end_session")
            # Still clear the session to prevent stuck state
            self.current_session = None
        return True
    
    def update_session_stats(self, pitch, min_threshold, current_goal):
        """Update session statistics with new pitch data"""
        if pitch > 0:
            # Update basic stats
            self.session_stats['min_pitch'] = min(self.session_stats['min_pitch'], pitch)
            self.session_stats['max_pitch'] = max(self.session_stats['max_pitch'], pitch)
            self.session_stats['total_time'] += 1
            
            # Calculate average pitch (running average for efficiency)
            if self.session_stats['total_time'] == 1:
                self.session_stats['avg_pitch'] = pitch
            else:
                # Weighted average to prevent memory issues with very long sessions
                weight = min(0.01, 1.0 / self.session_stats['total_time'])
                self.session_stats['avg_pitch'] = (
                    (1 - weight) * self.session_stats['avg_pitch'] + weight * pitch
                )
            
            # Track range achievements
            if pitch >= min_threshold:
                self.session_stats['time_in_range'] += 1
            
            if pitch >= current_goal:
                self.session_stats['goal_achievements'] += 1
                
            # Track session pitch range
            self.session_range_low = min(self.session_range_low, pitch)
            self.session_range_high = max(self.session_range_high, pitch)
            
            # Auto-save periodically (includes recovery file)
            current_time = time.time()
            if current_time - self.last_auto_save > self.auto_save_interval:
                self.save_progress_data()
                self._save_recovery_state()
                self.last_auto_save = current_time
    
    def handle_noise_pause(self, is_background_only):
        """Handle timer pausing for background noise"""
        current_time = time.time()
        
        if is_background_only:
            if not self.timer_paused_for_noise:
                self.timer_paused_for_noise = True
                self.noise_pause_start_time = current_time
                return "timer_paused"
            return "already_paused"
        else:
            if self.timer_paused_for_noise:
                # Resume timer
                pause_duration = current_time - self.noise_pause_start_time
                self.total_noise_pause_time += pause_duration
                self.timer_paused_for_noise = False
                self.noise_pause_start_time = None
                return "timer_resumed"
            return "timer_active"
    
    def check_dip_tolerance(self, pitch, min_threshold, dip_tolerance_duration):
        """Check if current pitch dip should trigger alert"""
        self.pitch_buffer.append(pitch)
        
        if len(self.pitch_buffer) >= 5:
            recent_median = statistics.median(list(self.pitch_buffer)[-5:])
        else:
            recent_median = pitch
            
        current_time = time.time()
        
        if recent_median < (min_threshold - 15):  # 15Hz below goal triggers dip
            if not self.in_dip:
                self.in_dip = True
                self.dip_start_time = current_time
                return False, {'in_dip': True, 'just_started': True}
            else:
                dip_duration = current_time - self.dip_start_time
                remaining_tolerance = max(0, dip_tolerance_duration - dip_duration)
                
                if dip_duration >= dip_tolerance_duration:
                    return True, {'in_dip': True, 'alert_triggered': True}
                else:
                    return False, {
                        'in_dip': True, 
                        'remaining_tolerance': remaining_tolerance
                    }
        else:
            if self.in_dip:
                # Recovered from dip
                if self.dip_start_time:
                    dip_duration = current_time - self.dip_start_time
                    self.session_stats['dip_recovery_time'] += dip_duration
                    self.session_stats['dip_count'] += 1
                
                self.in_dip = False
                self.dip_start_time = None
                return False, {'recovered': True}
            
            return False, {'normal': True}
    
    def update_alert_stats(self, alert_type="low"):
        """Update alert statistics"""
        if alert_type == "low":
            self.session_stats['total_alerts'] += 1
        elif alert_type == "high":
            self.session_stats['high_alerts'] = self.session_stats.get('high_alerts', 0) + 1

    def update_roughness_stats(self, roughness_metrics):
        """Update vocal roughness statistics

        Args:
            roughness_metrics: dict with jitter, shimmer, hnr, strain_detected
        """
        if not roughness_metrics:
            return

        jitter = roughness_metrics.get('jitter', 0)
        shimmer = roughness_metrics.get('shimmer', 0)
        hnr = roughness_metrics.get('hnr', 0)
        strain = roughness_metrics.get('strain_detected', False)

        # Update running averages
        samples = self.session_stats['roughness_samples']
        if samples == 0:
            self.session_stats['avg_jitter'] = jitter
            self.session_stats['avg_shimmer'] = shimmer
            self.session_stats['avg_hnr'] = hnr
        else:
            # Exponential moving average
            alpha = 0.1
            self.session_stats['avg_jitter'] = (
                alpha * jitter + (1 - alpha) * self.session_stats['avg_jitter']
            )
            self.session_stats['avg_shimmer'] = (
                alpha * shimmer + (1 - alpha) * self.session_stats['avg_shimmer']
            )
            self.session_stats['avg_hnr'] = (
                alpha * hnr + (1 - alpha) * self.session_stats['avg_hnr']
            )

        self.session_stats['roughness_samples'] += 1

        if strain:
            self.session_stats['strain_events'] += 1

    def update_voice_quality_stats(self, quality_metrics):
        """Update voice quality statistics (breathiness, nasality)
        
        Args:
            quality_metrics: dict with breathiness, nasality scores
        """
        if not quality_metrics:
            return
        
        breathiness = quality_metrics.get('breathiness', 0.0)
        nasality = quality_metrics.get('nasality', 0.0)
        
        # Get current samples
        b_samples = self.session_stats['voice_quality_metrics']['breathiness_samples']
        n_samples = self.session_stats['voice_quality_metrics']['nasality_samples']
        
        # Update running averages with exponential moving average
        alpha = 0.1
        
        if b_samples == 0:
            self.session_stats['voice_quality_metrics']['avg_breathiness'] = breathiness
        else:
            self.session_stats['voice_quality_metrics']['avg_breathiness'] = (
                alpha * breathiness + (1 - alpha) * self.session_stats['voice_quality_metrics']['avg_breathiness']
            )
        
        if n_samples == 0:
            self.session_stats['voice_quality_metrics']['avg_nasality'] = nasality
        else:
            self.session_stats['voice_quality_metrics']['avg_nasality'] = (
                alpha * nasality + (1 - alpha) * self.session_stats['voice_quality_metrics']['avg_nasality']
            )
        
        self.session_stats['voice_quality_metrics']['breathiness_samples'] += 1
        self.session_stats['voice_quality_metrics']['nasality_samples'] += 1
    
    def update_resonance_stats(self, resonance_data):
        """Update resonance statistics

        Args:
            resonance_data: dict with frequency, baseline, deviation
        """
        if not resonance_data:
            return

        frequency = resonance_data.get('frequency', 0)
        deviation = resonance_data.get('deviation', 0)

        if frequency <= 0:
            return

        # Update running averages
        samples = self.session_stats['resonance_samples']
        if samples == 0:
            self.session_stats['avg_resonance'] = frequency
            self.session_stats['resonance_shift'] = deviation
        else:
            alpha = 0.1
            self.session_stats['avg_resonance'] = (
                alpha * frequency + (1 - alpha) * self.session_stats['avg_resonance']
            )
            self.session_stats['resonance_shift'] = (
                alpha * deviation + (1 - alpha) * self.session_stats['resonance_shift']
            )

        self.session_stats['resonance_samples'] += 1

    def update_safety_warning_stats(self, warning_type):
        """Update safety warning statistics

        Args:
            warning_type: Type of safety warning (e.g., 'vocal_roughness', 'high_pitch_strain')
        """
        if 'safety_warnings' not in self.session_stats:
            self.session_stats['safety_warnings'] = {}

        if warning_type in ['vocal_roughness', 'high_pitch_strain', 'excessive_force', 'break_reminder']:
            self.session_stats['safety_warnings'][warning_type] = (
                self.session_stats['safety_warnings'].get(warning_type, 0) + 1
            )
    
    def get_session_summary(self):
        """Get current session summary"""
        if not self.current_session:
            return None
            
        elapsed = datetime.now() - self.session_stats['start_time']
        total_session_seconds = int(elapsed.total_seconds())
        active_training_seconds = max(0, total_session_seconds - int(self.total_noise_pause_time))
        
        summary = {
            'total_duration_seconds': total_session_seconds,
            'active_training_seconds': active_training_seconds,
            'noise_pause_seconds': int(self.total_noise_pause_time),
            'stats': self.session_stats.copy()
        }
        
        return summary
    
    def get_dip_info(self):
        """Get current dip information"""
        if not self.in_dip or not self.dip_start_time:
            return None
            
        dip_duration = time.time() - self.dip_start_time
        return {
            'in_dip': True,
            'duration': dip_duration,
            'start_time': self.dip_start_time
        }
    
    def save_session_data(self):
        """Save current session to progress tracking - requires minimum 1 minute of voice data"""
        try:
            if not self.current_session or self.session_stats['total_time'] == 0:
                return False

            # Calculate actual training time (excluding noise pauses)
            session_duration_seconds = (datetime.now() - self.session_stats['start_time']).total_seconds()
            active_training_seconds = max(0, session_duration_seconds - self.total_noise_pause_time)
            voice_data_seconds = self.session_stats['total_time']  # This is actual voice processing time

            # Require at least 1 minute (60 seconds) of voice data for session to be saved
            if voice_data_seconds < 60:
                return False

            session_data = {
                'date': datetime.now().isoformat(),
                'duration': (datetime.now() - self.session_stats['start_time']).total_seconds(),
                'duration_minutes': voice_data_seconds / 60,
                'avg_pitch': self.session_stats['avg_pitch'],
                'min_pitch': self.session_stats['min_pitch'],
                'max_pitch': self.session_stats['max_pitch'],
                'goal': self.current_session.get('goal', 165),
                'base_goal': self.current_session.get('goal', 165),  # Simplified for now
                'time_in_range_percent': (
                    self.session_stats['time_in_range'] / self.session_stats['total_time']
                ) * 100,
                'goal_achievement_percent': (
                    self.session_stats.get('goal_achievements', 0) / self.session_stats['total_time']
                ) * 100,
                'total_alerts': self.session_stats['total_alerts'],
                'dip_count': self.session_stats.get('dip_count', 0),
                'session_type': self.current_session.get('type', 'training'),
                # NEW: Vocal roughness metrics
                'avg_jitter': self.session_stats.get('avg_jitter', 0.0),
                'avg_shimmer': self.session_stats.get('avg_shimmer', 0.0),
                'avg_hnr': self.session_stats.get('avg_hnr', 0.0),
                'strain_events': self.session_stats.get('strain_events', 0),
                # NEW: Resonance metrics
                'avg_resonance': self.session_stats.get('avg_resonance', 0.0),
                'resonance_shift': self.session_stats.get('resonance_shift', 0.0),
                # NEW: Safety warnings summary
                'safety_warnings': self.session_stats.get('safety_warnings', {}),
                # Voice quality assessment
                'voice_quality': self._assess_voice_quality()
            }

            self.weekly_sessions.append(session_data)
            # Keep last 84 sessions (~12 weeks)
            self.weekly_sessions = self.weekly_sessions[-84:]
            
            # Calculate and store daily fatigue score
            self._calculate_daily_fatigue(session_data)
            
            self.save_progress_data()
            return True

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "SessionManager.save_session_data")
            return False
    
    def load_progress_data(self):
        """Load progress tracking data from file"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    self.weekly_sessions = data.get('weekly_sessions', [])
                    self.streak_count = data.get('streak_count', 0)
                    self.last_practice_date = data.get('last_practice_date', None)
                    self.grace_period_used = data.get('grace_period_used', None)
                    self.fatigue_history = data.get('fatigue_history', {})
                    self.user_break_preferences = data.get('user_break_preferences', {
                        'typical_break_intervals': [],
                        'preferred_break_duration': 2,
                        'last_break_time': None
                    })
            except Exception as e:
                self.weekly_sessions = []
                self.streak_count = 0
                self.last_practice_date = None
                self.grace_period_used = None
                self.fatigue_history = {}
                self.user_break_preferences = {
                    'typical_break_intervals': [],
                    'preferred_break_duration': 2,
                    'last_break_time': None
                }
        else:
            self.weekly_sessions = []
            self.streak_count = 0
            self.last_practice_date = None
            self.grace_period_used = None
            self.fatigue_history = {}
            self.user_break_preferences = {
                'typical_break_intervals': [],
                'preferred_break_duration': 2,
                'last_break_time': None
            }
    
    def save_progress_data(self):
        """Save progress tracking data to file"""
        try:
            data = {
                'weekly_sessions': self.weekly_sessions,
                'streak_count': self.streak_count,
                'last_practice_date': self.last_practice_date,
                'grace_period_used': self.grace_period_used,
                'fatigue_history': self.fatigue_history,
                'user_break_preferences': self.user_break_preferences,
                'last_updated': datetime.now().isoformat()
            }

            # Ensure directory exists
            os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)

            with open(self.progress_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "SessionManager.save_progress_data")
            return False
    
    def get_progress_trends(self):
        """Analyze progress trends from session history"""
        if len(self.weekly_sessions) < 2:
            return {
                'status': 'insufficient_data',
                'message': 'Not enough data for trend analysis'
            }
            
        recent_sessions = self.weekly_sessions[-7:]
        older_sessions = self.weekly_sessions[-14:-7] if len(self.weekly_sessions) >= 14 else []
        
        recent_avg = np.mean([s['avg_pitch'] for s in recent_sessions])
        
        analysis = {
            'recent_average': recent_avg,
            'total_sessions': len(self.weekly_sessions)
        }
        
        if older_sessions:
            older_avg = np.mean([s['avg_pitch'] for s in older_sessions])
            improvement = recent_avg - older_avg
            analysis['older_average'] = older_avg
            analysis['improvement_hz'] = improvement
            
            if improvement > 2:
                analysis['trend'] = 'improving'
            elif improvement > -2:
                analysis['trend'] = 'stable'
            else:
                analysis['trend'] = 'declining'
        else:
            analysis['trend'] = 'new_user'
            
        # Calculate consistency
        consistency = len([s for s in recent_sessions 
                         if s['avg_pitch'] >= s.get('base_goal', 165)]) / len(recent_sessions) * 100
        analysis['consistency_percent'] = consistency
        
        return analysis
    
    def get_session_history(self, limit=10):
        """Get recent session history"""
        return self.weekly_sessions[-limit:] if self.weekly_sessions else []
    
    def _assess_voice_quality(self):
        """Assess overall voice quality for this session

        Returns: string assessment ('excellent', 'good', 'fair', 'needs_improvement')
        """
        # Check if we have roughness metrics
        if self.session_stats.get('roughness_samples', 0) < 10:
            return 'unknown'

        jitter = self.session_stats.get('avg_jitter', 0)
        shimmer = self.session_stats.get('avg_shimmer', 0)
        hnr = self.session_stats.get('avg_hnr', 20)
        strain_events = self.session_stats.get('strain_events', 0)

        # Calculate quality score (0-100)
        score = 100

        # Penalize high jitter (healthy < 1%, strain > 2%)
        if jitter > 2.0:
            score -= 30
        elif jitter > 1.5:
            score -= 20
        elif jitter > 1.0:
            score -= 10

        # Penalize high shimmer (healthy < 5%, strain > 10%)
        if shimmer > 10.0:
            score -= 30
        elif shimmer > 7.0:
            score -= 20
        elif shimmer > 5.0:
            score -= 10

        # Penalize low HNR (good > 20dB, poor < 10dB)
        if hnr < 10.0:
            score -= 30
        elif hnr < 15.0:
            score -= 20
        elif hnr < 18.0:
            score -= 10

        # Penalize strain events
        if strain_events > 10:
            score -= 20
        elif strain_events > 5:
            score -= 10

        # Classify based on score
        if score >= 85:
            return 'excellent'
        elif score >= 70:
            return 'good'
        elif score >= 50:
            return 'fair'
        else:
            return 'needs_improvement'

    def _update_streak(self, practice_duration_seconds):
        """Update streak based on practice session
        
        Args:
            practice_duration_seconds: Duration of voice data in seconds
        """
        today = datetime.now().date().isoformat()
        
        # Update practice calendar
        if today not in self.practice_calendar:
            self.practice_calendar[today] = 0
        self.practice_calendar[today] += practice_duration_seconds / 60  # Store minutes
        
        # Only update streak once per day (first session of the day)
        if self.last_practice_date == today:
            return
            
        # Calculate days since last practice
        if self.last_practice_date:
            last_date = datetime.fromisoformat(self.last_practice_date).date()
            current_date = datetime.now().date()
            days_diff = (current_date - last_date).days
            
            if days_diff == 1:
                # Consecutive day - increment streak
                self.streak_count += 1
                self.grace_period_used = None
            elif days_diff == 2:
                # One day missed - check grace period
                week_start = current_date - (current_date - datetime(1970, 1, 1).date()).days % 7 * datetime.resolution
                week_key = week_start.isoformat()
                
                if self.grace_period_used != week_key:
                    # Use grace period - maintain streak
                    self.grace_period_used = week_key
                else:
                    # Grace period already used this week - reset streak
                    self.streak_count = 1
                    self.grace_period_used = None
            else:
                # More than 1 day missed - reset streak
                self.streak_count = 1
                self.grace_period_used = None
        else:
            # First ever practice session
            self.streak_count = 1
            
        self.last_practice_date = today
    
    def get_current_streak(self):
        """Get current streak count
        
        Returns:
            dict with streak_count, last_practice_date, and status
        """
        if not self.last_practice_date:
            return {
                'streak_count': 0,
                'last_practice_date': None,
                'status': 'no_streak',
                'message': 'Start practicing to begin your streak!'
            }
        
        last_date = datetime.fromisoformat(self.last_practice_date).date()
        current_date = datetime.now().date()
        days_diff = (current_date - last_date).days
        
        if days_diff == 0:
            # Practiced today
            return {
                'streak_count': self.streak_count,
                'last_practice_date': self.last_practice_date,
                'status': 'active',
                'message': f'🔥 {self.streak_count} Day Streak!'
            }
        elif days_diff == 1:
            # Haven't practiced today yet
            week_start = current_date - (current_date - datetime(1970, 1, 1).date()).days % 7 * datetime.resolution
            week_key = week_start.isoformat()
            grace_available = self.grace_period_used != week_key
            
            return {
                'streak_count': self.streak_count,
                'last_practice_date': self.last_practice_date,
                'status': 'at_risk',
                'message': 'Practice today to continue your streak!',
                'grace_available': grace_available
            }
        else:
            # Streak broken
            return {
                'streak_count': 0,
                'last_practice_date': self.last_practice_date,
                'status': 'broken',
                'message': 'Start a new streak today!'
            }
    
    def get_practice_calendar_data(self, days=30):
        """Get practice calendar data for heatmap
        
        Args:
            days: Number of days to retrieve (default 30)
            
        Returns:
            list of dicts with date and minutes practiced
        """
        calendar_data = []
        current_date = datetime.now().date()
        
        for i in range(days):
            date = current_date - timedelta(days=i)
            date_str = date.isoformat()
            minutes = self.practice_calendar.get(date_str, 0)
            
            calendar_data.append({
                'date': date_str,
                'minutes': minutes,
                'day_name': date.strftime('%a'),
                'day_number': date.day
            })
        
        return list(reversed(calendar_data))

    def get_practice_time_heatmap_data(self, days=30):
        """Get practice time heatmap data showing pitch patterns by day and hour
        
        Args:
            days: Number of days to analyze (default 30)
            
        Returns:
            dict: {day_of_week: {hour: {'avg_pitch': X, 'count': Y}}}
        """
        heatmap_data = {}
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter sessions within date range
        recent_sessions = [
            s for s in self.weekly_sessions
            if datetime.fromisoformat(s['date'].replace('Z', '+00:00')) >= cutoff_date
        ]
        
        if not recent_sessions:
            return heatmap_data
        
        # Group sessions by day of week and hour
        for session in recent_sessions:
            try:
                session_dt = datetime.fromisoformat(session['date'].replace('Z', '+00:00'))
                day_name = session_dt.strftime('%A')
                hour = session_dt.hour
                avg_pitch = session.get('avg_pitch', 0)
                
                if avg_pitch <= 0:
                    continue
                
                # Initialize day if not exists
                if day_name not in heatmap_data:
                    heatmap_data[day_name] = {}
                
                # Initialize hour if not exists
                if hour not in heatmap_data[day_name]:
                    heatmap_data[day_name][hour] = {'total_pitch': 0, 'count': 0}
                
                # Accumulate data
                heatmap_data[day_name][hour]['total_pitch'] += avg_pitch
                heatmap_data[day_name][hour]['count'] += 1
                
            except Exception as e:
                from utils.error_handler import log_error
                log_error(e, "SessionManager.get_practice_time_heatmap_data")
                continue
        
        # Calculate averages
        for day in heatmap_data:
            for hour in heatmap_data[day]:
                total = heatmap_data[day][hour]['total_pitch']
                count = heatmap_data[day][hour]['count']
                heatmap_data[day][hour]['avg_pitch'] = total / count if count > 0 else 0
                # Remove total_pitch as it's no longer needed
                del heatmap_data[day][hour]['total_pitch']
        
        return heatmap_data

    def clear_all_data(self):
        self.weekly_sessions = []
        self.session_stats = self._create_empty_stats()
        self.current_session = None
        self.last_practice_date = None
        self.streak_count = 0
        self.practice_calendar = {}
        self.grace_period_used = None

        # Try to delete progress file
        try:
            if os.path.exists(self.progress_file):
                os.remove(self.progress_file)
        except Exception:
            pass

        # Try to delete recovery file
        try:
            if os.path.exists(self.recovery_file):
                os.remove(self.recovery_file)
        except Exception:
            pass

        return True

    def _check_for_recovery(self):
        """Check for recovery file on startup and offer to restore session"""
        if not os.path.exists(self.recovery_file):
            return None
        
        try:
            with open(self.recovery_file, 'r') as f:
                recovery_data = json.load(f)
            
            # Check if recovery data is recent (within last 24 hours)
            timestamp = recovery_data.get('timestamp', 0)
            age_hours = (time.time() - timestamp) / 3600
            
            if age_hours > 24:
                # Recovery data too old, delete it
                os.remove(self.recovery_file)
                return None
            
            # Store recovery data for later decision
            self.pending_recovery = recovery_data
            logger = get_logger()
            logger.info(f"Found incomplete session from {datetime.fromtimestamp(timestamp)}")
            print(f"\n📦 Found incomplete session from {datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')}")
            print(f"   Duration: {recovery_data.get('duration_minutes', 0):.1f} minutes")
            print(f"   Use recover_session() to restore or start a new session to discard\n")
            
            return recovery_data
            
        except Exception as e:
            logger = get_logger()
            logger.error(f"Failed to read recovery file: {e}")
            try:
                os.remove(self.recovery_file)
            except:
                pass
            return None
    
    def _save_recovery_state(self):
        """Save current session state to recovery file"""
        if not self.current_session:
            return
        
        try:
            recovery_data = {
                'timestamp': time.time(),
                'session': self.current_session,
                'stats': self.session_stats.copy(),
                'duration_minutes': self.session_stats['total_time'] / 60,
                'session_range_low': self.session_range_low,
                'session_range_high': self.session_range_high,
                'total_noise_pause_time': self.total_noise_pause_time
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.recovery_file), exist_ok=True)
            
            with open(self.recovery_file, 'w') as f:
                json.dump(recovery_data, f, indent=2, default=str)
                
        except Exception as e:
            logger = get_logger()
            logger.error(f"Failed to save recovery state: {e}")
    
    def recover_session(self):
        """Recover incomplete session from crash/unexpected exit
        
        Returns:
            bool: True if session recovered successfully, False otherwise
        """
        if not hasattr(self, 'pending_recovery') or not self.pending_recovery:
            if os.path.exists(self.recovery_file):
                # Try to load recovery file directly
                try:
                    with open(self.recovery_file, 'r') as f:
                        self.pending_recovery = json.load(f)
                except Exception:
                    return False
            else:
                return False
        
        try:
            recovery_data = self.pending_recovery
            
            # Restore session state
            self.current_session = recovery_data.get('session')
            
            # Restore statistics
            stats = recovery_data.get('stats', {})
            for key, value in stats.items():
                if key == 'start_time':
                    try:
                        self.session_stats[key] = datetime.fromisoformat(value)
                    except:
                        self.session_stats[key] = datetime.now()
                else:
                    self.session_stats[key] = value
            
            # Restore other session data
            self.session_range_low = recovery_data.get('session_range_low', float('inf'))
            self.session_range_high = recovery_data.get('session_range_high', 0.0)
            self.total_noise_pause_time = recovery_data.get('total_noise_pause_time', 0.0)
            
            # Clear recovery file
            try:
                os.remove(self.recovery_file)
            except:
                pass
            
            # Clear pending recovery
            delattr(self, 'pending_recovery')
            
            logger = get_logger()
            logger.info(f"Successfully recovered session: {recovery_data.get('duration_minutes', 0):.1f} minutes")
            print(f"✅ Session recovered successfully!")
            print(f"   Continuing from {recovery_data.get('duration_minutes', 0):.1f} minutes\n")
            
            return True
            
        except Exception as e:
            logger = get_logger()
            logger.error(f"Failed to recover session: {e}")
            
            # Clean up on failure
            try:
                if os.path.exists(self.recovery_file):
                    os.remove(self.recovery_file)
            except:
                pass
            
            if hasattr(self, 'pending_recovery'):
                delattr(self, 'pending_recovery')
            
            return False
    
    def discard_recovery(self):
        """Discard pending recovery and start fresh"""
        try:
            if os.path.exists(self.recovery_file):
                os.remove(self.recovery_file)
            
            if hasattr(self, 'pending_recovery'):
                delattr(self, 'pending_recovery')
            
            logger = get_logger()
            logger.info("Discarded recovery data")
            return True
            
        except Exception as e:
            logger = get_logger()
            logger.error(f"Failed to discard recovery: {e}")
            return False

    def _calculate_daily_fatigue(self, session_data):
        """Calculate and store daily fatigue score based on session metrics
        
        Args:
            session_data: Session data dict with duration_minutes, strain_events, avg_jitter, avg_shimmer
        """
        today = datetime.now().date().isoformat()
        
        # Fatigue factors (0-100 scale, higher = more fatigue)
        duration_minutes = session_data.get('duration_minutes', 0)
        strain_events = session_data.get('strain_events', 0)
        avg_jitter = session_data.get('avg_jitter', 0)
        avg_shimmer = session_data.get('avg_shimmer', 0)
        
        # Calculate fatigue score
        fatigue_score = 0
        
        # Duration contribution (max 30 points)
        # 0-15 min = 5, 15-30 min = 10, 30-45 min = 20, 45+ min = 30
        if duration_minutes > 45:
            fatigue_score += 30
        elif duration_minutes > 30:
            fatigue_score += 20
        elif duration_minutes > 15:
            fatigue_score += 10
        else:
            fatigue_score += 5
        
        # Strain events contribution (max 35 points)
        # 0-3 = 0, 4-7 = 10, 8-15 = 20, 16+ = 35
        if strain_events > 15:
            fatigue_score += 35
        elif strain_events > 7:
            fatigue_score += 20
        elif strain_events > 3:
            fatigue_score += 10
        
        # Jitter contribution (max 20 points)
        # <1.0% = 0, 1.0-1.5% = 5, 1.5-2.0% = 10, >2.0% = 20
        if avg_jitter > 2.0:
            fatigue_score += 20
        elif avg_jitter > 1.5:
            fatigue_score += 10
        elif avg_jitter > 1.0:
            fatigue_score += 5
        
        # Shimmer contribution (max 15 points)
        # <5% = 0, 5-7% = 5, 7-10% = 10, >10% = 15
        if avg_shimmer > 10.0:
            fatigue_score += 15
        elif avg_shimmer > 7.0:
            fatigue_score += 10
        elif avg_shimmer > 5.0:
            fatigue_score += 5
        
        # If multiple sessions today, use weighted average
        if today in self.fatigue_history:
            existing_score = self.fatigue_history[today]
            self.fatigue_history[today] = (existing_score + fatigue_score) / 2
        else:
            self.fatigue_history[today] = fatigue_score
        
        # Keep only last 30 days
        cutoff_date = (datetime.now().date() - timedelta(days=30)).isoformat()
        self.fatigue_history = {
            date: score for date, score in self.fatigue_history.items()
            if date >= cutoff_date
        }

    def get_fatigue_trend(self, days=7):
        """Get fatigue trend over specified number of days
        
        Args:
            days: Number of days to analyze (default 7)
            
        Returns:
            dict with current_fatigue, avg_fatigue, trend, daily_scores
        """
        if not self.fatigue_history:
            return {
                'current_fatigue': 0,
                'avg_fatigue': 0,
                'trend': 'no_data',
                'daily_scores': []
            }
        
        # Get recent fatigue scores
        cutoff_date = (datetime.now().date() - timedelta(days=days)).isoformat()
        recent_scores = [
            {'date': date, 'score': score}
            for date, score in sorted(self.fatigue_history.items())
            if date >= cutoff_date
        ]
        
        if not recent_scores:
            return {
                'current_fatigue': 0,
                'avg_fatigue': 0,
                'trend': 'no_data',
                'daily_scores': []
            }
        
        scores = [item['score'] for item in recent_scores]
        current_fatigue = scores[-1] if scores else 0
        avg_fatigue = statistics.mean(scores) if scores else 0
        
        # Calculate trend (improving, stable, worsening)
        if len(scores) >= 3:
            recent_avg = statistics.mean(scores[-3:])
            older_avg = statistics.mean(scores[:-3]) if len(scores) > 3 else recent_avg
            
            if recent_avg > older_avg + 10:
                trend = 'worsening'
            elif recent_avg < older_avg - 10:
                trend = 'improving'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'current_fatigue': current_fatigue,
            'avg_fatigue': avg_fatigue,
            'trend': trend,
            'daily_scores': recent_scores
        }
    
    def break_pattern_analysis(self, break_taken_minutes: float = None) -> Dict[str, Any]:
        """Analyze and learn user's break patterns
        
        Args:
            break_taken_minutes: Time into session when break was taken (None = get recommendations)
            
        Returns:
            dict with recommended_break_time, learning_status, and confidence
        """
        if break_taken_minutes is not None:
            # Record break pattern
            self.user_break_preferences['typical_break_intervals'].append(break_taken_minutes)
            # Keep only last 20 break patterns
            self.user_break_preferences['typical_break_intervals'] = \
                self.user_break_preferences['typical_break_intervals'][-20:]
            self.user_break_preferences['last_break_time'] = datetime.now().isoformat()
            self.save_progress_data()
        
        # Calculate recommendations
        intervals = self.user_break_preferences['typical_break_intervals']
        
        if len(intervals) < 3:
            return {
                'recommended_break_time': 20,  # Default 20 minutes
                'learning_status': 'collecting_data',
                'confidence': 'low',
                'data_points': len(intervals),
                'message': 'Learning your break patterns...'
            }
        
        # Calculate average break timing
        avg_interval = statistics.mean(intervals)
        std_dev = statistics.stdev(intervals) if len(intervals) > 1 else 5
        
        # Determine confidence based on consistency
        if std_dev < 5:
            confidence = 'high'
        elif std_dev < 10:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        return {
            'recommended_break_time': round(avg_interval),
            'learning_status': 'learned',
            'confidence': confidence,
            'data_points': len(intervals),
            'std_deviation': round(std_dev, 1),
            'message': f'You typically take breaks around {round(avg_interval)} minutes'
        }
    
    def should_suggest_adaptive_break(self, current_session_minutes: float) -> Dict[str, Any]:
        """Determine if an adaptive break should be suggested
        
        Args:
            current_session_minutes: Current session duration in minutes
            
        Returns:
            dict with should_break, reason, and timing_info
        """
        break_analysis = self.break_pattern_analysis()
        recommended_time = break_analysis['recommended_break_time']
        
        # Check if we're near the user's typical break time
        time_diff = abs(current_session_minutes - recommended_time)
        
        if time_diff <= 2 and current_session_minutes >= recommended_time - 1:
            return {
                'should_break': True,
                'reason': 'natural_rhythm',
                'recommended_time': recommended_time,
                'confidence': break_analysis['confidence'],
                'message': f"Time for your usual {recommended_time}-minute break?"
            }
        elif current_session_minutes >= recommended_time + 10:
            return {
                'should_break': True,
                'reason': 'overdue',
                'recommended_time': recommended_time,
                'confidence': break_analysis['confidence'],
                'message': "You've gone longer than usual - consider a break"
            }
        else:
            return {
                'should_break': False,
                'reason': 'not_yet',
                'next_break_in': max(0, recommended_time - current_session_minutes),
                'message': f"Next break in ~{max(0, round(recommended_time - current_session_minutes))} minutes"
            }