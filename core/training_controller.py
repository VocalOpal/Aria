"""
Training Controller - Coordinates training sessions, exercises, and audio processing
Extracted from voice_trainer.py lines 672-731, 732-802, and audio callback logic
"""

import time
import numpy as np
from typing import Optional, Callable, Dict, Any
from collections import deque
from utils.file_operations import get_logger


class VoiceTrainingController:
    """Coordinates voice training sessions and exercises"""
    
    def __init__(self):
        self.current_exercise = None
        self.current_exercise_session = None
        self.is_training_active = False
        self.pause_training = False
        self.training_callback: Optional[Callable] = None
        
        # Audio processing optimization
        self._analysis_counter = 0
        self.resonance_quality = 0.5
        
        # Components (injected via dependencies)
        self.session_manager = None
        self.audio_manager = None
        self.safety_monitor = None
        self.progress_tracker = None
        self.analyzer = None
        self.alert_system = None
        self.achievement_manager = None
        self.ui_callback = None
    
    def set_dependencies(self, session_manager, audio_manager, safety_monitor, 
                        progress_tracker, analyzer, alert_system, achievement_manager=None):
        """Inject dependencies"""
        self.session_manager = session_manager
        self.audio_manager = audio_manager
        self.safety_monitor = safety_monitor
        self.progress_tracker = progress_tracker
        self.analyzer = analyzer
        self.alert_system = alert_system
        self.achievement_manager = achievement_manager
    
    def start_live_training(self, config: Dict[str, Any], ui_callback: Callable) -> bool:
        """Start live voice training session"""
        if not self._validate_dependencies():
            return False
            
        # Initialize audio system
        if not self.audio_manager.start_processing(self._create_audio_callback(config, ui_callback)):
            return False
        
        # Start session tracking
        current_goal = config.get('current_goal', 165)
        self.session_manager.start_session("live_training", current_goal)
        
        # Start safety monitoring
        if self.safety_monitor:
            self.safety_monitor.start_session()
        
        self.is_training_active = True
        self.pause_training = False
        return True
    
    def stop_live_training(self) -> Dict[str, Any]:
        """Stop live training and return session summary"""
        from utils.error_handler import log_error

        self.is_training_active = False
        session_duration = 0
        summary = None

        # Stop audio processing with error handling
        try:
            if self.audio_manager:
                self.audio_manager.stop_processing()
        except Exception as e:
            log_error(e, "TrainingController.stop_live_training - audio_manager.stop_processing")

        # End safety monitoring with error handling
        try:
            if self.safety_monitor:
                session_duration = self.safety_monitor.end_session()
        except Exception as e:
            log_error(e, "TrainingController.stop_live_training - safety_monitor.end_session")

        # Get session summary and end session with error handling
        try:
            if self.session_manager:
                summary = self.session_manager.get_session_summary()
        except Exception as e:
            log_error(e, "TrainingController.stop_live_training - session_manager.get_session_summary")

        try:
            if self.session_manager:
                self.session_manager.end_session()
        except Exception as e:
            log_error(e, "TrainingController.stop_live_training - session_manager.end_session")

        newly_unlocked = []
        try:
            if self.achievement_manager and self.session_manager:
                sessions = getattr(self.session_manager, 'weekly_sessions', [])
                if sessions:
                    previous_earned_count = getattr(self.session_manager, '_achievement_count', 0)
                    newly_unlocked = self.achievement_manager.check_for_new_achievements(sessions, previous_earned_count)

                    if newly_unlocked:
                        self.session_manager._achievement_count = previous_earned_count + len(newly_unlocked)

                        if self.ui_callback:
                            for achievement in newly_unlocked:
                                self._show_achievement_toast(achievement)
        except Exception as e:
            log_error(e, "TrainingController.stop_live_training - achievement check")

        return {
            'session_duration': session_duration,
            'summary': summary,
            'newly_unlocked_achievements': newly_unlocked
        }
    
    def start_exercise(self, exercise_name: str, exercise_data: Dict, ui_callback: Callable) -> bool:
        """Start a specific exercise session"""
        if not self._validate_dependencies():
            return False
        
        # Import here to avoid circular imports
        from gui.exercises import ExerciseSession
        
        # Create exercise session
        self.current_exercise = ExerciseSession(exercise_data)
        self.current_exercise.start()
        
        # Start progress tracking
        if self.progress_tracker:
            self.progress_tracker.start_session(exercise_name)
        
        # Initialize audio system with exercise-specific callback
        if not self.audio_manager.start_processing(self._create_exercise_callback(ui_callback)):
            self.current_exercise = None
            return False
        
        # Start session tracking
        self.session_manager.start_session("exercise", exercise_data.get('target_range', [165, 200])[0])
        self.is_training_active = True
        
        return True
    
    def stop_exercise(self) -> float:
        """Stop current exercise and return completion rate"""
        from utils.error_handler import log_error

        completion_rate = 0.0

        try:
            if self.current_exercise:
                completion_rate = 1.0 - (self.current_exercise.get_remaining_time() / self.current_exercise.duration)

                if self.progress_tracker:
                    self.progress_tracker.finish_session(completion_rate)

                self.current_exercise.stop()
                self.current_exercise = None
        except Exception as e:
            log_error(e, "TrainingController.stop_exercise - stopping exercise")

        # Stop audio processing with error handling
        try:
            if self.audio_manager:
                self.audio_manager.stop_processing()
        except Exception as e:
            log_error(e, "TrainingController.stop_exercise - audio_manager.stop_processing")

        # End session with error handling
        try:
            if self.session_manager:
                self.session_manager.end_session()
        except Exception as e:
            log_error(e, "TrainingController.stop_exercise - session_manager.end_session")

        self.is_training_active = False
        return completion_rate
    
    def run_warmup_routine(self, exercises_component, ui_callback: Callable):
        """Run complete warm-up routine"""
        sequence = exercises_component.get_warmup_sequence()
        
        for i, exercise_name in enumerate(sequence, 1):
            exercise_data = exercises_component.get_exercise(exercise_name)
            if not exercise_data:
                continue
            
            # UI callback for exercise info
            ui_callback('show_exercise', {
                'step': i,
                'total': len(sequence),
                'exercise': exercise_data
            })
            
            # Run this exercise
            if self.start_exercise(exercise_name, exercise_data, ui_callback):
                # Exercise loop
                while (self.current_exercise and 
                       self.current_exercise.is_active and 
                       not self.current_exercise.is_complete()):
                    time.sleep(0.1)  # Small delay to prevent busy waiting
                
                self.stop_exercise()
    
    def pause_resume_training(self) -> bool:
        """Toggle training pause state"""
        self.pause_training = not self.pause_training
        return self.pause_training
    
    def get_training_status(self) -> Dict[str, Any]:
        """Get current training status"""
        status = {
            'is_active': self.is_training_active,
            'is_paused': self.pause_training,
            'current_exercise': None
        }
        
        if self.current_exercise:
            status['current_exercise'] = {
                'remaining_time': self.current_exercise.get_remaining_time(),
                'is_complete': self.current_exercise.is_complete(),
                'name': getattr(self.current_exercise, 'exercise_data', {}).get('name', 'Unknown')
            }
        
        return status
    
    def _create_audio_callback(self, config: Dict[str, Any], ui_callback: Callable) -> Callable:
        """Create audio callback for live training"""
        def audio_callback(audio_data):
            try:
                self._process_audio_data(audio_data, config, ui_callback, session_type="live")
            except Exception as e:
                get_logger().error(f"Audio callback error: {e}")
        
        return audio_callback
    
    def _create_exercise_callback(self, ui_callback: Callable) -> Callable:
        """Create audio callback for exercise sessions"""
        def audio_callback(audio_data):
            try:
                # Simplified config for exercises
                config = {
                    'current_goal': 165,
                    'current_goal': 165,
                    'sensitivity': 1.0,
                    'vad_threshold': 0.01,
                    'noise_threshold': 0.02,
                    'dip_tolerance_duration': 5.0
                }
                self._process_audio_data(audio_data, config, ui_callback, session_type="exercise")
            except Exception as e:
                get_logger().error(f"Exercise audio callback error: {e}")
        
        return audio_callback
    
    def _process_audio_data(self, audio_data, config: Dict[str, Any], ui_callback: Callable, session_type: str):
        """Process audio data with noise handling and analysis"""
        if not self.analyzer:
            return
        
        # Handle noise learning phase
        def noise_feedback(message):
            ui_callback('noise_feedback', {'message': message})
        
        self.analyzer.update_noise_profile(audio_data, noise_feedback)
        if self.analyzer.learning_noise:
            return
        
        # Check for background noise and handle timer pausing
        vad_threshold = config.get('vad_threshold', 0.01)
        sensitivity = config.get('sensitivity', 1.0)
        noise_threshold = config.get('noise_threshold', 0.02)
        
        only_background = self.analyzer.check_background_noise_only(audio_data, vad_threshold, sensitivity)
        
        # Handle noise pause via session manager
        pause_status = self.session_manager.handle_noise_pause(only_background)
        
        if pause_status == "timer_paused":
            ui_callback('status_update', {'message': "Background noise only - timer paused"})
            return
        elif pause_status == "timer_resumed":
            ui_callback('status_update', {'message': "Voice detected - timer resumed"})
        
        # Skip processing if only background noise
        if only_background:
            return
        
        # Apply sensitivity and check signal level
        audio_data = audio_data * float(sensitivity)
        
        if float(np.max(np.abs(audio_data))) < float(noise_threshold):
            return
        
        # Voice activity detection
        if not self.analyzer.is_voice_active(audio_data, vad_threshold, sensitivity):
            return
        
        # Detect pitch
        pitch = self.analyzer.detect_pitch(audio_data)
        if not (self.analyzer.MIN_FREQ < pitch < self.analyzer.MAX_FREQ):
            return
        
        # Update session statistics
        min_threshold = config.get('current_goal', 165)  # Use current_goal as the minimum threshold
        current_goal = config.get('current_goal', 165)
        self.session_manager.update_session_stats(pitch, min_threshold, current_goal)
        
        # Skip heavy analysis if paused
        if self.pause_training:
            return
        
        # Optimize CPU usage with selective analysis
        self._analysis_counter += 1
        
        formant_data = None
        voice_quality_metrics = None
        if self._analysis_counter % 5 == 0:  # Heavy analysis every 5th frame
            formant_data = self.analyzer.analyze_formants(audio_data)
            self.resonance_quality = self.analyzer.calculate_resonance_quality(audio_data)

            # Update resonance stats if formant data is available
            if formant_data and 'f1' in formant_data:
                f1 = formant_data.get('f1', 0)
                if f1 > 0:
                    resonance_data = {
                        'frequency': f1,
                        'baseline': self.analyzer.resonance_baseline.get('f1', 500),
                        'deviation': f1 - self.analyzer.resonance_baseline.get('f1', 500)
                    }
                    self.session_manager.update_resonance_stats(resonance_data)
        
        # Voice quality analysis (less frequent - every 10th frame)
        if self._analysis_counter % 10 == 0:
            breathiness = self.analyzer.calculate_breathiness_score(audio_data)
            nasality = self.analyzer.calculate_nasality_score(audio_data)
            voice_quality_metrics = {
                'breathiness': breathiness,
                'nasality': nasality
            }
            # Update session stats
            self.session_manager.update_voice_quality_stats(voice_quality_metrics)

        # Vocal roughness analysis (every 15th frame to balance accuracy and performance)
        roughness_metrics = None
        if self._analysis_counter % 15 == 0:
            roughness_metrics = self.analyzer.calculate_vocal_roughness(audio_data, pitch)
            # Update session manager with roughness data
            self.session_manager.update_roughness_stats(roughness_metrics)

        # Voice safety monitoring
        if self.safety_monitor:
            energy_level = float(np.sqrt(np.mean(audio_data ** 2)))
            safety_warnings = self.safety_monitor.update_voice_data(pitch, energy_level, audio_data, roughness_metrics)

            for warning in safety_warnings:
                ui_callback('safety_warning', warning)
                # Track safety warnings in session stats
                warning_type = warning.get('type')
                if warning_type:
                    self.session_manager.update_safety_warning_stats(warning_type)
        
        # Update exercise progress if active
        if self.current_exercise:
            self.current_exercise.update_breathing(audio_data)
            if formant_data and self.progress_tracker:
                self.progress_tracker.update_formants(formant_data)
                self.progress_tracker.update_pitch(pitch)
        
        # Check dip tolerance and alerts
        dip_tolerance_duration = config.get('dip_tolerance_duration', 5.0)
        should_alert, dip_info = self.session_manager.check_dip_tolerance(pitch, min_threshold, dip_tolerance_duration)
        
        # Prepare status information for UI
        status_info = {
            'pitch': pitch,
            'goal_hz': min_threshold,
            'current_goal': current_goal,
            'resonance_quality': self.resonance_quality,
            'dip_info': dip_info,
            'formant_info': formant_data
        }
        
        # Add exercise info if active
        if self.current_exercise:
            status_info['exercise_info'] = {
                'remaining_time': self.current_exercise.get_remaining_time(),
                'complete': self.current_exercise.is_complete()
            }
        
        # Send status to UI
        ui_callback('training_status', status_info)
        
        # Handle alerts
        if should_alert:
            self.alert_system.play_low_alert()
            self.session_manager.update_alert_stats("low")
        
        # High pitch alert (with buffer to be less strict)
        high_pitch_threshold = getattr(self.alert_system, 'high_pitch_threshold', 400)
        if pitch > (high_pitch_threshold + 20):
            self.alert_system.play_high_alert()
            self.session_manager.update_alert_stats("high")
        
        # Check exercise completion
        if self.current_exercise and self.current_exercise.is_complete():
            ui_callback('exercise_complete', {'completion_rate': 1.0})
    
    def _validate_dependencies(self) -> bool:
        """Validate that all required dependencies are available"""
        required = [
            self.session_manager, 
            self.audio_manager, 
            self.analyzer, 
            self.alert_system
        ]
        return all(dep is not None for dep in required)
    
    def cleanup(self):
        """Cleanup controller resources"""
        from utils.error_handler import log_error

        try:
            if self.is_training_active:
                self.stop_live_training()
        except Exception as e:
            log_error(e, "TrainingController.cleanup - stop_live_training")

        try:
            if self.current_exercise:
                self.stop_exercise()
        except Exception as e:
            log_error(e, "TrainingController.cleanup - stop_exercise")

        self.current_exercise = None
        self.is_training_active = False
    
    def _show_achievement_toast(self, achievement: Dict[str, Any]):
        try:
            if self.ui_callback:
                self.ui_callback('achievement_unlocked', {
                    'name': achievement.get('name', 'Achievement Unlocked'),
                    'description': achievement.get('description', ''),
                    'rarity': achievement.get('rarity', 'common')
                })
        except Exception as e:
            get_logger().error(f"Failed to show achievement toast: {e}")