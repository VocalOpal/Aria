"""Export Manager - Handles exporting session data to CSV/PDF/JSON formats"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from .export_csv import export_sessions_to_csv


class ExportManager:
    """Manages exporting session data to various formats"""
    
    def __init__(self):
        self.csv_columns = [
            'date',
            'duration_minutes',
            'avg_pitch',
            'min_pitch',
            'max_pitch',
            'time_in_range_percent',
            'goal_achievement_percent',
            'avg_jitter',
            'avg_shimmer',
            'avg_hnr',
            'strain_events',
            'total_alerts',
            'dip_count',
            'voice_quality',
            'avg_resonance',
            'resonance_shift'
        ]
    
    def export_to_csv(self, sessions: List[Dict[str, Any]], output_path: str) -> bool:
        """Export all session data to CSV using dedicated CSV module
        
        Args:
            sessions: List of session dictionaries
            output_path: Path where CSV file will be saved
            
        Returns:
            True if export successful, False otherwise
        """
        return export_sessions_to_csv(sessions, output_path)
    
    def export_session_to_pdf(self, session: Dict[str, Any], output_path: str) -> bool:
        """Export single session to PDF
        
        Args:
            session: Session dictionary
            output_path: Path where PDF file will be saved
            
        Returns:
            True if export successful, False otherwise
        
        Note:
            Currently not implemented - no external PDF libs available
            Will be implemented when PDF library is added
        """
        return False
    
    def _session_to_csv_row(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Convert session dictionary to CSV row (DEPRECATED - use export_csv module)
        
        Args:
            session: Session dictionary from session manager
            
        Returns:
            Dictionary with CSV column values
        """
        from .export_csv import _format_session_for_csv
        return _format_session_for_csv(session)
    
    def get_export_preview(self, sessions: List[Dict[str, Any]], limit: int = 5) -> str:
        """Get a text preview of what will be exported
        
        Args:
            sessions: List of sessions to preview
            limit: Maximum number of sessions to show in preview
            
        Returns:
            Preview text string
        """
        if not sessions:
            return "No sessions to export"
        
        preview_sessions = sessions[-limit:] if len(sessions) > limit else sessions
        
        lines = [f"Export Preview ({len(sessions)} total sessions):"]
        lines.append("")
        lines.append(" | ".join(self.csv_columns))
        lines.append("-" * 80)
        
        for session in preview_sessions:
            row = self._session_to_csv_row(session)
            line_values = [str(row[col]) for col in self.csv_columns]
            lines.append(" | ".join(line_values))
        
        if len(sessions) > limit:
            lines.append(f"... and {len(sessions) - limit} more sessions")
        
        return "\n".join(lines)
    
    def export_to_json(self, sessions: List[Dict[str, Any]], achievement_manager=None, 
                      session_manager=None, output_path: str = None) -> Dict[str, Any]:
        """Export full user data to JSON (for Discord bot integration)
        
        Args:
            sessions: List of session dictionaries
            achievement_manager: VoiceAchievementSystem instance
            session_manager: VoiceSessionManager instance
            output_path: Optional path to save JSON file
            
        Returns:
            Complete export data dictionary
        """
        export_data = {
            'export_version': '1.0',
            'export_date': datetime.now().isoformat(),
            'app': 'Aria Voice Studio',
            'sessions': sessions,
            'stats': self._calculate_stats(sessions, session_manager),
        }
        
        # Add achievement data if available
        if achievement_manager:
            # Get achievements computed from session data
            total_sessions = len(sessions)
            total_time = sum(s.get('duration_minutes', 0) for s in sessions)
            streak_info = achievement_manager.calculate_streaks(sessions)
            pitch_data = achievement_manager.calculate_pitch_achievements(sessions)
            all_achievements = achievement_manager.get_all_achievements(
                total_sessions, total_time, streak_info, pitch_data, sessions
            )
            
            # Only include earned achievements
            earned = [a for a in all_achievements if a['earned']]
            
            export_data['achievements'] = {
                'unlocked': earned,
                'total_unlocked': len(earned),
                'total_available': len(all_achievements),
                'completion_percent': (len(earned) / len(all_achievements) * 100) if all_achievements else 0
            }
        
        # Save to file if path provided
        if output_path:
            try:
                with open(output_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                return export_data
            except Exception as e:
                from utils.error_handler import log_error
                log_error(e, "ExportManager.export_to_json")
                return None
        
        return export_data
    
    def _calculate_stats(self, sessions: List[Dict[str, Any]], session_manager=None) -> Dict[str, Any]:
        if not sessions:
            return {
                'total_sessions': 0,
                'total_hours': 0,
                'average_pitch': 0,
                'current_streak': 0,
                'best_streak': 0,
                'achievement_count': 0
            }

        total_minutes = sum(s.get('duration_minutes', s.get('duration', 0) / 60) for s in sessions)
        pitches = [s.get('avg_pitch', 0) for s in sessions if s.get('avg_pitch', 0) > 0]

        stats = {
            'total_sessions': len(sessions),
            'total_hours': round(total_minutes / 60, 2),
            'average_pitch': round(sum(pitches) / len(pitches), 1) if pitches else 0,
            'total_alerts': sum(s.get('total_alerts', 0) for s in sessions),
            'total_strain_events': sum(s.get('strain_events', 0) for s in sessions),
        }

        if session_manager:
            stats['current_streak'] = getattr(session_manager, 'streak_count', 0)
            stats['best_streak'] = getattr(session_manager, 'best_streak', 0)

        return stats
