"""Real-time spectrogram visualization widget with formant highlighting."""

import numpy as np
from collections import deque
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.signal import spectrogram
from utils.error_handler import log_error

from ..design_system import AriaColors, AriaTypography, AriaSpacing, AriaRadius


class SpectrogramWidget(QWidget):
    """Real-time spectrogram visualization with formant peak highlighting"""
    
    def __init__(self, sample_rate=44100, window_duration=3.0):
        super().__init__()
        self.sample_rate = sample_rate
        self.window_duration = window_duration
        
        # Rolling audio buffer (stores last 3 seconds)
        buffer_size = int(sample_rate * window_duration)
        self.audio_buffer = deque(maxlen=buffer_size)
        
        # Formant data cache
        self.current_formants = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the spectrogram UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(AriaSpacing.SM)
        
        # Title
        title = QLabel("Real-time Spectrogram")
        title.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: {AriaTypography.SUBHEADING}px;
                font-weight: 600;
                background: transparent;
                padding: {AriaSpacing.SM}px;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(8, 4), facecolor='#1a1a2e')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet(f"background: transparent; border-radius: {AriaRadius.LG}px;")
        
        # Create axis
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#0f0f1e')
        self.ax.set_xlabel('Time (s)', color='white', fontsize=10)
        self.ax.set_ylabel('Frequency (Hz)', color='white', fontsize=10)
        self.ax.tick_params(colors='white', labelsize=9)
        self.ax.grid(True, alpha=0.2, color='white', linestyle='--', linewidth=0.5)
        
        # Tight layout
        self.figure.tight_layout(pad=1.5)
        
        layout.addWidget(self.canvas)
        
        # Initialize empty spectrogram
        self.spectrogram_image = None
        self.formant_markers = []
    
    def update_audio(self, audio_chunk):
        """Update with new audio chunk
        
        Args:
            audio_chunk: Numpy array of audio samples
        """
        # Add to rolling buffer
        self.audio_buffer.extend(audio_chunk)
    
    def update_formants(self, formants):
        """Update formant data for highlighting
        
        Args:
            formants: List of formant frequencies [F1, F2, F3, ...]
        """
        self.current_formants = formants
    
    def refresh_display(self):
        """Refresh the spectrogram display"""
        if len(self.audio_buffer) < 1024:
            return
        
        # Convert buffer to numpy array
        audio_data = np.array(self.audio_buffer)
        
        # Compute spectrogram
        try:
            # Parameters for spectrogram
            nperseg = 512  # Window size
            noverlap = nperseg - 64  # Overlap for smooth display
            
            freqs, times, Sxx = spectrogram(
                audio_data,
                fs=self.sample_rate,
                nperseg=nperseg,
                noverlap=noverlap,
                window='hann'
            )
            
            # Limit frequency range to voice range (0-4000 Hz)
            freq_mask = freqs <= 4000
            freqs = freqs[freq_mask]
            Sxx = Sxx[freq_mask, :]
            
            # Convert to dB scale
            Sxx_db = 10 * np.log10(Sxx + 1e-10)
            
            # Clear previous plot
            self.ax.clear()
            
            # Plot spectrogram
            self.spectrogram_image = self.ax.pcolormesh(
                times,
                freqs,
                Sxx_db,
                shading='gouraud',
                cmap='plasma',  # Beautiful gradient colormap
                vmin=np.percentile(Sxx_db, 5),
                vmax=np.percentile(Sxx_db, 95)
            )
            
            # Highlight formant peaks
            if self.current_formants:
                self._highlight_formants(times)
            
            # Styling
            self.ax.set_facecolor('#0f0f1e')
            self.ax.set_xlabel('Time (s)', color='white', fontsize=10)
            self.ax.set_ylabel('Frequency (Hz)', color='white', fontsize=10)
            self.ax.set_xlim([0, self.window_duration])
            self.ax.set_ylim([0, 4000])
            self.ax.tick_params(colors='white', labelsize=9)
            self.ax.grid(True, alpha=0.2, color='white', linestyle='--', linewidth=0.5)
            
            # Refresh canvas
            self.canvas.draw_idle()
            
        except Exception as e:
            # Log error - spectrogram is supplementary
            log_error(e, "SpectrogramWidget.refresh_display")
    
    def _highlight_formants(self, times):
        """Highlight formant frequencies on the spectrogram
        
        Args:
            times: Time array from spectrogram
        """
        if not self.current_formants:
            return
        
        # Draw horizontal lines for each formant
        colors = ['#00ffff', '#ff00ff', '#ffff00']  # Cyan, Magenta, Yellow
        labels = ['F1', 'F2', 'F3']
        
        for i, (formant, color, label) in enumerate(zip(self.current_formants[:3], colors, labels)):
            if formant > 0:
                # Draw horizontal line at formant frequency
                self.ax.axhline(
                    y=formant,
                    color=color,
                    linestyle='--',
                    linewidth=2,
                    alpha=0.7,
                    label=f'{label}: {int(formant)} Hz'
                )
        
        # Add legend
        self.ax.legend(
            loc='upper right',
            facecolor='#1a1a2e',
            edgecolor='white',
            labelcolor='white',
            fontsize=8,
            framealpha=0.8
        )
    
    def clear(self):
        """Clear the spectrogram"""
        self.audio_buffer.clear()
        self.current_formants = None
        self.ax.clear()
        self.ax.set_facecolor('#0f0f1e')
        self.ax.set_xlabel('Time (s)', color='white', fontsize=10)
        self.ax.set_ylabel('Frequency (Hz)', color='white', fontsize=10)
        self.ax.tick_params(colors='white', labelsize=9)
        self.canvas.draw_idle()


class CompactSpectrogramWidget(QWidget):
    """Compact version of spectrogram for embedding in training screen"""
    
    def __init__(self, sample_rate=44100, window_duration=2.0):
        super().__init__()
        self.sample_rate = sample_rate
        self.window_duration = window_duration
        
        # Smaller buffer for compact display
        buffer_size = int(sample_rate * window_duration)
        self.audio_buffer = deque(maxlen=buffer_size)
        self.current_formants = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize compact UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Smaller matplotlib figure
        self.figure = Figure(figsize=(6, 2.5), facecolor='#1a1a2e')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet(f"background: transparent; border-radius: {AriaRadius.MD}px;")
        
        # Create axis
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#0f0f1e')
        self.ax.set_xlabel('Time (s)', color='white', fontsize=8)
        self.ax.set_ylabel('Freq (Hz)', color='white', fontsize=8)
        self.ax.tick_params(colors='white', labelsize=7)
        
        # Very tight layout
        self.figure.tight_layout(pad=0.5)
        
        layout.addWidget(self.canvas)
    
    def update_audio(self, audio_chunk):
        """Update with new audio chunk"""
        self.audio_buffer.extend(audio_chunk)
    
    def update_formants(self, formants):
        """Update formant data"""
        self.current_formants = formants
    
    def refresh_display(self):
        """Refresh the compact spectrogram"""
        if len(self.audio_buffer) < 512:
            return
        
        audio_data = np.array(self.audio_buffer)
        
        try:
            # Smaller window for faster processing
            freqs, times, Sxx = spectrogram(
                audio_data,
                fs=self.sample_rate,
                nperseg=256,
                noverlap=192,
                window='hann'
            )
            
            # Voice range only
            freq_mask = freqs <= 3000
            freqs = freqs[freq_mask]
            Sxx = Sxx[freq_mask, :]
            
            Sxx_db = 10 * np.log10(Sxx + 1e-10)
            
            self.ax.clear()
            
            self.ax.pcolormesh(
                times,
                freqs,
                Sxx_db,
                shading='gouraud',
                cmap='viridis',
                vmin=np.percentile(Sxx_db, 10),
                vmax=np.percentile(Sxx_db, 90)
            )
            
            # Add formant markers if available
            if self.current_formants:
                for i, formant in enumerate(self.current_formants[:2]):  # Only F1 and F2
                    if formant > 0 and formant < 3000:
                        self.ax.axhline(
                            y=formant,
                            color='cyan' if i == 0 else 'magenta',
                            linestyle=':',
                            linewidth=1.5,
                            alpha=0.6
                        )
            
            self.ax.set_facecolor('#0f0f1e')
            self.ax.set_xlim([0, self.window_duration])
            self.ax.set_ylim([0, 3000])
            self.ax.tick_params(colors='white', labelsize=7)
            
            self.canvas.draw_idle()
            
        except Exception as e:
            log_error(e, "CompactSpectrogramWidget.refresh_display")
    
    def clear(self):
        """Clear the spectrogram"""
        self.audio_buffer.clear()
        self.current_formants = None
        self.ax.clear()
        self.canvas.draw_idle()
