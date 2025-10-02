"""Formant tracking for voice resonance analysis using LPC (Linear Predictive Coding)"""

import numpy as np
from scipy.signal import lfilter
from collections import deque
import time
from utils.error_handler import log_error


class FormantAnalyzer:
    """Analyze formant frequencies for voice resonance quality assessment
    
    Formants are the resonant frequencies of the vocal tract. The first three formants
    (F1, F2, F3) are crucial for voice quality and gender perception:
    - F1 (300-900 Hz): Related to tongue height and jaw openness
    - F2 (900-3000 Hz): Related to tongue position (front/back)
    - F3 (1900-4000 Hz): Related to lip rounding and nasality
    
    Higher F2 and F3 values typically indicate a "brighter" or more feminine voice quality.
    """
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        
        # Caching for performance
        self._last_analysis_time = 0
        self._analysis_interval = 0.1  # Update every 100ms
        self._cached_formants = None
        
        # History for smoothing
        self.formant_history = deque(maxlen=10)  # Store last 10 readings
        
        # Expected formant ranges (Hz) for validation
        self.formant_ranges = {
            'F1': (200, 1000),
            'F2': (600, 3500),
            'F3': (1500, 4500)
        }
    
    def detect_formants(self, audio_data, sample_rate=None):
        """Detect first three formants (F1, F2, F3) using Linear Predictive Coding
        
        Args:
            audio_data: numpy array of audio samples
            sample_rate: override sample rate (optional)
            
        Returns:
            dict with F1, F2, F3 frequencies in Hz, or None if detection fails
        """
        if sample_rate is None:
            sample_rate = self.sample_rate
        
        # Performance optimization: check if enough time has passed
        current_time = time.time()
        if current_time - self._last_analysis_time < self._analysis_interval:
            return self._cached_formants
        
        self._last_analysis_time = current_time
        
        # Validate input
        if len(audio_data) < 512:
            return self._cached_formants
        
        # Pre-emphasis filter to boost higher frequencies
        pre_emphasized = self._apply_pre_emphasis(audio_data)
        
        # Window the signal
        windowed = pre_emphasized * np.hamming(len(pre_emphasized))
        
        # Calculate LPC coefficients
        # Order should be sample_rate/1000 + 2 (rule of thumb)
        # For 44100 Hz, order ≈ 46, but we use lower for performance
        lpc_order = min(16, len(windowed) // 3)
        
        try:
            lpc_coeffs = self._compute_lpc(windowed, lpc_order)
            
            # Find formants from LPC polynomial roots
            formants = self._extract_formants_from_lpc(lpc_coeffs, sample_rate)
            
            if formants:
                # Validate formants are in expected ranges
                validated = self._validate_formants(formants)
                
                if validated:
                    # Smooth with history
                    self.formant_history.append(validated)
                    smoothed = self._smooth_formants()
                    
                    self._cached_formants = smoothed
                    return smoothed
        
        except Exception as e:
            # Log error and return cached value
            log_error(e, "FormantAnalyzer.detect_formants")
        
        return self._cached_formants
    
    def _apply_pre_emphasis(self, audio_data, alpha=0.97):
        """Apply pre-emphasis filter to boost high frequencies
        
        Pre-emphasis compensates for the natural roll-off of high frequencies in voice.
        """
        return np.append(audio_data[0], audio_data[1:] - alpha * audio_data[:-1])
    
    def _compute_lpc(self, signal, order):
        """Compute Linear Predictive Coding coefficients using autocorrelation method
        
        LPC models the vocal tract as an all-pole filter.
        """
        # Compute autocorrelation
        autocorr = np.correlate(signal, signal, mode='full')
        autocorr = autocorr[len(autocorr) // 2:]
        
        # Normalize
        autocorr = autocorr / autocorr[0] if autocorr[0] > 0 else autocorr
        
        # Levinson-Durbin recursion to solve for LPC coefficients
        lpc_coeffs = self._levinson_durbin(autocorr[:order + 1], order)
        
        return lpc_coeffs
    
    def _levinson_durbin(self, r, order):
        """Levinson-Durbin algorithm for solving LPC coefficients
        
        Efficiently solves the Toeplitz system of equations.
        """
        a = np.zeros(order + 1)
        a[0] = 1.0
        
        if len(r) < order + 1:
            return a
        
        error = r[0]
        
        for i in range(1, order + 1):
            # Reflection coefficient
            if error == 0:
                break
                
            lambda_i = -sum(a[j] * r[i - j] for j in range(i)) / error
            
            # Update coefficients
            a_prev = a.copy()
            for j in range(1, i):
                a[j] = a_prev[j] + lambda_i * a_prev[i - j]
            a[i] = lambda_i
            
            # Update error
            error = error * (1.0 - lambda_i ** 2)
        
        return a
    
    def _extract_formants_from_lpc(self, lpc_coeffs, sample_rate):
        """Extract formant frequencies from LPC coefficients
        
        Formants correspond to the resonant frequencies, which are found
        from the complex roots of the LPC polynomial.
        """
        # Find roots of LPC polynomial
        roots = np.roots(lpc_coeffs)
        
        # Keep only roots inside unit circle (stable poles)
        roots = roots[np.abs(roots) < 1.0]
        
        # Convert to frequencies
        # Angle gives us the frequency in radians
        angles = np.angle(roots)
        
        # Convert to Hz
        freqs = angles * (sample_rate / (2 * np.pi))
        
        # Keep only positive frequencies
        freqs = freqs[freqs > 0]
        
        # Sort by frequency
        freqs = np.sort(freqs)
        
        # Extract first 3 formants
        if len(freqs) >= 3:
            return {
                'F1': float(freqs[0]),
                'F2': float(freqs[1]),
                'F3': float(freqs[2])
            }
        
        return None
    
    def _validate_formants(self, formants):
        """Validate formants are in expected physiological ranges
        
        Removes spurious detections outside realistic human voice ranges.
        """
        validated = {}
        
        for formant_name, freq in formants.items():
            if formant_name in self.formant_ranges:
                min_freq, max_freq = self.formant_ranges[formant_name]
                
                if min_freq <= freq <= max_freq:
                    validated[formant_name] = freq
                else:
                    # Out of range - invalidate this detection
                    return None
        
        # Must have all 3 formants
        if len(validated) == 3:
            return validated
        
        return None
    
    def _smooth_formants(self):
        """Smooth formants using exponential moving average"""
        if not self.formant_history:
            return None
        
        # Calculate weighted average (more weight on recent values)
        weights = np.linspace(0.5, 1.0, len(self.formant_history))
        weights = weights / weights.sum()
        
        smoothed = {'F1': 0, 'F2': 0, 'F3': 0}
        
        for i, formants in enumerate(self.formant_history):
            for key in smoothed:
                smoothed[key] += formants[key] * weights[i]
        
        return {k: float(v) for k, v in smoothed.items()}
    
    def formant_to_resonance_quality(self, formants):
        """Interpret formant values to determine voice resonance quality
        
        Args:
            formants: dict with F1, F2, F3 values
            
        Returns:
            dict with quality classification and interpretation
        """
        if not formants or not all(k in formants for k in ['F1', 'F2', 'F3']):
            return {
                'quality': 'Unknown',
                'brightness': 0.5,
                'description': 'Insufficient formant data',
                'F2_F3_avg': 0
            }
        
        F1 = formants['F1']
        F2 = formants['F2']
        F3 = formants['F3']
        
        # Calculate F2/F3 average as indicator of brightness
        # Higher F2 and F3 = brighter, more feminine voice
        F2_F3_avg = (F2 + F3) / 2
        
        # Brightness score (0.0 = very dark, 1.0 = very bright)
        # Typical ranges:
        # - Male voice: F2~1200Hz, F3~2500Hz, avg~1850Hz
        # - Female voice: F2~2200Hz, F3~3300Hz, avg~2750Hz
        # - Androgynous: ~2300Hz
        
        # Normalize to 0-1 scale
        brightness = (F2_F3_avg - 1500) / 2000  # Range: 1500-3500 Hz
        brightness = max(0.0, min(1.0, brightness))
        
        # Classify voice quality
        if F2_F3_avg < 1800:
            quality = "Very Dark"
            description = "Low resonance (chest voice dominant)"
        elif F2_F3_avg < 2100:
            quality = "Dark"
            description = "Warm, lower resonance"
        elif F2_F3_avg < 2500:
            quality = "Balanced"
            description = "Neutral resonance"
        elif F2_F3_avg < 2900:
            quality = "Bright"
            description = "Higher resonance, more forward"
        else:
            quality = "Very Bright"
            description = "Very high resonance (head voice)"
        
        # F1 interpretation (vowel openness)
        if F1 < 400:
            vowel_hint = "closed vowels (ee, oo)"
        elif F1 < 700:
            vowel_hint = "mid vowels (eh, oh)"
        else:
            vowel_hint = "open vowels (ah, aa)"
        
        return {
            'quality': quality,
            'brightness': brightness,
            'description': description,
            'F2_F3_avg': round(F2_F3_avg),
            'vowel_hint': vowel_hint,
            'F1': round(F1),
            'F2': round(F2),
            'F3': round(F3)
        }
    
    def get_formant_shift_trend(self):
        """Analyze formant shift trends over recent history
        
        Returns:
            dict with trend analysis
        """
        if len(self.formant_history) < 3:
            return {'status': 'insufficient_data'}
        
        # Extract F2 values over time
        f2_values = [f['F2'] for f in self.formant_history]
        
        # Calculate trend (positive = brightening, negative = darkening)
        trend_slope = (f2_values[-1] - f2_values[0]) / len(f2_values)
        
        if trend_slope > 50:
            trend = "brightening"
        elif trend_slope < -50:
            trend = "darkening"
        else:
            trend = "stable"
        
        return {
            'status': 'ok',
            'trend': trend,
            'slope': round(trend_slope, 2),
            'current_F2': round(f2_values[-1])
        }
    
    def reset(self):
        """Reset formant history and cache"""
        self.formant_history.clear()
        self._cached_formants = None
        self._last_analysis_time = 0
