"""
Audio Coordinator - Manages audio file analysis features
Extracted from voice_trainer.py lines 1260-1453 (audio analysis functionality)
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime


class VoiceAudioAnalyzerCoordinator:
    """Coordinates audio file analysis features"""
    
    def __init__(self, config_file="data/voice_config.json"):
        self.config_file = config_file
        
        # Components (will be injected)
        self.audio_file_analyzer = None
        self.pitch_goal_manager = None
        self.ui = None
        self.config_manager = None
    
    def set_dependencies(self, audio_file_analyzer, pitch_goal_manager, ui, config_manager):
        """Inject dependencies"""
        self.audio_file_analyzer = audio_file_analyzer
        self.pitch_goal_manager = pitch_goal_manager
        self.ui = ui
        self.config_manager = config_manager
    
    def show_audio_analysis_menu(self, menu_system):
        """Handle audio file analysis menu navigation"""
        while True:
            choice = menu_system.show_audio_analysis_menu()
            
            if choice == '0':
                break
            elif choice == '1':
                self.analyze_audio_file()
            elif choice == '2':
                self.view_analysis_history()
            elif choice == '3':
                self.set_goal_from_analysis()
            elif choice == '4':
                self.show_analysis_summary()
    
    def analyze_audio_file(self) -> bool:
        """Analyze an uploaded audio file"""
        if not self._validate_dependencies():
            return False
        
        try:
            # Get file path from user
            file_path = self.ui.get_file_path_input()
            
            if not file_path:
                self.ui.print_warning("No file path provided.")
                self.ui.wait_for_enter()
                return False
            
            # Check if file exists
            if not os.path.exists(file_path):
                self.ui.print_error(f"File not found: {file_path}")
                self.ui.wait_for_enter()
                return False
            
            # Check if file format is supported
            if not self.audio_file_analyzer.is_supported_file(file_path):
                supported_formats = ", ".join(self.audio_file_analyzer.supported_formats)
                self.ui.print_error(f"Unsupported file format. Supported formats: {supported_formats}")
                self.ui.wait_for_enter()
                return False
            
            # Perform analysis
            self.ui.print_info("Analyzing audio file... This may take a moment.")
            
            try:
                analysis_result = self.audio_file_analyzer.full_analysis(file_path)
                
                # Display results
                self.ui.print_audio_analysis_results(analysis_result)
                
                # Save to history
                self.pitch_goal_manager.add_analysis_result(analysis_result)
                
                # Ask if user wants to set this as goal
                summary = analysis_result.get('summary', {})
                if summary.get('recommended_target_low', 0) > 0:
                    print()
                    set_goal = input("Set the recommended target as your training goal? (y/n): ").strip().lower()
                    if set_goal in ['y', 'yes']:
                        low, high = self.pitch_goal_manager.set_goal_from_analysis(analysis_result)
                        if low and high:
                            self.ui.print_success(f"Training goal updated! New target: {low}-{high} Hz")
                            # Reload config to pick up changes
                            if self.config_manager:
                                self.config_manager.load_config()
                
                self.ui.wait_for_enter()
                return True
                
            except Exception as e:
                self.ui.print_error(f"Analysis failed: {e}")
                self.ui.wait_for_enter()
                return False
                
        except Exception as e:
            self.ui.print_error(f"Error: {e}")
            self.ui.wait_for_enter()
            return False
    
    def view_analysis_history(self):
        """View analysis history"""
        if not self._validate_dependencies():
            return
        
        history_summary = self.pitch_goal_manager.get_analysis_history_summary()
        self.ui.print_analysis_history(history_summary)
        self.ui.wait_for_enter()
    
    def set_goal_from_analysis(self) -> bool:
        """Set goal from previous analysis"""
        if not self._validate_dependencies():
            return False
        
        history_summary = self.pitch_goal_manager.get_analysis_history_summary()
        
        if history_summary.get('count', 0) == 0:
            self.ui.print_warning("No previous analyses found. Analyze an audio file first.")
            self.ui.wait_for_enter()
            return False
        
        # Show recent analyses and let user choose
        analyses = self.pitch_goal_manager.analysis_history
        if not analyses:
            self.ui.print_warning("No analysis data available.")
            self.ui.wait_for_enter()
            return False
        
        self.ui.clear_screen()
        print("[ Set Goal from Previous Analysis ]")
        self.ui.print_separator()
        
        # Show last few analyses
        recent_analyses = analyses[-5:] if len(analyses) > 5 else analyses
        for i, analysis in enumerate(recent_analyses, 1):
            file_info = analysis.get('file_info', {})
            pitch_info = analysis.get('pitch_analysis', {})
            summary = analysis.get('summary', {})
            
            filename = file_info.get('file_name', 'Unknown')
            mean_pitch = pitch_info.get('mean_pitch', 0)
            recommended_low = summary.get('recommended_target_low', 0)
            recommended_high = summary.get('recommended_target_high', 0)
            
            print(f"  {i}. {filename}")
            print(f"     Current pitch: {mean_pitch:.1f} Hz")
            print(f"     Recommended: {recommended_low}-{recommended_high} Hz")
            print()
        
        try:
            choice = input(f"Select analysis (1-{len(recent_analyses)}) or 0 to cancel: ").strip()
            
            if choice == '0':
                return False
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(recent_analyses):
                selected_analysis = recent_analyses[choice_idx]
                
                # Confirm and set goal
                summary = selected_analysis.get('summary', {})
                low = summary.get('recommended_target_low', 0)
                high = summary.get('recommended_target_high', 0)
                
                current_goal = self.config_manager.config.get('current_goal', 165) if self.config_manager else 165
                
                if self.ui.confirm_goal_setting(current_goal, low, high):
                    self.pitch_goal_manager.set_goal_from_analysis(selected_analysis)
                    if self.config_manager:
                        self.config_manager.load_config()  # Reload to pick up changes
                    self.ui.print_success(f"Training goal updated to {low}-{high} Hz!")
                    return True
                else:
                    self.ui.print_info("Goal not changed.")
                    return False
            else:
                self.ui.print_error("Invalid selection.")
                
        except (ValueError, IndexError):
            self.ui.print_error("Invalid input.")
        
        self.ui.wait_for_enter()
        return False
    
    def show_analysis_summary(self):
        """Show overall analysis summary"""
        if not self._validate_dependencies():
            return
        
        history_summary = self.pitch_goal_manager.get_analysis_history_summary()
        
        self.ui.clear_screen()
        print("[ Voice Analysis Summary ]")
        self.ui.print_separator()
        
        if history_summary.get('count', 0) == 0:
            print("No audio analyses have been performed yet.")
            print()
            print("Tips for getting started:")
            print("  • Record 5-10 seconds of your natural speaking voice")
            print("  • Use option 1 to analyze the file and get personalized recommendations")
            print("  • Set the recommended pitch range as your training goal")
            print("  • Practice with live training to reach your target range")
        else:
            pitch_range = history_summary.get('pitch_range', {})
            
            print(f"Total voice samples analyzed: {history_summary.get('valid_analyses', 0)}")
            
            if pitch_range:
                print()
                print("Your voice characteristics:")
                print(f"  • Lowest recorded pitch:  {pitch_range.get('lowest', 0):.1f} Hz")
                print(f"  • Highest recorded pitch: {pitch_range.get('highest', 0):.1f} Hz")
                print(f"  • Average pitch:          {pitch_range.get('average', 0):.1f} Hz")
                print(f"  • Most recent pitch:      {pitch_range.get('latest', 0):.1f} Hz")
                
                # Get current training goal for comparison
                print()
                current_goal = self.config_manager.config.get('current_goal', 165) if self.config_manager else 165
                print(f"Current training goal: {current_goal} Hz")
                
                avg_pitch = pitch_range.get('average', 0)
                if avg_pitch > 0:
                    if avg_pitch < current_goal * 0.8:
                        print("💡 Your average pitch is below your training goal - good progress opportunity!")
                    elif avg_pitch > current_goal * 1.2:
                        print("💡 Your average pitch is above your training goal - consider adjusting your target")
                    else:
                        print("✅ Your average pitch aligns well with your training goal!")
        
        print()
        self.ui.print_separator()
        self.ui.wait_for_enter()
    
    def get_analysis_statistics(self) -> Optional[Dict[str, Any]]:
        """Get analysis statistics for external use"""
        if not self.pitch_goal_manager:
            return None
        
        return self.pitch_goal_manager.get_analysis_history_summary()
    
    def batch_analyze_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Analyze multiple audio files in batch"""
        if not self._validate_dependencies():
            return {'error': 'Missing dependencies'}
        
        results = {
            'successful': [],
            'failed': [],
            'total_processed': 0
        }
        
        for file_path in file_paths:
            results['total_processed'] += 1
            
            try:
                if not os.path.exists(file_path):
                    results['failed'].append({
                        'file': file_path,
                        'error': 'File not found'
                    })
                    continue
                
                if not self.audio_file_analyzer.is_supported_file(file_path):
                    results['failed'].append({
                        'file': file_path,
                        'error': 'Unsupported file format'
                    })
                    continue
                
                analysis_result = self.audio_file_analyzer.full_analysis(file_path)
                self.pitch_goal_manager.add_analysis_result(analysis_result)
                
                results['successful'].append({
                    'file': file_path,
                    'result': analysis_result
                })
                
            except Exception as e:
                results['failed'].append({
                    'file': file_path,
                    'error': str(e)
                })
        
        return results
    
    def export_analysis_history(self, export_path: str) -> bool:
        """Export analysis history to file"""
        if not self.pitch_goal_manager:
            return False
        
        try:
            import json
            
            history_data = {
                'export_date': datetime.now().isoformat(),
                'analysis_history': self.pitch_goal_manager.analysis_history,
                'summary': self.pitch_goal_manager.get_analysis_history_summary()
            }
            
            with open(export_path, 'w') as f:
                json.dump(history_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error exporting analysis history: {e}")
            return False
    
    def clear_analysis_history(self) -> bool:
        """Clear all analysis history"""
        if not self.pitch_goal_manager:
            return False
        
        try:
            self.pitch_goal_manager.analysis_history = []
            self.pitch_goal_manager.save_analysis_history()
            return True
        except Exception as e:
            print(f"Error clearing analysis history: {e}")
            return False
    
    def _validate_dependencies(self) -> bool:
        """Validate that all required dependencies are available"""
        required = [
            self.audio_file_analyzer,
            self.pitch_goal_manager,
            self.ui
        ]
        return all(dep is not None for dep in required)