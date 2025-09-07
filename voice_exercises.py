import time
from collections import deque
import numpy as np

class VoiceExercises:
    """Voice training exercises for vocal development"""
    
    def __init__(self):
        self.exercises = {
            'humming_warmup': {
                'name': 'Humming Resonance Warm-up',
                'duration': 60,
                'instructions': 'Hum at comfortable pitch, feel vibrations in face/head (not chest)',
                'target_range': (160, 200),
                'breathing_focus': True,
                'tips': [
                    'Place hand on chest - should feel minimal vibration',
                    'Place hand on face/nose - should feel strong vibration',
                    'Start low and gradually move higher'
                ]
            },
            'lip_trills': {
                'name': 'Lip Trill Exercise',
                'duration': 45,
                'instructions': 'Make "brrr" sound, glide pitch up and down smoothly',
                'target_range': (150, 250),
                'breathing_focus': True,
                'tips': [
                    'Keep lips relaxed and loose',
                    'Use steady airflow',
                    'Glide smoothly between pitches'
                ]
            },
            'pitch_slides': {
                'name': 'Pitch Glides',
                'duration': 90,
                'instructions': 'Slide from low to high pitch on "nee" sound, focus on head resonance',
                'target_range': (140, 280),
                'breathing_focus': False,
                'tips': [
                    'Use "nee" sound for forward resonance',
                    'Start at comfortable low pitch',
                    'Glide smoothly to highest comfortable pitch',
                    'Focus resonance in face/head area'
                ]
            },
            'straw_phonation': {
                'name': 'Straw Phonation',
                'duration': 120,
                'instructions': 'Hum through imaginary straw, creates efficient phonation',
                'target_range': (165, 220),
                'breathing_focus': True,
                'tips': [
                    'Purse lips as if drinking through straw',
                    'Hum any comfortable pitch',
                    'Focus on smooth, controlled sound',
                    'This exercise improves vocal efficiency'
                ]
            },
            'resonance_shift': {
                'name': 'Forward Resonance Training',
                'duration': 75,
                'instructions': 'Say "me-may-my-mo-moo" focusing sound in nasal cavity/face',
                'target_range': (170, 250),
                'breathing_focus': False,
                'tips': [
                    'Feel vibrations in nose and face',
                    'Avoid chest resonance',
                    'Exaggerate the nasal quality',
                    'Practice slowly, then speed up'
                ]
            },
            'breathing_control': {
                'name': 'Diaphragmatic Breathing',
                'duration': 90,
                'instructions': 'Deep belly breathing, hand on chest should not move',
                'target_range': (0, 0),
                'breathing_focus': True,
                'tips': [
                    'Place one hand on chest, one on belly',
                    'Breathe so only belly hand moves',
                    'Chest should remain relatively still',
                    'This builds foundation for voice control'
                ]
            }
        }
        
    def get_exercise(self, name):
        """Get exercise by name"""
        return self.exercises.get(name)
        
    def get_all_exercises(self):
        """Get all available exercises"""
        return self.exercises
        
    def get_warmup_sequence(self):
        """Get recommended warm-up sequence"""
        return ['breathing_control', 'humming_warmup', 'lip_trills', 'pitch_slides']
        
    def validate_exercise_name(self, name):
        """Check if exercise name is valid"""
        return name in self.exercises


class ExerciseSession:
    """Manage an active exercise session"""
    
    def __init__(self, exercise_data):
        self.exercise_data = exercise_data
        self.start_time = None
        self.duration = exercise_data['duration']
        self.is_active = False
        self.breathing_tracker = BreathingTracker() if exercise_data['breathing_focus'] else None
        
    def start(self):
        """Start the exercise session"""
        self.start_time = time.time()
        self.is_active = True
        if self.breathing_tracker:
            self.breathing_tracker.start_tracking()
            
    def get_remaining_time(self):
        """Get remaining time in seconds"""
        if not self.start_time:
            return self.duration
            
        elapsed = time.time() - self.start_time
        remaining = max(0, self.duration - elapsed)
        return remaining
        
    def is_complete(self):
        """Check if exercise is complete"""
        return self.get_remaining_time() <= 0
        
    def stop(self):
        """Stop the exercise session"""
        self.is_active = False
        if self.breathing_tracker:
            self.breathing_tracker.stop_tracking()
            
    def update_breathing(self, audio_data):
        """Update breathing analysis if applicable"""
        if self.breathing_tracker and self.is_active:
            self.breathing_tracker.analyze_breath(audio_data)
            
    def get_breathing_quality(self):
        """Get current breathing quality score"""
        if self.breathing_tracker:
            return self.breathing_tracker.get_quality_score()
        return None


class BreathingTracker:
    """Track and analyze breathing patterns"""
    
    def __init__(self):
        self.breath_pattern = deque(maxlen=50)
        self.is_tracking = False
        self.quality_score = 0.0
        
    def start_tracking(self):
        """Start breath tracking"""
        self.is_tracking = True
        self.breath_pattern.clear()
        
    def stop_tracking(self):
        """Stop breath tracking"""
        self.is_tracking = False
        
    def analyze_breath(self, audio_data):
        """Analyze breathing from audio energy"""
        if not self.is_tracking:
            return
            
        # Calculate RMS energy efficiently
        energy = float(np.sqrt(np.mean(np.square(audio_data))))
        current_time = time.time()
        
        self.breath_pattern.append({
            'energy': energy,
            'timestamp': current_time
        })
        
        # Calculate breathing quality (steady vs erratic)
        if len(self.breath_pattern) >= 10:
            # Use list comprehension with slice for efficiency
            recent_energies = [b['energy'] for b in self.breath_pattern][-10:]
            energy_variance = np.var(recent_energies)
            
            # Lower variance = more controlled breathing
            self.quality_score = max(0.0, 1.0 - (energy_variance * 10.0))
            
    def get_quality_score(self):
        """Get current breathing quality score (0-1)"""
        return self.quality_score


class ProgressTracker:
    """Track exercise progress and improvements"""
    
    def __init__(self):
        self.exercise_history = []
        self.session_stats = {}
        
    def start_session(self, exercise_name):
        """Start tracking a new exercise session"""
        self.session_stats = {
            'exercise_name': exercise_name,
            'start_time': time.time(),
            'pitch_data': [],
            'formant_data': [],
            'breathing_data': [],
            'completion_rate': 0.0
        }
        
    def update_pitch(self, pitch):
        """Update pitch data for current session"""
        if 'pitch_data' in self.session_stats:
            self.session_stats['pitch_data'].append({
                'pitch': pitch,
                'timestamp': time.time()
            })
            
    def update_formants(self, formant_data):
        """Update formant data for current session"""
        if 'formant_data' in self.session_stats and formant_data:
            self.session_stats['formant_data'].append(formant_data)
            
    def update_breathing(self, quality_score):
        """Update breathing quality data"""
        if 'breathing_data' in self.session_stats and quality_score is not None:
            self.session_stats['breathing_data'].append({
                'quality': quality_score,
                'timestamp': time.time()
            })
            
    def finish_session(self, completion_rate):
        """Finish current exercise session"""
        if self.session_stats:
            self.session_stats['end_time'] = time.time()
            self.session_stats['completion_rate'] = completion_rate
            self.exercise_history.append(self.session_stats.copy())
            self.session_stats = {}
            
    def get_exercise_stats(self, exercise_name):
        """Get statistics for a specific exercise"""
        exercise_sessions = [s for s in self.exercise_history if s['exercise_name'] == exercise_name]
        
        if not exercise_sessions:
            return None
            
        # Calculate average metrics
        completion_rates = [s['completion_rate'] for s in exercise_sessions]
        avg_completion = np.mean(completion_rates)
        
        # Collect all pitch data efficiently
        all_pitches = []
        for session in exercise_sessions:
            pitch_data = session.get('pitch_data', [])
            all_pitches.extend([p['pitch'] for p in pitch_data])
            
        stats = {
            'sessions_completed': len(exercise_sessions),
            'avg_completion_rate': avg_completion,
            'avg_pitch': np.mean(all_pitches) if all_pitches else 0.0,
            'pitch_range': (float(min(all_pitches)), float(max(all_pitches))) if all_pitches else (0.0, 0.0)
        }
        
        return stats