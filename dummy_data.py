"""
Dummy data structure matching API-Sports.io format.
This will be replaced by real API calls to get_all_sports_dashboard_data()
"""

from datetime import datetime, timedelta
from typing import Dict, List


def get_dummy_fixtures() -> Dict[str, List[Dict]]:
    """Generate dummy fixture data matching API-Sports format"""
    now = datetime.now()
    
    return {
        'nfl': [
            {
                'fixture': {
                    'id': 1001,
                    'date': (now + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%S'),
                    'status': {'short': 'NS'},
                    'venue': {'name': 'Arrowhead Stadium', 'city': 'Kansas City'}
                },
                'league': {'name': 'NFL', 'country': 'USA'},
                'teams': {
                    'home': {'id': 1, 'name': 'Kansas City Chiefs', 'logo': ''},
                    'away': {'id': 2, 'name': 'Buffalo Bills', 'logo': ''}
                },
                'goals': {'home': None, 'away': None},
                'sport': {'name': 'NFL', 'type': 'team'}
            },
            {
                'fixture': {
                    'id': 1002,
                    'date': (now + timedelta(days=5)).strftime('%Y-%m-%dT%H:%M:%S'),
                    'status': {'short': 'NS'},
                    'venue': {'name': 'Lambeau Field', 'city': 'Green Bay'}
                },
                'league': {'name': 'NFL', 'country': 'USA'},
                'teams': {
                    'home': {'id': 3, 'name': 'Green Bay Packers', 'logo': ''},
                    'away': {'id': 4, 'name': 'Dallas Cowboys', 'logo': ''}
                },
                'goals': {'home': None, 'away': None},
                'sport': {'name': 'NFL', 'type': 'team'}
            },
            {
                'fixture': {
                    'id': 1004,
                    'date': (now + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%S'),
                    'status': {'short': 'NS'},
                    'venue': {'name': 'MetLife Stadium', 'city': 'East Rutherford'}
                },
                'league': {'name': 'NFL', 'country': 'USA'},
                'teams': {
                    'home': {'id': 7, 'name': 'New York Giants', 'logo': ''},
                    'away': {'id': 8, 'name': 'Philadelphia Eagles', 'logo': ''}
                },
                'goals': {'home': None, 'away': None},
                'sport': {'name': 'NFL', 'type': 'team'}
            },
            {
                'fixture': {
                    'id': 1005,
                    'date': (now + timedelta(days=4)).strftime('%Y-%m-%dT%H:%M:%S'),
                    'status': {'short': 'NS'},
                    'venue': {'name': 'Heinz Field', 'city': 'Pittsburgh'}
                },
                'league': {'name': 'NFL', 'country': 'USA'},
                'teams': {
                    'home': {'id': 9, 'name': 'Pittsburgh Steelers', 'logo': ''},
                    'away': {'id': 10, 'name': 'Cleveland Browns', 'logo': ''}
                },
                'goals': {'home': None, 'away': None},
                'sport': {'name': 'NFL', 'type': 'team'}
            }
        ],
        'nba': [
            {
                'fixture': {
                    'id': 2001,
                    'date': (now + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S'),
                    'status': {'short': 'NS'},
                    'venue': {'name': 'Crypto.com Arena', 'city': 'Los Angeles'}
                },
                'league': {'name': 'NBA', 'country': 'USA'},
                'teams': {
                    'home': {'id': 10, 'name': 'Los Angeles Lakers', 'logo': ''},
                    'away': {'id': 11, 'name': 'Boston Celtics', 'logo': ''}
                },
                'goals': {'home': None, 'away': None},
                'sport': {'name': 'NBA', 'type': 'team'}
            },
            {
                'fixture': {
                    'id': 2003,
                    'date': (now + timedelta(days=6)).strftime('%Y-%m-%dT%H:%M:%S'),
                    'status': {'short': 'NS'},
                    'venue': {'name': 'Madison Square Garden', 'city': 'New York'}
                },
                'league': {'name': 'NBA', 'country': 'USA'},
                'teams': {
                    'home': {'id': 14, 'name': 'New York Knicks', 'logo': ''},
                    'away': {'id': 15, 'name': 'Miami Heat', 'logo': ''}
                },
                'goals': {'home': None, 'away': None},
                'sport': {'name': 'NBA', 'type': 'team'}
            },
            {
                'fixture': {
                    'id': 2004,
                    'date': (now + timedelta(days=8)).strftime('%Y-%m-%dT%H:%M:%S'),
                    'status': {'short': 'NS'},
                    'venue': {'name': 'Chase Center', 'city': 'San Francisco'}
                },
                'league': {'name': 'NBA', 'country': 'USA'},
                'teams': {
                    'home': {'id': 16, 'name': 'Golden State Warriors', 'logo': ''},
                    'away': {'id': 17, 'name': 'Phoenix Suns', 'logo': ''}
                },
                'goals': {'home': None, 'away': None},
                'sport': {'name': 'NBA', 'type': 'team'}
            }
        ],
        'formula1': [
            {
                'fixture': {
                    'id': 3001,
                    'date': (now + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S'),
                    'status': {'short': 'NS'},
                    'venue': {'name': 'Silverstone Circuit', 'city': 'Silverstone'}
                },
                'league': {'name': 'Formula 1', 'country': 'UK'},
                'teams': {
                    'home': {'id': 20, 'name': 'Lewis Hamilton', 'logo': ''},
                    'away': {'id': 21, 'name': 'Max Verstappen', 'logo': ''}
                },
                'goals': {'home': None, 'away': None},
                'sport': {'name': 'Formula 1', 'type': 'driver'}
            }
        ],
        'nhl': [
            {
                'fixture': {
                    'id': 4002,
                    'date': (now + timedelta(days=9)).strftime('%Y-%m-%dT%H:%M:%S'),
                    'status': {'short': 'NS'},
                    'venue': {'name': 'Bell Centre', 'city': 'Montreal'}
                },
                'league': {'name': 'NHL', 'country': 'USA'},
                'teams': {
                    'home': {'id': 32, 'name': 'Montreal Canadiens', 'logo': ''},
                    'away': {'id': 33, 'name': 'Toronto Maple Leafs', 'logo': ''}
                },
                'goals': {'home': None, 'away': None},
                'sport': {'name': 'NHL', 'type': 'team'}
            }
        ]
    }


def get_dummy_results() -> Dict[str, List[Dict]]:
    """Generate dummy completed game data"""
    now = datetime.now()
    
    return {
        'nfl': [
            {
                'fixture': {
                    'id': 1003,
                    'date': (now - timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%S'),
                    'status': {'short': 'FT'},
                    'venue': {'name': 'SoFi Stadium', 'city': 'Los Angeles'}
                },
                'league': {'name': 'NFL', 'country': 'USA'},
                'teams': {
                    'home': {'id': 5, 'name': 'Los Angeles Rams', 'logo': ''},
                    'away': {'id': 6, 'name': 'San Francisco 49ers', 'logo': ''}
                },
                'goals': {'home': 28, 'away': 24},
                'sport': {'name': 'NFL', 'type': 'team'}
            },
            {
                'fixture': {
                    'id': 1006,
                    'date': (now - timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%S'),
                    'status': {'short': 'FT'},
                    'venue': {'name': 'AT&T Stadium', 'city': 'Arlington'}
                },
                'league': {'name': 'NFL', 'country': 'USA'},
                'teams': {
                    'home': {'id': 11, 'name': 'Dallas Cowboys', 'logo': ''},
                    'away': {'id': 12, 'name': 'Washington Commanders', 'logo': ''}
                },
                'goals': {'home': 31, 'away': 17},
                'sport': {'name': 'NFL', 'type': 'team'}
            }
        ],
        'nba': [
            {
                'fixture': {
                    'id': 2002,
                    'date': (now - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S'),
                    'status': {'short': 'FT'},
                    'venue': {'name': 'Chase Center', 'city': 'San Francisco'}
                },
                'league': {'name': 'NBA', 'country': 'USA'},
                'teams': {
                    'home': {'id': 12, 'name': 'Golden State Warriors', 'logo': ''},
                    'away': {'id': 13, 'name': 'Miami Heat', 'logo': ''}
                },
                'goals': {'home': 112, 'away': 108},
                'sport': {'name': 'NBA', 'type': 'team'}
            },
            {
                'fixture': {
                    'id': 2005,
                    'date': (now - timedelta(days=4)).strftime('%Y-%m-%dT%H:%M:%S'),
                    'status': {'short': 'FT'},
                    'venue': {'name': 'Fiserv Forum', 'city': 'Milwaukee'}
                },
                'league': {'name': 'NBA', 'country': 'USA'},
                'teams': {
                    'home': {'id': 18, 'name': 'Milwaukee Bucks', 'logo': ''},
                    'away': {'id': 19, 'name': 'Chicago Bulls', 'logo': ''}
                },
                'goals': {'home': 118, 'away': 105},
                'sport': {'name': 'NBA', 'type': 'team'}
            }
        ],
        'nhl': [
            {
                'fixture': {
                    'id': 4003,
                    'date': (now - timedelta(days=5)).strftime('%Y-%m-%dT%H:%M:%S'),
                    'status': {'short': 'FT'},
                    'venue': {'name': 'United Center', 'city': 'Chicago'}
                },
                'league': {'name': 'NHL', 'country': 'USA'},
                'teams': {
                    'home': {'id': 34, 'name': 'Chicago Blackhawks', 'logo': ''},
                    'away': {'id': 35, 'name': 'Detroit Red Wings', 'logo': ''}
                },
                'goals': {'home': 4, 'away': 2},
                'sport': {'name': 'NHL', 'type': 'team'}
            }
        ]
    }


def get_dummy_live_events() -> Dict[str, List[Dict]]:
    """Generate dummy live event data"""
    now = datetime.now()
    
    return {
        'nfl': [
            {
                'fixture': {
                    'id': 1007,
                    'date': now.strftime('%Y-%m-%dT%H:%M:%S'),
                    'status': {'short': 'LIVE', 'elapsed': 35},
                    'venue': {'name': 'Lambeau Field', 'city': 'Green Bay'}
                },
                'league': {'name': 'NFL', 'country': 'USA'},
                'teams': {
                    'home': {'id': 3, 'name': 'Green Bay Packers', 'logo': ''},
                    'away': {'id': 4, 'name': 'Dallas Cowboys', 'logo': ''}
                },
                'goals': {'home': 21, 'away': 14},
                'sport': {'name': 'NFL', 'type': 'team'}
            }
        ],
        'nhl': [
            {
                'fixture': {
                    'id': 4001,
                    'date': now.strftime('%Y-%m-%dT%H:%M:%S'),
                    'status': {'short': 'LIVE', 'elapsed': 45},
                    'venue': {'name': 'TD Garden', 'city': 'Boston'}
                },
                'league': {'name': 'NHL', 'country': 'USA'},
                'teams': {
                    'home': {'id': 30, 'name': 'Boston Bruins', 'logo': ''},
                    'away': {'id': 31, 'name': 'Toronto Maple Leafs', 'logo': ''}
                },
                'goals': {'home': 2, 'away': 1},
                'sport': {'name': 'NHL', 'type': 'team'}
            }
        ],
        'nba': [
            {
                'fixture': {
                    'id': 2006,
                    'date': now.strftime('%Y-%m-%dT%H:%M:%S'),
                    'status': {'short': 'LIVE', 'elapsed': 28},
                    'venue': {'name': 'Crypto.com Arena', 'city': 'Los Angeles'}
                },
                'league': {'name': 'NBA', 'country': 'USA'},
                'teams': {
                    'home': {'id': 10, 'name': 'Los Angeles Lakers', 'logo': ''},
                    'away': {'id': 11, 'name': 'Boston Celtics', 'logo': ''}
                },
                'goals': {'home': 58, 'away': 52},
                'sport': {'name': 'NBA', 'type': 'team'}
            }
        ]
    }


def get_dummy_standings(sport: str) -> List[Dict]:
    """Generate dummy standings data"""
    return [
        {
            'league': {
                'name': sport.upper(),
                'standings': [
                    [
                        {'rank': 1, 'team': {'name': 'Team A'}, 'points': 45},
                        {'rank': 2, 'team': {'name': 'Team B'}, 'points': 42}
                    ]
                ]
            }
        }
    ]


def get_dummy_news(team_name: str) -> List[Dict]:
    """Generate dummy news data for a team"""
    return [
        {
            'title': f'{team_name} Prepares for Crucial Matchup',
            'summary': 'Team looks to maintain winning streak in upcoming game.',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'source': 'Sports News'
        },
        {
            'title': f'{team_name} Star Player Returns from Injury',
            'summary': 'Key player expected to make impact in next game.',
            'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'source': 'Team Updates'
        }
    ]


def get_dummy_stats(team_name: str) -> Dict:
    """Generate dummy stats data for a team"""
    return {
        'wins': 12,
        'losses': 3,
        'win_percentage': 0.800,
        'points_per_game': 28.5,
        'rank': 2
    }


def get_dummy_play_by_play(fixture_id: int, sport: str) -> List[Dict]:
    """Generate dummy play-by-play data for a live game"""
    now = datetime.now()
    
    # Different play-by-play based on sport
    if sport == 'nfl':
        return [
            {
                'time': (now - timedelta(minutes=35)).strftime('%H:%M'),
                'period': '2nd',
                'event': 'Touchdown',
                'team': 'Green Bay Packers',
                'player': 'Aaron Jones',
                'description': 'Touchdown run by Aaron Jones (2 yards)'
            },
            {
                'time': (now - timedelta(minutes=28)).strftime('%H:%M'),
                'period': '2nd',
                'event': 'Touchdown',
                'team': 'Dallas Cowboys',
                'player': 'CeeDee Lamb',
                'description': 'Touchdown pass from Dak Prescott to CeeDee Lamb (15 yards)'
            },
            {
                'time': (now - timedelta(minutes=22)).strftime('%H:%M'),
                'period': '2nd',
                'event': 'Field Goal',
                'team': 'Green Bay Packers',
                'player': 'Mason Crosby',
                'description': 'Field goal by Mason Crosby (42 yards)'
            },
            {
                'time': (now - timedelta(minutes=15)).strftime('%H:%M'),
                'period': '2nd',
                'event': 'Touchdown',
                'team': 'Green Bay Packers',
                'player': 'Davante Adams',
                'description': 'Touchdown pass from Aaron Rodgers to Davante Adams (8 yards)'
            }
        ]
    elif sport == 'nba':
        return [
            {
                'time': (now - timedelta(minutes=28)).strftime('%H:%M'),
                'period': '2nd',
                'event': '3-Pointer',
                'team': 'Los Angeles Lakers',
                'player': 'LeBron James',
                'description': '3-pointer made by LeBron James'
            },
            {
                'time': (now - timedelta(minutes=25)).strftime('%H:%M'),
                'period': '2nd',
                'event': 'Dunk',
                'team': 'Boston Celtics',
                'player': 'Jayson Tatum',
                'description': 'Dunk by Jayson Tatum (Assist: Marcus Smart)'
            },
            {
                'time': (now - timedelta(minutes=20)).strftime('%H:%M'),
                'period': '2nd',
                'event': '3-Pointer',
                'team': 'Los Angeles Lakers',
                'player': 'Anthony Davis',
                'description': '3-pointer made by Anthony Davis'
            },
            {
                'time': (now - timedelta(minutes=18)).strftime('%H:%M'),
                'period': '2nd',
                'event': 'Timeout',
                'team': 'Boston Celtics',
                'player': None,
                'description': 'Team timeout called by Boston Celtics'
            }
        ]
    else:  # NHL default
        return [
            {
                'time': (now - timedelta(minutes=45)).strftime('%H:%M'),
                'period': '1st',
                'event': 'Goal',
                'team': 'Boston Bruins',
                'player': 'Brad Marchand',
                'description': 'Goal scored by Brad Marchand (Assist: Patrice Bergeron)'
            },
            {
                'time': (now - timedelta(minutes=32)).strftime('%H:%M'),
                'period': '1st',
                'event': 'Goal',
                'team': 'Toronto Maple Leafs',
                'player': 'Auston Matthews',
                'description': 'Goal scored by Auston Matthews (Assist: Mitch Marner)'
            },
            {
                'time': (now - timedelta(minutes=18)).strftime('%H:%M'),
                'period': '2nd',
                'event': 'Goal',
                'team': 'Boston Bruins',
                'player': 'David Pastrnak',
                'description': 'Goal scored by David Pastrnak (Power Play)'
            },
            {
                'time': (now - timedelta(minutes=5)).strftime('%H:%M'),
                'period': '2nd',
                'event': 'Penalty',
                'team': 'Toronto Maple Leafs',
                'player': 'Morgan Rielly',
                'description': '2-minute penalty for tripping'
            }
        ]


def get_sport_games(sport_key: str) -> Dict:
    """Get all games (live, upcoming, recent) for a specific sport"""
    live = get_dummy_live_events().get(sport_key, [])
    upcoming = get_dummy_fixtures().get(sport_key, [])
    recent = get_dummy_results().get(sport_key, [])
    
    return {
        'live': live,
        'upcoming': upcoming,
        'recent': recent
    }


def get_sport_news(sport_key: str) -> List[Dict]:
    """Get news for a specific sport"""
    sport_name = sport_key.upper()
    return [
        {
            'title': f'{sport_name} Season Update: Key Matchups This Week',
            'summary': 'Breaking down the most important games and storylines.',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'source': 'Sports Insider',
            'image': None
        },
        {
            'title': f'Top {sport_name} Teams Battle for Playoff Position',
            'summary': 'The race for postseason spots heats up as the season progresses.',
            'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'source': 'League News',
            'image': None
        },
        {
            'title': f'{sport_name} Star Player Sets New Record',
            'summary': 'Historic performance highlights the weekend action.',
            'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'source': 'Sports Center',
            'image': None
        },
        {
            'title': f'{sport_name} Trade Deadline Approaches',
            'summary': 'Teams make final moves before the deadline.',
            'date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
            'source': 'Trade Rumors',
            'image': None
        }
    ]


def get_sport_standings(sport_key: str) -> List[Dict]:
    """Get detailed standings for a specific sport"""
    # Generate more comprehensive standings
    teams = []
    if sport_key == 'nfl':
        teams = [
            {'rank': 1, 'team': 'Kansas City Chiefs', 'wins': 12, 'losses': 2, 'ties': 0, 'points': 0, 'win_pct': 0.857},
            {'rank': 2, 'team': 'Buffalo Bills', 'wins': 11, 'losses': 3, 'ties': 0, 'points': 0, 'win_pct': 0.786},
            {'rank': 3, 'team': 'Philadelphia Eagles', 'wins': 11, 'losses': 3, 'ties': 0, 'points': 0, 'win_pct': 0.786},
            {'rank': 4, 'team': 'Dallas Cowboys', 'wins': 10, 'losses': 4, 'ties': 0, 'points': 0, 'win_pct': 0.714},
            {'rank': 5, 'team': 'San Francisco 49ers', 'wins': 10, 'losses': 4, 'ties': 0, 'points': 0, 'win_pct': 0.714},
        ]
    elif sport_key == 'nba':
        teams = [
            {'rank': 1, 'team': 'Boston Celtics', 'wins': 25, 'losses': 6, 'ties': 0, 'points': 0, 'win_pct': 0.806},
            {'rank': 2, 'team': 'Milwaukee Bucks', 'wins': 23, 'losses': 8, 'ties': 0, 'points': 0, 'win_pct': 0.742},
            {'rank': 3, 'team': 'Denver Nuggets', 'wins': 22, 'losses': 9, 'ties': 0, 'points': 0, 'win_pct': 0.710},
            {'rank': 4, 'team': 'Philadelphia 76ers', 'wins': 21, 'losses': 10, 'ties': 0, 'points': 0, 'win_pct': 0.677},
            {'rank': 5, 'team': 'Miami Heat', 'wins': 20, 'losses': 11, 'ties': 0, 'points': 0, 'win_pct': 0.645},
        ]
    elif sport_key == 'nhl':
        teams = [
            {'rank': 1, 'team': 'Boston Bruins', 'wins': 28, 'losses': 8, 'ties': 0, 'points': 56, 'win_pct': 0.778},
            {'rank': 2, 'team': 'Toronto Maple Leafs', 'wins': 24, 'losses': 12, 'ties': 0, 'points': 48, 'win_pct': 0.667},
            {'rank': 3, 'team': 'Tampa Bay Lightning', 'wins': 22, 'losses': 14, 'ties': 0, 'points': 44, 'win_pct': 0.611},
            {'rank': 4, 'team': 'Florida Panthers', 'wins': 21, 'losses': 15, 'ties': 0, 'points': 42, 'win_pct': 0.583},
            {'rank': 5, 'team': 'Montreal Canadiens', 'wins': 19, 'losses': 17, 'ties': 0, 'points': 38, 'win_pct': 0.528},
        ]
    else:
        # Generic standings
        teams = [
            {'rank': 1, 'team': 'Team A', 'wins': 15, 'losses': 5, 'ties': 0, 'points': 0, 'win_pct': 0.750},
            {'rank': 2, 'team': 'Team B', 'wins': 14, 'losses': 6, 'ties': 0, 'points': 0, 'win_pct': 0.700},
            {'rank': 3, 'team': 'Team C', 'wins': 13, 'losses': 7, 'ties': 0, 'points': 0, 'win_pct': 0.650},
        ]
    
    return teams


def get_sport_stats(sport_key: str) -> Dict:
    """Get overall stats for a sport"""
    return {
        'total_games': 256,
        'games_played': 180,
        'games_remaining': 76,
        'top_scorer': 'Player Name',
        'most_wins': 'Team Name',
        'avg_score': 24.5
    }

