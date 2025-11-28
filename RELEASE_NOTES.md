# Aria Voice Studio - v5.2 Release Notes

**Release Date**: October 2025

## What's New in v5

### Achievement System
- Unlock achievements based on sessions, practice time, streaks, and goals
- Rarity levels: Common, Uncommon, Rare, Epic, Legendary
- Notifications in session summaries and Progress screen

### Discord Integration
- Export training stats to JSON
- Share progress with the community via Discord bot
- Leaderboards, comparisons, and profile cards
- Privacy controls for what you share

### Formant Tracking
- Real-time F1/F2/F3 analysis using LPC
- Visual formant indicators and resonance shift detection

### Advanced Safety Tracking
- Multi-day fatigue tracking with rest day recommendations
- Recovery scoring and auto-pause on critical strain

### Session Intelligence
- Time-based recommendations and adaptive break reminders
- Context-aware motivational messaging

### Voice Quality Analysis
- Breathiness and nasality scoring
- Enhanced vocal health metrics

### Real-time Spectrogram
- Frequency visualization with formant highlighting
- Configurable settings

### Performance Optimizations
- Reduced FFT workload via caching
- Lower I/O with batch saves
- Faster startup with lazy component loading
- Optimized buffer sizes for lower latency

## Installation

```bash
pip install -r requirements.txt
python main.py
```

## Requirements
- Python 3.8+
- Microphone access
- Windows/macOS/Linux

## What's Included
- Main application (`main.py`)
- Core voice analysis engine
- Full GUI with all screens
- Guided exercises library
- Health monitoring system
- Achievement tracking
- Documentation

## Quick Start
1. Complete onboarding to set a voice goal
2. Start live training for real-time pitch feedback
3. Use guided exercises (breathing, humming, slides, resonance)
4. Track stats, streaks, and achievements
5. Check weekly vocal health grades

## Known Issues
- None reported for v5

## Support
- Issues: https://github.com/VocalOpal/Aria/issues
- Documentation: see CLAUDE.md and AGENTS.md
- Contributing: see CONTRIBUTING.md

## Privacy & Safety
- All data stored locally
- No telemetry or cloud sync
- No internet required (except Discord bot)
- Research-based safety thresholds
- Not medical advice; consult an SLP for professional guidance

## License
GNU General Public License - see LICENSE file

---

Thank you for using Aria Voice Studio!