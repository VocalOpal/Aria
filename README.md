# MTF Voice Training Tool

A real-time voice pitch monitoring tool designed to help with MTF (male-to-female) voice training. The script continuously monitors your microphone input and plays an alert sound whenever your voice pitch drops below a configurable frequency threshold.

## Features

- **Real-time pitch detection** using autocorrelation
- **Configurable frequency threshold** for personalized training
- **Audio alerts** when pitch drops below threshold
- **Persistent configuration** saves your settings
- **Interactive controls** for adjusting threshold during use
- **Command-line options** for easy customization

## Installation

1. Install Python 3.7 or higher
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage
```bash
python voice_trainer.py
```

### With Custom Threshold
```bash
python voice_trainer.py --threshold 180
```

### With Custom Alert Sound
```bash
python voice_trainer.py --alert-sound path/to/your/sound.wav
```

### Command Line Options
- `--threshold`: Set pitch threshold in Hz (default: 165)
- `--alert-sound`: Path to custom alert sound file
- `--config`: Configuration file path (default: voice_config.json)

## Interactive Controls

While the program is running:
- **'q'**: Quit the program
- **'t'**: Adjust threshold interactively
- **'s'**: Save current configuration

## Frequency Ranges

Typical vocal frequency ranges:
- **Masculine voice**: 85-180 Hz
- **Androgynous voice**: 165-265 Hz
- **Feminine voice**: 165-265 Hz

Start with a threshold around 165 Hz and adjust based on your training goals.

## Configuration

Settings are automatically saved to `voice_config.json` and loaded on startup. You can manually edit this file or use the interactive controls.

## Troubleshooting

### Audio Issues
- Make sure your microphone is connected and working
- Check microphone permissions in your system settings
- Try adjusting your microphone volume if pitch detection isn't working

### Installation Issues
- On Windows, you may need to install Microsoft Visual C++ Build Tools for PyAudio
- On Linux, you might need: `sudo apt-get install portaudio19-dev python3-pyaudio`

## Tips for Voice Training

1. **Start gradually**: Begin with a comfortable threshold and gradually increase it
2. **Practice regularly**: Short, frequent sessions are more effective than long ones
3. **Focus on resonance**: Pitch is just one aspect - work on resonance and articulation too
4. **Record yourself**: Use additional tools to record and analyze your progress
5. **Be patient**: Voice training takes time and consistent practice

## Technical Details

- **Sample rate**: 44.1 kHz
- **Chunk size**: 4096 samples
- **Pitch detection**: Autocorrelation method
- **Frequency range**: 50-400 Hz detection range
- **Update rate**: Real-time processing

## License

This tool is provided as-is for educational and personal use :3
