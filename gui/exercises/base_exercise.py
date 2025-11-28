import time
from collections import deque
import numpy as np
from abc import ABC, abstractmethod


class BaseExercise(ABC):
    """Abstract base class for all exercises"""

    def __init__(self):
        self.name = ""
        self.duration = 60  # seconds
        self.instructions = ""
        self.target_range = (0, 0)  # Hz range
        self.breathing_focus = False
        self.tips = []
        self.purpose = ""  # Training purpose description
        self.benefits = ""  # Expected benefits
        self.metrics_relevant = []  # Which metrics are relevant: 'pitch', 'resonance', 'breathing'

    @abstractmethod
    def get_exercise_data(self):
        """Return exercise configuration dictionary"""
        pass

    def get_training_purpose(self):
        """Get the training purpose of this exercise"""
        return self.purpose

    def get_benefits(self):
        """Get expected benefits of this exercise"""
        return self.benefits

    def get_relevant_metrics(self):
        """Get list of metrics relevant to this exercise"""
        return self.metrics_relevant

    def should_show_pitch(self):
        """Whether pitch display is relevant for this exercise"""
        return 'pitch' in self.metrics_relevant

    def should_show_resonance(self):
        """Whether resonance display is relevant for this exercise"""
        return 'resonance' in self.metrics_relevant

    def should_show_breathing(self):
        """Whether breathing quality is relevant for this exercise"""
        return 'breathing' in self.metrics_relevant


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

        energy = float(np.sqrt(np.mean(np.square(audio_data))))
        current_time = time.time()

        self.breath_pattern.append({
            'energy': energy,
            'timestamp': current_time
        })

        if len(self.breath_pattern) >= 10:
            recent_energies = [b['energy'] for b in self.breath_pattern][-10:]
            energy_variance = np.var(recent_energies)

            # Calculate quality based on consistent, controlled breathing
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

        completion_rates = [s['completion_rate'] for s in exercise_sessions]
        avg_completion = np.mean(completion_rates)

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