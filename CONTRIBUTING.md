# Contributing to Aria Voice Studio

Thank you for your interest in contributing to Aria Voice Studio! This guide will help you get started.

## Code of Conduct

This project is committed to providing a welcoming and inclusive environment for everyone, regardless of gender identity, sexual orientation, disability, ethnicity, or religion.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in GitHub Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Your OS and Python version
   - Relevant logs from `logs/` directory

### Suggesting Features

1. Check existing issues for similar suggestions
2. Create a feature request issue with:
   - Clear use case description
   - Why this would benefit users
   - Proposed implementation (if applicable)

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** following our code style
4. **Test your changes**: `python run_tests.py all`
5. **Commit with clear messages**: `git commit -m "Add feature: description"`
6. **Push to your fork**: `git push origin feature/your-feature-name`
7. **Open a Pull Request** with description of changes

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/aria-voice-studio.git
cd aria-voice-studio

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py

# Run tests
python run_tests.py all
```

## Code Style Guidelines

### Python Style
- Follow PEP 8 conventions
- Use type hints where applicable
- Use snake_case for functions/variables
- Keep functions focused and single-purpose

### Critical Rules
1. **Emoji Handling**: ALWAYS use `convert_emoji_text()` from `utils/emoji_handler.py`
2. **File Operations**: Use `save_json_atomic()` and `load_json_safe()` from `utils/file_operations.py`
3. **Error Handling**: Use `log_error()` from `utils/error_handler.py`
4. **Design System**: Follow `gui/design_system.py` for UI consistency

### Testing
- Add tests for new features in `tests/`
- Use pytest fixtures from `conftest.py`
- Mark tests appropriately: `@pytest.mark.unit` or `@pytest.mark.integration`
- Aim for 80%+ coverage on core modules

## Project Structure

See `AGENTS.md` for detailed architecture information.

## Documentation

- Update README.md if adding user-facing features
- Update CLAUDE.md if changing architecture
- Add docstrings to new functions/classes
- Update type hints

## Testing Guidelines

```bash
# Run all tests
python run_tests.py all

# Run only unit tests
python run_tests.py unit

# Run with coverage
python run_tests.py coverage

# Run specific test
pytest tests/test_session_manager.py -v
```

## Privacy & Safety Principles

1. **Privacy-First**: All data local, no telemetry, explicit export only
2. **Safety-First**: Auto-pause on strain, research-based thresholds
3. **Inclusive**: MTF/FTM/NB support, non-prescriptive language
4. **Not Medical**: Always disclaim medical advice

## Areas Needing Help

- Adding new voice exercises with proper research backing
- Improving audio analysis accuracy
- UI/UX enhancements
- Documentation improvements
- Testing on different platforms
- Accessibility features

## Questions?

Feel free to:
- Open a discussion issue
- Ask in Discord community
- Review existing code and documentation

Thank you for making Aria better for everyone! 🎤
