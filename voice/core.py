import numpy as np
import pyaudio
import threading
import time
from scipy.signal import find_peaks, butter, filtfilt, welch
import pygame
from collections import deque
from scipy.ndimage import gaussian_filter1d
from .formant_analyzer import FormantAnalyzer
from utils.error_handler import log_error

class VoiceAnalyzer:
    """Core voice analysis and detection functionality"""

    def __init__(self, rate=44100, chunk=4096):
        # Audio buffer configuration optimized for real-time performance
        # RATE (44100 Hz): Standard audio quality, sufficient for voice (human voice < 4kHz fundamental)
        # CHUNK (4096 samples): ~93ms buffer provides balance between:
        #   - Latency: Low enough for real-time UI updates
        #   - Stability: Large enough to avoid audio dropouts
        #   - Pitch detection: Contains 5-15 pitch periods for 85-260 Hz range
        self.RATE = rate
        self.CHUNK = chunk
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1

        self._analysis_skip_counter = 0
        self._analysis_skip_interval = 2
        self._last_heavy_analysis = 0
        self._cached_formant_data = None
        self._cached_resonance = 0.5

        self.MIN_FREQ = 50
        self.MAX_FREQ = 400

        self.noise_profile = None
        self.noise_samples = deque(maxlen=150)
        self.learning_noise = True
        self.noise_learn_duration = 3.0
        self.start_time = time.time()
        self.last_noise_feedback_time = 0
        self.noise_samples_collected = 0
        self.background_noise_level = 0.0
        self.is_only_background_noise = False

        self.pitch_history = deque(maxlen=1000)
        self.formant_history = deque(maxlen=100)
        self.recent_energy = deque(maxlen=10)

        # Speech mode detection (backend only - for context-aware grading)
        self.speech_mode = 'unknown'
        self.speech_mode_confidence = 0.0

        self.current_resonance = {"quality": "Unknown", "frequency": 0, "updated": 0}

        # Reduced pitch smoothing for more immediate response (user feedback)
        self.pitch_smoothing_window = deque(maxlen=4)  # Reduced from 6 to 4 frames (~100ms)
        self.pitch_confidence_threshold = 0.45

        # Per-user resonance baseline tracking
        self.resonance_baseline = {"spectral_centroid": 1500, "f1": 500, "f2": 1500, "samples": 0}
        self.resonance_history_long = deque(maxlen=500)
        
        # Initialize formant analyzer
        self.formant_analyzer = FormantAnalyzer(sample_rate=rate)
        self.current_formants = None
        self.formant_quality = None

    def apply_noise_suppression(self, audio_data):
        """Remove background noise from voice input"""
        try:
            if self.noise_profile is None or len(self.noise_profile) == 0:
                return audio_data

            nyquist = self.RATE * 0.5
            low_cutoff = min(100.0 / nyquist, 0.49)
            try:
                b, a = butter(3, low_cutoff, btype='high')
                filtered = filtfilt(b, a, audio_data, method="gust")
            except (ValueError, RuntimeError) as e:
                filtered = audio_data

            noise_power = float(np.mean(self.noise_profile ** 2))
            current_power = float(np.mean(audio_data ** 2))

            if len(self.recent_energy) > 0:
                avg_recent_energy = np.mean(self.recent_energy)
                adaptive_threshold = max(noise_power * 1.5, avg_recent_energy * 0.3)
            else:
                adaptive_threshold = noise_power * 2.0

            if current_power < max(1e-10, adaptive_threshold):
                filtered *= 0.2

            return filtered
        except Exception as e:
            log_error(e, "VoiceAnalyzer.apply_noise_suppression")
            return audio_data

    def update_noise_profile(self, audio_data, callback=None):
        """Update background noise profile with progress feedback"""
        elapsed = time.time() - self.start_time
        current_time = time.time()

        if self.learning_noise and elapsed < self.noise_learn_duration:
            energy = float(np.sqrt(np.mean(audio_data ** 2)))

            if energy < 0.01:  
                self.noise_samples.append(audio_data.copy())
                self.noise_samples_collected += 1
                self.background_noise_level = (self.background_noise_level + energy) / 2

            if current_time - self.last_noise_feedback_time >= 0.5:
                progress = (elapsed / self.noise_learn_duration) * 100
                remaining = int(self.noise_learn_duration - elapsed)
                if callback:
                    callback(f"🤫 Please stay quiet... Calibrating microphone ({remaining}s)")
                self.last_noise_feedback_time = current_time

        elif self.learning_noise and elapsed >= self.noise_learn_duration:
            samples_count = len(self.noise_samples)
            if samples_count > 5:  
                self.noise_profile = np.concatenate(list(self.noise_samples))
                if callback:
                    callback(f"✓ Calibration complete! You can speak now.")
            else:
                self.noise_profile = np.zeros(1, dtype=np.float32)
                if callback:
                    callback(f"✓ Ready! You can speak now.")
            self.learning_noise = False

    def _calculate_audio_energy(self, audio_data, sensitivity=1.0):
        """Centralized energy calculation to avoid duplication"""
        energy = float(np.sqrt(np.mean(audio_data ** 2)))
        return energy * float(sensitivity)

    def _analyze_speech_characteristics(self, audio_data):
        """Centralized speech analysis to avoid duplication"""
        freqs, psd = welch(audio_data, self.RATE, nperseg=min(1024, len(audio_data)))
        if len(freqs) == 0 or len(psd) == 0:
            return 0.0

        speech_range = (freqs >= 200) & (freqs <= 2000)
        speech_energy = float(np.sum(psd[speech_range]))
        total_energy = float(np.sum(psd)) + 1e-12
        return speech_energy / total_energy

    def check_background_noise_only(self, audio_data, vad_threshold=0.01, sensitivity=1.0):
        """Check if we're only hearing background noise (for timer pausing)"""
        if self.learning_noise or self.noise_profile is None:
            return False

        adjusted_energy = self._calculate_audio_energy(audio_data, sensitivity)
        noise_level_threshold = self.background_noise_level * 3.0

        is_background = adjusted_energy <= max(noise_level_threshold, vad_threshold)
        self.is_only_background_noise = is_background
        return is_background

    def is_voice_active(self, audio_data, vad_threshold=0.01, sensitivity=1.0):
        """Check if there's actual voice in the audio"""
        adjusted_energy = self._calculate_audio_energy(audio_data, sensitivity)
        self.recent_energy.append(adjusted_energy / sensitivity)  

        if adjusted_energy < float(vad_threshold):
            return False

        speech_ratio = self._analyze_speech_characteristics(audio_data)
        return speech_ratio > 0.3 and adjusted_energy > float(vad_threshold)

    def detect_pitch(self, audio_data):
        """Find the fundamental frequency using optimized autocorrelation"""
        cleaned_audio = self.apply_noise_suppression(audio_data)

        # Optimize size for faster processing
        optimal_size = min(len(cleaned_audio), self.RATE // 5)
        if optimal_size < 200:
            return 0.0

        cleaned_audio = cleaned_audio[:optimal_size]

        # Pre-emphasis and windowing
        pre_emphasis = np.append(cleaned_audio[0], cleaned_audio[1:] - 0.97 * cleaned_audio[:-1])
        windowed = pre_emphasis * np.hamming(len(pre_emphasis))

        # Faster autocorrelation using FFT
        fft_data = np.fft.rfft(windowed, n=len(windowed)*2)
        correlation = np.fft.irfft(fft_data * np.conj(fft_data))[:len(windowed)]

        if correlation[0] > 0:
            correlation = correlation / correlation[0]

        min_period = max(int(self.RATE / self.MAX_FREQ), 15)
        max_period = min(int(self.RATE / self.MIN_FREQ), len(correlation) - 1)

        if max_period <= min_period:
            return 0.0

        search_range = correlation[min_period:max_period]
        if search_range.size == 0:
            return 0.0

        # Lighter smoothing for faster response
        smoothed = gaussian_filter1d(search_range, sigma=1.0)
        max_val = float(np.max(smoothed))
        peak_height_thresh = max(0.08 * max_val, 0.04)

        peaks, properties = find_peaks(smoothed,
                                     height=peak_height_thresh,
                                     distance=max(8, len(smoothed) // 60))

        if len(peaks) == 0:
            return 0.0

        best_peak_idx = int(np.argmax(properties['peak_heights']))
        period = int(peaks[best_peak_idx] + min_period)

        if period <= 0:
            return 0.0

        frequency = float(self.RATE) / float(period)

        # Confidence calculation
        peak_height = float(properties['peak_heights'][best_peak_idx])
        confidence = min(1.0, peak_height / max(0.25, max_val))

        # Fast smoothing
        if self.MIN_FREQ <= frequency <= self.MAX_FREQ and confidence >= self.pitch_confidence_threshold:
            self.pitch_smoothing_window.append(frequency)

            if len(self.pitch_smoothing_window) >= 2:
                # Simple exponential moving average for speed
                # Increased alpha from 0.6 to 0.75 for more immediate response (user feedback)
                alpha = 0.75
                smoothed_frequency = alpha * frequency + (1 - alpha) * self.pitch_smoothing_window[-2]
            else:
                smoothed_frequency = frequency

            self.pitch_history.append(smoothed_frequency)
            self.get_realtime_resonance(cleaned_audio)

            # Update formant analysis during pitch detection
            self._update_formants(cleaned_audio)

            # Update speech mode detection (backend only)
            self.detect_speech_mode()

            return smoothed_frequency
        else:
            return 0.0

    def get_pitch_with_confidence(self, audio_data):
        """Get pitch with explicit confidence value

        Returns: tuple (frequency, confidence)
        """
        cleaned_audio = self.apply_noise_suppression(audio_data)

        optimal_size = min(len(cleaned_audio), self.RATE // 4)
        if optimal_size < 256:
            return 0.0, 0.0

        cleaned_audio = cleaned_audio[:optimal_size]
        pre_emphasis = np.append(cleaned_audio[0], cleaned_audio[1:] - 0.97 * cleaned_audio[:-1])
        windowed = pre_emphasis * np.hamming(len(pre_emphasis))

        # Use FFT-based autocorrelation for consistency and speed
        fft_data = np.fft.rfft(windowed, n=len(windowed)*2)
        correlation = np.fft.irfft(fft_data * np.conj(fft_data))[:len(windowed)]

        if correlation[0] > 0:
            correlation = correlation / correlation[0]

        min_period = max(int(self.RATE / self.MAX_FREQ), 20)
        max_period = min(int(self.RATE / self.MIN_FREQ), len(correlation) - 1)

        if max_period <= min_period:
            return 0.0, 0.0

        search_range = correlation[min_period:max_period]
        if search_range.size == 0:
            return 0.0, 0.0

        smoothed = gaussian_filter1d(search_range, sigma=1.5)
        max_val = float(np.max(smoothed))
        peak_height_thresh = max(0.1 * max_val, 0.05)

        peaks, properties = find_peaks(smoothed,
                                     height=peak_height_thresh,
                                     distance=max(10, len(smoothed) // 50))

        if len(peaks) == 0:
            return 0.0, 0.0

        best_peak_idx = int(np.argmax(properties['peak_heights']))
        period = int(peaks[best_peak_idx] + min_period)

        if period <= 0:
            return 0.0, 0.0

        frequency = float(self.RATE) / float(period)
        peak_height = float(properties['peak_heights'][best_peak_idx])
        confidence = min(1.0, peak_height / max(0.3, max_val))

        return frequency, confidence

    def _get_power_spectral_density(self, audio_data, nperseg=1024):
        """Centralized PSD calculation with error handling"""
        try:
            return welch(audio_data, self.RATE, nperseg=min(nperseg, len(audio_data)))
        except Exception:
            return np.array([]), np.array([])

    def analyze_formants(self, audio_data):
        """Analyze formant frequencies with CPU optimization"""

        self._analysis_skip_counter += 1
        if self._analysis_skip_counter < self._analysis_skip_interval:
            return self._cached_formant_data

        self._analysis_skip_counter = 0
        current_time = time.time()

        if current_time - self._last_heavy_analysis < 0.2:  
            return self._cached_formant_data

        self._last_heavy_analysis = current_time

        freqs, psd = self._get_power_spectral_density(audio_data, nperseg=1024)  
        if len(freqs) == 0 or len(psd) == 0:
            return self._cached_formant_data

        try:
            peaks, properties = find_peaks(psd, height=np.max(psd) * 0.1, distance=20)

            if len(peaks) >= 2:
                formant_freqs = freqs[peaks[:3]]

                if len(formant_freqs) >= 2:
                    f1, f2 = formant_freqs[0], formant_freqs[1]
                    f2_f1_ratio = f2 / f1 if f1 > 0 else 0

                    resonance_clarity = min(1.0, (f2_f1_ratio - 2.0) / 2.0) if f2_f1_ratio > 2.0 else 0

                    formant_data = {
                        'f1': f1,
                        'f2': f2,
                        'f2_f1_ratio': f2_f1_ratio,
                        'resonance_clarity': resonance_clarity,
                        'timestamp': time.time()
                    }

                    self.formant_history.append(formant_data)
                    self._cached_formant_data = formant_data
                    return formant_data
        except Exception:
            pass

        return self._cached_formant_data

    def get_realtime_resonance(self, audio_data):
        """Fast resonance detection optimized for real-time display (<50ms) with baseline tracking"""
        current_time = time.time()

        if self._analysis_skip_counter % 3 != 0:
            return self.current_resonance

        try:
            fft = np.fft.rfft(audio_data[:1024])
            freqs = np.fft.rfftfreq(1024, 1/self.RATE)
            magnitude = np.abs(fft)

            speech_mask = (freqs >= 200) & (freqs <= 3000)
            speech_freqs = freqs[speech_mask]
            speech_magnitude = magnitude[speech_mask]

            if len(speech_magnitude) > 10:
                total_energy = np.sum(speech_magnitude) + 1e-12
                centroid = np.sum(speech_freqs * speech_magnitude) / total_energy

                # Update baseline (running average)
                self._update_resonance_baseline(centroid)

                # Calculate deviation from baseline
                baseline_centroid = self.resonance_baseline["spectral_centroid"]
                deviation = centroid - baseline_centroid

                # Classify quality relative to user's baseline
                if deviation < -300:
                    quality = "Very Warm (↓)"
                elif deviation < -100:
                    quality = "Warm (↓)"
                elif deviation < 100:
                    quality = "Balanced"
                elif deviation < 300:
                    quality = "Bright (↑)"
                else:
                    quality = "Very Bright (↑)"

                # Store in history for trend analysis
                self.resonance_history_long.append({
                    "centroid": centroid,
                    "deviation": deviation,
                    "timestamp": current_time
                })

                self.current_resonance = {
                    "quality": quality,
                    "frequency": round(centroid),
                    "baseline": round(baseline_centroid),
                    "deviation": round(deviation),
                    "updated": current_time
                }

        except Exception:
            pass

        return self.current_resonance

    def _update_resonance_baseline(self, centroid):
        """Update per-user resonance baseline with exponential moving average"""
        if self.resonance_baseline["samples"] == 0:
            # First sample - initialize baseline
            self.resonance_baseline["spectral_centroid"] = centroid
            self.resonance_baseline["samples"] = 1
        else:
            # Exponential moving average with slow adaptation (α = 0.01)
            alpha = 0.01
            self.resonance_baseline["spectral_centroid"] = (
                alpha * centroid + (1 - alpha) * self.resonance_baseline["spectral_centroid"]
            )
            self.resonance_baseline["samples"] += 1

    def detect_speech_mode(self):
        """Detect if user is in sustained vowel or conversational mode (backend only)

        Returns: 'sustained', 'conversational', 'unknown'
        """
        if len(self.pitch_history) < 20:
            return 'unknown'

        recent_pitches = list(self.pitch_history)[-40:]
        pitch_range = max(recent_pitches) - min(recent_pitches)
        pitch_std = np.std(recent_pitches)

        # Sustained vowel: very stable pitch (< 15 Hz variation)
        if pitch_range < 15 and pitch_std < 5:
            self.speech_mode = 'sustained'
            self.speech_mode_confidence = 0.9
        # Conversational: more variation
        elif pitch_range > 30 or pitch_std > 10:
            self.speech_mode = 'conversational'
            self.speech_mode_confidence = 0.8
        else:
            self.speech_mode = 'unknown'
            self.speech_mode_confidence = 0.5

        return self.speech_mode

    def _update_formants(self, audio_data):
        """Update formant analysis (called during pitch detection for efficiency)
        
        This method is lightweight and cached, so calling it frequently is safe.
        """
        try:
            # Detect formants (internally cached to avoid excessive computation)
            formants = self.formant_analyzer.detect_formants(audio_data, self.RATE)
            
            if formants:
                self.current_formants = formants
                
                # Get quality interpretation
                self.formant_quality = self.formant_analyzer.formant_to_resonance_quality(formants)
        except Exception as e:
            # Log error - formant analysis is supplementary
            log_error(e, "VoiceAnalyzer._update_formants")
    
    def calculate_breathiness_score(self, audio_data):
        """Calculate breathiness score using spectral noise ratio
        
        Breathiness is characterized by increased noise in the spectrum,
        particularly in higher frequencies. This measures the ratio of
        noise to harmonic content.
        
        Returns:
            float: Breathiness score from 0.0 (clear) to 1.0 (very breathy)
        """
        try:
            if len(audio_data) < 512:
                return 0.0
            
            # Compute power spectral density
            freqs, psd = self._get_power_spectral_density(audio_data, nperseg=1024)
            if len(freqs) == 0 or len(psd) == 0:
                return 0.0
            
            # Define frequency bands
            # Harmonic region (100-1500 Hz) - where voice harmonics are strong
            harmonic_mask = (freqs >= 100) & (freqs <= 1500)
            # High-frequency noise region (3000-8000 Hz) - where breathiness shows
            noise_mask = (freqs >= 3000) & (freqs <= 8000)
            
            harmonic_energy = np.sum(psd[harmonic_mask]) if np.any(harmonic_mask) else 1e-12
            noise_energy = np.sum(psd[noise_mask]) if np.any(noise_mask) else 0.0
            
            # Calculate spectral noise ratio (higher = more breathy)
            noise_ratio = noise_energy / (harmonic_energy + 1e-12)
            
            # Normalize to 0-1 scale (empirically tuned thresholds)
            breathiness_score = min(1.0, noise_ratio / 0.5)
            
            return float(breathiness_score)
            
        except Exception:
            return 0.0
    
    def calculate_nasality_score(self, audio_data):
        """Calculate nasality score using formant bandwidth analysis
        
        Nasality is characterized by:
        - Widened formant bandwidths (especially F1)
        - Additional nasal formants around 250 Hz and 2500 Hz
        - Reduced overall spectral clarity
        
        Returns:
            float: Nasality score from 0.0 (oral) to 1.0 (highly nasal)
        """
        try:
            if len(audio_data) < 1024:
                return 0.0
            
            # Compute power spectral density with higher resolution
            freqs, psd = self._get_power_spectral_density(audio_data, nperseg=2048)
            if len(freqs) == 0 or len(psd) == 0:
                return 0.0
            
            # Detect spectral peaks (formants)
            from scipy.signal import find_peaks
            peaks, properties = find_peaks(psd, height=np.max(psd) * 0.15, distance=30)
            
            if len(peaks) < 2:
                return 0.0
            
            peak_freqs = freqs[peaks]
            peak_heights = properties['peak_heights']
            
            # Look for nasal formant indicators
            nasal_indicators = 0.0
            
            # 1. Check for nasal formant around 250 Hz (nasal murmur)
            nasal_low_mask = (peak_freqs >= 200) & (peak_freqs <= 350)
            if np.any(nasal_low_mask):
                nasal_indicators += 0.3
            
            # 2. Check for nasal formant around 2500 Hz
            nasal_high_mask = (peak_freqs >= 2300) & (peak_freqs <= 2700)
            if np.any(nasal_high_mask):
                nasal_indicators += 0.2
            
            # 3. Measure spectral flatness (broader peaks indicate nasality)
            # Compare energy concentration vs spread
            if len(peaks) >= 2:
                # Get widths of first two formants
                try:
                    from scipy.signal import peak_widths
                    widths = peak_widths(psd, peaks[:3], rel_height=0.5)[0]
                    avg_width = np.mean(widths)
                    
                    # Wider peaks (> 40 bins) suggest more nasality
                    width_factor = min(0.5, avg_width / 80.0)
                    nasal_indicators += width_factor
                except:
                    pass
            
            # Normalize to 0-1
            nasality_score = min(1.0, nasal_indicators)
            
            return float(nasality_score)
            
        except Exception:
            return 0.0
    
    def analyze_chunk(self, audio_data, include_voice_quality=False):
        """Comprehensive analysis of audio chunk
        
        Args:
            audio_data: Audio samples to analyze
            include_voice_quality: Whether to include voice quality metrics (slower)
            
        Returns:
            dict: Analysis results including pitch, formants, and optionally voice quality
        """
        results = {
            'pitch': 0.0,
            'pitch_confidence': 0.0,
            'formants': None,
            'resonance': None,
            'voice_quality_metrics': None
        }
        
        try:
            # Pitch detection with confidence
            pitch, confidence = self.get_pitch_with_confidence(audio_data)
            results['pitch'] = pitch
            results['pitch_confidence'] = confidence
            
            # Get formant data
            formant_data = self.get_formant_data()
            if formant_data:
                results['formants'] = formant_data
            
            # Get resonance info
            resonance = self.get_realtime_resonance(audio_data)
            results['resonance'] = resonance
            
            # Voice quality metrics (optional, more expensive)
            if include_voice_quality:
                breathiness = self.calculate_breathiness_score(audio_data)
                nasality = self.calculate_nasality_score(audio_data)
                
                # Get roughness metrics if pitch is valid
                roughness = None
                if pitch > 0:
                    roughness = self.calculate_roughness_lightweight(audio_data, pitch)
                
                results['voice_quality_metrics'] = {
                    'breathiness': breathiness,
                    'nasality': nasality,
                    'hnr': roughness.get('hnr', 0.0) if roughness else 0.0,
                    'quality': roughness.get('quality', 'unknown') if roughness else 'unknown'
                }
            
            return results
            
        except Exception:
            return results
    
    def get_formant_data(self):
        """Get current formant data for display
        
        Returns:
            dict with F1, F2, F3 values and quality interpretation
        """
        if not self.current_formants:
            return None
        
        return {
            'formants': self.current_formants,
            'quality': self.formant_quality
        }
    
    def get_resonance_shift_analysis(self):
        """Analyze resonance shifts over the session

        Returns: dict with shift statistics
        """
        if len(self.resonance_history_long) < 10:
            return {
                "status": "insufficient_data",
                "message": "Not enough resonance data collected"
            }

        # Extract deviations
        deviations = [r["deviation"] for r in self.resonance_history_long]

        # Calculate statistics
        mean_deviation = float(np.mean(deviations))
        std_deviation = float(np.std(deviations))
        max_deviation = float(np.max(np.abs(deviations)))

        # Determine shift trend
        recent_30 = deviations[-30:] if len(deviations) >= 30 else deviations
        trend = "upward" if np.mean(recent_30) > 50 else "downward" if np.mean(recent_30) < -50 else "stable"

        return {
            "status": "ok",
            "mean_deviation": mean_deviation,
            "std_deviation": std_deviation,
            "max_deviation": max_deviation,
            "trend": trend,
            "consistency": "high" if std_deviation < 100 else "moderate" if std_deviation < 200 else "variable"
        }

    def calculate_resonance_quality(self, audio_data):
        """Calculate resonance quality with CPU optimization"""

        if self._analysis_skip_counter % 3 != 0:
            return self._cached_resonance

        freqs, psd = self._get_power_spectral_density(audio_data, nperseg=512)
        if len(freqs) == 0 or len(psd) == 0:
            return self._cached_resonance

        try:
            total_energy = np.sum(psd) + 1e-12
            spectral_centroid = np.sum(freqs * psd) / total_energy

            speech_range = (freqs >= 300) & (freqs <= 3000)
            speech_energy = np.sum(psd[speech_range]) if np.any(speech_range) else 0

            resonance_score = min(1.0, (spectral_centroid / 1500) * (speech_energy / total_energy) * 2)
            self._cached_resonance = resonance_score
            return resonance_score
        except Exception:
            return self._cached_resonance

    def calculate_vocal_roughness(self, audio_data, pitch):
        """Calculate vocal roughness metrics: jitter, shimmer, and HNR

        These metrics indicate vocal strain and voice quality issues:
        - Jitter: pitch period variation (normal < 1%, strain > 2%)
        - Shimmer: amplitude variation (normal < 5%, strain > 10%)
        - HNR: Harmonics-to-Noise Ratio in dB (good > 18dB, poor < 12dB)

        Returns: dict with jitter, shimmer, hnr, and strain_detected
        """
        try:
            if pitch <= 0 or len(audio_data) < 1024:
                return {"jitter": 0.0, "shimmer": 0.0, "hnr": 0.0, "strain_detected": False}

            # Calculate expected period from pitch
            expected_period = int(self.RATE / pitch)
            if expected_period < 20 or expected_period > len(audio_data) // 4:
                return {"jitter": 0.0, "shimmer": 0.0, "hnr": 0.0, "strain_detected": False}

            # === JITTER CALCULATION ===
            # Use adaptive threshold based on signal RMS and noise floor
            signal_rms = float(np.sqrt(np.mean(audio_data ** 2)))

            # Adaptive threshold: higher for cleaner signals, with noise floor baseline
            # Typical speech RMS: 0.01-0.1 (normalized float32)
            if signal_rms > 0.05:  # Strong signal
                peak_threshold = signal_rms * 0.65
            elif signal_rms > 0.02:  # Moderate signal
                peak_threshold = signal_rms * 0.55
            else:  # Weak signal - be more selective
                peak_threshold = max(signal_rms * 0.5, 0.015)

            # Prominence requirement to reject noise bumps
            prominence_threshold = peak_threshold * 0.7

            # Find peaks with strict distance constraint
            peaks, properties = find_peaks(
                audio_data,
                distance=int(expected_period * 0.85),  # Must be ~1 period apart
                height=peak_threshold,
                prominence=prominence_threshold
            )

            # Calculate jitter from period variation
            if len(peaks) >= 5:
                periods = np.diff(peaks)

                # Filter outliers: reject periods > ±30% of expected
                valid_mask = np.abs(periods - expected_period) < (expected_period * 0.3)
                valid_periods = periods[valid_mask]

                if len(valid_periods) >= 3:
                    mean_period = np.mean(valid_periods)
                    std_period = np.std(valid_periods)
                    jitter_percent = (std_period / mean_period * 100) if mean_period > 0 else 0.0
                    # Clamp to physiological maximum
                    jitter_percent = min(jitter_percent, 8.0)
                else:
                    jitter_percent = 0.0
            else:
                jitter_percent = 0.0

            # === SHIMMER CALCULATION ===
            if len(peaks) >= 5:
                peak_amplitudes = np.abs(audio_data[peaks])
                median_amp = np.median(peak_amplitudes)

                # Tight outlier rejection: ±60% of median
                valid_mask = np.abs(peak_amplitudes - median_amp) < (median_amp * 0.6)
                valid_amps = peak_amplitudes[valid_mask]

                if len(valid_amps) >= 3:
                    mean_amp = np.mean(valid_amps)
                    std_amp = np.std(valid_amps)
                    shimmer_percent = (std_amp / mean_amp * 100) if mean_amp > 0 else 0.0
                    # Clamp to physiological maximum
                    shimmer_percent = min(shimmer_percent, 15.0)
                else:
                    shimmer_percent = 0.0
            else:
                shimmer_percent = 0.0

            # === HNR CALCULATION (CORRECTED) ===
            # Use sufficient window for stable autocorrelation
            window_size = min(len(audio_data), max(2048, expected_period * 6))
            audio_segment = audio_data[:window_size]

            # Apply Hamming window
            windowed = audio_segment * np.hamming(len(audio_segment))

            # Compute autocorrelation (DO NOT NORMALIZE for HNR)
            autocorr = np.correlate(windowed, windowed, mode='full')
            mid_point = len(autocorr) // 2
            autocorr = autocorr[mid_point:]  # Take positive lags only

            # Extract power values
            r0 = float(autocorr[0])  # Total signal power

            # Find harmonic power at fundamental period (with tolerance)
            if expected_period < len(autocorr):
                # Check small range around expected period for peak
                search_start = max(1, expected_period - 3)
                search_end = min(len(autocorr), expected_period + 4)
                rT = float(np.max(autocorr[search_start:search_end]))
            else:
                rT = 0.0

            # Calculate HNR using clinical formula
            if r0 > 0 and rT > 0:
                noise_power = r0 - rT

                # Prevent division by zero and negative noise
                if noise_power > r0 * 0.001:  # Noise must be at least 0.1% of signal
                    hnr_db = 10.0 * np.log10(rT / noise_power)
                    # Clamp to realistic human range
                    # Theoretical max ~40 dB (pure tone), typical speech 15-25 dB
                    hnr_db = max(-5.0, min(35.0, hnr_db))
                else:
                    # Nearly perfect periodicity (e.g., synthetic tone)
                    hnr_db = 35.0
            else:
                hnr_db = 0.0

            # === STRAIN DETECTION ===
            # Use realistic thresholds for live conditions (not lab conditions)
            jitter_strain = jitter_percent > 1.5  # Clinical: > 1.0%, practical: > 1.5%
            shimmer_strain = shimmer_percent > 7.0  # Clinical: > 5%, practical: > 7%
            hnr_strain = hnr_db < 12.0  # Clinical: < 15 dB, practical: < 12 dB

            strain_detected = jitter_strain or shimmer_strain or hnr_strain

            return {
                "jitter": float(jitter_percent),
                "shimmer": float(shimmer_percent),
                "hnr": float(hnr_db),
                "strain_detected": strain_detected,
                "jitter_strain": jitter_strain,
                "shimmer_strain": shimmer_strain,
                "hnr_strain": hnr_strain
            }

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "VoiceAnalyzer.calculate_vocal_roughness")
            return {"jitter": 0.0, "shimmer": 0.0, "hnr": 0.0, "strain_detected": False}

    def calculate_roughness_lightweight(self, audio_data, pitch):
        """Lightweight vocal roughness check for real-time monitoring

        Only calculates HNR for speed (<10ms processing time)
        """
        try:
            if pitch <= 0 or len(audio_data) < 512:
                return {"hnr": 0.0, "quality": "unknown"}

            expected_period = int(self.RATE / pitch)
            if expected_period < 20 or expected_period > len(audio_data) // 2:
                return {"hnr": 0.0, "quality": "unknown"}

            # Use smaller window for speed (1024 samples ≈ 23ms at 44.1kHz)
            window_size = min(1024, len(audio_data))
            audio_segment = audio_data[:window_size]

            # Quick HNR calculation
            windowed = audio_segment * np.hamming(window_size)

            # Autocorrelation via FFT (faster than np.correlate)
            fft_data = np.fft.rfft(windowed, n=window_size*2)
            autocorr = np.fft.irfft(fft_data * np.conj(fft_data))[:window_size]

            # DO NOT NORMALIZE - we need absolute power values
            r0 = float(autocorr[0])

            # Get harmonic power at expected period
            if expected_period < len(autocorr):
                # Small search window for speed
                search_start = max(1, expected_period - 2)
                search_end = min(len(autocorr), expected_period + 3)
                rT = float(np.max(autocorr[search_start:search_end]))
            else:
                rT = 0.0

            # Calculate HNR
            if r0 > 0 and rT > 0:
                noise_power = r0 - rT

                if noise_power > r0 * 0.001:
                    hnr_db = 10.0 * np.log10(rT / noise_power)
                    hnr_db = max(-5.0, min(35.0, hnr_db))
                else:
                    hnr_db = 35.0
            else:
                hnr_db = 0.0

            # Classify quality with realistic thresholds for live conditions
            if hnr_db > 18:
                quality = "excellent"
            elif hnr_db > 14:
                quality = "good"
            elif hnr_db > 10:
                quality = "fair"
            elif hnr_db > 0:
                quality = "poor"
            else:
                quality = "unknown"

            return {"hnr": float(hnr_db), "quality": quality}

        except Exception as e:
            from utils.error_handler import log_error
            log_error(e, "VoiceAnalyzer.calculate_roughness_lightweight")
            return {"hnr": 0.0, "quality": "unknown"}

class AudioManager:
    """Handle audio stream management"""

    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.audio = None
        self.stream = None
        self.running = False
        self.audio_thread = None
        self.mock_mode = False
        self.error_message = None
        self.noise_floor_spectrum = None
        self.is_noise_calibrated = False

    def initialize_audio(self):
        """Initialize PyAudio with helpful error messages and graceful fallback"""
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=self.analyzer.FORMAT,
                channels=self.analyzer.CHANNELS,
                rate=self.analyzer.RATE,
                input=True,
                frames_per_buffer=self.analyzer.CHUNK
            )
            self.mock_mode = False
            self.error_message = None
            return True
        except Exception as e:

            self._cleanup_partial_audio_init()

            error_msg = str(e).lower()
            print(f"\n⚠️  Audio device initialization failed: {e}")
            print("\n--- Troubleshooting Tips ---")

            if "permission" in error_msg or "access" in error_msg:
                print("• Check microphone permissions in your system settings")
                print("• Close other applications that might be using the microphone")
                print("• Try running as administrator if on Windows")
            elif "device" in error_msg or "invalid" in error_msg:
                print("• Make sure your microphone is connected and recognized")
                print("• Try selecting a different audio input device in system settings")
                print("• Check if your microphone drivers are up to date")
            elif "format" in error_msg or "rate" in error_msg:
                print("• Your audio device may not support the required audio format")
                print("• Try using a different microphone or audio interface")
            else:
                print("• Make sure you have a working microphone connected")
                print("• Check your audio system settings")
                print("• Restart the application and try again")

            print("\n🔄 Running in MOCK MODE - Audio features disabled")
            print("   You can still view and configure settings")
            print("   Fix audio issues and restart to enable voice training\n")
            
            self.mock_mode = True
            self.error_message = f"Audio device unavailable: {str(e)}"
            return False

    def _cleanup_partial_audio_init(self):
        """Clean up partial audio initialization"""
        if hasattr(self, 'stream') and self.stream:
            try:
                self.stream.close()
            except:
                pass
            self.stream = None
        if hasattr(self, 'audio') and self.audio:
            try:
                self.audio.terminate()
            except:
                pass
            self.audio = None
    
    def calibrate_noise_profile(self, callback=None):
        """Capture background noise profile for adaptive noise gating
        
        Captures 2 seconds of silence to establish noise floor spectrum.
        This is used for more effective noise reduction during training.
        
        Args:
            callback: Optional callback for progress updates
            
        Returns:
            bool: True if calibration successful, False otherwise
        """
        if not self.stream:
            if callback:
                callback("Error: Audio stream not initialized")
            return False
        
        try:
            sample_duration = 2.0  # 2 second capture
            num_chunks = int(sample_duration * self.analyzer.RATE / self.analyzer.CHUNK)
            noise_samples = []
            
            if callback:
                callback("Capturing noise profile... Stay silent for 2 seconds")
            
            for i in range(num_chunks):
                try:
                    data = self.stream.read(self.analyzer.CHUNK, exception_on_overflow=False)
                except TypeError:
                    data = self.stream.read(self.analyzer.CHUNK)
                
                audio_data = np.frombuffer(data, dtype=np.float32)
                noise_samples.append(audio_data)
                
                # Progress feedback
                if callback and i % 5 == 0:
                    progress = int((i / num_chunks) * 100)
                    callback(f"Calibrating... {progress}%")
            
            # Combine all samples
            combined_noise = np.concatenate(noise_samples)
            
            # Calculate noise floor spectrum
            from scipy.signal import welch
            freqs, psd = welch(combined_noise, self.analyzer.RATE, nperseg=2048)
            
            # Store the noise floor spectrum
            self.noise_floor_spectrum = {
                'frequencies': freqs,
                'power': psd,
                'mean_power': np.mean(psd),
                'peak_power': np.max(psd),
                'timestamp': time.time()
            }
            
            # Also update analyzer's noise profile for compatibility
            self.analyzer.noise_profile = combined_noise
            self.is_noise_calibrated = True
            
            if callback:
                callback("✓ Noise calibration complete!")
            
            return True
            
        except Exception as e:
            if callback:
                callback(f"Calibration failed: {str(e)}")
            return False
    
    def get_adaptive_noise_gate_threshold(self, audio_data):
        """Calculate adaptive noise gate threshold based on noise profile
        
        Args:
            audio_data: Current audio chunk to analyze
            
        Returns:
            float: Adaptive threshold for noise gating
        """
        if not self.is_noise_calibrated or self.noise_floor_spectrum is None:
            # Fallback to default threshold
            return 0.01
        
        try:
            # Calculate current audio energy
            current_energy = float(np.sqrt(np.mean(audio_data ** 2)))
            
            # Use noise floor mean as base threshold
            noise_floor = self.noise_floor_spectrum['mean_power']
            
            # Set threshold at 2x noise floor (adaptive)
            adaptive_threshold = noise_floor * 2.0
            
            return max(adaptive_threshold, 0.005)  # Minimum threshold
            
        except Exception:
            return 0.01

    def start_processing(self, callback):
        """Start audio processing in background thread"""
        try:
            if not self.initialize_audio():
                return False

            self.running = True
            self.audio_thread = threading.Thread(target=self._audio_loop, args=(callback,))
            self.audio_thread.daemon = True
            self.audio_thread.start()
            return True
        except Exception as e:
            log_error(e, "AudioManager.start_processing")
            return False

    def _audio_loop(self, callback):
        """Audio processing loop"""
        while self.running:
            try:
                try:
                    data = self.stream.read(self.analyzer.CHUNK, exception_on_overflow=False)
                except TypeError:

                    data = self.stream.read(self.analyzer.CHUNK)

                if not data:
                    continue

                audio_data = np.frombuffer(data, dtype=np.float32)
                callback(audio_data)

            except Exception as e:
                if self.running:
                    print(f"Audio processing error: {e}")
                time.sleep(0.05)

    def stop_processing(self):
        """Stop audio processing and cleanup"""
        try:
            self.running = False

            if self.stream:
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                except Exception as e:
                    log_error(e, "AudioManager.stop_processing - closing stream")
                self.stream = None

            if self.audio:
                try:
                    self.audio.terminate()
                except Exception as e:
                    log_error(e, "AudioManager.stop_processing - terminating audio")
                self.audio = None

            if self.audio_thread and self.audio_thread.is_alive():
                self.audio_thread.join(timeout=1.0)
                if self.audio_thread.is_alive():
                    print("Warning: Audio thread did not terminate cleanly")
            self.audio_thread = None
        except Exception as e:
            log_error(e, "AudioManager.stop_processing")

class AlertSystem:
    """Handle audio alerts for pitch, safety, progress, and session events"""

    def __init__(self, volume=0.7):
        self.volume = volume
        self.sound_enabled = False
        self.last_low_alert_time = 0
        self.last_high_alert_time = 0
        self.last_safety_alert_time = 0
        self.last_progress_alert_time = 0
        self.alert_cooldown = 4.0
        self.safety_alert_cooldown = 10.0
        self.progress_alert_cooldown = 5.0
        self.high_pitch_threshold = 400

        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.sound_enabled = True
            self.create_alert_sounds()
        except Exception as e:
            print(f"Warning: Could not initialize audio alerts: {e}")

    def create_alert_sounds(self):
        """Create various alert sounds for different events"""
        duration = 0.15
        sample_rate = 22050
        frames = int(duration * sample_rate)
        t = np.arange(frames) / sample_rate

        fade_frames = int(0.01 * sample_rate)
        fade = np.linspace(0.0, 1.0, fade_frames, dtype=np.float32)

        # 1. LOW PITCH ALERT (pitch too low) - 600 Hz
        low_freq = 600
        arr_low = np.sin(2 * np.pi * low_freq * t).astype(np.float32)
        arr_low *= float(self.volume * 0.8)
        arr_low[:fade_frames] *= fade
        arr_low[-fade_frames:] *= fade[::-1]
        self.low_alert_array = np.column_stack([(arr_low * 32767).astype(np.int16)] * 2)

        # 2. HIGH PITCH ALERT (pitch too high / strain) - 1200 Hz with harmonic
        high_freq = 1200
        arr_high = np.sin(2 * np.pi * high_freq * t).astype(np.float32)
        arr_high += 0.3 * np.sin(2 * np.pi * high_freq * 2 * t).astype(np.float32)
        arr_high *= float(self.volume * 0.6)
        arr_high[:fade_frames] *= fade
        arr_high[-fade_frames:] *= fade[::-1]
        self.high_alert_array = np.column_stack([(arr_high * 32767).astype(np.int16)] * 2)

        # 3. PROGRESS/SUCCESS ALERT (goal achieved) - ascending tone 800→1000 Hz
        progress_freq_start = 800
        progress_freq_end = 1000
        freq_sweep = np.linspace(progress_freq_start, progress_freq_end, frames)
        phase = np.cumsum(2 * np.pi * freq_sweep / sample_rate)
        arr_progress = np.sin(phase).astype(np.float32)
        arr_progress *= float(self.volume * 0.7)
        arr_progress[:fade_frames] *= fade
        arr_progress[-fade_frames:] *= fade[::-1]
        self.progress_alert_array = np.column_stack([(arr_progress * 32767).astype(np.int16)] * 2)

        # 4. SAFETY WARNING (strain/roughness) - pulsing 700 Hz
        safety_freq = 700
        pulse_freq = 8  # 8 Hz pulsing
        arr_safety = np.sin(2 * np.pi * safety_freq * t).astype(np.float32)
        pulse_envelope = 0.5 + 0.5 * np.sin(2 * np.pi * pulse_freq * t)
        arr_safety *= pulse_envelope.astype(np.float32)
        arr_safety *= float(self.volume * 0.75)
        arr_safety[:fade_frames] *= fade
        arr_safety[-fade_frames:] *= fade[::-1]
        self.safety_alert_array = np.column_stack([(arr_safety * 32767).astype(np.int16)] * 2)

        # 5. SESSION START/END - gentle chime 880 Hz (A note)
        session_freq = 880
        arr_session = np.sin(2 * np.pi * session_freq * t).astype(np.float32)
        # Natural decay envelope
        decay = np.exp(-3 * t / duration).astype(np.float32)
        arr_session *= decay * float(self.volume * 0.6)
        arr_session[:fade_frames] *= fade
        self.session_alert_array = np.column_stack([(arr_session * 32767).astype(np.int16)] * 2)

        # 6. MILESTONE ALERT (major achievement) - double beep 1000 Hz
        milestone_frames = int(0.08 * sample_rate)
        gap_frames = int(0.05 * sample_rate)
        t_milestone = np.arange(milestone_frames) / sample_rate
        beep1 = np.sin(2 * np.pi * 1000 * t_milestone).astype(np.float32)
        beep2 = beep1.copy()
        fade_m = np.linspace(0.0, 1.0, int(0.01 * sample_rate), dtype=np.float32)
        beep1[:len(fade_m)] *= fade_m
        beep1[-len(fade_m):] *= fade_m[::-1]
        beep2[:len(fade_m)] *= fade_m
        beep2[-len(fade_m):] *= fade_m[::-1]
        gap = np.zeros(gap_frames, dtype=np.float32)
        arr_milestone = np.concatenate([beep1, gap, beep2]) * float(self.volume * 0.7)
        self.milestone_alert_array = np.column_stack([(arr_milestone * 32767).astype(np.int16)] * 2)

    def play_low_alert(self):
        """Play low pitch alert (pitch too low)"""
        if not self.sound_enabled:
            return

        current_time = time.time()
        if current_time - self.last_low_alert_time < self.alert_cooldown:
            return

        self.last_low_alert_time = current_time

        try:
            if hasattr(self, 'low_alert_array'):
                sound = pygame.sndarray.make_sound(self.low_alert_array)
                sound.set_volume(self.volume)
                sound.play()
        except Exception as e:
            print(f"Error playing low alert: {e}")

    def play_high_alert(self):
        """Play high pitch alert (pitch too high - head voice awareness)"""
        if not self.sound_enabled:
            return

        current_time = time.time()
        if current_time - self.last_high_alert_time < self.alert_cooldown:
            return

        self.last_high_alert_time = current_time

        try:
            if hasattr(self, 'high_alert_array'):
                sound = pygame.sndarray.make_sound(self.high_alert_array)
                sound.set_volume(self.volume * 0.7)
                sound.play()
        except Exception as e:
            print(f"Error playing high alert: {e}")

    def play_progress_alert(self):
        """Play progress/success alert (goal achieved, milestone hit)"""
        if not self.sound_enabled:
            return

        current_time = time.time()
        if current_time - self.last_progress_alert_time < self.progress_alert_cooldown:
            return

        self.last_progress_alert_time = current_time

        try:
            if hasattr(self, 'progress_alert_array'):
                sound = pygame.sndarray.make_sound(self.progress_alert_array)
                sound.set_volume(self.volume * 0.8)
                sound.play()
        except Exception as e:
            print(f"Error playing progress alert: {e}")

    def play_safety_alert(self, severity='light'):
        """Play safety warning alert (strain, roughness detected)

        Args:
            severity: 'light', 'strong', or 'critical'
        """
        if not self.sound_enabled:
            return

        current_time = time.time()
        if current_time - self.last_safety_alert_time < self.safety_alert_cooldown:
            return

        self.last_safety_alert_time = current_time

        try:
            if hasattr(self, 'safety_alert_array'):
                sound = pygame.sndarray.make_sound(self.safety_alert_array)

                # Adjust volume based on severity
                if severity == 'critical':
                    sound.set_volume(self.volume * 0.9)
                elif severity == 'strong':
                    sound.set_volume(self.volume * 0.75)
                else:  # light
                    sound.set_volume(self.volume * 0.6)

                sound.play()
        except Exception as e:
            print(f"Error playing safety alert: {e}")

    def play_session_alert(self, event_type='start'):
        """Play session start/end alert

        Args:
            event_type: 'start' or 'end'
        """
        if not self.sound_enabled:
            return

        try:
            if hasattr(self, 'session_alert_array'):
                sound = pygame.sndarray.make_sound(self.session_alert_array)
                sound.set_volume(self.volume * 0.7)
                sound.play()
        except Exception as e:
            print(f"Error playing session alert: {e}")

    def play_milestone_alert(self):
        """Play milestone achievement alert (major accomplishment)"""
        if not self.sound_enabled:
            return

        try:
            if hasattr(self, 'milestone_alert_array'):
                sound = pygame.sndarray.make_sound(self.milestone_alert_array)
                sound.set_volume(self.volume * 0.85)
                sound.play()
        except Exception as e:
            print(f"Error playing milestone alert: {e}")

    def set_volume(self, volume):
        """Set alert volume (0.0-1.0)"""
        self.volume = max(0.0, min(1.0, volume))

    def enable_sounds(self, enabled=True):
        """Enable or disable all alert sounds"""
        self.sound_enabled = enabled and pygame.mixer.get_init() is not None

    def cleanup(self):
        """Cleanup pygame mixer"""
        if self.sound_enabled:
            try:
                pygame.mixer.quit()
            except Exception:
                pass