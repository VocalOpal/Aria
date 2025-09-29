import sys
import locale
import logging
from typing import Dict, Optional, Union
from functools import lru_cache

logger = logging.getLogger(__name__)

class EmojiHandler:
    """Centralized emoji handling with intelligent fallback system"""

    EMOJI_MAP = {

        '🎯': {'ascii': '[TARGET]', 'context': 'goals'},
        '⏰': {'ascii': '[TIME]', 'context': 'time'},
        '🔔': {'ascii': '[BELL]', 'context': 'alerts'},
        '⏱️': {'ascii': '[TIMER]', 'context': 'time'},
        '💭': {'ascii': '[THOUGHT]', 'context': 'tips'},
        '🌱': {'ascii': '[SEEDLING]', 'context': 'growth'},
        '🎤': {'ascii': '[MIC]', 'context': 'audio'},
        '💪': {'ascii': '[STRONG]', 'context': 'achievement'},
        '🔥': {'ascii': '[FIRE]', 'context': 'achievement'},
        '⭐': {'ascii': '[STAR]', 'context': 'achievement'},
        '🏆': {'ascii': '[TROPHY]', 'context': 'achievement'},

        '🕐': {'ascii': '[CLOCK]', 'context': 'time'},
        '📅': {'ascii': '[CALENDAR]', 'context': 'schedule'},

        '📊': {'ascii': '[CHART]', 'context': 'data'},
        '📈': {'ascii': '[GRAPH]', 'context': 'data'},
        '📉': {'ascii': '[DECLINING]', 'context': 'data'},

        '✅': {'ascii': '[CHECK]', 'context': 'success'},
        '❌': {'ascii': '[X]', 'context': 'error'},
        '⚠️': {'ascii': '[WARNING]', 'context': 'warning'},
        '🚨': {'ascii': '[ALERT]', 'context': 'warning'},
        '🛡️': {'ascii': '[SHIELD]', 'context': 'safety'},

        '🎉': {'ascii': '[CELEBRATION]', 'context': 'achievement'},
        '✨': {'ascii': '[SPARKLES]', 'context': 'achievement'},
        '💡': {'ascii': '[BULB]', 'context': 'tips'},

        '📚': {'ascii': '[BOOKS]', 'context': 'education'},
        '🎓': {'ascii': '[GRADUATION]', 'context': 'education'},
        '📋': {'ascii': '[CLIPBOARD]', 'context': 'education'},

        '🩺': {'ascii': '[STETHOSCOPE]', 'context': 'health'},

        '🎙️': {'ascii': '[STUDIO_MIC]', 'context': 'audio'},
        '🔊': {'ascii': '[SPEAKER]', 'context': 'audio'},
        '🎧': {'ascii': '[HEADPHONES]', 'context': 'audio'},
        '📱': {'ascii': '[PHONE]', 'context': 'device'},
        '🔧': {'ascii': '[WRENCH]', 'context': 'device'},

        '↑': {'ascii': '^', 'context': 'direction'},
        '↓': {'ascii': 'v', 'context': 'direction'},
        '→': {'ascii': '->', 'context': 'direction'},
        '←': {'ascii': '<-', 'context': 'direction'},

        '💧': {'ascii': '[WATER]', 'context': 'health'},
        '🧘': {'ascii': '[MEDITATION]', 'context': 'health'},
        '🌿': {'ascii': '[LEAF]', 'context': 'health'},

        '📈': {'ascii': '[PROGRESS]', 'context': 'growth'},
        '🎯': {'ascii': '[AIM]', 'context': 'goals'},
        '🚀': {'ascii': '[ROCKET]', 'context': 'progress'},
        '🌟': {'ascii': '[SHINING]', 'context': 'achievement'},
        '🏋️': {'ascii': '[WEIGHT]', 'context': 'training'},
        '⬆️': {'ascii': '[UP]', 'context': 'direction'},

        '💎': {'ascii': '[DIAMOND]', 'context': 'achievement'},
        '🏅': {'ascii': '[MEDAL]', 'context': 'achievement'},
        '⏳': {'ascii': '[HOURGLASS]', 'context': 'time'},
        '🎪': {'ascii': '[CIRCUS]', 'context': 'achievement'},
        '🔒': {'ascii': '[LOCKED]', 'context': 'achievement'},
        '🏹': {'ascii': '[BOW]', 'context': 'achievement'},
    }

    def __init__(self):
        self._unicode_support = None
        self._encoding_info = None
        self._initialize_support()

    def _initialize_support(self):
        """Initialize Unicode support detection with comprehensive testing"""
        try:

            self._encoding_info = {
                'stdout_encoding': getattr(sys.stdout, 'encoding', None),
                'preferred_encoding': locale.getpreferredencoding(),
                'locale': locale.getlocale(),
                'platform': sys.platform
            }

            test_emojis = ['🎯', '✅', '❌', '⚠️']
            self._unicode_support = self._test_unicode_support(test_emojis)

            logger.info(f"Unicode support: {self._unicode_support}, Encoding: {self._encoding_info}")

        except Exception as e:
            logger.warning(f"Error detecting Unicode support: {e}")
            self._unicode_support = False

    def _test_unicode_support(self, test_emojis: list) -> bool:
        """Test if the current environment can handle Unicode emojis"""
        if not sys.stdout.encoding:
            return False

        try:

            encoding = sys.stdout.encoding
            for emoji in test_emojis:
                emoji.encode(encoding)

            if sys.platform.startswith('win'):

                if 'cmd' in sys.stdout.__class__.__name__.lower():
                    return False

            return True

        except (UnicodeEncodeError, AttributeError, LookupError):
            return False

    @lru_cache(maxsize=256)
    def convert_text(self, text: str, context: Optional[str] = None) -> str:
        """
        Convert text with emojis to appropriate format for current environment.

        Args:
            text: Text that may contain emojis
            context: Optional context hint for better ASCII fallbacks

        Returns:
            Text with emojis converted to ASCII if needed
        """
        if self._unicode_support:
            return text

        converted_text = text
        for emoji, mapping in self.EMOJI_MAP.items():
            if emoji in converted_text:

                if context and mapping.get('context') == context:
                    replacement = mapping['ascii']
                else:
                    replacement = mapping['ascii']

                converted_text = converted_text.replace(emoji, replacement)

        return converted_text

    def safe_print(self, *args, context: Optional[str] = None, **kwargs):
        """
        Print function that automatically handles emoji conversion.

        Args:
            *args: Arguments to print
            context: Optional context for better emoji conversion
            **kwargs: Keyword arguments passed to print()
        """
        converted_args = []
        for arg in args:
            if isinstance(arg, str):
                converted_args.append(self.convert_text(arg, context))
            else:
                converted_args.append(arg)

        try:

            import builtins
            if hasattr(builtins, '__print__'):
                builtins.__print__(*converted_args, **kwargs)
            else:
                builtins.print(*converted_args, **kwargs)
        except UnicodeEncodeError as e:

            logger.warning(f"Unicode error in print, using ASCII fallback: {e}")
            ascii_args = []
            for arg in converted_args:
                if isinstance(arg, str):
                    ascii_args.append(arg.encode('ascii', 'replace').decode('ascii'))
                else:
                    ascii_args.append(str(arg))
            import builtins
            if hasattr(builtins, '__print__'):
                builtins.__print__(*ascii_args, **kwargs)
            else:
                builtins.print(*ascii_args, **kwargs)

    def format_message(self, template: str, context: Optional[str] = None, **kwargs) -> str:
        """
        Format a message template with emoji conversion and variable substitution.

        Args:
            template: Template string with {variables} and emojis
            context: Optional context for emoji conversion
            **kwargs: Variables for template substitution

        Returns:
            Formatted string with emojis converted if necessary
        """
        try:
            formatted = template.format(**kwargs)
            return self.convert_text(formatted, context)
        except (KeyError, ValueError) as e:
            logger.error(f"Error formatting message template: {e}")
            return self.convert_text(template, context)

    def get_status_indicator(self, status: str) -> str:
        """Get appropriate status indicator emoji/ASCII for given status"""
        status_map = {
            'success': '✅' if self._unicode_support else '[OK]',
            'error': '❌' if self._unicode_support else '[ERROR]',
            'warning': '⚠️' if self._unicode_support else '[WARNING]',
            'info': '💡' if self._unicode_support else '[INFO]',
            'progress': '📈' if self._unicode_support else '[PROGRESS]',
            'target': '🎯' if self._unicode_support else '[TARGET]',
            'celebration': '🎉' if self._unicode_support else '[CELEBRATION]'
        }
        return status_map.get(status.lower(), '')

    def supports_unicode(self) -> bool:
        """Check if current environment supports Unicode emojis"""
        return self._unicode_support

    def get_encoding_info(self) -> Dict[str, Union[str, tuple, None]]:
        """Get detailed encoding information for debugging"""
        return self._encoding_info.copy() if self._encoding_info else {}

_emoji_handler = EmojiHandler()

def safe_print(*args, context: Optional[str] = None, **kwargs):
    """Global safe print function"""
    _emoji_handler.safe_print(*args, context=context, **kwargs)

def convert_emoji_text(text: str, context: Optional[str] = None) -> str:
    """Global emoji conversion function"""
    return _emoji_handler.convert_text(text, context)

def format_message(template: str, context: Optional[str] = None, **kwargs) -> str:
    """Global message formatting function"""
    return _emoji_handler.format_message(template, context, **kwargs)

def get_status_indicator(status: str) -> str:
    """Global status indicator function"""
    return _emoji_handler.get_status_indicator(status)

def supports_unicode() -> bool:
    """Check if Unicode is supported"""
    return _emoji_handler.supports_unicode()

def get_encoding_info() -> Dict[str, Union[str, tuple, None]]:
    """Get encoding information"""
    return _emoji_handler.get_encoding_info()