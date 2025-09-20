import os
import time
import sys
from datetime import datetime

# Check if terminal supports Unicode (for emoji fallback)
def supports_unicode():
    """Check if the terminal supports Unicode characters"""
    try:
        import locale, sys
        encoding = sys.stdout.encoding or locale.getpreferredencoding()
        "🎯".encode(encoding)
        return True
    except (UnicodeEncodeError, AttributeError):
        return False

UNICODE_SUPPORT = supports_unicode()

# Emoji handling moved to utils.emoji_handler - use that instead

# Cross-platform keyboard handling
try:
    if os.name == 'nt':  # Windows
        import msvcrt
        def get_key():
            """Get a single keypress on Windows"""
            key = msvcrt.getch()
            if key == b'\xe0':  # Arrow key prefix
                key = msvcrt.getch()
                if key == b'H':  # Up arrow
                    return 'up'
                elif key == b'P':  # Down arrow
                    return 'down'
                elif key == b'K':  # Left arrow
                    return 'left'
                elif key == b'M':  # Right arrow
                    return 'right'
                return None  # Unknown arrow key
            elif key == b'\r':  # Enter
                return 'enter'
            elif key == b'\x1b':  # Escape
                return 'escape'
            else:
                try:
                    return key.decode('utf-8').lower()
                except UnicodeDecodeError:
                    return None
    else:  # Unix/Linux/Mac
        import tty, termios
        def get_key():
            """Get a single keypress on Unix systems"""
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.cbreak(fd)
                key = sys.stdin.read(1)
                if key == '\x1b':  # Escape sequence
                    key = sys.stdin.read(2)
                    if key == '[A':  # Up arrow
                        return 'up'
                    elif key == '[B':  # Down arrow
                        return 'down'
                    elif key == '[C':  # Right arrow
                        return 'right'
                    elif key == '[D':  # Left arrow
                        return 'left'
                elif key == '\r' or key == '\n':  # Enter
                    return 'enter'
                elif key == '\x1b':  # Escape
                    return 'escape'
                else:
                    return key.lower()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return None
    
    KEYBOARD_SUPPORT = True
except ImportError:
    # Fallback if keyboard modules aren't available
    def get_key():
        return input().strip().lower()
    KEYBOARD_SUPPORT = False

# Temporarily disable keyboard support for testing
# KEYBOARD_SUPPORT = False

class TerminalUI:
    """Clean terminal-style user interface"""
    
    def __init__(self):
        self.width = 80
        self.app_name = "Aria Voice Studio"
        self.version = "v4.0"
        self.tagline = "Your voice, your journey, your authentic self"
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_header(self):
        """Print application header"""
        self.clear_screen()
        print("=" * self.width)
        title = f"{self.app_name} {self.version}"
        padding = (self.width - len(title)) // 2
        print(" " * padding + title)
        
        tagline_padding = (self.width - len(self.tagline)) // 2
        print(" " * tagline_padding + self.tagline)
        print("=" * self.width)
        print()
        
    def print_separator(self, char="-", width=None):
        """Print separator line"""
        if width is None:
            width = self.width
        print(char * width)
        
    def print_menu(self, title, options, description=None):
        """Print menu with options"""
        print(f"[ {title} ]")
        if description:
            print(f"{description}")
        print()
        
        for key, desc in options.items():
            print(f"  {key:10} - {desc}")
        print()
        self.print_separator()
    
    def print_menu_with_highlight(self, title, options, description=None, selected_key=None):
        """Print menu with options and highlight selected option"""
        print(f"[ {title} ]")
        if description:
            print(f"{description}")
        print()
        
        for key, desc in options.items():
            if key == selected_key and KEYBOARD_SUPPORT:
                # Highlight selected option
                print(f"> {key:9} - {desc} <")
            else:
                print(f"  {key:10} - {desc}")
        print()
        self.print_separator()
        
    def print_status_line(self, text, clear_line=True):
        """Print status line with optional clear"""
        if clear_line:
            # Clear current line and return to start
            print(f"\r{' ' * self.width}\r", end="")
        print(f"{text}", end="", flush=True)
        
    def print_exercise_info(self, exercise_data):
        """Print exercise information"""
        print(f"Exercise: {exercise_data['name']}")
        print(f"Duration: {exercise_data['duration']} seconds")
        print(f"Instructions: {exercise_data['instructions']}")
        
        if exercise_data['target_range'][0] > 0:
            low, high = exercise_data['target_range']
            print(f"Target Range: {low}-{high} Hz")
            
        if exercise_data['breathing_focus']:
            print("Focus: Diaphragmatic breathing control")
            
        if 'tips' in exercise_data:
            print("\nTips:")
            for tip in exercise_data['tips']:
                print(f"  - {tip}")
        print()
        
    def print_session_stats(self, stats, goal_hz, base_hz, noise_pause_time=0.0):
        """Print session statistics with improved formatting including noise pause handling"""
        print("\n[ Session Summary ]")
        
        if stats['total_time'] > 0:
            elapsed = datetime.now() - stats['start_time']
            # Calculate active training time (excluding background noise pauses)
            total_session_seconds = int(elapsed.total_seconds())
            active_training_seconds = max(0, total_session_seconds - int(noise_pause_time))
            
            total_time = stats['total_time']
            time_ratio = (stats['time_in_range'] / total_time) * 100.0 if total_time > 0 else 0.0
            goal_ratio = (stats.get('goal_achievements', 0) / total_time) * 100.0 if total_time > 0 else 0.0
            
            # Format durations nicely
            def format_duration(seconds):
                mins, secs = divmod(seconds, 60)
                hours, mins = divmod(mins, 60)
                if hours > 0:
                    return f"{hours}h {mins}m {secs}s"
                elif mins > 0:
                    return f"{mins}m {secs}s"
                else:
                    return f"{secs}s"
                    
            total_duration_str = format_duration(total_session_seconds)
            active_duration_str = format_duration(active_training_seconds)
            
            # Show both total and active training time if there were pauses
            if noise_pause_time > 5.0:  # Only show if significant pause time
                print(f"Total Session: {total_duration_str} | Active Training: {active_duration_str}")
                pause_str = format_duration(int(noise_pause_time))
                print(f"Background Noise Pauses: {pause_str}")
            else:
                print(f"Session Duration: {active_duration_str}")
                
            print(f"Average Pitch: {stats['avg_pitch']:.1f} Hz (Range: {stats['min_pitch']:.1f}-{stats['max_pitch']:.1f} Hz)")
            print(f"Current Goal: {goal_hz:.1f} Hz | Base Target: {base_hz:.1f} Hz")
            
            # Progress bars
            goal_bar = self.create_progress_bar(goal_ratio, 20)
            base_bar = self.create_progress_bar(time_ratio, 20)
            
            print(f"Goal Achievement: {goal_bar} {goal_ratio:.1f}%")
            print(f"Base Achievement: {base_bar} {time_ratio:.1f}%")
            
            # Alert summary
            total_alerts = stats['total_alerts']
            high_alerts = stats.get('high_alerts', 0)
            dip_count = stats.get('dip_count', 0)
            
            print(f"Session Feedback: {total_alerts} low alerts, {high_alerts} high alerts, {dip_count} dips")
            
        self.print_separator()
        
    def create_progress_bar(self, percentage, width=20):
        """Create a simple text progress bar"""
        filled = int((percentage / 100.0) * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
        
    def print_progress_analysis(self, analysis_text):
        """Print progress analysis"""
        print("\n[ Progress Analysis ]")
        print(analysis_text)
        self.print_separator()
        
    def get_user_input(self, prompt="Enter command"):
        """Get user input with prompt"""
        return input(f"{prompt}: ").strip().lower()
        
    def print_error(self, message):
        """Print error message"""
        print(f"ERROR: {message}")
        
    def print_warning(self, message):
        """Print warning message"""
        print(f"WARNING: {message}")
        
    def print_success(self, message):
        """Print success message"""
        print(f"SUCCESS: {message}")
        
    def print_info(self, message):
        """Print info message"""
        print(f"INFO: {message}")
        
    def wait_for_enter(self, message="Press Enter to continue..."):
        """Wait for user to press Enter"""
        input(message)
        
    def print_audio_analysis_results(self, analysis_result):
        """Print comprehensive audio analysis results"""
        self.clear_screen()
        print("[ Audio Analysis Results ]")
        self.print_separator()
        
        # File information
        file_info = analysis_result.get('file_info', {})
        print(f"File: {file_info.get('file_name', 'Unknown')}")
        print(f"Duration: {file_info.get('duration_seconds', 0):.1f} seconds")
        print(f"Size: {file_info.get('file_size_mb', 0):.1f} MB")
        print()
        
        # Pitch analysis
        pitch_analysis = analysis_result.get('pitch_analysis', {})
        if pitch_analysis.get('mean_pitch', 0) > 0:
            print("[ Pitch Analysis ]")
            print(f"  Average Pitch:     {pitch_analysis.get('mean_pitch', 0):.1f} Hz")
            print(f"  Median Pitch:      {pitch_analysis.get('median_pitch', 0):.1f} Hz")
            print(f"  Pitch Range:       {pitch_analysis.get('min_pitch', 0):.1f} - {pitch_analysis.get('max_pitch', 0):.1f} Hz")
            print(f"  Pitch Stability:   {pitch_analysis.get('pitch_stability', 0):.1%}")
            print(f"  Voice Clarity:     {pitch_analysis.get('voiced_percentage', 0):.1f}%")
        else:
            print("[ Pitch Analysis ]")
            print("  No clear pitch detected in this audio file")
        print()
        
        # Summary and recommendations
        summary = analysis_result.get('summary', {})
        if summary:
            print("[ Assessment & Recommendations ]")
            print(f"  Overall Score:     {summary.get('overall_score', 0):.1f}/1.0")
            print(f"  Assessment:        {summary.get('pitch_assessment', 'N/A')}")
            print(f"  Recommendation:    {summary.get('goal_suggestion', 'N/A')}")
            
            if summary.get('recommended_target_low', 0) > 0:
                print(f"  Suggested Range:   {summary.get('recommended_target_low', 0)} - {summary.get('recommended_target_high', 0)} Hz")
        print()
        
        # Spectral features
        spectral = analysis_result.get('spectral_analysis', {})
        if spectral.get('formant_f1_estimate', 0) > 0:
            print("[ Voice Quality Features ]")
            print(f"  Formant F1:        {spectral.get('formant_f1_estimate', 0):.0f} Hz")
            print(f"  Formant F2:        {spectral.get('formant_f2_estimate', 0):.0f} Hz")
            if spectral.get('f2_f1_ratio', 0) > 0:
                print(f"  F2/F1 Ratio:       {spectral.get('f2_f1_ratio', 0):.2f}")
        
        self.print_separator()
        
    def print_analysis_history(self, history_summary):
        """Print analysis history summary"""
        self.clear_screen()
        print("[ Analysis History ]")
        self.print_separator()
        
        if history_summary.get('count', 0) == 0:
            print("No previous audio analyses found.")
            print("Upload and analyze an audio file to see your voice characteristics!")
        else:
            print(f"Total Analyses: {history_summary.get('count', 0)}")
            print(f"Valid Analyses: {history_summary.get('valid_analyses', 0)}")
            
            pitch_range = history_summary.get('pitch_range', {})
            if pitch_range:
                print()
                print("[ Pitch Summary ]")
                print(f"  Lowest Pitch:      {pitch_range.get('lowest', 0):.1f} Hz")
                print(f"  Highest Pitch:     {pitch_range.get('highest', 0):.1f} Hz")
                print(f"  Average Pitch:     {pitch_range.get('average', 0):.1f} Hz")
                print(f"  Latest Pitch:      {pitch_range.get('latest', 0):.1f} Hz")
                
            recent_files = history_summary.get('recent_files', [])
            if recent_files:
                print()
                print("[ Recent Files ]")
                for i, filename in enumerate(recent_files, 1):
                    print(f"  {i}. {filename}")
        
        print()
        self.print_separator()
        
    def print_file_browser_help(self):
        """Print file browser help text"""
        print("\n[ File Selection Help ]")
        print("Supported formats: .wav, .mp3, .flac, .ogg, .m4a, .aac")
        print("Tips:")
        print("  • Use clear speech recordings for best results")
        print("  • Recordings should be at least 3-5 seconds long")
        print("  • Avoid background music or noise")
        print("  • Speaking or singing works equally well")
        print()
        
    def get_file_path_input(self, prompt="Enter full path to audio file"):
        """Get file path input from user"""
        self.print_file_browser_help()
        return input(f"{prompt}: ").strip().strip('"\'')
        
    def confirm_goal_setting(self, current_goal, new_low, new_high):
        """Confirm setting new training goal"""
        print(f"\n[ Goal Setting Confirmation ]")
        print(f"Current training goal: {current_goal} Hz")
        print(f"Recommended new range: {new_low} - {new_high} Hz")
        print()
        response = input("Set this as your new training goal? (y/n): ").strip().lower()
        return response in ['y', 'yes']
        
    def print_training_status(self, pitch, goal_hz, dip_info=None, resonance_quality=None, 
                            exercise_info=None, formant_info=None, config=None):
        """Print natural, human-friendly training status with smoothed display"""
        # Get display preferences from config
        smooth_enabled = config.get('smooth_display_enabled', True) if config else True
        range_size = config.get('display_range_size', 10) if config else 10
        exact_mode = config.get('exact_numbers_mode', False) if config else False
        
        # Display format based on settings
        if exact_mode or not smooth_enabled:
            # Traditional exact display
            status = f"{pitch:.1f} Hz"
        else:
            # Smoothed range display
            range_start = int(pitch // range_size) * range_size
            range_end = range_start + range_size
            status = f"{range_start}-{range_end} Hz"
            
            # Show trend within range for more context
            position_in_range = ((pitch - range_start) / range_size) * 100
            if position_in_range < 25:
                trend = " (lower)"
            elif position_in_range > 75:
                trend = " (higher)"
            else:
                trend = " (mid)"
            status += trend
        
        # Simple goal feedback
        if pitch >= goal_hz:
            status += " - Good!"
            if dip_info and dip_info.get('recovered'):
                status += " (back on track)"
        elif pitch >= goal_hz * 0.85:  # Close to target
            status += " - Almost there"
        else:
            if exact_mode or not smooth_enabled:
                status += f" - Target: {goal_hz:.0f} Hz"
            else:
                target_range_start = int(goal_hz // range_size) * range_size
                target_range_end = target_range_start + range_size
                status += f" - Target: {target_range_start}-{target_range_end} Hz"
        
        # Alert warning system
        alert_warning = self._get_alert_warning(pitch, goal_hz, dip_info, config)
        if alert_warning:
            status += f" | {alert_warning}"
        
        # Only show dip info when actively in a dip
        elif dip_info and dip_info.get('in_dip'):
            remaining = dip_info.get('remaining_tolerance', 0)
            if remaining > 1:
                status += f" (dip: {remaining:.0f}s left)"
            else:
                status += " (dip ending soon)"
        
        # Exercise progress (only when active)
        if exercise_info:
            remaining = exercise_info.get('remaining_time', 0)
            if remaining > 0:
                mins, secs = divmod(int(remaining), 60)
                if mins > 0:
                    status += f" | Exercise: {mins}:{secs:02d}"
                else:
                    status += f" | Exercise: {secs}s"
                
        self.print_status_line(status)
    
    def _get_alert_warning(self, pitch, goal_hz, dip_info, config):
        """Generate predictive alert warnings"""
        if not config:
            return None
            
        alert_warning_time = config.get('alert_warning_time', 5.0)
        
        # Check if we're approaching a dip alert
        if dip_info and dip_info.get('in_dip'):
            remaining = dip_info.get('remaining_tolerance', 0)
            if remaining <= alert_warning_time and remaining > 0:
                return f"⚠️ Alert in {remaining:.0f}s"
        
        # Check if we're getting close to dip territory
        elif pitch < goal_hz and pitch < goal_hz * 0.9:
            return "⚠️ Getting low"
            
        return None


class MenuSystem:
    """Handle menu navigation and user input with keyboard navigation support"""
    
    def __init__(self, ui):
        self.ui = ui
        self.current_menu = 'main'
        self.keyboard_nav_enabled = KEYBOARD_SUPPORT
        self.selected_option = 0
        
    def _get_navigation_input(self, valid_options):
        """Enhanced input with keyboard navigation support"""
        if not self.keyboard_nav_enabled:
            print("\n[Type your choice and press Enter, or 'h' for help]")
            user_input = input("Choice: ").strip().lower()
            if user_input == 'h':
                self._show_keyboard_help()
                return self._get_navigation_input(valid_options)
            return user_input
        
        # Initialize selected option if needed
        if self.selected_option >= len(valid_options):
            self.selected_option = 0
            
        print(f"\n[Navigation: ↑↓ arrow keys to move, Enter to select, or type option directly]")
        print(f"[Current selection: {valid_options[self.selected_option]}]")
        
        # Check if we have multi-character options
        has_multi_char = any(len(opt) > 1 and opt not in ['up', 'down', 'enter', 'escape'] for opt in valid_options)
        if has_multi_char:
            print("[You can type full commands like 'start', 'clear', 'save']")
        
        while True:
            print("Use arrow keys to navigate, Enter to select, or type option: ", end="", flush=True)
            key = get_key()
            
            if key == 'up':
                self.selected_option = (self.selected_option - 1) % len(valid_options)
                print(f"\r[Selected: {valid_options[self.selected_option]}]" + " " * 40, end="", flush=True)
            elif key == 'down':
                self.selected_option = (self.selected_option + 1) % len(valid_options)
                print(f"\r[Selected: {valid_options[self.selected_option]}]" + " " * 40, end="", flush=True)
            elif key == 'enter':
                print()  # New line
                return valid_options[self.selected_option]
            elif key == 'h':
                print()  # New line
                self._show_keyboard_help()
                print(f"[Current selection: {valid_options[self.selected_option]}]")
            elif key and key in valid_options:
                # Accept both single character and multi-character options
                print()  # New line
                return key
            elif key and len(key) == 1:
                # If it's a single character, try to start typing mode
                print()  # New line
                print(f"Type command (starting with '{key}'): {key}", end="")
                rest_of_input = input().strip().lower()
                full_input = key + rest_of_input
                if full_input in valid_options:
                    return full_input
                else:
                    print(f"Invalid option '{full_input}'. Valid choices: {', '.join(valid_options)}")
                    print(f"[Current selection: {valid_options[self.selected_option]}]")
            elif key == 'escape' or key == 'q':
                print()  # New line
                return 'q' if 'q' in valid_options else '0'
        
    def _show_keyboard_help(self):
        """Show keyboard navigation help"""
        print("\n[ Keyboard Navigation Help ]")
        if self.keyboard_nav_enabled:
            print("• Use ↑↓ arrow keys to navigate between options")
            print("• Press Enter to select the highlighted option")
            print("• Or type commands directly (e.g., '1', 'start', 'clear', 'save')")
            print("• Use 'h' anytime for this help")
            print("• Use 'q' to quit or '0' to go back in most menus")
            print("• Press Escape to quit current menu")
        else:
            print("• Type the number/letter of your choice (e.g., '1', '2', 'q')")
            print("• Press Enter after typing your selection")
            print("• Use 'h' anytime for this help")
            print("• Use 'q' to quit or '0' to go back in most menus")
            print("• All options are accessible via keyboard")
        input("\nPress Enter to continue...")
        
    def show_main_menu(self):
        """Show redesigned, beginner-friendly main menu"""
        self.ui.print_header()
        
        options = {
            '1': 'Live Voice Training',
            '2': 'Voice Exercises & Warm-ups', 
            '3': 'Audio File Pitch Analysis',
            '4': 'Progress & Statistics',
            '5': 'Settings & Configuration',
            'q': 'Quit Application'
        }
        
        valid_options = ['1', '2', '3', '4', '5', 'q']
        description = "New to voice training? Start with Settings to set your voice goals!"
        
        if self.keyboard_nav_enabled and hasattr(self, 'selected_option'):
            selected_key = valid_options[self.selected_option] if self.selected_option < len(valid_options) else None
            self.ui.print_menu_with_highlight("Main Menu", options, description, selected_key)
        else:
            self.ui.print_menu("Main Menu", options, description)
        
        return self._get_navigation_input(valid_options)
        
    def show_main_menu_with_streak(self, streak_info=None):
        """Show main menu with optional streak motivation"""
        self.ui.print_header()
        
        # Add streak motivation if available
        if streak_info and streak_info.get('current_streak', 0) > 0:
            current_streak = streak_info['current_streak']
            print(f"🔥 Current Streak: {current_streak} day{'s' if current_streak != 1 else ''}!")
            
            if current_streak >= 7:
                print("🎉 Amazing dedication! You're on fire!")
            elif current_streak >= 3:
                print("⭐ Great consistency! Keep it up!")
            elif current_streak >= 1:
                print("🌱 Good start! Build that streak!")
            print()
        
        options = {
            '1': 'Live Voice Training',
            '2': 'Voice Exercises & Warm-ups', 
            '3': 'Audio File Pitch Analysis',
            '4': 'Progress & Statistics',
            '5': 'Settings & Configuration',
            'q': 'Quit Application'
        }
        
        valid_options = ['1', '2', '3', '4', '5', 'q']
        
        # Customize description based on streak
        if streak_info and streak_info.get('current_streak', 0) > 0:
            description = f"Keep your {streak_info['current_streak']}-day streak alive with training!"
        else:
            description = "New to voice training? Start with Settings to set your voice goals!"
        
        if self.keyboard_nav_enabled and hasattr(self, 'selected_option'):
            selected_key = valid_options[self.selected_option] if self.selected_option < len(valid_options) else None
            self.ui.print_menu_with_highlight("Main Menu", options, description, selected_key)
        else:
            self.ui.print_menu("Main Menu", options, description)
        
        return self._get_navigation_input(valid_options)
        
    def show_exercise_menu(self, exercises):
        """Show redesigned exercise menu with better descriptions"""
        self.ui.print_header()
        
        print("🏋️ Build your voice skills with targeted exercises\n")
        
        options = {}
        exercise_descriptions = {
            'humming_warmup': 'Gentle warm-up to prepare your voice',
            'lip_trills': 'Relaxing lip exercises for smooth pitch control',
            'pitch_slides': 'Practice moving between different pitches',
            'straw_phonation': 'Efficient voice production technique',
            'resonance_shift': 'Learn to place your voice in the right spot',
            'breathing_control': 'Foundation breathing for voice control'
        }
        
        for i, (key, exercise) in enumerate(exercises.items(), 1):
            desc = exercise_descriptions.get(key, exercise['name'])
            options[str(i)] = f"{exercise['name']} - {desc} ({exercise['duration']}s)"
            
        options['w'] = 'Complete 5-Minute Warm-up Routine (Recommended for beginners!)'
        options['0'] = 'Back to Main Menu'
        
        description = "New to exercises? Try the Warm-up Routine first!"
        self.ui.print_menu("Voice Exercises & Training", options, description)
        
        valid_options = [str(i) for i in range(1, len(exercises)+1)] + ['w', '0']
        return self._get_navigation_input(valid_options)
        
    def show_training_menu(self):
        """Show live training menu"""
        self.ui.print_header()
        
        options = {
            'start': 'Start Training Session',
            'quick': 'Quick Settings',
            '0': 'Back to Main Menu'
        }
        
        description = "Live voice training with real-time feedback"
        self.ui.print_menu("Voice Training", options, description)
        
        return self._get_navigation_input(['start', 'quick', '0'])
        
    def show_settings_menu(self):
        """Show simplified settings menu"""
        self.ui.print_header()
        
        options = {
            '1': 'Voice Goals & Presets',
            '2': 'Target Pitch Settings', 
            '3': 'Microphone & Audio',
            '4': 'Alert Preferences',
            '5': 'Advanced Options',
            '6': 'Voice Safety & Wellness',
            'save': 'Save Configuration',
            'clear': 'Clear Account Data',
            '0': 'Back to Main Menu'
        }
        
        self.ui.print_menu("Settings", options, "Configure your voice training experience")
        
        return self._get_navigation_input(['1', '2', '3', '4', '5', '6', 'save', 'clear', '0'])
        
    def show_technical_settings_menu(self):
        """Show technical settings menu"""
        self.ui.print_header()
        
        options = {
            'n': 'Noise & Audio Settings',
            'a': 'Alert Configuration',
            'd': 'Dip Tolerance Settings',
            'h': 'High Pitch Alert Threshold',
            'u': 'UI Display Settings (Smooth/Exact mode)',
            'reset': 'Reset All Settings to Defaults',
            '0': 'Back to Settings Menu'
        }
        
        self.ui.print_menu("Technical Settings", options, "Fine-tune audio processing and alerts")
        
        return self._get_navigation_input(['n', 'a', 'd', 'h', 'u', 'reset', '0'])
        
    def show_progress_menu(self):
        """Show progress and statistics menu"""
        self.ui.print_header()
        
        options = {
            '1': 'Progress Overview',
            '2': 'Recent Training Sessions',
            '3': 'Achievements & Milestones',
            '4': 'Current Session Stats',
            '0': 'Back to Main Menu'
        }
        
        self.ui.print_menu("Progress & Statistics", options)
        
        return self._get_navigation_input(['1', '2', '3', '4', '0'])
        
    def show_preset_menu(self, presets):
        """Show voice preset selection menu"""
        self.ui.print_header()
        
        options = {
            '1': 'MTF - Feminine voice training',
            '2': 'FTM - Masculine voice development', 
            '3': 'Non-Binary (Higher) - Androgynous with elevation',
            '4': 'Non-Binary (Lower) - Androgynous with deepening',
            '5': 'Non-Binary (Neutral) - Maintain range with control',
            '6': 'Custom - Manual configuration',
            '0': 'Back to Settings'
        }
        
        self.ui.print_menu("Voice Presets", options, "Select a preset that matches your vocal goals")
        
        return self._get_navigation_input(['1', '2', '3', '4', '5', '6', '0'])

    def show_audio_analysis_menu(self):
        """Show audio file analysis menu"""
        self.ui.print_header()
        
        options = {
            '1': 'Analyze Audio File - Upload and analyze pitch/Hz',
            '2': 'View Analysis History - See previous analyses', 
            '3': 'Set Goal from Analysis - Use analysis results as training target',
            '4': 'Analysis Summary - Overview of your voice characteristics',
            '0': 'Back to Main Menu'
        }
        
        description = "Upload audio clips to analyze pitch and set training goals"
        self.ui.print_menu("Audio File Pitch Analysis", options, description)
        
        return self._get_navigation_input(['1', '2', '3', '4', '0'])

    def show_training_controls(self):
        """Show simplified training session controls"""
        print("\n[ Training Controls ]")
        print("  q      - Stop training")
        print("  stats  - Show session stats")
        print("  pause  - Pause/resume")
        print("  save   - Save progress")
        self.ui.print_separator()


