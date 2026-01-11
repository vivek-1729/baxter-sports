"""
Standalone image resolution module for sports events.
Decoupled from UI rendering, easily swappable.
"""

import requests
import os
import json
import hashlib
from typing import List, Optional, Dict
import time


class ImageResolver:
    """Resolves high-quality images for sports events using Google Custom Search API"""
    
    GOOGLE_API_URL = "https://www.googleapis.com/customsearch/v1"
    CUSTOM_SEARCH_ENGINE_ID = "225f7025a8a80475a"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the image resolver
        
        Args:
            api_key: Google API key. If not provided, will try to get from environment variable
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.cache = {}  # In-memory cache
        self.cache_dir = 'data/image_cache'
        os.makedirs(self.cache_dir, exist_ok=True)
        self._load_cache_from_disk()  # Load persistent cache on startup
        self.last_request_time = 0
        self.min_request_interval = 0.5  # Rate limiting: 500ms between requests
    
    def _get_cache_file_path(self, query: str) -> str:
        """Get file path for cached query"""
        cache_key = hashlib.md5(query.lower().strip().encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _load_cache_from_disk(self):
        """Load cache from disk on startup"""
        if not os.path.exists(self.cache_dir):
            return
        
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(self.cache_dir, filename), 'r') as f:
                            data = json.load(f)
                            query = data.get('query', '')
                            urls = data.get('urls', [])
                            if query and urls:
                                self.cache[query.lower().strip()] = urls
                    except (json.JSONDecodeError, IOError):
                        # Skip corrupted cache files
                        pass
        except OSError:
            # Directory doesn't exist or can't be read
            pass
    
    def _save_cache_to_disk(self, query: str, urls: List[str]):
        """Save cache to disk for persistence"""
        if not urls:
            return
        
        cache_file = self._get_cache_file_path(query)
        try:
            with open(cache_file, 'w') as f:
                json.dump({'query': query, 'urls': urls}, f)
        except IOError:
            # Can't write to cache, continue without it
            pass
    
    def _make_request(self, query: str) -> List[str]:
        """
        Make a request to Google Custom Search API
        
        Args:
            query: Search query string
            
        Returns:
            List of image URLs
        """
        if not self.api_key:
            return []
        
        # Rate limiting
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        # Check cache (in-memory first, then disk)
        cache_key = query.lower().strip()
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Check disk cache
        cache_file = self._get_cache_file_path(query)
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    urls = data.get('urls', [])
                    if urls:
                        # Load into memory cache for faster access
                        self.cache[cache_key] = urls
                        return urls
            except (json.JSONDecodeError, IOError):
                # Corrupted cache file, continue to API request
                pass
        
        try:
            params = {
                'key': self.api_key,
                'cx': self.CUSTOM_SEARCH_ENGINE_ID,
                'q': query,
                'searchType': 'image',
                'num': 4,  # Fetch up to 4 images
                'safe': 'active',
                'imgSize': 'large',
                'imgType': 'photo'
            }
            
            response = requests.get(self.GOOGLE_API_URL, params=params)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                urls = [item.get('link', '') for item in items if item.get('link')]
                
                # Cache the results (both in-memory and on disk)
                if urls:
                    self.cache[cache_key] = urls
                    self._save_cache_to_disk(query, urls)
                return urls
            else:
                return []
        except Exception:
            return []
    
    def resolve_event_image(self, event: Dict) -> Optional[str]:
        """
        Resolve a high-quality image URL for a sports event
        
        Args:
            event: Event dictionary with teams, players, sport, etc.
            
        Returns:
            Best candidate image URL or None
        """
        # Build query string from event data
        query_parts = []
        
        # Add sport/league
        sport = event.get('sport', {}).get('name', '')
        if sport:
            query_parts.append(sport)
        
        # Add team names (for team sports)
        home_team = event.get('teams', {}).get('home', {}).get('name', '')
        away_team = event.get('teams', {}).get('away', {}).get('name', '')
        
        if home_team and away_team:
            query_parts.append(f"{home_team} vs {away_team}")
        elif home_team:
            query_parts.append(home_team)
        elif away_team:
            query_parts.append(away_team)
        
        # Add event name if available
        event_name = event.get('league', {}).get('name', '')
        if event_name:
            query_parts.append(event_name)
        
        # Build query
        query = ' '.join(query_parts) if query_parts else 'sports'
        
        # Fetch images
        image_urls = self._make_request(query)
        
        # Return first (best) candidate
        return image_urls[0] if image_urls else None
    
    def resolve_team_image(self, team_name: str, sport: str = '') -> Optional[str]:
        """
        Resolve image for a specific team
        
        Args:
            team_name: Name of the team
            sport: Optional sport name for better results
            
        Returns:
            Image URL or None
        """
        query = f"{team_name} {sport}".strip()
        image_urls = self._make_request(query)
        return image_urls[0] if image_urls else None
    
    def resolve_player_image(self, player_name: str, sport: str = '') -> Optional[str]:
        """
        Resolve image for a specific player
        
        Args:
            player_name: Name of the player
            sport: Optional sport name for better results
            
        Returns:
            Image URL or None
        """
        query = f"{player_name} {sport}".strip()
        image_urls = self._make_request(query)
        return image_urls[0] if image_urls else None


# Global instance (can be initialized with API key)
_image_resolver = None

def get_image_resolver() -> ImageResolver:
    """Get or create the global image resolver instance"""
    global _image_resolver
    if _image_resolver is None:
        _image_resolver = ImageResolver()
    return _image_resolver

