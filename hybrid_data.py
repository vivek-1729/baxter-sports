"""
Hybrid Data Source - Uses real API data when available, dummy data as fallback
"""

from typing import Dict, List
from datetime import datetime, timedelta
from dummy_data import (
    get_dummy_fixtures, 
    get_dummy_results, 
    get_dummy_live_events,
    get_dummy_standings,
    get_dummy_news,
    get_dummy_stats
)
from smart_cache import cached_call, CACHE_DURATIONS

# Import real API functions
try:
    from sports_backend import (
        get_live_games,
        get_upcoming_games,
        get_recent_games,
        get_standings
    )
    from api_adapter import (
        transform_games_list,
        transform_standings_to_dummy_format,
        separate_games_by_status
    )
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

# Sports that have real API data available
REAL_DATA_SPORTS = ['nba', 'nfl', 'nhl', 'mlb']


def get_live_data() -> Dict[str, List[Dict]]:
    """
    Get live games using real API when available, dummy data as fallback
    CACHED: 30 seconds (live data changes quickly)
    
    Returns:
        Dict mapping sport to list of live games
    """
    def _fetch():
        live_data = {}
        dummy = get_dummy_live_events()
        
        for sport in ['nfl', 'nhl', 'nba', 'mlb', 'cricket', 'formula1', 'tennis', 'golf']:
            if sport in REAL_DATA_SPORTS and API_AVAILABLE:
                try:
                    # Get real live games
                    raw_games = get_live_games(sport)
                    live_data[sport] = transform_games_list(raw_games, sport)
                except Exception as e:
                    print(f"⚠️  API error for {sport} live games: {e}, using dummy data")
                    live_data[sport] = dummy.get(sport, [])
            else:
                # Use dummy data for unsupported sports
                live_data[sport] = dummy.get(sport, [])
        
        return live_data
    
    return cached_call('live_games_all', _fetch, ttl_seconds=CACHE_DURATIONS['live_games'])


def get_upcoming_data() -> Dict[str, List[Dict]]:
    """
    Get upcoming games using real API when available, dummy data as fallback
    CACHED: 10 minutes (schedules don't change often)
    
    Returns:
        Dict mapping sport to list of upcoming games
    """
    def _fetch():
        upcoming_data = {}
        dummy = get_dummy_fixtures()
        
        for sport in ['nfl', 'nhl', 'nba', 'mlb', 'cricket', 'formula1', 'tennis', 'golf']:
            if sport in REAL_DATA_SPORTS and API_AVAILABLE:
                try:
                    # Get real upcoming games (next 3 days for speed)
                    raw_games = get_upcoming_games(sport, days=3)
                    all_games = transform_games_list(raw_games, sport)
                    
                    # Separate by status and get only upcoming
                    separated = separate_games_by_status(all_games)
                    upcoming_data[sport] = separated['upcoming']
                except Exception as e:
                    print(f"⚠️  API error for {sport} upcoming games: {e}, using dummy data")
                    upcoming_data[sport] = dummy.get(sport, [])
            else:
                # Use dummy data for unsupported sports
                upcoming_data[sport] = dummy.get(sport, [])
        
        return upcoming_data
    
    return cached_call('upcoming_games_all', _fetch, ttl_seconds=CACHE_DURATIONS['upcoming_games'])


def get_recent_data() -> Dict[str, List[Dict]]:
    """
    Get recent games using real API when available, dummy data as fallback
    CACHED: 5 minutes (recent results don't change once final)
    
    Returns:
        Dict mapping sport to list of recent games
    """
    def _fetch():
        recent_data = {}
        dummy = get_dummy_results()
        
        for sport in ['nfl', 'nhl', 'nba', 'mlb', 'cricket', 'formula1', 'tennis', 'golf']:
            if sport in REAL_DATA_SPORTS and API_AVAILABLE:
                try:
                    # Get real recent games (last 3 days for speed)
                    raw_games = get_recent_games(sport, days=3)
                    all_games = transform_games_list(raw_games, sport)
                    
                    # Separate by status and get only recent
                    separated = separate_games_by_status(all_games)
                    recent_data[sport] = separated['recent']
                except Exception as e:
                    print(f"⚠️  API error for {sport} recent games: {e}, using dummy data")
                    recent_data[sport] = dummy.get(sport, [])
            else:
                # Use dummy data for unsupported sports
                recent_data[sport] = dummy.get(sport, [])
        
        return recent_data
    
    return cached_call('recent_games_all', _fetch, ttl_seconds=CACHE_DURATIONS['recent_games'])


def get_standings_data(sport: str) -> List[Dict]:
    """
    Get standings using real API when available, dummy data as fallback
    CACHED: 1 hour (standings update slowly)
    
    Args:
        sport: Sport key
        
    Returns:
        Standings data
    """
    def _fetch():
        if sport in REAL_DATA_SPORTS and API_AVAILABLE:
            try:
                # Get real standings
                raw_standings = get_standings(sport)
                return transform_standings_to_dummy_format(raw_standings, sport)
            except Exception as e:
                print(f"⚠️  API error for {sport} standings: {e}, using dummy data")
                return get_dummy_standings(sport)
        else:
            # Use dummy data for unsupported sports
            return get_dummy_standings(sport)
    
    return cached_call(f'standings_{sport}', _fetch, ttl_seconds=CACHE_DURATIONS['standings'])


# News still uses dummy data (no API available yet)
def get_news_data(team_name: str) -> List[Dict]:
    """Get news - currently only dummy data available"""
    return get_dummy_news(team_name)


def get_team_stats_from_standings(sport_key: str, team_name: str) -> Dict:
    """
    Extract a specific team's stats from standings data
    
    This is SMART - we already have standings cached, just extract the team!
    
    Args:
        sport_key: Sport identifier (nba, nfl, etc.)
        team_name: Team name to look for
        
    Returns:
        Dict with wins, losses, win_percentage, rank, or None if not found
    """
    if not team_name or sport_key not in REAL_DATA_SPORTS:
        return None
    
    try:
        # Get standings (already cached!)
        standings_data = get_standings_data(sport_key)
        
        if not standings_data:
            return None
        
        # Navigate the standings structure
        for standing_group in standings_data:
            if 'league' not in standing_group:
                continue
            
            for standings_list in standing_group['league'].get('standings', []):
                for team in standings_list:
                    # Match team name (case-insensitive, flexible matching)
                    team_obj = team.get('team', {})
                    api_team_name = team_obj.get('name', '') if isinstance(team_obj, dict) else str(team_obj)
                    
                    # Try matching full name or abbreviation
                    if (team_name.lower() in api_team_name.lower() or 
                        api_team_name.lower() in team_name.lower()):
                        
                        return {
                            'wins': team.get('wins', 0),
                            'losses': team.get('losses', 0),
                            'win_percentage': team.get('winPercent', 0),
                            'rank': team.get('rank', 0),
                            'points_per_game': 0  # Not available yet
                        }
        
        return None
    except Exception as e:
        print(f"⚠️  Error extracting stats for {team_name} in {sport_key}: {e}")
        return None


def get_stats_data(team_name: str, sport_key: str = None) -> Dict:
    """
    Get team stats - uses REAL data from standings when available!
    
    Args:
        team_name: Team name
        sport_key: Sport identifier (optional for backwards compatibility)
        
    Returns:
        Dict with wins, losses, win_percentage, rank
    """
    # Try to get real stats from standings
    if sport_key:
        real_stats = get_team_stats_from_standings(sport_key, team_name)
        if real_stats:
            return real_stats
    
    # Fallback to dummy data
    return get_dummy_stats(team_name)


# Convenience function to get all dashboard data at once
def get_all_dashboard_data(selected_sports: List[str]) -> Dict:
    """
    Get all data needed for dashboard
    
    Args:
        selected_sports: List of sport keys
        
    Returns:
        Dict with live, upcoming, recent data
    """
    all_live = get_live_data()
    all_upcoming = get_upcoming_data()
    all_recent = get_recent_data()
    
    # Filter to only selected sports
    return {
        'live': {sport: all_live.get(sport, []) for sport in selected_sports},
        'upcoming': {sport: all_upcoming.get(sport, []) for sport in selected_sports},
        'recent': {sport: all_recent.get(sport, []) for sport in selected_sports}
    }


def get_sport_games(sport_key: str) -> Dict:
    """
    Get games for a single sport page - REUSES dashboard cache for ZERO API calls!
    
    This is SMART:
    - Dashboard already fetched all sports data and cached it
    - We just read from that SAME cache (no new API calls)
    - Live: Dummy data (no API support yet)
    - Upcoming: Real data from cache (limited to 8 for 2 rows)
    - Recent: Real data from cache (limited to 8 for 2 rows)
    
    Performance: ~10-50ms (just reading from cache) ⚡
    
    Args:
        sport_key: Sport identifier (nba, nfl, etc.)
        
    Returns:
        Dict with 'live', 'upcoming', 'recent' game lists
    """
    # Read from SAME cache keys that dashboard uses (already warmed!)
    all_upcoming = get_upcoming_data()
    all_recent = get_recent_data()
    
    # Extract this sport's data (already cached, zero API calls!)
    upcoming = all_upcoming.get(sport_key, [])[:8]  # Limit to 8 for 2 rows
    recent = all_recent.get(sport_key, [])[:8]      # Limit to 8 for 2 rows
    
    # Live: Use dummy data for now (no live game API yet)
    live_dummy = get_dummy_live_events()
    live = live_dummy.get(sport_key, [])
    
    # If no real data found, fallback to dummy
    if not upcoming:
        upcoming = get_dummy_fixtures().get(sport_key, [])[:8]
    if not recent:
        recent = get_dummy_results().get(sport_key, [])[:8]
    
    return {
        'live': live,
        'upcoming': upcoming,
        'recent': recent
    }

