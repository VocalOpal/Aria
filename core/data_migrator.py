"""Data Migration System - Handles schema versioning and data migrations."""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import shutil
from utils.error_handler import log_error


class DataMigrator:
    """Manages data versioning and schema migrations"""
    
    CURRENT_SCHEMA_VERSION = 5
    
    def __init__(self, data_dir: str = None):
        """Initialize the data migrator
        
        Args:
            data_dir: Path to data directory (defaults to ./data)
        """
        try:
            if data_dir is None:
                data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
            
            self.data_dir = Path(data_dir)
            self.backup_dir = self.data_dir / 'backups'
            self.backup_dir.mkdir(exist_ok=True)
        except Exception as e:
            log_error(e, "DataMigrator.__init__")
            # Set defaults even on error
            self.data_dir = Path('./data')
            self.backup_dir = self.data_dir / 'backups'
    
    def detect_version(self, file_path: Path) -> int:
        """Detect schema version of a data file
        
        Args:
            file_path: Path to the data file
            
        Returns:
            Schema version number (1-5, or 0 if unable to detect)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check for explicit schema_version field
            if 'schema_version' in data:
                return data['schema_version']
            
            # Infer version from structure
            if 'profiles' in data:
                # profiles.json
                if isinstance(data['profiles'], list) and len(data['profiles']) > 0:
                    if 'created_date' in data['profiles'][0]:
                        return 4  # Has timestamps
                    return 3  # Basic profile structure
            
            if 'sessions' in data:
                # session data
                if isinstance(data['sessions'], list) and len(data['sessions']) > 0:
                    session = data['sessions'][0]
                    if 'avg_jitter' in session and 'avg_shimmer' in session:
                        return 4  # Has advanced metrics
                    return 3  # Basic session structure
            
            # Default to version 1 for unknown structures
            return 1
            
        except (json.JSONDecodeError, FileNotFoundError):
            return 0
    
    def migrate_data(self, from_version: int, to_version: int = None) -> Dict[str, any]:
        """Migrate all data files from one version to another
        
        Args:
            from_version: Current schema version
            to_version: Target schema version (defaults to CURRENT_SCHEMA_VERSION)
            
        Returns:
            Dict with migration results: {'success': bool, 'files_migrated': list, 'errors': list}
        """
        try:
            if to_version is None:
                to_version = self.CURRENT_SCHEMA_VERSION
            
            if from_version >= to_version:
                return {
                    'success': True,
                    'message': 'Already at target version or newer',
                    'files_migrated': [],
                    'errors': []
                }
            
            results = {
                'success': True,
                'files_migrated': [],
                'errors': []
            }
            
            # Create backup before migration
            backup_path = self._create_backup()
            results['backup_path'] = str(backup_path)
            
            # Find all JSON files
            json_files = list(self.data_dir.glob('*.json'))
            
            # Migrate each version step
            for version in range(from_version, to_version):
                next_version = version + 1
                
                for file_path in json_files:
                    try:
                        current_version = self.detect_version(file_path)
                        
                        if current_version == version:
                            self._migrate_file(file_path, version, next_version)
                            results['files_migrated'].append(str(file_path.name))
                            
                    except Exception as e:
                        results['errors'].append(f"{file_path.name}: {str(e)}")
                        results['success'] = False
                        log_error(e, f"DataMigrator.migrate_data - {file_path.name}")
            
            return results
        except Exception as e:
            log_error(e, "DataMigrator.migrate_data")
            return {
                'success': False,
                'message': f'Migration failed: {str(e)}',
                'files_migrated': [],
                'errors': [str(e)]
            }
    
    def _migrate_file(self, file_path: Path, from_version: int, to_version: int):
        """Migrate a single file from one version to another
        
        Args:
            file_path: Path to the file to migrate
            from_version: Current version
            to_version: Target version
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Apply migration based on version jump
        migration_method = f"_migrate_v{from_version}_to_v{to_version}"
        
        if hasattr(self, migration_method):
            migrated_data = getattr(self, migration_method)(data)
            
            # Add schema version field
            migrated_data['schema_version'] = to_version
            
            # Write migrated data
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(migrated_data, f, indent=2, ensure_ascii=False)
        else:
            # Generic migration: just add schema_version
            data['schema_version'] = to_version
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _migrate_v1_to_v2(self, data: Dict) -> Dict:
        """Migrate from v1 to v2 - Add basic metadata"""
        data['migrated_at'] = datetime.now().isoformat()
        return data
    
    def _migrate_v2_to_v3(self, data: Dict) -> Dict:
        """Migrate from v2 to v3 - Add profile/session structure"""
        # Ensure proper list structures
        if 'profiles' in data and not isinstance(data['profiles'], list):
            data['profiles'] = []
        
        if 'sessions' in data and not isinstance(data['sessions'], list):
            data['sessions'] = []
        
        return data
    
    def _migrate_v3_to_v4(self, data: Dict) -> Dict:
        """Migrate from v3 to v4 - Add timestamps and advanced metrics"""
        # Add created_date to profiles if missing
        if 'profiles' in data:
            for profile in data['profiles']:
                if 'created_date' not in profile:
                    profile['created_date'] = datetime.now().isoformat()
        
        # Add default metric values to sessions if missing
        if 'sessions' in data:
            for session in data['sessions']:
                if 'avg_jitter' not in session:
                    session['avg_jitter'] = 0.0
                if 'avg_shimmer' not in session:
                    session['avg_shimmer'] = 0.0
                if 'avg_hnr' not in session:
                    session['avg_hnr'] = 18.0
                if 'strain_events' not in session:
                    session['strain_events'] = 0
        
        return data
    
    def _migrate_v4_to_v5(self, data: Dict) -> Dict:
        """Migrate from v4 to v5 - Add long-term analytics support"""
        # Add monthly_aggregates for historical data
        if 'sessions' in data:
            data['monthly_aggregates'] = self._generate_monthly_aggregates(data['sessions'])
        
        # Add yearly_aggregates
        if 'sessions' in data:
            data['yearly_aggregates'] = self._generate_yearly_aggregates(data['sessions'])
        
        # Add migration timestamp
        data['last_aggregation'] = datetime.now().isoformat()
        
        return data
    
    def _generate_monthly_aggregates(self, sessions: List[Dict]) -> Dict:
        """Generate monthly aggregates from session data
        
        Args:
            sessions: List of session dictionaries
            
        Returns:
            Dict keyed by 'YYYY-MM' with aggregated metrics
        """
        monthly_data = {}
        
        for session in sessions:
            # Parse session date
            session_date = session.get('start_time') or session.get('date')
            if not session_date:
                continue
            
            if isinstance(session_date, str):
                try:
                    date_obj = datetime.fromisoformat(session_date)
                except:
                    continue
            else:
                date_obj = session_date
            
            # Create month key
            month_key = date_obj.strftime('%Y-%m')
            
            # Initialize month data
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'sessions': [],
                    'total_sessions': 0
                }
            
            # Add session metrics
            monthly_data[month_key]['sessions'].append({
                'jitter': session.get('avg_jitter', 0),
                'shimmer': session.get('avg_shimmer', 0),
                'hnr': session.get('avg_hnr', 0),
                'strain_events': session.get('strain_events', 0)
            })
            monthly_data[month_key]['total_sessions'] += 1
        
        return monthly_data
    
    def _generate_yearly_aggregates(self, sessions: List[Dict]) -> Dict:
        """Generate yearly aggregates from session data
        
        Args:
            sessions: List of session dictionaries
            
        Returns:
            Dict keyed by 'YYYY' with aggregated metrics
        """
        yearly_data = {}
        
        for session in sessions:
            # Parse session date
            session_date = session.get('start_time') or session.get('date')
            if not session_date:
                continue
            
            if isinstance(session_date, str):
                try:
                    date_obj = datetime.fromisoformat(session_date)
                except:
                    continue
            else:
                date_obj = session_date
            
            # Create year key
            year_key = date_obj.strftime('%Y')
            
            # Initialize year data
            if year_key not in yearly_data:
                yearly_data[year_key] = {
                    'sessions': [],
                    'total_sessions': 0
                }
            
            # Add session metrics
            yearly_data[year_key]['sessions'].append({
                'jitter': session.get('avg_jitter', 0),
                'shimmer': session.get('avg_shimmer', 0),
                'hnr': session.get('avg_hnr', 0),
                'strain_events': session.get('strain_events', 0)
            })
            yearly_data[year_key]['total_sessions'] += 1
        
        return yearly_data
    
    def _create_backup(self) -> Path:
        """Create a backup of all data files
        
        Returns:
            Path to backup directory
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f'backup_{timestamp}'
        backup_path.mkdir(exist_ok=True)
        
        # Copy all JSON files
        for json_file in self.data_dir.glob('*.json'):
            shutil.copy2(json_file, backup_path / json_file.name)
        
        return backup_path
    
    def add_schema_version_to_file(self, file_path: Path, version: int = None):
        """Add schema_version field to a data file
        
        Args:
            file_path: Path to the file
            version: Version number (defaults to CURRENT_SCHEMA_VERSION)
        """
        if version is None:
            version = self.CURRENT_SCHEMA_VERSION
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data['schema_version'] = version
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error adding schema version to {file_path}: {e}")
    
    def verify_migration(self, expected_version: int = None) -> Dict[str, any]:
        """Verify all data files are at expected version
        
        Args:
            expected_version: Expected schema version (defaults to CURRENT_SCHEMA_VERSION)
            
        Returns:
            Dict with verification results
        """
        if expected_version is None:
            expected_version = self.CURRENT_SCHEMA_VERSION
        
        results = {
            'all_valid': True,
            'files': {},
            'errors': []
        }
        
        json_files = list(self.data_dir.glob('*.json'))
        
        for file_path in json_files:
            try:
                detected_version = self.detect_version(file_path)
                results['files'][file_path.name] = {
                    'version': detected_version,
                    'valid': detected_version == expected_version
                }
                
                if detected_version != expected_version:
                    results['all_valid'] = False
                    
            except Exception as e:
                results['errors'].append(f"{file_path.name}: {str(e)}")
                results['all_valid'] = False
        
        return results
