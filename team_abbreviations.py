"""
Team abbreviation mappings for all sports
Maps full team names to their abbreviations/logos
"""

TEAM_ABBREVIATIONS = {
    'nfl': {
        'Arizona Cardinals': 'ARI',
        'Atlanta Falcons': 'ATL',
        'Baltimore Ravens': 'BAL',
        'Buffalo Bills': 'BUF',
        'Carolina Panthers': 'CAR',
        'Chicago Bears': 'CHI',
        'Cincinnati Bengals': 'CIN',
        'Cleveland Browns': 'CLE',
        'Dallas Cowboys': 'DAL',
        'Denver Broncos': 'DEN',
        'Detroit Lions': 'DET',
        'Green Bay Packers': 'GB',
        'Houston Texans': 'HOU',
        'Indianapolis Colts': 'IND',
        'Jacksonville Jaguars': 'JAX',
        'Kansas City Chiefs': 'KC',
        'Las Vegas Raiders': 'LV',
        'Los Angeles Chargers': 'LAC',
        'Los Angeles Rams': 'LAR',
        'Miami Dolphins': 'MIA',
        'Minnesota Vikings': 'MIN',
        'New England Patriots': 'NE',
        'New Orleans Saints': 'NO',
        'New York Giants': 'NYG',
        'New York Jets': 'NYJ',
        'Philadelphia Eagles': 'PHI',
        'Pittsburgh Steelers': 'PIT',
        'San Francisco 49ers': 'SF',
        'Seattle Seahawks': 'SEA',
        'Tampa Bay Buccaneers': 'TB',
        'Tennessee Titans': 'TEN',
        'Washington Commanders': 'WAS'
    },
    'nhl': {
        'Anaheim Ducks': 'ANA',
        'Arizona Coyotes': 'ARI',
        'Boston Bruins': 'BOS',
        'Buffalo Sabres': 'BUF',
        'Calgary Flames': 'CGY',
        'Carolina Hurricanes': 'CAR',
        'Chicago Blackhawks': 'CHI',
        'Colorado Avalanche': 'COL',
        'Columbus Blue Jackets': 'CBJ',
        'Dallas Stars': 'DAL',
        'Detroit Red Wings': 'DET',
        'Edmonton Oilers': 'EDM',
        'Florida Panthers': 'FLA',
        'Los Angeles Kings': 'LAK',
        'Minnesota Wild': 'MIN',
        'Montreal Canadiens': 'MTL',
        'Nashville Predators': 'NSH',
        'New Jersey Devils': 'NJD',
        'New York Islanders': 'NYI',
        'New York Rangers': 'NYR',
        'Ottawa Senators': 'OTT',
        'Philadelphia Flyers': 'PHI',
        'Pittsburgh Penguins': 'PIT',
        'San Jose Sharks': 'SJS',
        'Seattle Kraken': 'SEA',
        'St. Louis Blues': 'STL',
        'Tampa Bay Lightning': 'TB',
        'Toronto Maple Leafs': 'TOR',
        'Vancouver Canucks': 'VAN',
        'Vegas Golden Knights': 'VGK',
        'Washington Capitals': 'WSH',
        'Winnipeg Jets': 'WPG'
    },
    'nba': {
        'Atlanta Hawks': 'ATL',
        'Boston Celtics': 'BOS',
        'Brooklyn Nets': 'BKN',
        'Charlotte Hornets': 'CHA',
        'Chicago Bulls': 'CHI',
        'Cleveland Cavaliers': 'CLE',
        'Dallas Mavericks': 'DAL',
        'Denver Nuggets': 'DEN',
        'Detroit Pistons': 'DET',
        'Golden State Warriors': 'GSW',
        'Houston Rockets': 'HOU',
        'Indiana Pacers': 'IND',
        'LA Clippers': 'LAC',
        'Los Angeles Lakers': 'LAL',
        'Memphis Grizzlies': 'MEM',
        'Miami Heat': 'MIA',
        'Milwaukee Bucks': 'MIL',
        'Minnesota Timberwolves': 'MIN',
        'New Orleans Pelicans': 'NOP',
        'New York Knicks': 'NYK',
        'Oklahoma City Thunder': 'OKC',
        'Orlando Magic': 'ORL',
        'Philadelphia 76ers': 'PHI',
        'Phoenix Suns': 'PHX',
        'Portland Trail Blazers': 'POR',
        'Sacramento Kings': 'SAC',
        'San Antonio Spurs': 'SAS',
        'Toronto Raptors': 'TOR',
        'Utah Jazz': 'UTA',
        'Washington Wizards': 'WAS'
    },
    'mlb': {
        'Arizona Diamondbacks': 'ARI',
        'Atlanta Braves': 'ATL',
        'Baltimore Orioles': 'BAL',
        'Boston Red Sox': 'BOS',
        'Chicago Cubs': 'CHC',
        'Chicago White Sox': 'CWS',
        'Cincinnati Reds': 'CIN',
        'Cleveland Guardians': 'CLE',
        'Colorado Rockies': 'COL',
        'Detroit Tigers': 'DET',
        'Houston Astros': 'HOU',
        'Kansas City Royals': 'KC',
        'Los Angeles Angels': 'LAA',
        'Los Angeles Dodgers': 'LAD',
        'Miami Marlins': 'MIA',
        'Milwaukee Brewers': 'MIL',
        'Minnesota Twins': 'MIN',
        'New York Mets': 'NYM',
        'New York Yankees': 'NYY',
        'Oakland Athletics': 'OAK',
        'Philadelphia Phillies': 'PHI',
        'Pittsburgh Pirates': 'PIT',
        'San Diego Padres': 'SD',
        'San Francisco Giants': 'SF',
        'Seattle Mariners': 'SEA',
        'St. Louis Cardinals': 'STL',
        'Tampa Bay Rays': 'TB',
        'Texas Rangers': 'TEX',
        'Toronto Blue Jays': 'TOR',
        'Washington Nationals': 'WSH'
    },
    'cricket': {
        'Afghanistan': 'AFG',
        'Australia': 'AUS',
        'Bangladesh': 'BAN',
        'England': 'ENG',
        'India': 'IND',
        'Ireland': 'IRE',
        'New Zealand': 'NZ',
        'Pakistan': 'PAK',
        'South Africa': 'SA',
        'Sri Lanka': 'SL',
        'West Indies': 'WI',
        'Zimbabwe': 'ZIM'
    }
}


def get_team_abbreviation(sport: str, team_name: str) -> str:
    """
    Get team abbreviation for a given sport and team name
    
    Args:
        sport: Sport key (nfl, nhl, nba, mlb, cricket)
        team_name: Full team name
        
    Returns:
        Team abbreviation or original name if not found
    """
    sport_abbrevs = TEAM_ABBREVIATIONS.get(sport.lower(), {})
    return sport_abbrevs.get(team_name, team_name)

