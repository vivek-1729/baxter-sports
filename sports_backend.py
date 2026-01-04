"""
Sports Dashboard Backend
Fetches data from API-Sports.io for multiple sports including:
NFL, NHL, NBA, MLB, Cricket, Formula 1, Tennis, Golf
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time
import os


class SportsAPIClient:
    """Client for interacting with API-Sports.io"""
    
    BASE_URL = "https://v1.api-sports.io"
    
    # Sport endpoints mapping
    SPORT_ENDPOINTS = {
        'nfl': 'american-football',
        'nhl': 'ice-hockey',
        'nba': 'basketball',
        'mlb': 'baseball',
        'cricket': 'cricket',
        'formula1': 'formula-1',
        'tennis': 'tennis',
        'golf': 'golf'
    }
    
    # League IDs (common leagues - may need adjustment)
    LEAGUE_IDS = {
        'nfl': 1,  # NFL
        'nhl': 57,  # NHL
        'nba': 12,  # NBA
        'mlb': 1,   # MLB
        'cricket': None,  # Cricket has multiple leagues
        'formula1': 1,  # Formula 1
        'tennis': None,  # Tennis has multiple tournaments
        'golf': None  # Golf has multiple tournaments
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the API client
        
        Args:
            api_key: API-Sports.io API key. If not provided, will try to get from environment variable
        """
        self.api_key = api_key or os.getenv('SPORTS_API_KEY')
        if not self.api_key:
            raise ValueError("API key is required. Set SPORTS_API_KEY environment variable or pass api_key parameter")
        
        self.headers = {
            'x-apisports-key': self.api_key
        }
        self.last_request_time = 0
        self.min_request_interval = 0.1  # Rate limiting: 100ms between requests
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict:
        """
        Make a request to the API with rate limiting
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        # Rate limiting
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params or {})
        self.last_request_time = time.time()
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            raise Exception("Rate limit exceeded. Please wait before making more requests.")
        else:
            response.raise_for_status()
            return {}
    
    def get_upcoming_games(self, sport: str, days_ahead: int = 14) -> List[Dict]:
        """
        Get upcoming games/fixtures for a sport
        
        Args:
            sport: Sport name (nfl, nhl, nba, mlb, cricket, formula1, tennis, golf)
            days_ahead: Number of days to look ahead (default: 14)
            
        Returns:
            List of upcoming games
        """
        sport_endpoint = self.SPORT_ENDPOINTS.get(sport.lower())
        if not sport_endpoint:
            raise ValueError(f"Unknown sport: {sport}")
        
        today = datetime.now()
        end_date = today + timedelta(days=days_ahead)
        
        params = {
            'from': today.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d')
        }
        
        # Add league/season filters where applicable
        league_id = self.LEAGUE_IDS.get(sport.lower())
        if league_id:
            params['league'] = league_id
            params['season'] = today.year
        
        # For sports with multiple leagues, get all upcoming fixtures
        endpoint = f"{sport_endpoint}/fixtures"
        response = self._make_request(endpoint, params)
        
        return response.get('response', [])
    
    def get_recent_scores(self, sport: str, days_back: int = 7) -> List[Dict]:
        """
        Get recent scores/results for a sport
        
        Args:
            sport: Sport name
            days_back: Number of days to look back (default: 7)
            
        Returns:
            List of recent games with scores
        """
        sport_endpoint = self.SPORT_ENDPOINTS.get(sport.lower())
        if not sport_endpoint:
            raise ValueError(f"Unknown sport: {sport}")
        
        today = datetime.now()
        start_date = today - timedelta(days=days_back)
        
        params = {
            'from': start_date.strftime('%Y-%m-%d'),
            'to': today.strftime('%Y-%m-%d')
        }
        
        # Add league/season filters where applicable
        league_id = self.LEAGUE_IDS.get(sport.lower())
        if league_id:
            params['league'] = league_id
            params['season'] = today.year
        
        endpoint = f"{sport_endpoint}/fixtures"
        response = self._make_request(endpoint, params)
        
        return response.get('response', [])
    
    def get_standings(self, sport: str, league_id: Optional[int] = None) -> List[Dict]:
        """
        Get standings/rankings for a sport
        
        Args:
            sport: Sport name
            league_id: Optional league ID (uses default if not provided)
            
        Returns:
            Standings data
        """
        sport_endpoint = self.SPORT_ENDPOINTS.get(sport.lower())
        if not sport_endpoint:
            raise ValueError(f"Unknown sport: {sport}")
        
        league_id = league_id or self.LEAGUE_IDS.get(sport.lower())
        if not league_id:
            # For sports without a default league, return empty
            return []
        
        params = {
            'league': league_id,
            'season': datetime.now().year
        }
        
        endpoint = f"{sport_endpoint}/standings"
        response = self._make_request(endpoint, params)
        
        return response.get('response', [])
    
    def get_team_statistics(self, sport: str, team_id: int, league_id: Optional[int] = None) -> Dict:
        """
        Get team statistics
        
        Args:
            sport: Sport name
            team_id: Team ID
            league_id: Optional league ID (uses default if not provided)
            
        Returns:
            Team statistics
        """
        sport_endpoint = self.SPORT_ENDPOINTS.get(sport.lower())
        if not sport_endpoint:
            raise ValueError(f"Unknown sport: {sport}")
        
        league_id = league_id or self.LEAGUE_IDS.get(sport.lower())
        if not league_id:
            return {}
        
        params = {
            'league': league_id,
            'season': datetime.now().year,
            'team': team_id
        }
        
        endpoint = f"{sport_endpoint}/teams/statistics"
        response = self._make_request(endpoint, params)
        
        return response.get('response', {})
    
    def get_player_statistics(self, sport: str, player_id: int, league_id: Optional[int] = None) -> Dict:
        """
        Get player statistics
        
        Args:
            sport: Sport name
            player_id: Player ID
            league_id: Optional league ID (uses default if not provided)
            
        Returns:
            Player statistics
        """
        sport_endpoint = self.SPORT_ENDPOINTS.get(sport.lower())
        if not sport_endpoint:
            raise ValueError(f"Unknown sport: {sport}")
        
        league_id = league_id or self.LEAGUE_IDS.get(sport.lower())
        if not league_id:
            return {}
        
        params = {
            'league': league_id,
            'season': datetime.now().year,
            'player': player_id
        }
        
        endpoint = f"{sport_endpoint}/players"
        response = self._make_request(endpoint, params)
        
        return response.get('response', {})
    
    def get_all_teams(self, sport: str, league_id: Optional[int] = None) -> List[str]:
        """
        Get all teams for a sport
        
        Args:
            sport: Sport name
            league_id: Optional league ID (uses default if not provided)
            
        Returns:
            List of team names
        """
        sport_endpoint = self.SPORT_ENDPOINTS.get(sport.lower())
        if not sport_endpoint:
            return []
        
        league_id = league_id or self.LEAGUE_IDS.get(sport.lower())
        if not league_id:
            return []
        
        teams = []
        try:
            # Try to get teams from standings
            standings = self.get_standings(sport, league_id)
            for standing_group in standings:
                if isinstance(standing_group, dict) and 'league' in standing_group:
                    league_data = standing_group.get('league', {})
                    standings_data = league_data.get('standings', [])
                    for group in standings_data:
                        if isinstance(group, list):
                            for team_data in group:
                                if isinstance(team_data, dict) and 'team' in team_data:
                                    team_name = team_data['team'].get('name', '')
                                    if team_name and team_name not in teams:
                                        teams.append(team_name)
            
            # Also try teams endpoint if available
            params = {
                'league': league_id,
                'season': datetime.now().year
            }
            endpoint = f"{sport_endpoint}/teams"
            response = self._make_request(endpoint, params)
            api_teams = response.get('response', [])
            
            for team_data in api_teams:
                if isinstance(team_data, dict) and 'team' in team_data:
                    team_name = team_data['team'].get('name', '')
                    if team_name and team_name not in teams:
                        teams.append(team_name)
        except Exception:
            pass
        
        return sorted(teams)
    
    def get_all_players(self, sport: str, league_id: Optional[int] = None) -> List[str]:
        """
        Get all players/drivers for a sport
        
        Args:
            sport: Sport name
            league_id: Optional league ID (uses default if not provided)
            
        Returns:
            List of player/driver names
        """
        sport_endpoint = self.SPORT_ENDPOINTS.get(sport.lower())
        if not sport_endpoint:
            return []
        
        players = []
        try:
            league_id = league_id or self.LEAGUE_IDS.get(sport.lower())
            
            if sport.lower() == 'formula1':
                # For F1, get drivers from standings
                standings = self.get_standings(sport, league_id)
                for standing_group in standings:
                    if isinstance(standing_group, dict) and 'league' in standing_group:
                        league_data = standing_group.get('league', {})
                        standings_data = league_data.get('standings', [])
                        for group in standings_data:
                            if isinstance(group, list):
                                for driver_data in group:
                                    if isinstance(driver_data, dict) and 'driver' in driver_data:
                                        driver_name = driver_data['driver'].get('name', '')
                                        if driver_name and driver_name not in players:
                                            players.append(driver_name)
            elif league_id:
                # For other sports, try players endpoint
                params = {
                    'league': league_id,
                    'season': datetime.now().year
                }
                endpoint = f"{sport_endpoint}/players"
                response = self._make_request(endpoint, params)
                api_players = response.get('response', [])
                
                for player_data in api_players:
                    if isinstance(player_data, dict) and 'player' in player_data:
                        player_name = player_data['player'].get('name', '')
                        if player_name and player_name not in players:
                            players.append(player_name)
        except Exception:
            pass
        
        return sorted(players)
    
    def get_all_sports_dashboard_data(self) -> Dict[str, Dict]:
        """
        Get all dashboard data for all supported sports
        
        Returns:
            Dictionary with data for each sport
        """
        sports = ['nfl', 'nhl', 'nba', 'mlb', 'cricket', 'formula1', 'tennis', 'golf']
        dashboard_data = {}
        
        for sport in sports:
            try:
                print(f"Fetching data for {sport.upper()}...")
                dashboard_data[sport] = {
                    'upcoming_games': self.get_upcoming_games(sport),
                    'recent_scores': self.get_recent_scores(sport),
                    'standings': self.get_standings(sport)
                }
            except Exception as e:
                print(f"Error fetching {sport}: {str(e)}")
                dashboard_data[sport] = {
                    'upcoming_games': [],
                    'recent_scores': [],
                    'standings': [],
                    'error': str(e)
                }
        
        return dashboard_data
    
    # Sport-specific helper methods
    
    def get_nfl_data(self) -> Dict:
        """Get all NFL data"""
        return {
            'upcoming_games': self.get_upcoming_games('nfl'),
            'recent_scores': self.get_recent_scores('nfl'),
            'standings': self.get_standings('nfl')
        }
    
    def get_nhl_data(self) -> Dict:
        """Get all NHL data"""
        return {
            'upcoming_games': self.get_upcoming_games('nhl'),
            'recent_scores': self.get_recent_scores('nhl'),
            'standings': self.get_standings('nhl')
        }
    
    def get_nba_data(self) -> Dict:
        """Get all NBA data"""
        return {
            'upcoming_games': self.get_upcoming_games('nba'),
            'recent_scores': self.get_recent_scores('nba'),
            'standings': self.get_standings('nba')
        }
    
    def get_mlb_data(self) -> Dict:
        """Get all MLB data"""
        return {
            'upcoming_games': self.get_upcoming_games('mlb'),
            'recent_scores': self.get_recent_scores('mlb'),
            'standings': self.get_standings('mlb')
        }
    
    def get_cricket_data(self) -> Dict:
        """Get all Cricket data"""
        return {
            'upcoming_games': self.get_upcoming_games('cricket'),
            'recent_scores': self.get_recent_scores('cricket'),
            'standings': []  # Cricket standings vary by league
        }
    
    def get_formula1_data(self) -> Dict:
        """Get all Formula 1 data"""
        return {
            'upcoming_games': self.get_upcoming_games('formula1'),  # Upcoming races
            'recent_scores': self.get_recent_scores('formula1'),  # Recent race results
            'standings': self.get_standings('formula1')  # Driver/Constructor standings
        }
    
    def get_tennis_data(self) -> Dict:
        """Get all Tennis data"""
        return {
            'upcoming_games': self.get_upcoming_games('tennis'),
            'recent_scores': self.get_recent_scores('tennis'),
            'standings': []  # Tennis rankings are separate endpoint
        }
    
    def get_golf_data(self) -> Dict:
        """Get all Golf data"""
        return {
            'upcoming_games': self.get_upcoming_games('golf'),  # Upcoming tournaments
            'recent_scores': self.get_recent_scores('golf'),  # Recent tournament results
            'standings': []  # Golf rankings are separate endpoint
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize client (API key from environment variable or pass directly)
    # client = SportsAPIClient(api_key="your_api_key_here")
    client = SportsAPIClient()  # Uses API_SPORTS_KEY env variable
    
    # Get data for a specific sport
    print("Fetching NFL data...")
    nfl_data = client.get_nfl_data()
    print(f"NFL Upcoming Games: {len(nfl_data['upcoming_games'])}")
    print(f"NFL Recent Scores: {len(nfl_data['recent_scores'])}")
    
    # Get all sports data at once
    print("\nFetching all sports data...")
    all_data = client.get_all_sports_dashboard_data()
    
    # Print summary
    for sport, data in all_data.items():
        print(f"\n{sport.upper()}:")
        print(f"  Upcoming: {len(data.get('upcoming_games', []))}")
        print(f"  Recent: {len(data.get('recent_scores', []))}")
        print(f"  Standings: {len(data.get('standings', []))}")

