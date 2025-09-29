import numpy as np
import librosa
from pathlib import Path
import json
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from scipy.signal import find_peaks
from utils.file_operations import get_logger

class AudioFileAnalyzer:
    """Analyze pitch and Hz characteristics of uploaded audio files"""

    def __init__(self):
        self.supported_formats = ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac']
        self.sample_rate = 22050
        self.hop_length = 512
        self.frame_length = 2048

    def is_supported_file(self, file_path: str) -> bool:
        """Check if file format is supported"""
        return Path(file_path).suffix.lower() in self.supported_formats

    def load_audio_file(self, file_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file and return audio data and sample rate"""
        try:

            audio_data, sr = librosa.load(file_path, sr=self.sample_rate)
            return audio_data, sr
        except Exception as e:
            raise ValueError(f"Could not load audio file: {e}")

    def analyze_fundamental_frequency(self, audio_data: np.ndarray, sr: int) -> Dict:
        """Find pitch characteristics of the audio"""
        try:

            f0_yin = librosa.yin(audio_data, fmin=50, fmax=400, 
                               sr=sr, hop_length=self.hop_length)

            voiced_f0 = f0_yin[f0_yin > 0]

            if len(voiced_f0) == 0:
                return {
                    'mean_pitch': 0.0,
                    'median_pitch': 0.0,
                    'min_pitch': 0.0,
                    'max_pitch': 0.0,
                    'std_pitch': 0.0,
                    'pitch_range': 0.0,
                    'voiced_percentage': 0.0,
                    'pitch_stability': 0.0,
                    'analysis_method': 'yin',
                    'total_frames': len(f0_yin),
                    'voiced_frames': 0
                }

            mean_pitch = float(np.mean(voiced_f0))
            median_pitch = float(np.median(voiced_f0))
            min_pitch = float(np.min(voiced_f0))
            max_pitch = float(np.max(voiced_f0))
            std_pitch = float(np.std(voiced_f0))
            pitch_range = max_pitch - min_pitch
            voiced_percentage = (len(voiced_f0) / len(f0_yin)) * 100

            pitch_stability = 1.0 - min(1.0, std_pitch / mean_pitch) if mean_pitch > 0 else 0.0

            return {
                'mean_pitch': mean_pitch,
                'median_pitch': median_pitch,
                'min_pitch': min_pitch,
                'max_pitch': max_pitch,
                'std_pitch': std_pitch,
                'pitch_range': pitch_range,
                'voiced_percentage': voiced_percentage,
                'pitch_stability': pitch_stability,
                'analysis_method': 'yin',
                'total_frames': len(f0_yin),
                'voiced_frames': len(voiced_f0)
            }

        except Exception as e:
            raise ValueError(f"Could not analyze fundamental frequency: {e}")

    def analyze_spectral_features(self, audio_data: np.ndarray, sr: int) -> Dict:
        """Analyze spectral features relevant to voice feminization"""
        try:

            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sr)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sr)[0]

            stft = librosa.stft(audio_data, hop_length=self.hop_length, n_fft=self.frame_length)
            magnitude = np.abs(stft)

            formant_estimates = self._estimate_formants(magnitude, sr)

            return {
                'spectral_centroid_mean': float(np.mean(spectral_centroid)),
                'spectral_centroid_std': float(np.std(spectral_centroid)),
                'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
                'spectral_bandwidth_mean': float(np.mean(spectral_bandwidth)),
                'formant_f1_estimate': formant_estimates.get('f1', 0.0),
                'formant_f2_estimate': formant_estimates.get('f2', 0.0),
                'f2_f1_ratio': formant_estimates.get('f2_f1_ratio', 0.0)
            }

        except (ValueError, TypeError, AttributeError) as e:

            return {
                'spectral_centroid_mean': 0.0,
                'spectral_centroid_std': 0.0,
                'spectral_rolloff_mean': 0.0,
                'spectral_bandwidth_mean': 0.0,
                'formant_f1_estimate': 0.0,
                'formant_f2_estimate': 0.0,
                'f2_f1_ratio': 0.0
            }

    def _estimate_formants(self, magnitude_spectrum: np.ndarray, sr: int) -> Dict:
        """Simple formant estimation from magnitude spectrum"""
        try:

            avg_magnitude = np.mean(magnitude_spectrum, axis=1)

            freqs = librosa.fft_frequencies(sr=sr, n_fft=self.frame_length)

            formant_range = (freqs >= 200) & (freqs <= 3000)
            formant_freqs = freqs[formant_range]
            formant_magnitudes = avg_magnitude[formant_range]

            if len(formant_magnitudes) == 0:
                return {'f1': 0.0, 'f2': 0.0, 'f2_f1_ratio': 0.0}

            peaks, _ = find_peaks(formant_magnitudes, height=np.max(formant_magnitudes) * 0.3, distance=10)

            if len(peaks) >= 2:

                peak_magnitudes = formant_magnitudes[peaks]
                sorted_indices = np.argsort(peak_magnitudes)[::-1]

                f1_idx = peaks[sorted_indices[0]]
                f2_idx = peaks[sorted_indices[1]]

                f1_freq = float(formant_freqs[f1_idx])
                f2_freq = float(formant_freqs[f2_idx])

                if f1_freq > f2_freq:
                    f1_freq, f2_freq = f2_freq, f1_freq

                f2_f1_ratio = f2_freq / f1_freq if f1_freq > 0 else 0.0

                return {
                    'f1': f1_freq,
                    'f2': f2_freq,
                    'f2_f1_ratio': f2_f1_ratio
                }

            return {'f1': 0.0, 'f2': 0.0, 'f2_f1_ratio': 0.0}

        except (ImportError, ValueError, IndexError) as e:

            return {'f1': 0.0, 'f2': 0.0, 'f2_f1_ratio': 0.0}

    def analyze_voice_quality(self, audio_data: np.ndarray, sr: int) -> Dict:
        """Analyze voice quality metrics"""
        try:

            rms = librosa.feature.rms(y=audio_data)[0]

            zcr = librosa.feature.zero_crossing_rate(audio_data)[0]

            spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sr)

            return {
                'rms_energy_mean': float(np.mean(rms)),
                'rms_energy_std': float(np.std(rms)),
                'zero_crossing_rate_mean': float(np.mean(zcr)),
                'spectral_contrast_mean': float(np.mean(spectral_contrast)),
                'voice_quality_score': self._calculate_voice_quality_score(rms, zcr)
            }

        except (ValueError, TypeError, AttributeError) as e:

            return {
                'rms_energy_mean': 0.0,
                'rms_energy_std': 0.0,
                'zero_crossing_rate_mean': 0.0,
                'spectral_contrast_mean': 0.0,
                'voice_quality_score': 0.0
            }

    def _calculate_voice_quality_score(self, rms: np.ndarray, zcr: np.ndarray) -> float:
        """Calculate a simple voice quality score (0-1)"""
        try:

            rms_consistency = 1.0 - min(1.0, np.std(rms) / (np.mean(rms) + 1e-10))
            zcr_score = min(1.0, np.mean(zcr) / 0.1)  

            return float((rms_consistency + zcr_score) / 2.0)
        except (ValueError, ZeroDivisionError, TypeError):
            return 0.0

    def full_analysis(self, file_path: str) -> Dict:
        """Perform complete pitch and voice analysis of audio file"""
        if not self.is_supported_file(file_path):
            raise ValueError(f"Unsupported file format. Supported: {self.supported_formats}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        try:

            audio_data, sr = self.load_audio_file(file_path)

            file_info = {
                'file_path': file_path,
                'file_name': Path(file_path).name,
                'file_size_mb': round(os.path.getsize(file_path) / (1024 * 1024), 2),
                'duration_seconds': float(len(audio_data) / sr),
                'sample_rate': sr,
                'analysis_timestamp': datetime.now().isoformat()
            }

            pitch_analysis = self.analyze_fundamental_frequency(audio_data, sr)
            spectral_analysis = self.analyze_spectral_features(audio_data, sr)
            quality_analysis = self.analyze_voice_quality(audio_data, sr)

            analysis_results = {
                'file_info': file_info,
                'pitch_analysis': pitch_analysis,
                'spectral_analysis': spectral_analysis,
                'voice_quality': quality_analysis,
                'summary': self._generate_analysis_summary(pitch_analysis, spectral_analysis)
            }

            return analysis_results

        except (FileNotFoundError, OSError) as e:
            raise FileNotFoundError(f"Analysis failed - file issue: {e}")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Analysis failed - data processing error: {e}")
        except Exception as e:
            raise RuntimeError(f"Analysis failed - unexpected error: {e}")

    def _generate_analysis_summary(self, pitch_analysis: Dict, spectral_analysis: Dict) -> Dict:
        """Generate a summary assessment of the voice sample"""
        try:
            mean_pitch = pitch_analysis.get('mean_pitch', 0)
            pitch_stability = pitch_analysis.get('pitch_stability', 0)
            voiced_percentage = pitch_analysis.get('voiced_percentage', 0)
            f2_f1_ratio = spectral_analysis.get('f2_f1_ratio', 0)

            pitch_range_metric = min(1.0, max(0.0, (mean_pitch - 80) / 220)) if mean_pitch > 0 else 0  
            stability_score = pitch_stability
            clarity_score = voiced_percentage / 100
            resonance_metric = min(1.0, max(0.0, (f2_f1_ratio - 1.5) / 2.5)) if f2_f1_ratio > 0 else 0  

            overall_score = (pitch_range_metric + stability_score + clarity_score + resonance_metric) / 4

            if mean_pitch == 0:
                pitch_assessment = "No clear pitch detected"
                goal_suggestion = "Try recording with clearer speech"
            elif mean_pitch < 120:
                pitch_assessment = "Lower pitch range (80-120 Hz)"
                goal_suggestion = f"Current range allows for exploration of {int(mean_pitch + 20)}-{int(mean_pitch + 60)} Hz"
            elif mean_pitch < 165:
                pitch_assessment = "Lower-mid pitch range (120-165 Hz)"
                goal_suggestion = f"Good foundation - explore {int(mean_pitch + 15)}-{int(mean_pitch + 45)} Hz range"
            elif mean_pitch < 200:
                pitch_assessment = "Mid-range pitch (165-200 Hz)"
                goal_suggestion = f"Versatile range - consider exploring {int(mean_pitch - 20)}-{int(mean_pitch + 30)} Hz"
            elif mean_pitch < 250:
                pitch_assessment = "Upper-mid pitch range (200-250 Hz)"
                goal_suggestion = f"Good range! Fine-tune around {int(mean_pitch - 10)}-{int(mean_pitch + 10)} Hz"
            else:
                pitch_assessment = "High pitch range"
                goal_suggestion = f"Consider stabilizing around {int(mean_pitch - 20)}-{int(mean_pitch)} Hz"

            return {
                'overall_score': round(overall_score, 2),
                'pitch_range_score': round(pitch_range_metric, 2),
                'stability_score': round(stability_score, 2),
                'clarity_score': round(clarity_score, 2),
                'resonance_score': round(resonance_metric, 2),
                'pitch_assessment': pitch_assessment,
                'goal_suggestion': goal_suggestion,
                'recommended_target_low': max(50, int(mean_pitch - 10)) if mean_pitch > 0 else 165,
                'recommended_target_high': min(400, int(mean_pitch + 20)) if mean_pitch > 0 else 185
            }

        except (ValueError, KeyError, TypeError) as e:

            return {
                'overall_score': 0.0,
                'pitch_range_score': 0.0,
                'stability_score': 0.0,
                'clarity_score': 0.0,
                'resonance_score': 0.0,
                'pitch_assessment': "Analysis error",
                'goal_suggestion': "Please try with a different audio file",
                'recommended_target_low': 165,
                'recommended_target_high': 185
            }

class PitchGoalManager:
    """Manage pitch goals based on analyzed audio files"""

    def __init__(self, config_file="data/voice_config.json"):
        self.config_file = config_file
        self.analysis_history_file = config_file.replace('.json', '_analysis_history.json')
        self.analysis_history = []
        self.load_analysis_history()

    def load_analysis_history(self):
        """Load previous analysis results"""
        try:
            if os.path.exists(self.analysis_history_file):
                with open(self.analysis_history_file, 'r') as f:
                    self.analysis_history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, PermissionError):
            self.analysis_history = []

    def save_analysis_history(self):
        """Save analysis history to file"""
        try:
            with open(self.analysis_history_file, 'w') as f:
                json.dump(self.analysis_history, f, indent=2)
        except (OSError, PermissionError, json.JSONEncodeError) as e:
            get_logger().warning(f"Could not save analysis history: {e}")

    def add_analysis_result(self, analysis_result: Dict, set_as_goal: bool = False):
        """Add analysis result to history and optionally set as goal"""

        self.analysis_history.append(analysis_result)

        if len(self.analysis_history) > 50:
            self.analysis_history = self.analysis_history[-50:]

        self.save_analysis_history()

        if set_as_goal:
            self.set_goal_from_analysis(analysis_result)

    def set_goal_from_analysis(self, analysis_result: Dict):
        """Set training goal based on analysis result"""
        try:
            summary = analysis_result.get('summary', {})
            pitch_analysis = analysis_result.get('pitch_analysis', {})

            target_low = summary.get('recommended_target_low', 165)
            target_high = summary.get('recommended_target_high', 185)
            current_pitch = pitch_analysis.get('mean_pitch', 0)

            config = {}
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'r') as f:
                        config = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError, PermissionError):
                    pass

            config['current_goal'] = target_low
            config['base_goal'] = target_low
            config['target_range'] = [target_low, target_high]
            config['analysis_based_goal'] = True
            config['source_analysis'] = {
                'file_name': analysis_result.get('file_info', {}).get('file_name', 'unknown'),
                'current_pitch': current_pitch,
                'timestamp': datetime.now().isoformat()
            }

            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)

            return target_low, target_high

        except (OSError, PermissionError, json.JSONEncodeError) as e:
            get_logger().warning(f"Could not set goal from analysis: {e}")
            return None, None

    def get_analysis_history_summary(self) -> Dict:
        """Get summary of analysis history"""
        if not self.analysis_history:
            return {'count': 0, 'message': 'No previous analyses'}

        try:

            pitches = []
            for analysis in self.analysis_history:
                pitch = analysis.get('pitch_analysis', {}).get('mean_pitch', 0)
                if pitch > 0:
                    pitches.append(pitch)

            if not pitches:
                return {'count': len(self.analysis_history), 'message': 'No valid pitch data'}

            return {
                'count': len(self.analysis_history),
                'valid_analyses': len(pitches),
                'pitch_range': {
                    'lowest': round(min(pitches), 1),
                    'highest': round(max(pitches), 1),
                    'average': round(sum(pitches) / len(pitches), 1),
                    'latest': round(pitches[-1], 1) if pitches else 0
                },
                'recent_files': [
                    analysis.get('file_info', {}).get('file_name', 'unknown')
                    for analysis in self.analysis_history[-5:]
                ]
            }

        except (KeyError, ValueError, TypeError) as e:
            return {'count': len(self.analysis_history), 'message': 'Error processing history'}