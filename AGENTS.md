# Aria Voice Studio - Agent Guide

## Build/Lint/Test Commands
- **Run app**: `python main.py`
- **Run all tests**: `python run_tests.py all`
- **Run unit tests**: `python run_tests.py unit`
- **Run single test**: `pytest tests/test_session_manager.py -v`
- **Run with coverage**: `python run_tests.py coverage`

## Architecture & Codebase Structure
- **core/**: Business logic (VoiceSessionManager, VoiceTrainingController, VoiceConfigurationManager, VoiceAudioAnalyzerCoordinator, VoiceSafetyCoordinator)
- **voice/**: Audio analysis pipeline (pitch detection, formant tracking, safety monitoring)
- **gui/**: PyQt6 interface with design system (screens, components, AriaColors/AriaTypography classes)
- **utils/**: Utilities (emoji_handler.py, file_operations.py, error_handler.py)
- **data/**: Local JSON-based data storage (profiles, sessions, settings) - created at runtime
- **logs/**: Daily error logs with GlobalErrorHandler
- **No databases**: All data stored locally in JSON files with atomic operations

## Code Style Guidelines
- **PEP 8** with type hints and docstrings
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Critical patterns**:
  - Always use `convert_emoji_text()` for emoji handling
  - Use `save_json_atomic()`/`load_json_safe()` for file operations
  - Use `log_error()` for error handling
  - Follow `gui/design_system.py` for UI consistency
- **Error handling**: Global error handler captures all exceptions to daily logs
- **Imports**: Absolute imports, utilities from utils/ package
- **Testing**: pytest with fixtures, mark @pytest.mark.unit/.integration, aim for 80% coverage
