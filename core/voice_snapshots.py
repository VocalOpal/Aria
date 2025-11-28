"""
Voice Snapshots Manager - Records progress snapshots for journey tracking
"""

import os
import json
import time
import wave
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from utils.file_operations import safe_save_config, safe_load_config, get_logger


class VoiceSnapshotManager:
    """Manages voice progress snapshots for tracking improvement over time"""
    
    def __init__(self, snapshots_dir="data/snapshots"):
        self.snapshots_dir = Path(snapshots_dir)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata_file = self.snapshots_dir / "snapshots_metadata.json"
        self.snapshots_list: List[Dict] = []
        self.session_count = 0
        self.milestone_interval = 10
        
        self.load_metadata()
        
    def load_metadata(self):
        """Load snapshots metadata from disk"""
        try:
            if self.metadata_file.exists():
                data = safe_load_config(str(self.metadata_file))
                self.snapshots_list = data.get('snapshots', [])
                self.session_count = data.get('session_count', 0)
            else:
                self.snapshots_list = []
                self.session_count = 0
        except Exception as e:
            get_logger().error(f"Error loading snapshot metadata: {e}")
            self.snapshots_list = []
            self.session_count = 0
    
    def save_metadata(self):
        """Save snapshots metadata to disk"""
        try:
            data = {
                'snapshots': self.snapshots_list,
                'session_count': self.session_count,
                'last_updated': datetime.now().isoformat()
            }
            safe_save_config(str(self.metadata_file), data)
        except Exception as e:
            get_logger().error(f"Error saving snapshot metadata: {e}")
    
    def increment_session(self):
        """Increment session counter and check for auto-save milestone"""
        self.session_count += 1
        should_auto_save = (self.session_count % self.milestone_interval == 0)
        return should_auto_save
    
    def record_snapshot(
        self, 
        audio_data: np.ndarray, 
        sample_rate: int,
        session_stats: Dict,
        duration_seconds: float = 5.0,
        is_milestone: bool = False,
        note: str = ""
    ) -> Optional[str]:
        """
        Record a voice snapshot with metadata
        
        Args:
            audio_data: Raw audio data (numpy array)
            sample_rate: Audio sample rate
            session_stats: Current session statistics
            duration_seconds: Target duration (will trim/pad as needed)
            is_milestone: Whether this is an auto-milestone snapshot
            note: Optional user note about this snapshot
            
        Returns:
            Snapshot ID or None if failed
        """
        try:
            timestamp = datetime.now()
            snapshot_id = timestamp.strftime("%Y%m%d_%H%M%S")
            
            audio_filename = f"snapshot_{snapshot_id}.wav"
            audio_path = self.snapshots_dir / audio_filename
            
            target_samples = int(duration_seconds * sample_rate)
            
            if len(audio_data) > target_samples:
                trimmed_audio = audio_data[:target_samples]
            else:
                padding = target_samples - len(audio_data)
                trimmed_audio = np.pad(audio_data, (0, padding), mode='constant')
            
            trimmed_audio = np.clip(trimmed_audio, -1.0, 1.0)
            audio_int16 = (trimmed_audio * 32767).astype(np.int16)
            
            with wave.open(str(audio_path), 'w') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_int16.tobytes())
            
            metadata = {
                'id': snapshot_id,
                'timestamp': timestamp.isoformat(),
                'filename': audio_filename,
                'duration': duration_seconds,
                'sample_rate': sample_rate,
                'is_milestone': is_milestone,
                'milestone_number': self.session_count if is_milestone else None,
                'note': note,
                'stats': {
                    'avg_pitch': session_stats.get('avg_pitch', 0),
                    'min_pitch': session_stats.get('min_pitch', 0),
                    'max_pitch': session_stats.get('max_pitch', 0),
                    'avg_resonance': session_stats.get('avg_resonance', 0),
                    'avg_hnr': session_stats.get('avg_hnr', 0),
                    'total_time': session_stats.get('total_time', 0),
                }
            }
            
            self.snapshots_list.append(metadata)
            self.save_metadata()
            
            get_logger().info(f"Voice snapshot saved: {snapshot_id}")
            return snapshot_id
            
        except Exception as e:
            get_logger().error(f"Error recording snapshot: {e}")
            return None
    
    def get_snapshots(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get list of all snapshots, newest first
        
        Args:
            limit: Maximum number to return (None for all)
            
        Returns:
            List of snapshot metadata dicts
        """
        sorted_snapshots = sorted(
            self.snapshots_list, 
            key=lambda x: x['timestamp'], 
            reverse=True
        )
        
        if limit:
            return sorted_snapshots[:limit]
        return sorted_snapshots
    
    def get_snapshot_by_id(self, snapshot_id: str) -> Optional[Dict]:
        """Get a specific snapshot by ID"""
        for snapshot in self.snapshots_list:
            if snapshot['id'] == snapshot_id:
                return snapshot
        return None
    
    def get_snapshot_path(self, snapshot_id: str) -> Optional[Path]:
        """Get the file path for a snapshot"""
        snapshot = self.get_snapshot_by_id(snapshot_id)
        if snapshot:
            path = self.snapshots_dir / snapshot['filename']
            if path.exists():
                return path
        return None
    
    def compare_snapshots(
        self, 
        snapshot1_id: str, 
        snapshot2_id: str
    ) -> Optional[Dict]:
        """
        Compare two snapshots and return improvement metrics
        
        Args:
            snapshot1_id: Earlier snapshot ID
            snapshot2_id: Later snapshot ID
            
        Returns:
            Dictionary with comparison metrics or None
        """
        snap1 = self.get_snapshot_by_id(snapshot1_id)
        snap2 = self.get_snapshot_by_id(snapshot2_id)
        
        if not snap1 or not snap2:
            return None
        
        stats1 = snap1['stats']
        stats2 = snap2['stats']
        
        comparison = {
            'snapshot1': {
                'id': snapshot1_id,
                'timestamp': snap1['timestamp'],
                'note': snap1.get('note', '')
            },
            'snapshot2': {
                'id': snapshot2_id,
                'timestamp': snap2['timestamp'],
                'note': snap2.get('note', '')
            },
            'improvements': {
                'pitch_change': stats2['avg_pitch'] - stats1['avg_pitch'],
                'pitch_range_change': (
                    (stats2['max_pitch'] - stats2['min_pitch']) - 
                    (stats1['max_pitch'] - stats1['min_pitch'])
                ),
                'resonance_change': stats2['avg_resonance'] - stats1['avg_resonance'],
                'quality_change': stats2['avg_hnr'] - stats1['avg_hnr'],
            },
            'stats_comparison': {
                'pitch': {
                    'before': stats1['avg_pitch'],
                    'after': stats2['avg_pitch'],
                    'change': stats2['avg_pitch'] - stats1['avg_pitch']
                },
                'resonance': {
                    'before': stats1['avg_resonance'],
                    'after': stats2['avg_resonance'],
                    'change': stats2['avg_resonance'] - stats1['avg_resonance']
                },
                'quality': {
                    'before': stats1['avg_hnr'],
                    'after': stats2['avg_hnr'],
                    'change': stats2['avg_hnr'] - stats1['avg_hnr']
                }
            },
            'time_between': self._calculate_time_diff(
                snap1['timestamp'], 
                snap2['timestamp']
            )
        }
        
        return comparison
    
    def _calculate_time_diff(self, time1_iso: str, time2_iso: str) -> Dict:
        """Calculate human-readable time difference between two timestamps"""
        time1 = datetime.fromisoformat(time1_iso)
        time2 = datetime.fromisoformat(time2_iso)
        
        diff = abs((time2 - time1).total_seconds())
        
        days = int(diff // 86400)
        hours = int((diff % 86400) // 3600)
        minutes = int((diff % 3600) // 60)
        
        return {
            'total_seconds': diff,
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'formatted': f"{days}d {hours}h {minutes}m" if days > 0 else f"{hours}h {minutes}m"
        }
    
    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot and its audio file"""
        try:
            snapshot = self.get_snapshot_by_id(snapshot_id)
            if not snapshot:
                return False
            
            audio_path = self.snapshots_dir / snapshot['filename']
            if audio_path.exists():
                audio_path.unlink()
            
            self.snapshots_list = [
                s for s in self.snapshots_list 
                if s['id'] != snapshot_id
            ]
            self.save_metadata()
            
            return True
        except Exception as e:
            get_logger().error(f"Error deleting snapshot: {e}")
            return False
    
    def get_milestone_snapshots(self) -> List[Dict]:
        """Get only milestone snapshots"""
        return [s for s in self.snapshots_list if s.get('is_milestone', False)]
    
    def get_total_count(self) -> int:
        """Get total number of snapshots"""
        return len(self.snapshots_list)
