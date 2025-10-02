"""CSV Export Module - Handles exporting session data to CSV format"""

import csv
from datetime import datetime
from typing import List, Dict, Any


def export_sessions_to_csv(sessions: List[Dict[str, Any]], filepath: str) -> bool:
    """Export session data to CSV file
    
    Args:
        sessions: List of session dictionaries from session manager
        filepath: Path where CSV file will be saved
        
    Returns:
        True if export successful, False otherwise
    """
    try:
        if not sessions:
            return False
        
        csv_columns = [
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
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, extrasaction='ignore')
            writer.writeheader()
            
            for session in sessions:
                row = _format_session_for_csv(session)
                writer.writerow(row)
        
        return True
        
    except Exception as e:
        from utils.error_handler import log_error
        log_error(e, "export_csv.export_sessions_to_csv")
        return False


def _format_session_for_csv(session: Dict[str, Any]) -> Dict[str, Any]:
    """Format session data for CSV export
    
    Args:
        session: Session dictionary from session manager
        
    Returns:
        Dictionary with formatted CSV values
    """
    try:
        date_obj = datetime.fromisoformat(session['date'].replace('Z', '+00:00'))
        date_str = date_obj.strftime('%Y-%m-%d %H:%M:%S')
    except:
        date_str = session.get('date', 'Unknown')
    
    duration_minutes = session.get('duration_minutes', session.get('duration', 0) / 60)
    
    return {
        'date': _escape_csv_value(date_str),
        'duration_minutes': round(duration_minutes, 2),
        'avg_pitch': round(session.get('avg_pitch', 0), 1),
        'min_pitch': round(session.get('min_pitch', 0), 1),
        'max_pitch': round(session.get('max_pitch', 0), 1),
        'time_in_range_percent': round(session.get('time_in_range_percent', 0), 2),
        'goal_achievement_percent': round(session.get('goal_achievement_percent', 0), 2),
        'avg_jitter': round(session.get('avg_jitter', 0), 4),
        'avg_shimmer': round(session.get('avg_shimmer', 0), 4),
        'avg_hnr': round(session.get('avg_hnr', 0), 2),
        'strain_events': session.get('strain_events', 0),
        'total_alerts': session.get('total_alerts', 0),
        'dip_count': session.get('dip_count', 0),
        'voice_quality': _escape_csv_value(session.get('voice_quality', 'Unknown')),
        'avg_resonance': round(session.get('avg_resonance', 0), 1),
        'resonance_shift': round(session.get('resonance_shift', 0), 2)
    }


def _escape_csv_value(value: str) -> str:
    """Escape special characters in CSV values
    
    Args:
        value: String value to escape
        
    Returns:
        Escaped string safe for CSV
    """
    if not isinstance(value, str):
        return str(value)
    
    value = str(value).replace('"', '""')
    
    if ',' in value or '"' in value or '\n' in value:
        return f'"{value}"'
    
    return value
