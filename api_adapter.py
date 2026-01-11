"""
API Adapter - Transforms ESPN/MLB API data to match dummy data format
This ensures seamless integration without changing the UI code
"""

from datetime import datetime
from typing import Dict, List


def transform_game_to_dummy_format(game: Dict, sport: str) -> Dict:
    """
    Transform ESPN/MLB game data to dummy data format
    
    Args:
        game: Raw game data from ESPN or MLB API
        sport: Sport key (nba, nfl, nhl, mlb)
        
    Returns:
        Game data in dummy format
    """
    # Determine status short code and completion status
    status = game.get('status', '')
    is_live = game.get('is_live', False)
    is_completed = game.get('is_completed', False) or status in ['Final', 'Final/OT', 'Final/SO']
    
    if is_live:
        status_short = 'LIVE'
    elif is_completed:
        status_short = 'FT'
    else:
        status_short = 'NS'  # Not Started
    
    # Build dummy format
    return {
        'fixture': {
            'id': game.get('id'),
            'date': game.get('date'),
            'status': {'short': status_short, 'long': status},
            'venue': {'name': '', 'city': ''}
        },
        'is_completed': is_completed,
        'league': {
            'name': sport.upper(),
            'country': 'USA'
        },
        'teams': {
            'home': {
                'id': game['home'].get('team', ''),
                'name': game['home'].get('team', ''),
                'logo': game['home'].get('logo', ''),
                'abbreviation': game['home'].get('abbreviation', '')
            },
            'away': {
                'id': game['away'].get('team', ''),
                'name': game['away'].get('team', ''),
                'logo': game['away'].get('logo', ''),
                'abbreviation': game['away'].get('abbreviation', '')
            }
        },
        'goals': {
            'home': game['home'].get('score'),
            'away': game['away'].get('score')
        },
        'sport': {
            'name': sport.upper(),
            'type': 'team'
        },
        'sport_key': sport
    }


def transform_games_list(games: List[Dict], sport: str) -> List[Dict]:
    """
    Transform a list of games to dummy format
    
    Args:
        games: List of raw game data
        sport: Sport key
        
    Returns:
        List of games in dummy format
    """
    return [transform_game_to_dummy_format(game, sport) for game in games]


def transform_standings_to_dummy_format(standings: List[Dict], sport: str) -> List[Dict]:
    """
    Transform ESPN/MLB standings to dummy format
    
    Args:
        standings: Raw standings data
        sport: Sport key
        
    Returns:
        Standings in dummy format
    """
    if not standings:
        return []
    
    # Convert standings to dummy format
    standings_data = []
    for team in standings:
        standings_data.append({
            'rank': team.get('divisionRank', len(standings_data) + 1),  # Use division rank
            'team': {
                'name': team.get('team', ''),
                'logo': team.get('logo', ''),
                'abbreviation': team.get('abbreviation', '')
            },
            'points': team.get('wins', 0) * 3,  # Simple point system
            'all': {
                'played': team.get('wins', 0) + team.get('losses', 0),
                'win': team.get('wins', 0),
                'lose': team.get('losses', 0)
            },
            'wins': team.get('wins', 0),
            'losses': team.get('losses', 0),
            'winPercent': team.get('winPercent', 0),
            'division': team.get('division', '')
        })
    
    return [{
        'league': {
            'name': sport.upper(),
            'standings': [standings_data]
        }
    }]


def separate_games_by_status(games: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Separate games into live, upcoming, and recent based on status
    
    Args:
        games: List of games in dummy format
        
    Returns:
        Dict with 'live', 'upcoming', 'recent' keys
    """
    now = datetime.now()
    
    live = []
    upcoming = []
    recent = []
    
    for game in games:
        status_short = game['fixture']['status']['short']
        
        try:
            game_date = datetime.fromisoformat(game['fixture']['date'].replace('Z', ''))
            time_diff = (now - game_date).total_seconds() / 3600  # hours
        except:
            time_diff = 0
        
        if status_short == 'LIVE':
            live.append(game)
        elif status_short == 'FT':
            recent.append(game)
        elif time_diff < -2:  # Game is more than 2 hours in future
            upcoming.append(game)
        elif time_diff > 2:  # Game was more than 2 hours ago
            recent.append(game)
        else:
            # Close to game time, consider it upcoming
            upcoming.append(game)
    
    return {
        'live': live,
        'upcoming': upcoming,
        'recent': recent
    }

