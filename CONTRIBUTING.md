# Contributing to Aria Voice Studio

Thank you for your interest in contributing to Aria Voice Studio! This project aims to provide accessible, effective voice training tools for everyone. We welcome contributions from developers, voice training experts, accessibility advocates, and community members.

## 🌟 Ways to Contribute

### 🐛 Report Issues
- Use our [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- Include system information and steps to reproduce
- Check existing issues before creating new ones

### 💡 Suggest Features
- Use our [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
- Explain the problem and proposed solution
- Consider voice training context and user needs

### 🔧 Code Contributions
- Bug fixes and improvements
- New features and exercises
- Performance optimizations
- Documentation improvements

### 📚 Documentation
- Improve README clarity
- Add voice training guides
- Create tutorials and examples
- Update troubleshooting sections

## 🚀 Getting Started

### Prerequisites
- Python 3.7+ (3.9+ recommended)
- Git for version control
- Microphone for testing audio features

### Development Setup
1. **Fork the repository** on GitHub
2. **Clone your fork locally:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Aria.git
   cd Aria
   ```
3. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Test the application:**
   ```bash
   python main.py
   ```

### Making Changes
1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make your changes** following our coding standards
3. **Test thoroughly** - especially audio-related features
4. **Commit with clear messages:**
   ```bash
   git commit -m "Add: Brief description of changes"
   ```

## 📋 Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings for classes and functions
- Keep functions focused and reasonably sized
- Comment complex audio processing algorithms

### Audio Development Notes
- **Test with various microphones** - built-in, USB, headsets
- **Consider different audio environments** - quiet vs. noisy
- **Validate across platforms** - Windows, macOS, Linux
- **Handle audio errors gracefully** - provide helpful error messages
- **Respect user privacy** - no audio data should be stored or transmitted

### Voice Training Considerations
- **Be inclusive** - support all voice training goals (MTF, FTM, non-binary)
- **Provide encouragement** - positive, supportive messaging
- **Respect expertise** - consult voice training professionals when possible
- **Consider accessibility** - features for different abilities
- **Safety first** - avoid features that could strain voices

## 🧪 Testing

### Manual Testing Checklist
- [ ] Application starts without errors
- [ ] Microphone detection and initialization works
- [ ] Real-time pitch detection is responsive and accurate
- [ ] Audio file analysis processes various formats correctly
- [ ] Settings save and load properly
- [ ] Menu navigation works smoothly
- [ ] Error handling provides helpful messages

### Audio Testing
- Test with different microphone types
- Verify noise suppression effectiveness  
- Check pitch detection accuracy across voice ranges
- Validate audio file format support

### Cross-Platform Testing
- Windows: Test PyAudio initialization
- macOS: Verify microphone permissions
- Linux: Check ALSA/PulseAudio compatibility

## 📝 Pull Request Process

### Before Submitting
1. **Ensure your code works** on your local setup
2. **Test key features** that might be affected by your changes  
3. **Update documentation** if you've changed functionality
4. **Check for merge conflicts** with the main branch

### Pull Request Guidelines
1. **Use descriptive titles:** "Fix pitch detection accuracy" not "Bug fix"
2. **Explain the changes:** What problem does this solve? How?
3. **Reference issues:** Link to related bug reports or feature requests
4. **Small, focused changes:** Easier to review and merge
5. **Test instructions:** Help reviewers verify your changes work

### Review Process
- Maintainers will review your PR and may request changes
- Discussion and feedback help improve the contribution
- Once approved, your changes will be merged
- Thank you for your patience during the review process!

## 💬 Community Guidelines

### Be Respectful and Inclusive
- Welcome newcomers and answer questions helpfully
- Respect different voice training goals and experiences
- Use inclusive language and avoid assumptions
- Focus on technical merits in discussions

### Voice Training Sensitivity
- Remember this project serves people working on personal voice goals
- Be encouraging and supportive, not critical
- Respect privacy and personal experiences
- Consider the emotional aspects of voice training

## 🆘 Getting Help

### Questions About Contributing
- Open a GitHub issue with the "question" label
- Check existing documentation and issues first
- Be specific about what you need help with

### Technical Development Help
- Include your development environment details
- Share error messages and logs
- Describe what you've already tried

### Voice Training Expertise
- We welcome input from voice training professionals
- Speech-language pathologists and voice coaches are especially valuable
- Help us ensure features are safe and effective

## 🎯 Project Priorities

### High Priority Areas
- **Accessibility improvements** - screen readers, keyboard navigation
- **Cross-platform compatibility** - especially audio system integration  
- **Voice safety features** - prevent vocal strain and injury
- **Beginner-friendly features** - better onboarding and guidance
- **Performance optimizations** - faster startup, lower CPU usage

### Current Focus Areas
- Improving pitch detection accuracy
- Better noise suppression algorithms
- More comprehensive voice exercises
- Enhanced progress tracking and motivation

## 📄 License

By contributing to Aria Voice Studio, you agree that your contributions will be licensed under the MIT License that covers the project. This ensures the project remains open and accessible to all users.

## 🙏 Recognition

Contributors who make significant improvements will be recognized in:
- README.md acknowledgments section
- Release notes for major contributions
- Project documentation where appropriate

---

**Questions?** Don't hesitate to open an issue or reach out. We're here to help and appreciate your interest in making voice training more accessible for everyone!