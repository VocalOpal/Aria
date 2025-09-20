"""
Menu Coordinator - Handles all menu navigation and user interactions
Extracted from voice_trainer.py lines 826-903, 999-1696 (menu handling)
"""

from typing import Dict, Any, Optional, Callable
from .achievement_system import VoiceAchievementSystem


class VoiceMenuCoordinator:
    """Coordinates menu navigation and user interactions"""
    
    def __init__(self):
        # Components (will be injected)
        self.ui = None
        self.menu_system = None
        self.config_manager = None
        self.session_manager = None
        self.training_controller = None
        self.audio_coordinator = None
        self.safety_coordinator = None
        
        # Achievement system
        self.achievement_system = VoiceAchievementSystem()
    
    def set_dependencies(self, ui, menu_system, config_manager, session_manager, 
                        training_controller, audio_coordinator, safety_coordinator):
        """Inject dependencies"""
        self.ui = ui
        self.menu_system = menu_system
        self.config_manager = config_manager
        self.session_manager = session_manager
        self.training_controller = training_controller
        self.audio_coordinator = audio_coordinator
        self.safety_coordinator = safety_coordinator
    
    def show_main_menu_loop(self) -> str:
        """Main menu navigation loop"""
        if not self._validate_dependencies():
            return 'error'
        
        while True:
            # Get streak information for motivation
            streak_info = None
            if self.session_manager and self.session_manager.weekly_sessions:
                streak_info = self.achievement_system.calculate_streaks(self.session_manager.weekly_sessions)
            
            # Show main menu with streak motivation
            if hasattr(self.menu_system, 'show_main_menu_with_streak') and streak_info:
                choice = self.menu_system.show_main_menu_with_streak(streak_info)
            else:
                choice = self.menu_system.show_main_menu()
            
            if choice == 'q':
                return 'quit'
            elif choice == '1':
                # Live voice training
                if self._handle_training_menu():
                    continue
            elif choice == '2':
                # Voice exercises
                self._handle_exercise_menu()
            elif choice == '3':
                # Audio File Pitch Analysis
                if self.audio_coordinator:
                    self.audio_coordinator.show_audio_analysis_menu(self.menu_system)
            elif choice == '4':
                # Progress & Statistics
                self._handle_progress_menu()
            elif choice == '5':
                # Settings & Configuration
                self._handle_settings_menu()
    
    def _handle_training_menu(self) -> bool:
        """Handle live training menu"""
        training_choice = self.menu_system.show_training_menu()
        
        if training_choice == 'start':
            return self._start_live_training()
        elif training_choice == 'quick':
            self._show_quick_settings_menu()
            return False
        
        return False
    
    def _start_live_training(self) -> bool:
        """Start live training session with UI callbacks"""
        if not self.training_controller or not self.config_manager:
            self.ui.print_error("Training system not available")
            return False
        
        self.ui.clear_screen()
        print("[ Live Voice Training ]")
        print("Initializing audio system...")
        
        # Get current configuration
        config = self.config_manager.get_config()
        
        # Create UI callback handler
        def ui_callback(callback_type: str, data: Dict[str, Any]):
            self._handle_training_ui_callback(callback_type, data)
        
        # Start training
        if not self.training_controller.start_live_training(config, ui_callback):
            self.ui.print_error("Failed to initialize audio system")
            self.ui.wait_for_enter()
            return False
        
        # Show training instructions
        self._show_training_instructions(config)
        
        # Training loop
        try:
            while self.training_controller.is_training_active:
                print("\n[Type command: q=quit, stats=statistics, pause=toggle pause, save=save progress]")
                user_input = input("Command: ").strip().lower()
                
                if user_input == 'q':
                    break
                elif user_input == 'stats':
                    self._show_current_session_stats()
                elif user_input == 'pause':
                    is_paused = self.training_controller.pause_resume_training()
                    status = "paused" if is_paused else "resumed"
                    print(f"\nTraining {status}")
                elif user_input == 'save':
                    if self.session_manager:
                        self.session_manager.save_session_data()
                    print("Progress saved")
                elif user_input == 'help' or user_input == 'h':
                    self._show_training_help()
                elif user_input == '':
                    continue  # Just continue monitoring if empty input
                    
        except (KeyboardInterrupt, EOFError):
            pass
        
        # Stop training and show results
        results = self.training_controller.stop_live_training()
        self._show_training_results(results)
        
        return True
    
    def _handle_training_ui_callback(self, callback_type: str, data: Dict[str, Any]):
        """Handle UI callbacks from training controller"""
        if callback_type == 'noise_feedback':
            message = data.get('message', '')
            print(f"\r{message}", end="", flush=True)
        
        elif callback_type == 'status_update':
            message = data.get('message', '')
            if 'paused' in message.lower():
                print(f"\r[Background noise only - timer paused] Waiting for voice...", end="", flush=True)
            elif 'resumed' in message.lower():
                print(f"\r[Voice detected - timer resumed]                              ", end="", flush=True)
        
        elif callback_type == 'training_status':
            if self.ui and self.config_manager:
                config = self.config_manager.get_config()
                self.ui.print_training_status(
                    pitch=data.get('pitch', 0),
                    goal_hz=data.get('goal_hz', 165),
                    dip_info=data.get('dip_info'),
                    resonance_quality=data.get('resonance_quality', 0.5),
                    exercise_info=data.get('exercise_info'),
                    formant_info=data.get('formant_info'),
                    config=config
                )
        
        elif callback_type == 'safety_warning':
            if self.safety_coordinator:
                self.safety_coordinator.handle_safety_warning(data)
        
        elif callback_type == 'exercise_complete':
            print("\nExercise completed!")
    
    def _show_training_help(self):
        """Show available commands during training"""
        print("\n=== Live Training Commands ===")
        print("q        - Quit training session")
        print("stats    - Show current session statistics")
        print("pause    - Pause/resume training")
        print("save     - Save current progress")
        print("help, h  - Show this help")
        print("(Empty)  - Continue monitoring")
        print("==============================")
    
    def _show_training_instructions(self, config: Dict[str, Any]):
        """Show training session instructions"""
        recommended_duration = self.config_manager.get_recommended_session_duration(self.session_manager)
        current_goal = config.get('current_goal', 165)
        dip_tolerance = config.get('dip_tolerance_duration', 5.0)
        high_pitch_threshold = config.get('high_pitch_threshold', 400)
        
        print("\n=== Getting Ready ===")
        print("Step 1: Please stay quiet for background noise detection")
        print("Step 2: The system will learn your environment (8 seconds)")  
        print("Step 3: Begin speaking when prompted")
        print(f"\n🎯 Your goal: {current_goal} Hz (small steps toward your target range)")
        print(f"⏰ Dip tolerance: {dip_tolerance}s (allows natural variation)")
        print(f"🔔 High pitch alert: {high_pitch_threshold} Hz (for head voice awareness)")
        print(f"⏱️  Recommended session: {recommended_duration} minutes")
        print("💭 Remember: Everyone progresses at their own pace - be patient with yourself!")
        print("\nStarting background noise detection...")
        print()
        self.menu_system.show_training_controls()
    
    def _show_current_session_stats(self):
        """Show current session statistics"""
        if self.session_manager and self.ui:
            summary = self.session_manager.get_session_summary()
            if summary:
                config = self.config_manager.get_config()
                current_goal = config.get('current_goal', 165)
                base_goal = config.get('base_goal', 165)
                
                print("\n")
                self.ui.print_session_stats(
                    summary['stats'], 
                    current_goal, 
                    base_goal, 
                    summary.get('noise_pause_seconds', 0)
                )
                self.menu_system.show_training_controls()
    
    def _show_training_results(self, results: Dict[str, Any]):
        """Show training session results with achievement notifications"""
        session_duration = results.get('session_duration', 0)
        summary = results.get('summary')
        
        # Check for new achievements if session was saved
        if self.session_manager and self.session_manager.weekly_sessions:
            # Calculate how many achievements were earned before this session
            pre_session_count = len(self.session_manager.weekly_sessions) - 1
            previous_earned_count = 0
            
            if pre_session_count > 0:
                temp_sessions = self.session_manager.weekly_sessions[:pre_session_count]
                temp_achievements = self.achievement_system.get_all_achievements(
                    len(temp_sessions),
                    sum(s.get('duration_minutes', 0) for s in temp_sessions),
                    self.achievement_system.calculate_streaks(temp_sessions),
                    self.achievement_system.calculate_pitch_achievements(temp_sessions),
                    temp_sessions
                )
                previous_earned_count = len([a for a in temp_achievements if a['earned']])
            
            # Check for new achievements
            new_achievements = self.achievement_system.check_for_new_achievements(
                self.session_manager.weekly_sessions, previous_earned_count
            )
        else:
            new_achievements = []
        
        if summary:
            config = self.config_manager.get_config()
            current_goal = config.get('current_goal', 165)
            base_goal = config.get('base_goal', 165)
            
            self.ui.print_session_stats(
                summary['stats'], 
                current_goal, 
                base_goal, 
                summary.get('noise_pause_seconds', 0)
            )
        
        # Show achievement notifications if any were earned
        if new_achievements:
            if len(new_achievements) == 1:
                self.achievement_system.show_achievement_notification(new_achievements[0])
            else:
                self.achievement_system.show_milestone_celebration(new_achievements)
            
            # Pause to let user appreciate the achievement
            input("\nPress Enter to continue...")
        
        # Show safety summary for longer sessions
        if session_duration > 5 and self.safety_coordinator:
            self.safety_coordinator.show_safety_summary(session_duration)
        
        self.ui.wait_for_enter()
    
    def _handle_exercise_menu(self):
        """Handle exercise menu navigation"""
        from voice_exercises import VoiceExercises
        exercises_component = VoiceExercises()
        
        while True:
            exercises = exercises_component.get_all_exercises()
            choice = self.menu_system.show_exercise_menu(exercises)
            
            if choice == '0':
                break
            elif choice == 'w':
                self._run_warmup_routine(exercises_component)
            elif choice == 'b':
                self._run_single_exercise('breathing_control', exercises_component)
            else:
                # Try to match exercise by number
                try:
                    exercise_num = int(choice) - 1
                    exercise_keys = list(exercises.keys())
                    if 0 <= exercise_num < len(exercise_keys):
                        exercise_name = exercise_keys[exercise_num]
                        self._run_single_exercise(exercise_name, exercises_component)
                except ValueError:
                    self.ui.print_error("Invalid selection")
                    self.ui.wait_for_enter()
    
    def _run_single_exercise(self, exercise_name: str, exercises_component):
        """Run a single exercise"""
        exercise_data = exercises_component.get_exercise(exercise_name)
        if not exercise_data:
            self.ui.print_error(f"Exercise '{exercise_name}' not found")
            return
        
        self.ui.clear_screen()
        print("[ Voice Exercise Session ]")
        self.ui.print_exercise_info(exercise_data)
        
        self.ui.wait_for_enter("Press Enter to begin exercise...")
        
        # Create UI callback for exercise
        def ui_callback(callback_type: str, data: Dict[str, Any]):
            self._handle_training_ui_callback(callback_type, data)
        
        # Start exercise
        if self.training_controller.start_exercise(exercise_name, exercise_data, ui_callback):
            print("Exercise started! Follow the instructions and maintain target pitch range.")
            print("Press 'q' to stop early, or wait for automatic completion.")
            print()
            
            # Exercise loop
            try:
                while (self.training_controller.current_exercise and 
                       self.training_controller.current_exercise.is_active and 
                       not self.training_controller.current_exercise.is_complete()):
                    user_input = input().strip().lower()
                    if user_input == 'q':
                        break
                        
            except (KeyboardInterrupt, EOFError):
                pass
            
            # Stop exercise and show results
            completion_rate = self.training_controller.stop_exercise()
            
            print(f"\nExercise session completed! ({completion_rate*100:.0f}% finished)")
            
            if self.session_manager:
                summary = self.session_manager.get_session_summary()
                if summary and self.ui:
                    config = self.config_manager.get_config()
                    self.ui.print_session_stats(summary['stats'], 
                                               config.get('current_goal', 165), 
                                               config.get('base_goal', 165))
        
        self.ui.wait_for_enter()
    
    def _run_warmup_routine(self, exercises_component):
        """Run complete warm-up routine"""
        self.ui.clear_screen()
        print("[ 5-Minute Vocal Warm-up Routine ]")
        
        sequence = exercises_component.get_warmup_sequence()
        print("This routine will guide you through essential exercises.")
        print(f"Total exercises: {len(sequence)}")
        print()
        
        self.ui.wait_for_enter("Press Enter to begin warm-up routine...")
        
        # Run warmup via training controller
        def ui_callback(callback_type: str, data: Dict[str, Any]):
            if callback_type == 'show_exercise':
                step = data.get('step', 1)
                total = data.get('total', len(sequence))
                exercise = data.get('exercise', {})
                
                self.ui.clear_screen()
                print(f"[ Warm-up Step {step}/{total} ]")
                self.ui.print_exercise_info(exercise)
                self.ui.wait_for_enter(f"Press Enter to start exercise {step}...")
            else:
                self._handle_training_ui_callback(callback_type, data)
        
        # Use training controller for warmup
        if hasattr(self.training_controller, 'run_warmup_routine'):
            self.training_controller.run_warmup_routine(exercises_component, ui_callback)
        
        self.ui.clear_screen()
        print("Warm-up routine completed!")
        print("Your voice is now ready for training sessions.")
        self.ui.wait_for_enter()
    
    def _handle_progress_menu(self):
        """Handle progress and statistics menu"""
        while True:
            choice = self.menu_system.show_progress_menu()
            
            if choice == '0':
                break
            elif choice == '1':
                self._show_progress_trends()
            elif choice == '2':
                self._show_training_history()
            elif choice == '3':
                self._show_achievements()
            elif choice == '4':
                self._show_current_session_stats()
    
    def _show_progress_trends(self):
        """Show progress trend analysis"""
        if not self.session_manager:
            self.ui.print_info("Session manager not available")
            self.ui.wait_for_enter()
            return
        
        trends = self.session_manager.get_progress_trends()
        
        if trends.get('status') == 'insufficient_data':
            self.ui.print_info(trends.get('message', 'Not enough data'))
            self.ui.wait_for_enter()
            return
        
        # Build analysis text
        analysis = f"Recent Average: {trends['recent_average']:.1f} Hz\n"
        analysis += f"Total Sessions: {trends['total_sessions']}\n"
        
        if 'older_average' in trends:
            improvement = trends['improvement_hz']
            analysis += f"Previous Average: {trends['older_average']:.1f} Hz\n"
            
            if improvement > 2:
                analysis += f"Great improvement! (+{improvement:.1f} Hz)\n"
            elif improvement > 0:
                analysis += f"Steady progress (+{improvement:.1f} Hz)\n"
            elif improvement > -2:
                analysis += f"Maintaining level ({improvement:.1f} Hz)\n"
            else:
                analysis += f"Temporary dip ({improvement:.1f} Hz) - Keep practicing!\n"
        
        analysis += f"Weekly Consistency: {trends.get('consistency_percent', 0):.0f}%\n"
        
        # Show suggested next goal if applicable
        if trends['recent_average'] >= self.config_manager.config.get('current_goal', 165) * 0.9:
            next_goal = self.config_manager.config.get('current_goal', 165) + self.config_manager.config.get('goal_increment', 3)
            analysis += f"\nSuggested next goal: {next_goal:.0f} Hz\n"
        
        self.ui.print_progress_analysis(analysis)
        self.ui.wait_for_enter()
    
    def _show_training_history(self):
        """Show recent training history"""
        if not self.session_manager:
            self.ui.print_info("Session manager not available")
            self.ui.wait_for_enter()
            return
        
        history = self.session_manager.get_session_history(10)
        
        if not history:
            self.ui.print_info("No training history available")
            self.ui.wait_for_enter()
            return
        
        self.ui.clear_screen()
        print("[ Training History - Last 10 Sessions ]")
        self.ui.print_separator()
        
        for i, session in enumerate(reversed(history), 1):
            try:
                date = session.get('date', 'Unknown')
                if 'T' in date:  # ISO format
                    from datetime import datetime
                    dt = datetime.fromisoformat(date)
                    date = dt.strftime('%Y-%m-%d %H:%M')
                
                duration = session.get('duration_minutes', 0)
                avg_pitch = session.get('avg_pitch', 0)
                goal = session.get('goal', 0)
                
                print(f"{i:2d}. {date} | {duration:4.1f}min | Avg: {avg_pitch:5.1f}Hz | Goal: {goal:.0f}Hz")
            except Exception:
                print(f"{i:2d}. [Error displaying session data]")
        
        self.ui.print_separator()
        self.ui.wait_for_enter()
    
    def _show_achievements(self):
        """Show achievements, milestones, and streak tracking"""
        if not self.session_manager:
            self.ui.print_info("Session manager not available")
            self.ui.wait_for_enter()
            return
        
        self.ui.clear_screen()
        print("[ Achievements & Milestones ]")
        print("🏆 Your voice training journey:")
        print()
        
        # Use the achievement system to display everything
        self.achievement_system.display_achievements_summary(self.session_manager.weekly_sessions)
        
        self.ui.wait_for_enter()
    
    def _handle_settings_menu(self):
        """Handle settings and configuration menu"""
        while True:
            choice = self.menu_system.show_settings_menu()
            
            if choice == '0':
                break
            elif choice == '1':  # Voice Goals
                self._handle_preset_menu()
            elif choice == '2':  # Target Pitch
                self._adjust_target_pitch()
            elif choice == '3':  # Microphone Settings
                self._adjust_microphone_settings()
            elif choice == '4':  # Alert Preferences
                self._show_alert_preferences()
            elif choice == '5':  # Advanced Options
                self._handle_technical_settings()
            elif choice == '6':  # Voice Safety & Wellness
                if self.safety_coordinator:
                    self.safety_coordinator.show_voice_safety_menu(self.menu_system)
            elif choice == 'save':
                if self.config_manager.save_config():
                    self.ui.print_success("Configuration saved")
                else:
                    self.ui.print_error("Failed to save configuration")
                self.ui.wait_for_enter()
            elif choice == 'clear':
                self._clear_account_data()
    
    def _handle_preset_menu(self):
        """Handle voice preset selection"""
        from voice_presets import VoicePresets
        presets = VoicePresets()
        
        while True:
            choice = self.menu_system.show_preset_menu(presets.get_preset_list())
            
            if choice == '0':
                break
            
            preset_mapping = {
                '1': 'mtf',
                '2': 'ftm', 
                '3': 'nonbinary_higher',
                '4': 'nonbinary_lower',
                '5': 'nonbinary_neutral',
                '6': 'custom'
            }
            
            preset_name = preset_mapping.get(choice)
            if preset_name and preset_name != 'custom':
                if self._show_preset_details_and_confirm(preset_name, presets):
                    break
    
    def _show_preset_details_and_confirm(self, preset_name: str, presets) -> bool:
        """Show preset details and apply if confirmed"""
        preset = presets.get_preset(preset_name)
        if not preset:
            return False
        
        self.ui.clear_screen()
        print(f"[ {preset['name']} ]")
        print("=" * 60)
        print(f"Description: {preset['description']}")
        print(f"Starting frequency: {preset['base_frequency']} Hz")
        print(f"Target frequency: {preset['target_frequency']} Hz")
        print(f"High pitch alert: {preset['high_alert_threshold']} Hz")
        print()
        print("This preset will configure:")
        for tip in preset['tips']:
            print(f"  • {tip}")
        print()
        
        confirm = input("Apply this preset? (y/n): ").strip().lower()
        if confirm in ['y', 'yes']:
            if self.config_manager.apply_preset(preset_name):
                print("\n✅ Preset applied successfully!")
                print("Your settings have been updated. Don't forget to save them!")
                return True
            else:
                print("\n❌ Failed to apply preset.")
        else:
            print("Preset not applied.")
        
        self.ui.wait_for_enter()
        return False
    
    def _adjust_target_pitch(self):
        """Adjust target pitch settings"""
        if self.config_manager:
            current_value = self.config_manager.config.get('current_goal', 165)
            new_value = self.config_manager.adjust_threshold(current_value)
            if new_value != current_value:
                self.ui.print_success(f"Target pitch updated to {new_value} Hz")
        self.ui.wait_for_enter()
    
    def _adjust_microphone_settings(self):
        """Adjust microphone sensitivity"""
        if self.config_manager:
            current_value = self.config_manager.config.get('sensitivity', 1.0)
            new_value = self.config_manager.adjust_sensitivity(current_value)
            if new_value != current_value:
                self.ui.print_success(f"Sensitivity updated to {new_value}")
        self.ui.wait_for_enter()
    
    def _show_alert_preferences(self):
        """Show alert preferences"""
        config = self.config_manager.get_config()
        
        self.ui.clear_screen()
        print("[ Alert Preferences ]")
        print(f"Current high pitch threshold: {config.get('high_pitch_threshold', 400)} Hz")
        print(f"Current dip tolerance: {config.get('dip_tolerance_duration', 5.0)} seconds")
        print()
        print("These settings control when and how often the app beeps to guide you.")
        print("Most users find the default settings work well!")
        self.ui.wait_for_enter("Press Enter to return to settings...")
    
    def _handle_technical_settings(self):
        """Handle technical settings menu"""
        while True:
            choice = self.menu_system.show_technical_settings_menu()
            
            if choice == '0':
                break
            elif choice == 'n':  # Noise settings
                self._show_noise_settings()
            elif choice == 'a':  # Alert settings
                self._show_alert_settings()
            elif choice == 'd':  # Dip tolerance
                self._adjust_dip_tolerance()
            elif choice == 'h':  # High pitch threshold
                self._adjust_high_pitch_threshold()
            elif choice == 'u':  # UI display settings
                self._show_ui_display_settings()
            elif choice == 'reset':
                self._reset_all_settings()
    
    def _show_noise_settings(self):
        """Show noise and audio settings"""
        config = self.config_manager.get_config()
        
        self.ui.clear_screen()
        print("[ Noise & Audio Settings ]")
        print(f"Current noise threshold: {config.get('noise_threshold', 0.02)}")
        print(f"Current VAD threshold: {config.get('vad_threshold', 0.01)}")
        print("\nThese settings control background noise filtering.")
        print("Lower values = more sensitive to quiet sounds")
        print("Higher values = ignore more background noise")
        self.ui.wait_for_enter("Press Enter to return to technical settings...")
    
    def _show_alert_settings(self):
        """Show alert configuration"""
        self.ui.clear_screen()
        print("[ Alert Configuration ]")
        print("Alert settings control the beep sounds.")
        print("Volume and timing are set to work well for voice training.")
        self.ui.wait_for_enter("Press Enter to return to technical settings...")
    
    def _show_ui_display_settings(self):
        """Configure UI display settings"""
        if not self.config_manager:
            return
            
        config = self.config_manager.get_config()
        
        while True:
            self.ui.clear_screen()
            print("[ UI Display Settings ]")
            print("Configure how pitch information is displayed during training\n")
            
            # Current settings
            smooth_enabled = config.get('smooth_display_enabled', True)
            exact_mode = config.get('exact_numbers_mode', False)
            range_size = config.get('display_range_size', 10)
            alert_warning_time = config.get('alert_warning_time', 5.0)
            
            print(f"Current Display Mode: {'Exact Numbers' if exact_mode else 'Smooth Ranges'}")
            print(f"Smooth Display: {'Enabled' if smooth_enabled else 'Disabled'}")
            print(f"Range Size: {range_size} Hz")
            print(f"Alert Warning Time: {alert_warning_time}s")
            
            print("\nPreview Examples:")
            if exact_mode or not smooth_enabled:
                print("  Exact mode: '162.4 Hz - Good!'")
            else:
                print(f"  Range mode: '160-170 Hz (mid) - Good!'")
            
            print("\nOptions:")
            print("1. Toggle display mode (Exact ↔ Smooth)")
            print("2. Adjust range size (5-20 Hz)")
            print("3. Adjust alert warning time (2-10s)")
            print("0. Back to technical settings")
            
            choice = input("\nChoice: ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                if exact_mode:
                    config['exact_numbers_mode'] = False
                    config['smooth_display_enabled'] = True
                    print("Switched to Smooth Range display")
                else:
                    config['exact_numbers_mode'] = True
                    config['smooth_display_enabled'] = False
                    print("Switched to Exact Numbers display")
                self.config_manager.save_config()
                self.ui.wait_for_enter()
            elif choice == '2':
                try:
                    new_size = int(input("Enter range size (5-20 Hz): ").strip())
                    if 5 <= new_size <= 20:
                        config['display_range_size'] = new_size
                        self.config_manager.save_config()
                        print(f"Range size set to {new_size} Hz")
                    else:
                        print("Range size must be between 5-20 Hz")
                except ValueError:
                    print("Please enter a valid number")
                self.ui.wait_for_enter()
            elif choice == '3':
                try:
                    new_time = float(input("Enter warning time (2-10 seconds): ").strip())
                    if 2.0 <= new_time <= 10.0:
                        config['alert_warning_time'] = new_time
                        self.config_manager.save_config()
                        print(f"Alert warning time set to {new_time}s")
                    else:
                        print("Warning time must be between 2-10 seconds")
                except ValueError:
                    print("Please enter a valid number")
                self.ui.wait_for_enter()
    
    def _adjust_dip_tolerance(self):
        """Adjust dip tolerance setting"""
        if self.config_manager:
            current_value = self.config_manager.config.get('dip_tolerance_duration', 5.0)
            new_value = self.config_manager.adjust_dip_tolerance(current_value)
            if new_value != current_value:
                self.ui.print_success(f"Dip tolerance updated to {new_value} seconds")
        self.ui.wait_for_enter()
    
    def _adjust_high_pitch_threshold(self):
        """Adjust high pitch threshold"""
        if self.config_manager:
            current_value = self.config_manager.config.get('high_pitch_threshold', 400)
            new_value = self.config_manager.adjust_high_pitch_threshold(current_value)
            if new_value != current_value:
                self.ui.print_success(f"High pitch threshold updated to {new_value} Hz")
        self.ui.wait_for_enter()
    
    def _reset_all_settings(self):
        """Reset all settings to defaults"""
        self.ui.clear_screen()
        print("[ Reset Settings ]")
        print("This will reset ALL settings to their default values.")
        confirm = input("Are you sure? (y/N): ").strip().lower()
        
        if confirm == 'y':
            if self.config_manager.reset_to_defaults():
                self.ui.print_success("Settings reset to defaults")
            else:
                self.ui.print_error("Failed to reset settings")
        else:
            print("Reset cancelled.")
        
        self.ui.wait_for_enter()
    
    def _show_quick_settings_menu(self):
        """Show quick settings during training"""
        print("\n[ Quick Settings ]")
        print("  t - Adjust threshold")
        print("  s - Adjust sensitivity") 
        print("  d - Adjust dip tolerance")
        print("Press Enter to continue training...")
        
        choice = input("Setting: ").strip().lower()
        
        if choice == 't':
            self._adjust_target_pitch()
        elif choice == 's':
            self._adjust_microphone_settings()
        elif choice == 'd':
            self._adjust_dip_tolerance()
    
    def _clear_account_data(self):
        """Clear all user account data with multiple warnings"""
        self.ui.clear_screen()
        print("⚠️  [ CLEAR ACCOUNT DATA ] ⚠️ ")
        print("=" * 60)
        print("This will permanently delete ALL of your voice training data:")
        print()
        print("❌ Your training history and progress statistics")
        print("❌ Your personal voice goals and settings") 
        print("❌ Your session records and achievements")
        print("❌ Your preset configurations")
        print()
        print("🚨 THIS CANNOT BE UNDONE! 🚨")
        print()
        
        # First confirmation
        confirm1 = input("Are you absolutely sure you want to delete everything? (type 'YES' to continue): ").strip()
        if confirm1 != 'YES':
            print("Account data NOT deleted. Returning to settings.")
            self.ui.wait_for_enter()
            return
        
        print()
        print("Final warning: You will lose ALL progress and have to start over!")
        print()
        
        # Second confirmation
        confirm2 = input("Type 'DELETE ALL MY DATA' to permanently clear your account: ").strip()
        if confirm2 != 'DELETE ALL MY DATA':
            print("Account data NOT deleted. Returning to settings.")
            self.ui.wait_for_enter()
            return
        
        # Actually clear the data
        success = True
        
        if self.config_manager:
            success &= self.config_manager.clear_all_data()
        
        if self.session_manager:
            success &= self.session_manager.clear_all_data()
        
        if success:
            print()
            print("✅ Account data has been permanently deleted.")
            print("You can now set up your voice training goals from scratch.")
            print()
            print("Returning to main menu...")
        else:
            print()
            print("⚠️ Some data may not have been completely cleared.")
            print("You may need to manually delete remaining files.")
        
        self.ui.wait_for_enter()
    
    def _validate_dependencies(self) -> bool:
        """Validate that required dependencies are available"""
        required = [self.ui, self.menu_system, self.config_manager]
        return all(dep is not None for dep in required)