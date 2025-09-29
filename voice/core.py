import numpy as np
import pyaudio
import threading
import time
from scipy.signal import find_peaks, butter, filtfilt, welch
import pygame
from collections import deque
from datetime import datetime
from scipy.ndimage import gaussian_filter1d

class VoiceAnalyzer:
    """Core voice analysis and detection functionality"""

    def __init__(self, rate=44100, chunk=4096):
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
        self.noise_samples = deque(maxlen=200)
        self.learning_noise = True
        self.noise_learn_duration = 8.0          
        self.start_time = time.time()
        self.last_noise_feedback_time = 0       
        self.noise_samples_collected = 0        
        self.background_noise_level = 0.0       
        self.is_only_background_noise = False   

        self.pitch_history = deque(maxlen=1000)
        self.formant_history = deque(maxlen=100)
        self.recent_energy = deque(maxlen=10)

        self.current_resonance = {"quality": "Unknown", "frequency": 0, "updated": 0}

    def apply_noise_suppression(self, audio_data):
        """Remove background noise from voice input"""
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

    def update_noise_profile(self, audio_data, callback=None):
        """Update background noise profile with progress feedback"""
        elapsed = time.time() - self.start_time
        current_time = time.time()

        if self.learning_noise and elapsed < self.noise_learn_duration:
            energy = float(np.sqrt(np.mean(audio_data ** 2)))

            if energy < 0.008:  
                self.noise_samples.append(audio_data.copy())
                self.noise_samples_collected += 1
                self.background_noise_level = (self.background_noise_level + energy) / 2

            if current_time - self.last_noise_feedback_time >= 2.0:
                progress = (elapsed / self.noise_learn_duration) * 100
                samples_collected = len(self.noise_samples)
                if callback:
                    callback(f"Learning background noise... {progress:.0f}% ({samples_collected} samples)")
                self.last_noise_feedback_time = current_time

        elif self.learning_noise and elapsed >= self.noise_learn_duration:

            samples_count = len(self.noise_samples)
            if samples_count > 10:  
                self.noise_profile = np.concatenate(list(self.noise_samples))
                if callback:
                    callback(f"Background noise learned! ({samples_count} samples, level: {self.background_noise_level:.4f})")
                    callback("Ready to start voice training - begin speaking!")
            else:
                self.noise_profile = np.zeros(1, dtype=np.float32)
                if callback:
                    callback(f"Limited noise samples ({samples_count}) - using basic noise reduction")
                    callback("Ready to start voice training - begin speaking!")
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
        """Find the fundamental frequency using autocorrelation"""
        cleaned_audio = self.apply_noise_suppression(audio_data)

        optimal_size = min(len(cleaned_audio), self.RATE // 4)  
        if optimal_size < 256:  
            return 0.0

        cleaned_audio = cleaned_audio[:optimal_size]

        pre_emphasis = np.append(cleaned_audio[0], cleaned_audio[1:] - 0.97 * cleaned_audio[:-1])
        windowed = pre_emphasis * np.hamming(len(pre_emphasis))

        correlation = np.correlate(windowed, windowed, mode='full')
        mid_point = len(correlation) // 2
        correlation = correlation[mid_point:]

        if correlation[0] > 0:
            correlation = correlation / correlation[0]

        min_period = max(int(self.RATE / self.MAX_FREQ), 20)
        max_period = min(int(self.RATE / self.MIN_FREQ), len(correlation) - 1)

        if max_period <= min_period:
            return 0.0

        search_range = correlation[min_period:max_period]
        if search_range.size == 0:
            return 0.0

        smoothed = gaussian_filter1d(search_range, sigma=1.5)
        max_val = float(np.max(smoothed))
        peak_height_thresh = max(0.1 * max_val, 0.05)

        peaks, properties = find_peaks(smoothed, 
                                     height=peak_height_thresh, 
                                     distance=max(10, len(smoothed) // 50))

        if len(peaks) == 0:
            return 0.0

        best_peak_idx = int(np.argmax(properties['peak_heights']))
        period = int(peaks[best_peak_idx] + min_period)

        if period <= 0:
            return 0.0

        frequency = float(self.RATE) / float(period)

        if self.MIN_FREQ <= frequency <= self.MAX_FREQ:

            self.pitch_history.append(frequency)

            self.get_realtime_resonance(cleaned_audio)

            return frequency
        else:
            return 0.0

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
        """Fast resonance detection optimized for real-time display (<50ms)"""
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

                if centroid < 900:
                    quality = "Warm"
                elif centroid < 1400:
                    quality = "Balanced"
                elif centroid < 2200:
                    quality = "Bright"
                else:
                    quality = "Very Bright"

                self.current_resonance = {
                    "quality": quality,
                    "frequency": round(centroid),
                    "updated": current_time
                }

        except Exception:

            pass

        return self.current_resonance

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

class AudioManager:
    """Handle audio stream management"""

    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.audio = None
        self.stream = None
        self.running = False
        self.audio_thread = None

    def initialize_audio(self):
        """Initialize PyAudio with helpful error messages"""
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=self.analyzer.FORMAT,
                channels=self.analyzer.CHANNELS,
                rate=self.analyzer.RATE,
                input=True,
                frames_per_buffer=self.analyzer.CHUNK
            )
            return True
        except Exception as e:

            self._cleanup_partial_audio_init()

            error_msg = str(e).lower()
            print(f"Error initializing audio system: {e}")
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

            print("• If problems persist, try restarting your computer")
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

    def start_processing(self, callback):
        """Start audio processing in background thread"""
        if not self.initialize_audio():
            return False

        self.running = True
        self.audio_thread = threading.Thread(target=self._audio_loop, args=(callback,))
        self.audio_thread.daemon = True
        self.audio_thread.start()
        return True

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
        self.running = False

        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

        if self.audio:
            try:
                self.audio.terminate()
            except Exception:
                pass
            self.audio = None

        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1.0)
            if self.audio_thread.is_alive():

                print("Warning: Audio thread did not terminate cleanly")
        self.audio_thread = None

class AlertSystem:
    """Handle audio alerts for low and high pitch"""

    def __init__(self, volume=0.7):
        self.volume = volume
        self.sound_enabled = False
        self.last_low_alert_time = 0
        self.last_high_alert_time = 0
        self.alert_cooldown = 4.0 
        self.high_pitch_threshold = 400  

        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.sound_enabled = True
            self.create_alert_sounds()
        except Exception as e:
            print(f"Warning: Could not initialize audio alerts: {e}")

    def create_alert_sounds(self):
        """Create low and high pitch alert sounds"""
        duration = 0.15
        sample_rate = 22050

        low_freq = 600
        frames = int(duration * sample_rate)
        t = np.arange(frames) / sample_rate
        arr_low = np.sin(2 * np.pi * low_freq * t).astype(np.float32)
        arr_low *= float(self.volume * 0.8)  

        high_freq = 1200
        arr_high = np.sin(2 * np.pi * high_freq * t).astype(np.float32)

        arr_high += 0.3 * np.sin(2 * np.pi * high_freq * 2 * t).astype(np.float32)
        arr_high *= float(self.volume * 0.6)  

        fade_frames = int(0.01 * sample_rate)
        fade = np.linspace(0.0, 1.0, fade_frames, dtype=np.float32)

        for arr in [arr_low, arr_high]:
            arr[:fade_frames] *= fade
            arr[-fade_frames:] *= fade[::-1]

        self.low_alert_array = np.column_stack([(arr_low * 32767).astype(np.int16)] * 2)
        self.high_alert_array = np.column_stack([(arr_high * 32767).astype(np.int16)] * 2)

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

    def cleanup(self):
        """Cleanup pygame mixer"""
        if self.sound_enabled:
            try:
                pygame.mixer.quit()
            except Exception:
                pass