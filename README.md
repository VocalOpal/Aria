# Aria Voice Studio v4.2

**Your voice, your journey, your authentic self**

A modern PyQt6-based voice training application with real-time pitch monitoring, guided exercises, and comprehensive audio file analysis to help you develop your authentic voice. Features a beautiful, intuitive GUI with advanced safety monitoring and progress tracking.

##  Features Overview

### **Live Voice Training**
- Real-time pitch monitoring with intuitive visual feedback
- Progressive goal system with adaptive improvement tracking
- Advanced safety monitoring to prevent vocal strain
- Voice resonance analysis with breathing pattern detection
- Auto-save progress with comprehensive session analytics
- Modern GUI with responsive controls and real-time statistics

### **Voice Exercises & Warm-ups**
- Interactive guided exercise system with visual timers and instructions
- Comprehensive exercise library: humming, lip trills, pitch slides, straw phonation
- Resonance shift training and advanced breathing control techniques
- Progress tracking with completion rates and performance analytics
- Modular exercise components with customizable difficulty levels

### **Audio File Pitch Analysis**
- Upload and analyze voice recordings with comprehensive pitch analysis
- Get personalized training goal recommendations based on your voice characteristics
- Track progress with detailed analysis history and trend visualization
- Automatic goal setting from analysis results with safety considerations
- Advanced voice quality metrics and optional assessment scoring
- Export analysis results for external review and tracking

### **Progress & Statistics**
- Detailed session statistics and performance trends
- Weekly and long-term progress visualization
- Goal achievement tracking and improvement analysis
- Voice characteristic evolution over time

### **Smart Configuration**
- Comprehensive voice preset system (MTF, FTM, Non-Binary variations)
- Intelligent goal progression with safety-based adaptation
- Advanced audio settings with microphone calibration and noise suppression
- Customizable alert preferences and visual feedback options
- Component-based architecture with modular settings management
- Automatic configuration backup and recovery system

## 🚀 Quick Start

### 🚀 Installation Guide

#### System Requirements
- **Python 3.9+** (recommended for best compatibility)
- **Operating System:** Windows 10+, macOS 10.15+, or Linux with GUI support
- **Audio:** Microphone access for real-time training
- **Memory:** 4GB+ RAM recommended for audio processing

#### Installation Steps

1. **Install Python**
   - Download Python 3.9+ from [python.org](https://www.python.org/downloads/)
   - Ensure "Add Python to PATH" is checked during installation
   - Verify installation: `python --version`

2. **Download Aria Voice Studio**
   - Clone or download this repository
   - Open terminal/command prompt in the project directory

3. **Set up Virtual Environment** (Recommended)
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Launch the Application**
   ```bash
   python main.py
   ```

#### Troubleshooting Installation
- If PyAudio fails to install, try: `pip install pipwin && pipwin install pyaudio`
- For M1 Macs, you may need: `brew install portaudio && pip install pyaudio`
- Linux users may need: `sudo apt-get install python3-pyqt6`

### First-Time Setup
1. **Launch the application** - A modern GUI window will open
2. **Complete onboarding** - Follow the guided setup process for your voice goals
3. **Choose a voice preset** that matches your objectives in Settings
4. **Perform audio analysis** - Upload a voice sample for personalized recommendations
5. **Configure microphone** - Test and adjust audio input settings
6. **Start your training journey** with customized goals and visual feedback

## How to Use

### GUI Navigation

The application features a modern graphical interface with intuitive navigation:

- **Training Screen**: Real-time pitch monitoring with visual feedback
- **Exercises Screen**: Guided exercises and warm-ups with timers
- **Audio Analysis Screen**: Upload and analyze voice recordings
- **Progress Screen**: Detailed statistics and training history
- **Settings Screen**: Comprehensive configuration options

Navigation is handled through the main navigation widget with clear visual indicators for each section.

### Audio File Pitch Analysis Guide

#### **Getting Started**
1. **Access the feature:** Click "Audio Analysis" in the main navigation
2. **Upload audio file:** Browse and select your voice recording
3. **Analyze:** Click "Analyze Audio File" for detailed voice analysis
4. **Set goals:** Use "Set Goal from Analysis" to apply recommendations as training targets

#### **Supported Audio Formats**
- `.wav` (recommended for best quality)
- `.mp3`, `.flac`, `.ogg`, `.m4a`, `.aac`

#### **Recording Tips**
✅ **DO:**
- Use your natural speaking voice
- Record 5-10 seconds of continuous speech
- Ensure quiet environment (no background noise)
- Try reading a paragraph or sustained vowel sounds

❌ **AVOID:**
- Background music or noise
- Very short clips (under 3 seconds)
- Multiple people talking
- Whispering or shouting

#### **Understanding Your Analysis**
- **Average Pitch:** Your typical fundamental frequency
- **Pitch Range:** Lowest to highest frequencies detected
- **Pitch Stability:** Consistency of your voice (higher = more stable)
- **Voice Clarity:** Percentage of clear speech vs. silence/noise
- **Assessment Categories:**
  - Low pitch: Masculine characteristics
  - Lower-mid: Androgynous, leaning masculine  
  - Mid-range: Neutral/androgynous
  - Upper-mid: Feminine characteristics
  - High pitch: Very feminine range

#### **Analysis Screen Features**
- **Analyze Audio File** - Upload and analyze new voice recordings
- **View Analysis History** - Browse previous analyses with trend visualization
- **Set Goal from Analysis** - Apply analysis results as training targets
- **Analysis Summary** - Comprehensive overview of voice characteristics
- **Export Results** - Save analysis data for external review

### Live Training Session
1. **Start training:** Navigate to Training Screen and click "Start Training"
2. **Speak naturally** - real-time visual feedback shows your pitch
3. **Follow visual indicators** - stay within your target frequency range
4. **Use GUI controls:**
   - Stop button - End current training session
   - Pause/Resume toggle - Control session flow
   - Settings button - Adjust training parameters
   - Progress indicators show session statistics in real-time

### Voice Exercises
1. **Access exercises:** Click "Exercises" in the main navigation
2. **Browse exercise categories** - organized by type and difficulty
3. **Select exercises** from the visual grid layout
4. **Follow guided instructions** with built-in timers and progress tracking
5. **Try the warm-up routine** - perfect starting point for beginners

## Configuration & Settings

### Voice Presets Available
- **MTF (Male-to-Female)** - Feminine voice training
- **FTM (Female-to-Male)** - Masculine voice development
- **Non-Binary (Higher)** - Androgynous with elevation
- **Non-Binary (Lower)** - Androgynous with deepening  
- **Non-Binary (Neutral)** - Maintain range with control
- **Custom** - Manual configuration

### Settings Menu Structure
```
Settings & Configuration
├── Voice Goals & Presets       - Choose your voice development path
├── Target Pitch Settings       - Customize frequency thresholds  
├── Microphone & Audio         - Audio input and sensitivity
├── Alert Preferences          - Notification sounds and timing
├── Technical Options          - Fine-tune audio and detection settings
├── Save Configuration         - Persist your settings
└── Clear Account Data         - Reset all progress and settings
```

## Frequency Reference

### Typical Vocal Ranges
- **Masculine voice:** 85-180 Hz
- **Androgynous voice:** 165-265 Hz  
- **Feminine voice:** 165-265 Hz
- **Very high feminine:** 200-300 Hz

*Note: Individual voices vary significantly. Use the audio analysis feature to find your optimal range.*

## Application Files

The application creates and manages these files:
- `data/voice_config.json` - Your settings and training goals
- `data/voice_config_progress.json` - Session history and statistics
- `data/voice_config_analysis_history.json` - Audio analysis results and history
- `data/backups/` - Automatic configuration backups
- `logs/` - Application logs and error tracking

## Troubleshooting

### Audio Issues
- **No microphone input:** Check microphone permissions and connections
- **Poor pitch detection:** Adjust microphone sensitivity in Settings → Microphone & Audio
- **Background noise:** Use the built-in noise learning (first 8 seconds of each session)

### Installation Problems
- **Windows:** May need Microsoft Visual C++ Build Tools for PyAudio
- **macOS:** Install PortAudio with `brew install portaudio`
- **Linux:** Install dependencies with `sudo apt-get install portaudio19-dev python3-pyaudio`
- **PyQt6 Issues:** Ensure you have PyQt6 (not PyQt5) installed
- **Permission Issues:** May need to grant microphone access on macOS/Windows

### Analysis Issues
- **File not found:** Ensure complete file path, use quotes for paths with spaces
- **Analysis fails:** Verify supported format, check for actual voice content
- **Unexpected results:** Avoid background noise, multiple speakers, very short clips

## Training Tips

### For Beginners
1. **Start with audio analysis** - get personalized recommendations
2. **Use preset goals** - choose MTF, FTM, or Non-Binary presets as starting points
3. **Begin with exercises** - try the 5-minute warm-up routine
4. **Practice consistently** - short, frequent sessions work best

### Experienced Users
1. **Track your progress** - use the analysis history to monitor improvement
2. **Adjust goals progressively** - increase targets as you improve
3. **Focus on consistency** - stability is as important as pitch
4. **Combine techniques** - use live training, exercises, and regular analysis

### Voice Feminization Specific
- **Start around 165-180 Hz** and gradually work higher
- **Focus on resonance** - pitch alone doesn't create feminine voice
- **Practice daily** - voice training requires consistent muscle memory development  
- **Record regularly** - use audio analysis to track your progress objectively

## Technical Details

### Architecture
- **GUI Framework:** PyQt6 with modern design system
- **Audio Processing:** 44.1 kHz sample rate, 4096 sample chunks
- **Pitch Detection:** Advanced autocorrelation and YIN algorithms
- **Analysis Engine:** librosa with spectral analysis and machine learning
- **Real-time Processing:** Sub-100ms latency for live feedback
- **Component System:** Modular architecture with dependency injection
- **Safety Systems:** Built-in voice strain monitoring and session limits

### Dependencies
- **Core:** numpy, scipy, scikit-learn for signal processing
- **Audio:** pyaudio, librosa, pygame for audio I/O and analysis
- **GUI:** PyQt6 for cross-platform interface
- **Visualization:** matplotlib for progress charts and analysis
- **Cross-platform:** Full Windows, macOS, Linux support

## License

This application is provided for educational and personal use. Developed with care for the voice training community.

---

**Need help?** The app includes detailed help text and guided setup. Each menu has instructions and tips for effective voice training.
