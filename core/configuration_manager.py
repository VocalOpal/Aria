"""
Configuration Manager - Manages all configuration, presets, and goal updates
Extracted from voice_trainer.py lines 319-457, 904-998
"""

import json
import os
from pathlib import Path
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime
from utils.file_operations import safe_save_config, safe_load_config, get_logger
from utils.emoji_handler import convert_emoji_text, get_status_indicator


class VoiceConfigurationManager:
    """Manages voice training configuration and settings"""
    
    def __init__(self, config_file="data/voice_config.json"):
        self.config_file = config_file
        
        # Default configuration
        self.default_config = {
            'base_goal': 165,
            'current_goal': 165,
            'goal_increment': 3,
            'sensitivity': 1.0,
            'vad_threshold': 0.01,
            'noise_threshold': 0.02,
            'dip_tolerance_duration': 6.0,
            'auto_save_interval': 30,
            'high_pitch_threshold': 400,
            'session_duration_target': 15 * 60,
            'max_recommended_duration': 45 * 60,
            'setup_completed': False,
            'onboarding_completed': False,
            # Analysis mode settings
            'analysis_mode': 'Balanced',  # Strict, Balanced, or Looser
            # Smoothed display settings
            'smooth_display_enabled': True,
            'display_range_size': 10,  # Hz range for smoothed display (e.g. 160-170 Hz)
            'alert_warning_time': 5.0,  # Seconds before beep to show warning
            'exact_numbers_mode': False  # True to show exact Hz, False for ranges
        }
        
        # Current configuration
        self.config = self.default_config.copy()

        # Initialize logger
        self.logger = get_logger()

        # Load existing configuration
        self.load_config()
    
    def load_config(self) -> bool:
        """Load configuration from file using safe operations"""
        try:
            config_data = safe_load_config(self.config_file, self.default_config)
            self.config.update(config_data)
            self.logger.info(f"Configuration loaded from {self.config_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return False
    
    def save_config(self) -> bool:
        """Save current configuration to file using atomic operations"""
        try:
            success = safe_save_config(self.config, self.config_file)
            if success:
                self.logger.info(f"Configuration saved to {self.config_file}")
            else:
                self.logger.error(f"Failed to save configuration to {self.config_file}")
            return success
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update configuration with new values"""
        self.config.update(updates)
        return self.save_config()
    
    def apply_preset(self, preset_name: str) -> bool:
        """Apply a voice preset to current configuration"""
        try:
            from voice.presets import VoicePresets
            presets = VoicePresets()
            preset = presets.get_preset(preset_name)
            
            if not preset:
                return False
            
            updated_config = presets.apply_preset_to_config(preset_name, self.config)
            self.config.update(updated_config)
            
            # Mark preset as applied
            self.config['current_preset'] = preset_name
            self.config['preset_applied_date'] = datetime.now().isoformat()
            
            return self.save_config()
            
        except Exception as e:
            self.logger.error(f"Error applying preset: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values"""
        # Preserve some user-specific settings
        preserve_keys = ['setup_completed', 'onboarding_completed', 'current_preset']
        preserved = {key: self.config.get(key) for key in preserve_keys if key in self.config}
        
        self.config = self.default_config.copy()
        self.config.update(preserved)
        
        return self.save_config()
    
    def update_current_goal(self, session_manager) -> float:
        """Update current goal based on adaptive progression system"""
        if not hasattr(session_manager, 'weekly_sessions') or not session_manager.weekly_sessions:
            # First time user - set adaptive starting point
            self._set_adaptive_starting_goal()
            return self.config['current_goal']
        
        # Get user's current average from recent sessions
        recent_sessions = session_manager.weekly_sessions[-10:]  # Last 10 sessions
        if len(recent_sessions) < 3:
            return self.config['current_goal']  # Need more data
        
        current_avg = np.mean([s['avg_pitch'] for s in recent_sessions])
        
        # Determine target goals based on voice training type
        target_goals = self._get_progressive_targets(current_avg)
        
        # Check consistency over recent sessions
        recent_4_sessions = recent_sessions[-4:]
        consistency_rate = sum(1 for s in recent_4_sessions 
                             if abs(s['avg_pitch'] - self.config['current_goal']) <= 10) / len(recent_4_sessions)
        
        # Very gradual progression - only advance if consistently hitting current goal
        if consistency_rate >= 0.70 and current_avg >= (self.config['current_goal'] - 5):
            # Ready to progress
            next_target = self._get_next_progressive_target(current_avg, target_goals)
            if next_target > self.config['current_goal']:
                # Small step forward (2-5 Hz at a time)
                increment = min(self.config['goal_increment'], 5)
                self.config['current_goal'] = min(next_target, self.config['current_goal'] + increment)
            elif next_target < self.config['current_goal']:
                # Small step backward (FTM training)
                decrement = min(abs(self.config['goal_increment']), 3)
                self.config['current_goal'] = max(next_target, self.config['current_goal'] - decrement)
        elif consistency_rate < 0.50:
            # Struggling - take a small step back to build confidence
            step_back = min(3, abs(self.config['goal_increment']) // 2)
            if self.config['goal_increment'] > 0:  # MTF training
                self.config['current_goal'] = max(self.config['base_goal'], self.config['current_goal'] - step_back)
            else:  # FTM training
                self.config['current_goal'] = min(self.config['base_goal'], self.config['current_goal'] + step_back)
        
        # Ensure goal stays within safe ranges
        self.config['current_goal'] = max(80, min(350, self.config['current_goal']))
        # threshold_hz is now unified with current_goal
        
        # Save updated goal
        self.save_config()
        return self.config['current_goal']
    
    def _set_adaptive_starting_goal(self):
        """Set starting goal based on user's voice type and current capabilities"""
        self.config['current_goal'] = self.config['base_goal']
    
    def _get_progressive_targets(self, current_avg: float) -> list:
        """Get progressive target milestones based on voice training type"""
        if self.config['goal_increment'] > 0:  # MTF training
            if current_avg < 165:
                return [165, 180, 200]
            elif current_avg < 200:
                return [180, 200, 220]
            else:
                return [200, 220, 240]
        else:  # FTM training
            if current_avg > 155:
                return [155, 140, 125]
            elif current_avg > 125:
                return [140, 125, 110]
            else:
                return [125, 110, 100]
    
    def _get_next_progressive_target(self, current_avg: float, targets: list) -> float:
        """Get the next appropriate target from the progression list"""
        for target in targets:
            if self.config['goal_increment'] > 0 and target > current_avg + 5:
                return target
            elif self.config['goal_increment'] < 0 and target < current_avg - 5:
                return target
        return targets[-1]  # Return final target if close to completion
    
    def get_recommended_session_duration(self, session_manager) -> str:
        """Get recommended session duration based on user experience"""
        if not hasattr(session_manager, 'weekly_sessions') or not session_manager.weekly_sessions:
            return "10-15"  # Beginners start small
        
        total_sessions = len(session_manager.weekly_sessions)
        recent_sessions = session_manager.weekly_sessions[-10:]
        
        if total_sessions < 5:
            return "10-20"  # Still building habits
        elif total_sessions < 15:
            avg_duration = np.mean([s.get('duration_minutes', 15) for s in recent_sessions])
            if avg_duration < 20:
                return "15-25"  # Gradually increasing
            else:
                return "20-30"
        else:
            # Experienced users
            avg_duration = np.mean([s.get('duration_minutes', 20) for s in recent_sessions])
            if avg_duration < 25:
                return "20-35"
            else:
                return "30-45"  # Cap at 45 minutes
    
    def set_threshold(self, new_value: float) -> bool:
        """Set pitch threshold programmatically"""
        try:
            if 80 <= new_value <= 350:  # Validate range
                self.config['current_goal'] = new_value
                return self.save_config()
            else:
                self.logger.warning(f"Threshold {new_value} Hz is outside safe range (80-350 Hz)")
                return False
        except Exception as e:
            self.logger.error(f"Error setting threshold: {e}")
            return False
    
    def set_sensitivity(self, new_value: float) -> bool:
        """Set microphone sensitivity programmatically"""
        try:
            # Clamp to valid range
            value = max(0.1, min(3.0, new_value))
            self.config['sensitivity'] = value
            return self.save_config()
        except Exception as e:
            self.logger.error(f"Error setting sensitivity: {e}")
            return False
    
    def set_dip_tolerance(self, new_value: float) -> bool:
        """Set dip tolerance programmatically"""
        try:
            # Clamp to valid range
            value = max(0.5, min(10.0, new_value))
            self.config['dip_tolerance_duration'] = value
            return self.save_config()
        except Exception as e:
            self.logger.error(f"Error setting dip tolerance: {e}")
            return False
    
    def set_high_pitch_threshold(self, new_value: float) -> bool:
        """Set high pitch threshold programmatically"""
        try:
            # Clamp to valid range
            value = max(300, min(500, new_value))
            self.config['high_pitch_threshold'] = value
            return self.save_config()
        except Exception as e:
            self.logger.error(f"Error setting high pitch threshold: {e}")
            return False
    
    def is_first_time_setup(self) -> bool:
        """Check if this is first-time setup"""
        return not self.config.get('setup_completed', False)
    
    def mark_setup_complete(self):
        """Mark initial setup as completed"""
        self.config['setup_completed'] = True
        self.config['setup_date'] = datetime.now().isoformat()
        self.save_config()
    
    def is_onboarding_needed(self) -> bool:
        """Check if onboarding is needed"""
        return not self.config.get('onboarding_completed', False)
    
    def mark_onboarding_complete(self):
        """Mark onboarding as completed"""
        self.config['onboarding_completed'] = True
        self.config['onboarding_date'] = datetime.now().isoformat()
        self.save_config()
    
    def clear_all_data(self) -> bool:
        """Clear configuration file"""
        try:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
            
            # Reset to defaults but mark as needing setup
            self.config = self.default_config.copy()
            self.config['setup_completed'] = False
            self.config['onboarding_completed'] = False
            
            return True
        except Exception as e:
            self.logger.error(f"Error clearing config data: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration"""
        return {
            'voice_goal': self.config.get('current_preset', 'Custom'),
            'current_goal_hz': self.config['current_goal'],
            'base_goal_hz': self.config['base_goal'],
            'goal_increment': self.config['goal_increment'],
            'training_direction': 'MTF' if self.config['goal_increment'] > 0 else 'FTM' if self.config['goal_increment'] < 0 else 'Neutral',
            'sensitivity': self.config['sensitivity'],
            'dip_tolerance': self.config['dip_tolerance_duration'],
            'high_pitch_alert': self.config['high_pitch_threshold'],
            'setup_completed': self.config['setup_completed'],
            'onboarding_completed': self.config['onboarding_completed']
        }