# Aria Voice Studio v4.0

**Your voice, your journey, your authentic self**

A comprehensive voice training application featuring real-time pitch monitoring, guided exercises, and advanced audio file analysis for personalized voice development.

##  Features Overview

### **Live Voice Training**
- Real-time pitch monitoring with gentle feedback alerts
- Progressive goal system that adapts to your improvement  
- Advanced formant analysis for authentic voice feminization
- Breathing pattern training and resonance quality detection
- Auto-save progress with comprehensive trend analysis

### **Voice Exercises & Warm-ups**
- Guided warm-up routines (5-minute beginner routine available)
- Targeted exercises: humming, lip trills, pitch slides, straw phonation
- Resonance shift training and breathing control exercises
- Exercise progress tracking and completion rates

### **Audio File Pitch Analysis** *(NEW!)*
- Upload audio clips to analyze your voice pitch and characteristics
- Get personalized training goal recommendations based on your actual voice
- Track your progress by comparing recordings over time
- Automatic goal setting from voice analysis results
- Comprehensive voice quality metrics and femininity scoring

### **Progress & Statistics**
- Detailed session statistics and performance trends
- Weekly and long-term progress visualization
- Goal achievement tracking and improvement analysis
- Voice characteristic evolution over time

### **Smart Configuration**
- Voice preset system (MTF, FTM, Non-Binary options)
- Adaptive goal progression based on your improvement
- Customizable alert preferences and audio settings
- Microphone sensitivity and noise suppression controls

## 🚀 Quick Start

### Installation
1. **Install Python 3.7+** (3.9+ recommended)
2. **Install dependencies in CMD**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application:**
   ```bash
   python main.py
   ```

### First-Time Setup
1. **Launch the app** - you'll be guided through initial setup
2. **Choose a voice preset** that matches your goals (Settings → Voice Goals & Presets)
3. **Try the audio analysis** - record a 5-10 second voice sample for personalized recommendations
4. **Start training** with your customized goals

## How to Use

### Main Menu Navigation
```
1. Live Voice Training     - Real-time pitch monitoring
2. Voice Exercises         - Guided exercises and warm-ups  
3. Audio File Analysis     - Upload & analyze voice recordings
4. Progress & Statistics   - View your training progress
5. Settings & Config       - Customize your training experience
```

### Audio File Pitch Analysis Guide

#### **Getting Started**
1. **Access the feature:** Main Menu → Option 3
2. **Record your voice:** 5-10 seconds of natural speaking
3. **Analyze:** Upload your recording for detailed analysis
4. **Set goals:** Use recommendations as your training targets

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

#### **Analysis Menu Options**
1. **Analyze Audio File** - Upload new recording for analysis
2. **View Analysis History** - See all previous analyses and trends
3. **Set Goal from Analysis** - Choose from recent analyses as training goals
4. **Analysis Summary** - Overview of your voice characteristics

### Live Training Session
1. **Start training:** Main Menu → Option 1 → Start Training
2. **Speak naturally** - the app monitors your pitch in real-time
3. **Follow visual feedback** - stay above your target frequency
4. **Use controls:**
   - `q` - Stop training
   - `stats` - Show session statistics
   - `pause` - Pause/resume training
   - `save` - Save current progress

### Voice Exercises
1. **Access exercises:** Main Menu → Option 2
2. **Try the warm-up routine** (Option W) - great for beginners
3. **Choose specific exercises** based on your needs
4. **Follow on-screen instructions** and duration timers

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
├── Advanced Options           - Fine-tune technical parameters
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

## Troubleshooting

### Audio Issues
- **No microphone input:** Check microphone permissions and connections
- **Poor pitch detection:** Adjust microphone sensitivity in Settings → Microphone & Audio
- **Background noise:** Use the built-in noise learning (first 8 seconds of each session)

### Installation Problems
- **Windows:** May need Microsoft Visual C++ Build Tools for PyAudio
- **macOS:** Install with `brew install portaudio` 
- **Linux:** Install with `sudo apt-get install portaudio19-dev python3-pyaudio`

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

### Advanced Training
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

- **Audio Processing:** 44.1 kHz sample rate, 4096 sample chunks
- **Pitch Detection:** Autocorrelation and YIN algorithms
- **Analysis Engine:** librosa with advanced spectral analysis  
- **Real-time Processing:** Sub-100ms latency for live feedback
- **Cross-platform:** Windows, macOS, Linux support

## License

This application is provided for educational and personal use. Developed with care for the voice training community.

---

**Need help?** The application includes comprehensive help text and guided setup. Each menu provides detailed instructions and tips for effective voice training.
