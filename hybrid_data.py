"""
Hybrid Data Source - Uses real API data when available, dummy data as fallback
"""

from typing import Dict, List
from datetime import datetime, timedelta, timezone
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
        get_standings,
        # New sports
        get_cricket_fixtures,
        get_cricket_results,
        get_tennis_matches,
        get_tennis_rankings,
        get_golf_tournament,
        get_f1_schedule,
        get_f1_next_race
    )
    from api_adapter import (
        transform_games_list,
        transform_standings_to_dummy_format,
        separate_games_by_status,
        parse_datetime_safe,
        # New sport transformers
        transform_cricket_match_to_dummy,
        transform_tennis_match_to_dummy,
        transform_golf_event_to_dummy,
        transform_f1_race_to_dummy
    )
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    # Define a fallback if API not available
    def parse_datetime_safe(date_str: str) -> datetime:
        try:
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except:
            return datetime.now(timezone.utc)

# Sports that have real API data available
REAL_DATA_SPORTS = ['nba', 'nfl', 'nhl', 'mlb', 'cricket', 'tennis', 'golf', 'formula1']


def _is_game_in_past(game: Dict) -> bool:
    """
    Check if a game's date/time has passed (client-side check)
    
    Args:
        game: Game dict in dummy format
        
    Returns:
        True if game date has passed, False otherwise
    """
    try:
        game_date_str = game['fixture']['date']
        
        # Use safe date parser (always returns timezone-aware)
        game_date = parse_datetime_safe(game_date_str)
        
        # Get current time in UTC
        now = datetime.now(timezone.utc)
        
        # Game is in past if it's more than 2 hours ago (accounting for game duration)
        time_diff_hours = (now - game_date).total_seconds() / 3600
        return time_diff_hours > 2
    except Exception as e:
        print(f"⚠️  Error checking game date: {e}")
        return False


def _recategorize_by_time(upcoming_games: Dict[str, List[Dict]], recent_games: Dict[str, List[Dict]]) -> tuple[Dict[str, List[Dict]], Dict[str, List[Dict]]]:
    """
    Move games from upcoming to recent if their date has passed (client-side logic)
    
    Args:
        upcoming_games: Dict of sport -> list of upcoming games
        recent_games: Dict of sport -> list of recent games
        
    Returns:
        Tuple of (updated_upcoming, updated_recent)
    """
    updated_upcoming = {}
    updated_recent = {}
    
    for sport in upcoming_games.keys():
        still_upcoming = []
        moved_to_recent = []
        
        for game in upcoming_games.get(sport, []):
            if _is_game_in_past(game):
                # Mark as completed
                game['is_completed'] = True
                game['fixture']['status']['short'] = 'FT'
                moved_to_recent.append(game)
            else:
                still_upcoming.append(game)
        
        updated_upcoming[sport] = still_upcoming
        
        # Merge moved games with existing recent games
        existing_recent = recent_games.get(sport, [])
        updated_recent[sport] = moved_to_recent + existing_recent
    
    # Add sports that weren't in upcoming but are in recent
    for sport in recent_games.keys():
        if sport not in updated_recent:
            updated_recent[sport] = recent_games[sport]
    
    return updated_upcoming, updated_recent


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
                    # Handle new sports with custom data functions
                    if sport == 'cricket':
                        cricket_data = get_cricket_data()
                        upcoming_data[sport] = cricket_data.get('upcoming', [])
                    elif sport == 'tennis':
                        tennis_data = get_tennis_data()
                        # Filter for upcoming/live matches
                        all_matches = tennis_data.get('matches', [])
                        upcoming_data[sport] = [m for m in all_matches if not m.get('is_completed')]
                    elif sport == 'golf':
                        golf_data = get_golf_data()
                        # Golf tournaments are ongoing
                        upcoming_data[sport] = golf_data.get('tournament', [])
                    elif sport == 'formula1':
                        f1_data = get_f1_data()
                        # Get upcoming races from schedule
                        from datetime import datetime, timezone
                        now = datetime.now(timezone.utc)
                        all_races = f1_data.get('schedule', [])
                        upcoming_data[sport] = [r for r in all_races if not r.get('is_completed')]
                    else:
                        # Traditional team sports (NBA, NFL, NHL, MLB)
                        raw_games = get_upcoming_games(sport, days=3)
                        all_games = transform_games_list(raw_games, sport)
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
                    # Handle new sports with custom data functions
                    if sport == 'cricket':
                        cricket_data = get_cricket_data()
                        recent_data[sport] = cricket_data.get('recent', [])
                    elif sport == 'tennis':
                        tennis_data = get_tennis_data()
                        # Filter for completed matches
                        all_matches = tennis_data.get('matches', [])
                        recent_data[sport] = [m for m in all_matches if m.get('is_completed')]
                    elif sport == 'golf':
                        # Golf doesn't have "recent" concept, skip
                        recent_data[sport] = []
                    elif sport == 'formula1':
                        # F1 recent races would come from completed races in schedule
                        recent_data[sport] = []  # TODO: Add F1 recent race results
                    else:
                        # Traditional team sports (NBA, NFL, NHL, MLB)
                        raw_games = get_recent_games(sport, days=7)
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


def get_timeline_data() -> tuple[Dict[str, List[Dict]], Dict[str, List[Dict]]]:
    """
    Get upcoming and recent games with SMART client-side re-categorization
    
    This ensures games are properly moved from upcoming to recent based on current time,
    even if the cache hasn't expired yet.
    
    Returns:
        Tuple of (upcoming_games, recent_games) with real-time categorization
    """
    # Get cached data
    upcoming = get_upcoming_data()
    recent = get_recent_data()
    
    # Re-categorize based on current time (moves past games from upcoming to recent)
    updated_upcoming, updated_recent = _recategorize_by_time(upcoming, recent)
    
    return updated_upcoming, updated_recent


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
                            'division': team.get('division', 'Conference'),
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


# ==========================================
# NEW SPORTS DATA FUNCTIONS
# ==========================================

def get_cricket_data(team_filter=None):
    """
    Get cricket fixtures and results
    
    Args:
        team_filter: Optional team name to filter
        
    Returns:
        Dict with 'upcoming' and 'recent' match lists
    """
    if not API_AVAILABLE or 'cricket' not in REAL_DATA_SPORTS:
        return {
            'upcoming': get_dummy_fixtures().get('cricket', []),
            'recent': get_dummy_results().get('cricket', [])
        }
    
    try:
        # Use cached calls for performance
        upcoming_raw = cached_call(
            'cricket_upcoming',
            lambda: get_cricket_fixtures(team_filter),
            CACHE_DURATIONS.get('cricket_upcoming', 86400)
        )
        
        recent_raw = cached_call(
            f'cricket_recent_{team_filter or "all"}',
            lambda: get_cricket_results(days=7, team_filter=team_filter),
            CACHE_DURATIONS.get('cricket_recent', 3600)
        )
        
        # Transform to dummy format
        upcoming = [transform_cricket_match_to_dummy(m) for m in (upcoming_raw or [])]
        recent = [transform_cricket_match_to_dummy(m) for m in (recent_raw or [])]
        
        return {
            'upcoming': upcoming,
            'recent': recent
        }
    except Exception as e:
        print(f"Error fetching cricket data: {e}")
        return {
            'upcoming': get_dummy_fixtures().get('cricket', []),
            'recent': get_dummy_results().get('cricket', [])
        }


def get_tennis_data():
    """
    Get tennis matches and rankings
    
    Returns:
        Dict with 'matches' and 'rankings'
    """
    if not API_AVAILABLE or 'tennis' not in REAL_DATA_SPORTS:
        return {
            'matches': get_dummy_fixtures().get('tennis', []),
            'rankings': []
        }
    
    try:
        # Get ATP and WTA matches
        atp_data = cached_call(
            'tennis_atp',
            lambda: get_tennis_matches("atp"),
            CACHE_DURATIONS.get('tennis_matches', 1800)
        )
        
        wta_data = cached_call(
            'tennis_wta',
            lambda: get_tennis_matches("wta"),
            CACHE_DURATIONS.get('tennis_matches', 1800)
        )
        
        rankings = cached_call(
            'tennis_rankings',
            lambda: get_tennis_rankings("atp"),
            CACHE_DURATIONS.get('tennis_rankings', 86400)
        )
        
        # Transform matches
        matches = []
        for data in [atp_data, wta_data]:
            if data and "events" in data:
                for event in data["events"]:
                    if "groupings" in event:
                        for grouping in event["groupings"]:
                            for comp in grouping.get("competitions", []):
                                transformed = transform_tennis_match_to_dummy(event, comp)
                                if transformed:
                                    matches.append(transformed)
        
        return {
            'matches': matches,
            'rankings': rankings
        }
    except Exception as e:
        print(f"Error fetching tennis data: {e}")
        return {
            'matches': get_dummy_fixtures().get('tennis', []),
            'rankings': []
        }


def get_golf_data():
    """
    Get current golf tournament
    
    Returns:
        Dict with tournament data
    """
    if not API_AVAILABLE or 'golf' not in REAL_DATA_SPORTS:
        return {'tournament': get_dummy_fixtures().get('golf', [])}
    
    try:
        golf_data = cached_call(
            'golf_tournament',
            get_golf_tournament,
            CACHE_DURATIONS.get('golf_tournament', 3600)
        )
        
        # Transform tournament
        events = []
        if golf_data and "events" in golf_data:
            for event in golf_data["events"]:
                transformed = transform_golf_event_to_dummy(event)
                if transformed:
                    events.append(transformed)
        
        return {'tournament': events}
    except Exception as e:
        print(f"Error fetching golf data: {e}")
        return {'tournament': get_dummy_fixtures().get('golf', [])}


def get_f1_data():
    """
    Get F1 schedule and next race
    
    Returns:
        Dict with 'schedule' and 'next_race'
    """
    if not API_AVAILABLE or 'formula1' not in REAL_DATA_SPORTS:
        return {
            'schedule': get_dummy_fixtures().get('formula1', []),
            'next_race': None
        }
    
    try:
        schedule_raw = cached_call(
            'f1_schedule',
            lambda: get_f1_schedule("current"),
            CACHE_DURATIONS.get('f1_schedule', 604800)  # 7 days
        )
        
        next_race_raw = cached_call(
            'f1_next_race',
            get_f1_next_race,
            CACHE_DURATIONS.get('f1_next_race', 86400)  # 24 hours
        )
        
        # Transform races
        schedule = [transform_f1_race_to_dummy(r) for r in (schedule_raw or [])]
        next_race = transform_f1_race_to_dummy(next_race_raw) if next_race_raw else None
        
        return {
            'schedule': schedule,
            'next_race': next_race
        }
    except Exception as e:
        print(f"Error fetching F1 data: {e}")
        return {
            'schedule': get_dummy_fixtures().get('formula1', []),
            'next_race': None
        }

