"""
Training Controller - Coordinates training sessions, exercises, and audio processing
Extracted from voice_trainer.py lines 672-731, 732-802, and audio callback logic
"""

import time
import numpy as np
from typing import Optional, Callable, Dict, Any
from collections import deque


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
    
    def set_dependencies(self, session_manager, audio_manager, safety_monitor, 
                        progress_tracker, analyzer, alert_system):
        """Inject dependencies"""
        self.session_manager = session_manager
        self.audio_manager = audio_manager
        self.safety_monitor = safety_monitor
        self.progress_tracker = progress_tracker
        self.analyzer = analyzer
        self.alert_system = alert_system
    
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
        self.is_training_active = False
        
        # Stop audio processing
        if self.audio_manager:
            self.audio_manager.stop_processing()
        
        # End safety monitoring and get duration
        session_duration = 0
        if self.safety_monitor:
            session_duration = self.safety_monitor.end_session()
        
        # Get session summary
        summary = None
        if self.session_manager:
            summary = self.session_manager.get_session_summary()
            self.session_manager.end_session()
        
        return {
            'session_duration': session_duration,
            'summary': summary
        }
    
    def start_exercise(self, exercise_name: str, exercise_data: Dict, ui_callback: Callable) -> bool:
        """Start a specific exercise session"""
        if not self._validate_dependencies():
            return False
        
        # Import here to avoid circular imports
        from voice_exercises import ExerciseSession
        
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
        completion_rate = 0.0
        
        if self.current_exercise:
            completion_rate = 1.0 - (self.current_exercise.get_remaining_time() / self.current_exercise.duration)
            
            if self.progress_tracker:
                self.progress_tracker.finish_session(completion_rate)
            
            self.current_exercise.stop()
            self.current_exercise = None
        
        # Stop audio processing
        if self.audio_manager:
            self.audio_manager.stop_processing()
        
        # End session
        if self.session_manager:
            self.session_manager.end_session()
        
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
                print(f"Audio callback error: {e}")
        
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
                print(f"Exercise audio callback error: {e}")
        
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
        if self._analysis_counter % 5 == 0:  # Heavy analysis every 5th frame
            formant_data = self.analyzer.analyze_formants(audio_data)
            self.resonance_quality = self.analyzer.calculate_resonance_quality(audio_data)
        
        # Voice safety monitoring
        if self.safety_monitor:
            energy_level = float(np.sqrt(np.mean(audio_data ** 2)))
            safety_warnings = self.safety_monitor.update_voice_data(pitch, energy_level, audio_data)
            
            for warning in safety_warnings:
                ui_callback('safety_warning', warning)
        
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
        if self.is_training_active:
            self.stop_live_training()
        
        if self.current_exercise:
            self.stop_exercise()
        
        self.current_exercise = None
        self.is_training_active = False