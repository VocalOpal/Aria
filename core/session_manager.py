"""
Session Manager - Handles session lifecycle, statistics, and progress tracking
Extracted from voice_trainer.py lines 184-317, 538-671, 803-825
"""

import numpy as np
import time
import json
import os
from collections import deque
from datetime import datetime
import statistics


class VoiceSessionManager:
    """Manages voice training session lifecycle, stats, and progress"""
    
    def __init__(self, config_file="data/voice_config.json"):
        self.config_file = config_file
        self.progress_file = config_file.replace('.json', '_progress.json')
        
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
            'last_update': time.time()
        }
    
    def start_session(self, session_type="training", current_goal=165):
        """Start a new training session"""
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
        if self.current_session:
            self.save_session_data()
            self.current_session = None
        return True
    
    def update_session_stats(self, pitch, threshold_hz, current_goal):
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
            if pitch >= threshold_hz:
                self.session_stats['time_in_range'] += 1
            
            if pitch >= current_goal:
                self.session_stats['goal_achievements'] += 1
                
            # Track session pitch range
            self.session_range_low = min(self.session_range_low, pitch)
            self.session_range_high = max(self.session_range_high, pitch)
            
            # Auto-save periodically
            current_time = time.time()
            if current_time - self.last_auto_save > self.auto_save_interval:
                self.save_progress_data()
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
    
    def check_dip_tolerance(self, pitch, threshold_hz, dip_tolerance_duration):
        """Check if current pitch dip should trigger alert"""
        self.pitch_buffer.append(pitch)
        
        if len(self.pitch_buffer) >= 5:
            recent_median = statistics.median(list(self.pitch_buffer)[-5:])
        else:
            recent_median = pitch
            
        current_time = time.time()
        
        if recent_median < (threshold_hz - 15):  # 15Hz below goal triggers dip
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
        if not self.current_session or self.session_stats['total_time'] == 0:
            return False
        
        # Calculate actual training time (excluding noise pauses)
        session_duration_seconds = (datetime.now() - self.session_stats['start_time']).total_seconds()
        active_training_seconds = max(0, session_duration_seconds - self.total_noise_pause_time)
        voice_data_seconds = self.session_stats['total_time']  # This is actual voice processing time
        
        # Require at least 1 minute (60 seconds) of voice data for session to be saved
        if voice_data_seconds < 60:
            print(f"\nSession too short to save (need 1+ minutes of voice data, got {voice_data_seconds:.0f}s)")
            print("Try training longer to build meaningful progress data!")
            return False
            
        try:
            session_data = {
                'date': datetime.now().isoformat(),
                'duration_minutes': (datetime.now() - self.session_stats['start_time']).total_seconds() / 60,
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
                'session_type': self.current_session.get('type', 'training')
            }
            
            self.weekly_sessions.append(session_data)
            # Keep last 84 sessions (~12 weeks)
            self.weekly_sessions = self.weekly_sessions[-84:]
            self.save_progress_data()
            return True
            
        except Exception as e:
            print(f"Error saving session data: {e}")
            return False
    
    def load_progress_data(self):
        """Load progress tracking data from file"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    self.weekly_sessions = data.get('weekly_sessions', [])
            except Exception as e:
                print(f"Error loading progress data: {e}")
                self.weekly_sessions = []
        else:
            self.weekly_sessions = []
    
    def save_progress_data(self):
        """Save progress tracking data to file"""
        data = {
            'weekly_sessions': self.weekly_sessions,
            'last_updated': datetime.now().isoformat()
        }
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
            
            with open(self.progress_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving progress data: {e}")
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
    
    def clear_all_data(self):
        """Clear all session and progress data"""
        self.weekly_sessions = []
        self.session_stats = self._create_empty_stats()
        self.current_session = None
        
        # Try to delete progress file
        try:
            if os.path.exists(self.progress_file):
                os.remove(self.progress_file)
        except Exception:
            pass
        
        return True