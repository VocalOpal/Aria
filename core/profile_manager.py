"""
Multi-Profile Support - Manage different voice training profiles
"""

import json
import os
import uuid
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from utils.file_operations import safe_save_config, safe_load_config, get_logger
from utils.emoji_handler import convert_emoji_text


class Profile:
    """Represents a voice training profile"""
    
    def __init__(self, id: str, name: str, icon: str, goal_range: tuple, 
                 preset: str, created_date: str = None):
        self.id = id
        self.name = name
        self.icon = icon
        self.goal_range = goal_range  # (min_hz, max_hz)
        self.preset = preset
        self.created_date = created_date or datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'goal_range': self.goal_range,
            'preset': self.preset,
            'created_date': self.created_date
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Profile':
        """Create profile from dictionary"""
        return Profile(
            id=data['id'],
            name=data['name'],
            icon=data['icon'],
            goal_range=tuple(data['goal_range']),
            preset=data['preset'],
            created_date=data.get('created_date')
        )


class ProfileManager:
    """Manages voice training profiles"""
    
    def __init__(self, profiles_file="data/profiles.json"):
        self.profiles_file = profiles_file
        self.profiles_dir = "data/profiles"
        self.logger = get_logger()
        self.profiles: Dict[str, Profile] = {}
        self.current_profile_id: Optional[str] = None
        
        # Ensure profiles directory exists
        os.makedirs(self.profiles_dir, exist_ok=True)
        
        # Load profiles
        self.load_profiles()
        
        # Create default profiles if this is first run
        if not self.profiles:
            self._create_default_profiles()
    
    def load_profiles(self) -> bool:
        """Load profiles from file"""
        try:
            if os.path.exists(self.profiles_file):
                data = safe_load_config(self.profiles_file, {})
                
                # Load profile objects
                for profile_data in data.get('profiles', []):
                    profile = Profile.from_dict(profile_data)
                    self.profiles[profile.id] = profile
                
                # Load current profile
                self.current_profile_id = data.get('current_profile_id')
                
                self.logger.info(f"Loaded {len(self.profiles)} profiles")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error loading profiles: {e}")
            return False
    
    def save_profiles(self, create_backup: bool = False) -> bool:
        """
        Save profiles to file.
        
        Args:
            create_backup: If True, creates backup before saving
        
        Returns:
            True if successful
        """
        try:
            data = {
                'profiles': [p.to_dict() for p in self.profiles.values()],
                'current_profile_id': self.current_profile_id
            }
            success = safe_save_config(data, self.profiles_file, create_backup=create_backup)
            if success:
                self.logger.debug("Profiles saved successfully")
            return success
        except Exception as e:
            self.logger.error(f"Error saving profiles: {e}")
            return False
    
    def create_profile(self, name: str, icon: str, goal_range: tuple, 
                      preset: str, copy_from: str = None) -> Optional[Profile]:
        """Create a new profile"""
        try:
            profile_id = str(uuid.uuid4())
            profile = Profile(profile_id, name, icon, goal_range, preset)
            
            self.profiles[profile_id] = profile
            
            # Create profile-specific config file
            config_file = self._get_profile_config_path(profile_id)
            
            if copy_from and copy_from in self.profiles:
                # Copy config from existing profile
                source_config = self._get_profile_config_path(copy_from)
                if os.path.exists(source_config):
                    shutil.copy2(source_config, config_file)
            else:
                # Create config from preset
                from voice.presets import VoicePresets
                presets_manager = VoicePresets()
                preset_config = presets_manager.apply_preset_to_config(preset, {})
                
                # Override goal settings
                preset_config['base_goal'] = goal_range[0]
                preset_config['current_goal'] = goal_range[0]
                
                safe_save_config(preset_config, config_file)
            
            self.save_profiles()
            self.logger.info(f"Created profile: {name}")
            return profile
            
        except Exception as e:
            self.logger.error(f"Error creating profile: {e}")
            return None
    
    def switch_profile(self, profile_id: str) -> bool:
        """Switch to a different profile"""
        try:
            if profile_id not in self.profiles:
                self.logger.error(f"Profile {profile_id} not found")
                return False
            
            self.current_profile_id = profile_id
            self.save_profiles()
            self.logger.info(f"Switched to profile: {self.profiles[profile_id].name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error switching profile: {e}")
            return False
    
    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile"""
        try:
            if profile_id not in self.profiles:
                return False
            
            # Don't allow deleting the last profile
            if len(self.profiles) <= 1:
                self.logger.warning("Cannot delete the last profile")
                return False
            
            # Delete profile config file
            config_file = self._get_profile_config_path(profile_id)
            if os.path.exists(config_file):
                os.remove(config_file)
            
            # Remove profile
            del self.profiles[profile_id]
            
            # Switch to another profile if this was current
            if self.current_profile_id == profile_id:
                self.current_profile_id = next(iter(self.profiles.keys()))
            
            # Backup on profile deletion (significant change)
            self.save_profiles(create_backup=True)
            self.logger.info(f"Deleted profile: {profile_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting profile: {e}")
            return False
    
    def get_all(self) -> List[Profile]:
        """Get all profiles"""
        return list(self.profiles.values())
    
    def get_current(self) -> Optional[Profile]:
        """Get current profile"""
        if self.current_profile_id and self.current_profile_id in self.profiles:
            return self.profiles[self.current_profile_id]
        return None
    
    def get_profile_config_path(self, profile_id: str = None) -> str:
        """Get config file path for a profile"""
        if profile_id is None:
            profile_id = self.current_profile_id
        return self._get_profile_config_path(profile_id)
    
    def _get_profile_config_path(self, profile_id: str) -> str:
        """Internal method to get profile config path"""
        return os.path.join(self.profiles_dir, f"{profile_id}_config.json")
    
    def _create_default_profiles(self, user_config=None):
        """
        Create default profiles based on user's onboarding choices.
        
        Creates only 1 main profile to keep things simple and user-friendly.
        Users can manually create additional profiles if needed.
        """
        try:
            # Load existing config if available
            main_config = "data/voice_config.json"
            existing_config = None
            if os.path.exists(main_config):
                existing_config = safe_load_config(main_config, {})
            
            # Determine user's voice goal from config
            config_source = user_config or existing_config or {}
            preset_key = self._map_config_to_preset(config_source)
            target_range = config_source.get('target_pitch_range', [140, 200])
            target_tuple = tuple(target_range) if isinstance(target_range, (list, tuple)) else (140, 200)
            
            # Create ONE main profile based on user's onboarding choice
            main_profile = None
            
            if preset_key == 'mtf':
                main_profile = self.create_profile(
                    name="My Voice Training",
                    icon="🎤",
                    goal_range=target_tuple if len(target_tuple) == 2 else (165, 220),
                    preset="mtf"
                )
                
            elif preset_key == 'ftm':
                main_profile = self.create_profile(
                    name="My Voice Training",
                    icon="🎤",
                    goal_range=target_tuple if len(target_tuple) == 2 else (85, 165),
                    preset="ftm"
                )
                
            elif preset_key == 'nonbinary_higher':
                main_profile = self.create_profile(
                    name="My Voice Training",
                    icon="🎤",
                    goal_range=target_tuple if len(target_tuple) == 2 else (145, 220),
                    preset="nonbinary_higher"
                )
                
            elif preset_key == 'nonbinary_lower':
                main_profile = self.create_profile(
                    name="My Voice Training",
                    icon="🎤",
                    goal_range=target_tuple if len(target_tuple) == 2 else (100, 165),
                    preset="nonbinary_lower"
                )
                
            else:
                # Neutral/Custom default
                main_profile = self.create_profile(
                    name="My Voice Training",
                    icon="🎤",
                    goal_range=target_tuple if len(target_tuple) == 2 else (130, 200),
                    preset="nonbinary_neutral"
                )
            
            # Copy existing config to main profile if it exists
            if existing_config and main_profile:
                dest_config = self._get_profile_config_path(main_profile.id)
                if os.path.exists(main_config):
                    shutil.copy2(main_config, dest_config)
            
            if main_profile:
                self.current_profile_id = main_profile.id
            
            # Backup on initial profile creation (one-time)
            self.save_profiles(create_backup=True)
            self.logger.info(f"Created default profile based on user goal: {config_source.get('voice_goals', '')}")
            return main_profile
            
        except Exception as e:
            self.logger.error(f"Error creating default profiles: {e}")
            return None

    def apply_onboarding_config(self, user_config: Dict[str, Any]) -> Optional[Profile]:
        """
        Apply onboarding selection to the active profile and sync config file.
        """
        try:
            if not user_config:
                return None

            preset_key = self._map_config_to_preset(user_config)
            target_range = user_config.get('target_pitch_range', [140, 200])
            target_tuple = tuple(target_range) if isinstance(target_range, (list, tuple)) else (140, 200)
            profile_name = user_config.get('profile_name', "My Voice Training")
            profile_icon = convert_emoji_text(str(user_config.get('profile_icon', "🎤")))

            # Prefer current profile; fall back to first available
            profile = self.get_current() if self.profiles else None
            if profile is None and self.profiles:
                profile = next(iter(self.profiles.values()), None)

            preset_for_profile = preset_key or 'custom'

            if profile is None:
                profile = self.create_profile(profile_name, profile_icon, target_tuple, preset_for_profile)
            else:
                profile.name = profile_name or profile.name
                profile.icon = profile_icon or profile.icon
                profile.goal_range = target_tuple
                profile.preset = preset_for_profile
                self.current_profile_id = profile.id
                self.save_profiles()

            if profile:
                config_path = self.get_profile_config_path(profile.id)
                config_data = safe_load_config(config_path, {})
                config_data.update(user_config)
                safe_save_config(config_data, config_path)

            return profile
        except Exception as e:
            self.logger.error(f"Error applying onboarding config: {e}")
            return None

    def _map_config_to_preset(self, config: Dict[str, Any]) -> str:
        """Map mixed onboarding/config fields to a preset key."""
        preset_field = config.get('current_preset') or config.get('voice_preset') or config.get('voice_goals', '')
        text = preset_field.lower() if isinstance(preset_field, str) else ''

        if 'mtf' in text or 'feminine' in text:
            return 'mtf'
        if 'ftm' in text or 'masculine' in text:
            return 'ftm'
        if 'higher' in text:
            return 'nonbinary_higher'
        if 'lower' in text:
            return 'nonbinary_lower'
        if 'neutral' in text or 'androgynous' in text:
            return 'nonbinary_neutral'
        if 'custom' in text:
            return 'custom'
        return 'custom'
        return 'custom'
