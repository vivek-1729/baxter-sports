"""
Preferences storage module - JSON file-based storage
Simple, reliable, easy to migrate to database later
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path


class PreferencesStorage:
    """Handles saving and loading user preferences"""
    
    def __init__(self, storage_dir: str = "data/preferences"):
        """
        Initialize preferences storage
        
        Args:
            storage_dir: Directory to store preference files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, user_id: str) -> Path:
        """Get file path for a user's preferences"""
        return self.storage_dir / f"{user_id}.json"
    
    def save_preferences(self, user_id: str, selected_sports: List[str], 
                        favorites: Dict[str, str]) -> bool:
        """
        Save user preferences to JSON file
        
        Args:
            user_id: Unique user identifier
            selected_sports: List of selected sport keys
            favorites: Dictionary mapping sport_key to favorite team/player
            
        Returns:
            True if successful, False otherwise
        """
        try:
            preferences = {
                "user_id": user_id,
                "selected_sports": selected_sports,
                "favorites": favorites,
                "updated_at": datetime.now().isoformat()
            }
            
            # Check if file exists to preserve created_at
            file_path = self._get_file_path(user_id)
            if file_path.exists():
                existing = self.load_preferences(user_id)
                if existing:
                    preferences["created_at"] = existing.get("created_at", 
                                                           datetime.now().isoformat())
                else:
                    preferences["created_at"] = datetime.now().isoformat()
            else:
                preferences["created_at"] = datetime.now().isoformat()
            
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(preferences, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving preferences: {e}")
            return False
    
    def load_preferences(self, user_id: str) -> Optional[Dict]:
        """
        Load user preferences from JSON file
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Preferences dictionary or None if not found
        """
        try:
            file_path = self._get_file_path(user_id)
            if not file_path.exists():
                return None
            
            with open(file_path, 'r') as f:
                preferences = json.load(f)
            
            return preferences
        except Exception as e:
            print(f"Error loading preferences: {e}")
            return None
    
    def update_preferences(self, user_id: str, selected_sports: Optional[List[str]] = None,
                          favorites: Optional[Dict[str, str]] = None) -> bool:
        """
        Update existing preferences (merge with existing)
        
        Args:
            user_id: Unique user identifier
            selected_sports: Optional new selected sports (merges with existing)
            favorites: Optional new favorites (merges with existing)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            existing = self.load_preferences(user_id)
            if not existing:
                # Create new if doesn't exist
                if selected_sports and favorites:
                    return self.save_preferences(user_id, selected_sports, favorites)
                return False
            
            # Merge with existing
            updated_sports = selected_sports if selected_sports else existing.get("selected_sports", [])
            updated_favorites = existing.get("favorites", {}).copy()
            if favorites:
                updated_favorites.update(favorites)
            
            return self.save_preferences(user_id, updated_sports, updated_favorites)
        except Exception as e:
            print(f"Error updating preferences: {e}")
            return False
    
    def delete_preferences(self, user_id: str) -> bool:
        """
        Delete user preferences
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self._get_file_path(user_id)
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting preferences: {e}")
            return False


# Global instance
_preferences_storage = None

def get_preferences_storage() -> PreferencesStorage:
    """Get or create the global preferences storage instance"""
    global _preferences_storage
    if _preferences_storage is None:
        _preferences_storage = PreferencesStorage()
    return _preferences_storage

