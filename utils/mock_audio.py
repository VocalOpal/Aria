"""Mock audio device and test tone generation for automated testing"""

import numpy as np
import threading
import time
from typing import Optional, Callable
from collections import deque


def generate_test_tone(frequency: float, duration: float, sample_rate: int = 44100, 
                       amplitude: float = 0.3, noise_level: float = 0.0) -> np.ndarray:
    """Generate a test tone at specified frequency
    
    Args:
        frequency: Frequency in Hz
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        amplitude: Amplitude (0.0 to 1.0)
        noise_level: Background noise level (0.0 to 1.0)
    
    Returns:
        numpy array of audio samples
    """
    num_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    
    # Generate pure sine wave
    signal = amplitude * np.sin(2 * np.pi * frequency * t)
    
    # Add harmonics for more realistic voice
    signal += (amplitude * 0.3) * np.sin(2 * np.pi * frequency * 2 * t)  # 2nd harmonic
    signal += (amplitude * 0.15) * np.sin(2 * np.pi * frequency * 3 * t)  # 3rd harmonic
    
    # Add noise if requested
    if noise_level > 0:
        noise = np.random.normal(0, noise_level, num_samples)
        signal += noise
    
    # Normalize to prevent clipping
    if np.max(np.abs(signal)) > 0:
        signal = signal / np.max(np.abs(signal)) * amplitude
    
    return signal.astype(np.float32)


def generate_chirp(start_freq: float, end_freq: float, duration: float, 
                   sample_rate: int = 44100) -> np.ndarray:
    """Generate a frequency sweep (chirp) from start to end frequency
    
    Args:
        start_freq: Starting frequency in Hz
        end_freq: Ending frequency in Hz
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
    
    Returns:
        numpy array of audio samples
    """
    num_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    
    # Linear frequency sweep
    instantaneous_freq = start_freq + (end_freq - start_freq) * t / duration
    phase = 2 * np.pi * np.cumsum(instantaneous_freq) / sample_rate
    
    signal = 0.3 * np.sin(phase)
    return signal.astype(np.float32)


class VoiceCondition:
    """Predefined voice condition presets for testing"""
    
    CLEAR = {
        'frequency': 165,
        'amplitude': 0.3,
        'noise_level': 0.01,
        'jitter': 0.5,
        'shimmer': 3.0,
        'hnr': 20.0
    }
    
    STRAINED = {
        'frequency': 280,
        'amplitude': 0.4,
        'noise_level': 0.15,
        'jitter': 2.5,
        'shimmer': 10.0,
        'hnr': 10.0
    }
    
    NOISY = {
        'frequency': 165,
        'amplitude': 0.25,
        'noise_level': 0.25,
        'jitter': 1.2,
        'shimmer': 6.0,
        'hnr': 13.0
    }
    
    BREATHY = {
        'frequency': 190,
        'amplitude': 0.2,
        'noise_level': 0.12,
        'jitter': 0.8,
        'shimmer': 5.5,
        'hnr': 14.0
    }


class MockAudioDevice:
    """Mock audio device for automated testing
    
    Simulates real audio input device with controllable conditions
    """
    
    def __init__(self, sample_rate: int = 44100, chunk_size: int = 4096):
        """Initialize mock audio device
        
        Args:
            sample_rate: Sample rate in Hz
            chunk_size: Number of samples per chunk
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.is_streaming = False
        self.stream_thread: Optional[threading.Thread] = None
        self.audio_callback: Optional[Callable] = None
        
        # Current voice parameters
        self.frequency = 165.0
        self.amplitude = 0.3
        self.noise_level = 0.01
        self.condition = 'clear'
        
        # Buffer for generated audio
        self.audio_buffer = deque(maxlen=100)
        
        # Simulation control
        self.variation_enabled = True
        self.pitch_variation = 3.0  # Hz
    
    def set_frequency(self, frequency: float):
        """Set the fundamental frequency
        
        Args:
            frequency: Frequency in Hz
        """
        self.frequency = frequency
    
    def set_condition(self, condition: str):
        """Set voice condition preset
        
        Args:
            condition: One of 'clear', 'strained', 'noisy', 'breathy'
        """
        condition_map = {
            'clear': VoiceCondition.CLEAR,
            'strained': VoiceCondition.STRAINED,
            'noisy': VoiceCondition.NOISY,
            'breathy': VoiceCondition.BREATHY
        }
        
        if condition in condition_map:
            params = condition_map[condition]
            self.frequency = params['frequency']
            self.amplitude = params['amplitude']
            self.noise_level = params['noise_level']
            self.condition = condition
    
    def generate_chunk(self) -> np.ndarray:
        """Generate one chunk of audio data
        
        Returns:
            numpy array of audio samples
        """
        # Add natural pitch variation if enabled
        freq = self.frequency
        if self.variation_enabled:
            freq += np.random.uniform(-self.pitch_variation, self.pitch_variation)
        
        # Generate audio chunk
        duration = self.chunk_size / self.sample_rate
        audio_data = generate_test_tone(
            frequency=freq,
            duration=duration,
            sample_rate=self.sample_rate,
            amplitude=self.amplitude,
            noise_level=self.noise_level
        )
        
        return audio_data
    
    def start_stream(self, callback: Callable[[np.ndarray], None]):
        """Start streaming audio data
        
        Args:
            callback: Function to call with each audio chunk
        """
        self.is_streaming = True
        self.audio_callback = callback
        self.stream_thread = threading.Thread(target=self._stream_loop, daemon=True)
        self.stream_thread.start()
    
    def stop_stream(self):
        """Stop streaming audio data"""
        self.is_streaming = False
        if self.stream_thread:
            self.stream_thread.join(timeout=1.0)
    
    def _stream_loop(self):
        """Internal streaming loop"""
        chunk_duration = self.chunk_size / self.sample_rate
        
        while self.is_streaming:
            # Generate and send audio chunk
            audio_chunk = self.generate_chunk()
            
            if self.audio_callback:
                self.audio_callback(audio_chunk)
            
            # Sleep to simulate real-time
            time.sleep(chunk_duration)
    
    def simulate_voice_change(self, start_freq: float, end_freq: float, duration: float):
        """Simulate gradual voice change over time
        
        Args:
            start_freq: Starting frequency in Hz
            end_freq: Ending frequency in Hz  
            duration: Duration of change in seconds
        """
        steps = int(duration * self.sample_rate / self.chunk_size)
        freq_step = (end_freq - start_freq) / steps
        
        self.frequency = start_freq
        
        for _ in range(steps):
            self.frequency += freq_step
            time.sleep(self.chunk_size / self.sample_rate)
    
    def inject_silence(self, duration: float):
        """Inject silence for specified duration
        
        Args:
            duration: Silence duration in seconds
        """
        old_amplitude = self.amplitude
        self.amplitude = 0.0
        time.sleep(duration)
        self.amplitude = old_amplitude
    
    def inject_noise_burst(self, duration: float, intensity: float = 0.5):
        """Inject burst of noise
        
        Args:
            duration: Noise burst duration in seconds
            intensity: Noise intensity (0.0 to 1.0)
        """
        old_noise = self.noise_level
        self.noise_level = intensity
        time.sleep(duration)
        self.noise_level = old_noise
    
    def get_metrics(self) -> dict:
        """Get current voice quality metrics
        
        Returns:
            Dictionary of current metrics based on condition
        """
        condition_map = {
            'clear': VoiceCondition.CLEAR,
            'strained': VoiceCondition.STRAINED,
            'noisy': VoiceCondition.NOISY,
            'breathy': VoiceCondition.BREATHY
        }
        
        if self.condition in condition_map:
            params = condition_map[self.condition]
            return {
                'jitter': params['jitter'],
                'shimmer': params['shimmer'],
                'hnr': params['hnr']
            }
        
        return {
            'jitter': 0.8,
            'shimmer': 4.0,
            'hnr': 18.0
        }


def create_test_session_audio(frequencies: list, duration_per_freq: float = 1.0,
                              sample_rate: int = 44100) -> np.ndarray:
    """Create audio for entire test session with multiple frequencies
    
    Args:
        frequencies: List of frequencies to generate
        duration_per_freq: Duration for each frequency in seconds
        sample_rate: Sample rate in Hz
    
    Returns:
        Concatenated audio array
    """
    audio_segments = []
    
    for freq in frequencies:
        segment = generate_test_tone(
            frequency=freq,
            duration=duration_per_freq,
            sample_rate=sample_rate
        )
        audio_segments.append(segment)
    
    return np.concatenate(audio_segments)


if __name__ == '__main__':
    # Demo/test the mock audio functionality
    print("Testing mock audio generation...")
    
    # Test tone generation
    tone = generate_test_tone(frequency=165, duration=0.5)
    print(f"Generated {len(tone)} samples of 165 Hz tone")
    
    # Test chirp
    chirp = generate_chirp(start_freq=100, end_freq=250, duration=2.0)
    print(f"Generated {len(chirp)} samples of chirp")
    
    # Test mock device
    device = MockAudioDevice()
    device.set_condition('clear')
    chunk = device.generate_chunk()
    print(f"Generated chunk of {len(chunk)} samples")
    
    print("\nMock audio system ready for testing!")
