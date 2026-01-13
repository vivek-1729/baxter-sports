"""
API Adapter - Transforms ESPN/MLB API data to match dummy data format
This ensures seamless integration without changing the UI code
"""

from datetime import datetime, timezone
from typing import Dict, List


def parse_datetime_safe(date_str: str) -> datetime:
    """
    Parse a date string and ALWAYS return a timezone-aware UTC datetime
    
    Handles multiple formats:
    - ISO with timezone: "2024-01-12T19:00:00Z"
    - ISO without timezone: "2024-01-12T19:00:00"
    - Date only: "2024-01-12"
    
    Args:
        date_str: Date string to parse
        
    Returns:
        Timezone-aware datetime in UTC
    """
    try:
        if 'T' in date_str:
            # Has time component
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            # Date only
            dt = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Ensure timezone-aware (assume UTC if naive)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        return dt
    except Exception as e:
        print(f"⚠️  Error parsing date '{date_str}': {e}")
        return datetime.now(timezone.utc)


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
    now = datetime.now(timezone.utc)  # ALWAYS use timezone-aware!
    
    live = []
    upcoming = []
    recent = []
    
    for game in games:
        status_short = game['fixture']['status']['short']
        
        try:
            # Use safe date parser (always returns timezone-aware)
            game_date = parse_datetime_safe(game['fixture']['date'])
            time_diff = (now - game_date).total_seconds() / 3600  # hours
        except Exception as e:
            print(f"⚠️  Error in game date comparison: {e}")
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


# ==========================================
# NEW SPORTS TRANSFORMERS
# ==========================================

def transform_cricket_match_to_dummy(match: Dict) -> Dict:
    """Transform cricket match to dummy format"""
    teams = match.get('teams', [])
    scores = match.get('scores', {})
    
    return {
        'fixture': {
            'id': f"cricket_{match.get('date', '')}_{teams[0] if teams else 'unknown'}",
            'date': match.get('start_time', match.get('date')),
            'status': {
                'short': 'LIVE' if match.get('status') == 'Live' else 'NS' if match.get('status') == 'Upcoming' else 'FT',
                'long': match.get('status', 'Scheduled')
            },
            'venue': {'name': match.get('venue', ''), 'city': ''}
        },
        'is_completed': match.get('status') == 'Complete',
        'league': {'name': 'CRICKET', 'country': 'International'},
        'teams': {
            'home': {
                'name': teams[0] if len(teams) > 0 else 'TBD',
                'logo': f"/static/images/cricket/{teams[0].lower().replace(' ', '_')}.png" if len(teams) > 0 else "",
                'score': scores.get(teams[0], '') if scores and len(teams) > 0 else None
            },
            'away': {
                'name': teams[1] if len(teams) > 1 else 'TBD',
                'logo': f"/static/images/cricket/{teams[1].lower().replace(' ', '_')}.png" if len(teams) > 1 else "",
                'score': scores.get(teams[1], '') if scores and len(teams) > 1 else None
            }
        },
        'goals': {
            'home': scores.get(teams[0], None) if scores and len(teams) > 0 else None,
            'away': scores.get(teams[1], None) if scores and len(teams) > 1 else None
        },
        'match_type': match.get('match_type', 'ODI'),
        'series': match.get('series', ''),
        'result': match.get('result', '')
    }


def transform_tennis_match_to_dummy(event: Dict, competition: Dict) -> Dict:
    """Transform tennis match to dummy format (individual sport)"""
    competitors = competition.get('competitors', [])
    
    if len(competitors) >= 2:
        player1 = competitors[0].get('athlete', {})
        player2 = competitors[1].get('athlete', {})
        
        return {
            'fixture': {
                'id': competition.get('id'),
                'date': competition.get('date'),
                'status': {
                    'short': 'LIVE' if competition.get('status', {}).get('type', {}).get('state') == 'in' else 'FT' if competition.get('status', {}).get('type', {}).get('state') == 'post' else 'NS',
                    'long': competition.get('status', {}).get('type', {}).get('description', 'Scheduled')
                },
                'venue': {'name': event.get('name', ''), 'city': ''}
            },
            'is_completed': competition.get('status', {}).get('type', {}).get('state') == 'post',
            'league': {'name': 'TENNIS', 'country': 'ATP/WTA'},
            'teams': {
                'home': {
                    'name': player1.get('displayName', 'Player 1'),
                    'logo': '',
                    'country': player1.get('flag', {}).get('alt', ''),
                    'rank': player1.get('rank', 'N/A'),
                    'score': competitors[0].get('score', '')
                },
                'away': {
                    'name': player2.get('displayName', 'Player 2'),
                    'logo': '',
                    'country': player2.get('flag', {}).get('alt', ''),
                    'rank': player2.get('rank', 'N/A'),
                    'score': competitors[1].get('score', '')
                }
            },
            'goals': {
                'home': competitors[0].get('score', None),
                'away': competitors[1].get('score', None)
            },
            'tournament': event.get('name', '')
        }
    return None


def transform_golf_event_to_dummy(event: Dict) -> Dict:
    """Transform golf tournament to dummy format"""
    tournament_name = event.get('name', 'PGA Tournament')
    
    return {
        'fixture': {
            'id': event.get('id'),
            'date': event.get('date'),
            'status': {
                'short': 'LIVE' if event.get('status', {}).get('type', {}).get('state') == 'in' else 'FT' if event.get('status', {}).get('type', {}).get('state') == 'post' else 'NS',
                'long': event.get('status', {}).get('type', {}).get('description', 'Scheduled')
            },
            'venue': {'name': tournament_name, 'city': ''}
        },
        'is_completed': event.get('status', {}).get('type', {}).get('state') == 'post',
        'league': {'name': 'GOLF', 'country': 'PGA'},
        'teams': {
            'home': {
                'name': tournament_name,
                'logo': ''
            },
            'away': {
                'name': 'Field',
                'logo': ''
            }
        },
        'goals': {
            'home': None,
            'away': None
        },
        'tournament': tournament_name,
        'competitors': []  # Will be populated with player standings
    }


def transform_f1_race_to_dummy(race: Dict) -> Dict:
    """Transform F1 race to dummy format"""
    race_name = race.get('race_name', 'Grand Prix')
    circuit = race.get('circuit', '')
    
    return {
        'fixture': {
            'id': f"f1_{race.get('round', '')}_{race.get('date', '')}",
            'date': race.get('date', ''),
            'status': {
                'short': 'NS',  # Most races will be upcoming
                'long': 'Scheduled'
            },
            'venue': {'name': circuit, 'city': race.get('location', '')}
        },
        'is_completed': False,
        'league': {'name': 'FORMULA 1', 'country': race.get('country', '')},
        'teams': {
            'home': {
                'name': race_name,
                'logo': ''
            },
            'away': {
                'name': circuit,
                'logo': ''
            }
        },
        'goals': {
            'home': None,
            'away': None
        },
        'race_name': race_name,
        'circuit': circuit,
        'round': race.get('round', ''),
        'season': race.get('season', '')
    }

