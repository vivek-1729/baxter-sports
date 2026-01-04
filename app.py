"""
Flask application for Sports Dashboard
Handles user preferences for sports and favorite teams/players
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from sports_backend import SportsAPIClient
from dummy_data import get_dummy_fixtures, get_dummy_results, get_dummy_live_events, get_dummy_news, get_dummy_stats, get_dummy_standings
from image_resolver import get_image_resolver
from preferences_storage import get_preferences_storage
from team_abbreviations import get_team_abbreviation
from user_auth import register_user, authenticate_user, get_user_by_id
from datetime import datetime, timedelta
from functools import wraps
import os
import uuid

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.permanent_session_lifetime = timedelta(days=30)  # Remember login for 30 days

# Sport configuration
SPORTS = {
    'nfl': {'name': 'NFL', 'icon': '🏈', 'type': 'team'},
    'nhl': {'name': 'NHL', 'icon': '🏒', 'type': 'team'},
    'nba': {'name': 'NBA', 'icon': '🏀', 'type': 'team'},
    'mlb': {'name': 'MLB', 'icon': '⚾', 'type': 'team'},
    'cricket': {'name': 'Cricket', 'icon': '🏏', 'type': 'team'},
    'formula1': {'name': 'Formula 1', 'icon': '🏎️', 'type': 'driver'},
    'tennis': {'name': 'Tennis', 'icon': '🎾', 'type': 'player'},
    'golf': {'name': 'Golf', 'icon': '⛳', 'type': 'player'}
}

# Comprehensive lists of ALL teams/players for each sport
ALL_OPTIONS = {
    'nfl': [
        'Arizona Cardinals', 'Atlanta Falcons', 'Baltimore Ravens', 'Buffalo Bills',
        'Carolina Panthers', 'Chicago Bears', 'Cincinnati Bengals', 'Cleveland Browns',
        'Dallas Cowboys', 'Denver Broncos', 'Detroit Lions', 'Green Bay Packers',
        'Houston Texans', 'Indianapolis Colts', 'Jacksonville Jaguars', 'Kansas City Chiefs',
        'Las Vegas Raiders', 'Los Angeles Chargers', 'Los Angeles Rams', 'Miami Dolphins',
        'Minnesota Vikings', 'New England Patriots', 'New Orleans Saints', 'New York Giants',
        'New York Jets', 'Philadelphia Eagles', 'Pittsburgh Steelers', 'San Francisco 49ers',
        'Seattle Seahawks', 'Tampa Bay Buccaneers', 'Tennessee Titans', 'Washington Commanders'
    ],
    'nhl': [
        'Anaheim Ducks', 'Arizona Coyotes', 'Boston Bruins', 'Buffalo Sabres',
        'Calgary Flames', 'Carolina Hurricanes', 'Chicago Blackhawks', 'Colorado Avalanche',
        'Columbus Blue Jackets', 'Dallas Stars', 'Detroit Red Wings', 'Edmonton Oilers',
        'Florida Panthers', 'Los Angeles Kings', 'Minnesota Wild', 'Montreal Canadiens',
        'Nashville Predators', 'New Jersey Devils', 'New York Islanders', 'New York Rangers',
        'Ottawa Senators', 'Philadelphia Flyers', 'Pittsburgh Penguins', 'San Jose Sharks',
        'Seattle Kraken', 'St. Louis Blues', 'Tampa Bay Lightning', 'Toronto Maple Leafs',
        'Vancouver Canucks', 'Vegas Golden Knights', 'Washington Capitals', 'Winnipeg Jets'
    ],
    'nba': [
        'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets',
        'Chicago Bulls', 'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets',
        'Detroit Pistons', 'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers',
        'LA Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies', 'Miami Heat',
        'Milwaukee Bucks', 'Minnesota Timberwolves', 'New Orleans Pelicans', 'New York Knicks',
        'Oklahoma City Thunder', 'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns',
        'Portland Trail Blazers', 'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors',
        'Utah Jazz', 'Washington Wizards'
    ],
    'mlb': [
        'Arizona Diamondbacks', 'Atlanta Braves', 'Baltimore Orioles', 'Boston Red Sox',
        'Chicago Cubs', 'Chicago White Sox', 'Cincinnati Reds', 'Cleveland Guardians',
        'Colorado Rockies', 'Detroit Tigers', 'Houston Astros', 'Kansas City Royals',
        'Los Angeles Angels', 'Los Angeles Dodgers', 'Miami Marlins', 'Milwaukee Brewers',
        'Minnesota Twins', 'New York Mets', 'New York Yankees', 'Oakland Athletics',
        'Philadelphia Phillies', 'Pittsburgh Pirates', 'San Diego Padres', 'San Francisco Giants',
        'Seattle Mariners', 'St. Louis Cardinals', 'Tampa Bay Rays', 'Texas Rangers',
        'Toronto Blue Jays', 'Washington Nationals'
    ],
    'cricket': [
        'Afghanistan', 'Australia', 'Bangladesh', 'England',
        'India', 'Ireland', 'New Zealand', 'Pakistan',
        'South Africa', 'Sri Lanka', 'West Indies', 'Zimbabwe',
        'Netherlands', 'Scotland', 'Nepal', 'Oman',
        'Papua New Guinea', 'United States', 'United Arab Emirates', 'Canada'
    ],
    'formula1': [
        'Lewis Hamilton', 'Max Verstappen', 'Charles Leclerc', 'Lando Norris',
        'Carlos Sainz', 'Fernando Alonso', 'George Russell', 'Sergio Pérez',
        'Oscar Piastri', 'Pierre Gasly', 'Esteban Ocon', 'Valtteri Bottas',
        'Lance Stroll', 'Yuki Tsunoda', 'Alexander Albon', 'Daniel Ricciardo',
        'Kevin Magnussen', 'Nico Hülkenberg', 'Guanyu Zhou', 'Logan Sargeant'
    ],
    'tennis': [
        'Novak Djokovic', 'Carlos Alcaraz', 'Daniil Medvedev', 'Jannik Sinner',
        'Andrey Rublev', 'Stefanos Tsitsipas', 'Holger Rune', 'Casper Ruud',
        'Taylor Fritz', 'Alexander Zverev', 'Tommy Paul', 'Karen Khachanov',
        'Frances Tiafoe', 'Cameron Norrie', 'Ben Shelton', 'Lorenzo Musetti',
        'Iga Świątek', 'Aryna Sabalenka', 'Coco Gauff', 'Elena Rybakina',
        'Jessica Pegula', 'Ons Jabeur', 'Maria Sakkari', 'Caroline Garcia',
        'Petra Kvitová', 'Barbora Krejčíková', 'Beatriz Haddad Maia', 'Madison Keys',
        'Rafael Nadal', 'Andy Murray', 'Stan Wawrinka', 'Dominic Thiem'
    ],
    'golf': [
        'Tiger Woods', 'Rory McIlroy', 'Scottie Scheffler', 'Jon Rahm',
        'Viktor Hovland', 'Xander Schauffele', 'Patrick Cantlay', 'Collin Morikawa',
        'Jordan Spieth', 'Justin Thomas', 'Dustin Johnson', 'Brooks Koepka',
        'Matt Fitzpatrick', 'Tommy Fleetwood', 'Shane Lowry', 'Cameron Smith',
        'Hideki Matsuyama', 'Sungjae Im', 'Tom Kim', 'Max Homa',
        'Sam Burns', 'Tony Finau', 'Wyndham Clark', 'Brian Harman',
        'Rickie Fowler', 'Jason Day', 'Adam Scott', 'Sergio García'
    ]
}


def login_required(f):
    """Decorator to require login for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('username'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Homepage with NFL image and two buttons"""
    return render_template('homepage.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        success, user_data = authenticate_user(username, password)
        if success:
            session.permanent = True  # Make session persistent
            session['user_id'] = user_data['user_id']
            session['username'] = user_data['username']
            
            # Load user preferences
            storage = get_preferences_storage()
            saved_prefs = storage.load_preferences(user_data['user_id'])
            if saved_prefs:
                session['selected_sports'] = saved_prefs.get('selected_sports', [])
                session['favorites'] = saved_prefs.get('favorites', {})
                session['preferences_set'] = True
                return redirect(url_for('dashboard'))
            else:
                # No preferences yet, go to sport selection
                return redirect(url_for('select_sports'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
        else:
            success, error_msg = register_user(username, password)
            if success:
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash(error_msg or 'Registration failed', 'error')
    
    return render_template('register.html')


@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('index'))


@app.route('/live-games')
def live_games():
    """Public live games view (no login required) - shows dummy data"""
    # Use all sports for public view
    selected_sports = list(SPORTS.keys())
    username = session.get('username', '')
    
    # Build timeline with dummy data
    timeline_events = []
    live_events = get_dummy_live_events()
    upcoming_fixtures = get_dummy_fixtures()
    recent_results = get_dummy_results()
    
    # Process all events
    for sport_key in selected_sports:
        if sport_key in live_events:
            for event in live_events[sport_key]:
                event['sport_key'] = sport_key
                event['is_live'] = True
                timeline_events.append(event)
        
        if sport_key in upcoming_fixtures:
            for event in upcoming_fixtures[sport_key]:
                event['sport_key'] = sport_key
                event['is_live'] = False
                timeline_events.append(event)
        
        if sport_key in recent_results:
            for event in recent_results[sport_key]:
                event['sport_key'] = sport_key
                event['is_live'] = False
                event['is_completed'] = True
                timeline_events.append(event)
    
    # Sort events
    def get_event_date(event):
        try:
            date_str = event.get('fixture', {}).get('date', '')
            if date_str:
                if 'T' in date_str:
                    return datetime.fromisoformat(date_str.replace('Z', ''))
                else:
                    return datetime.strptime(date_str, '%Y-%m-%d')
            return datetime.now()
        except:
            return datetime.now()
    
    timeline_events.sort(key=lambda x: (
        0 if x.get('is_live') else 1,
        get_event_date(x)
    ))
    
    first_row_events = timeline_events[:8]
    second_row_events = timeline_events[8:]
    
    # Resolve images
    image_resolver = get_image_resolver()
    for event in first_row_events + second_row_events[:10]:
        try:
            event['background_image'] = image_resolver.resolve_event_image(event)
        except Exception:
            event['background_image'] = None
    
    # Get hero data
    hero_data = {}
    if timeline_events:
        first_event = timeline_events[0]
        team_name = None
        if first_event.get('teams', {}).get('home', {}).get('name'):
            team_name = first_event['teams']['home']['name']
        elif first_event.get('teams', {}).get('away', {}).get('name'):
            team_name = first_event['teams']['away']['name']
        
        if team_name:
            hero_data['news'] = get_dummy_news(team_name)
            hero_data['stats'] = get_dummy_stats(team_name)
            hero_data['standings'] = get_dummy_standings(first_event['sport_key'])
    
    modal_data = {}
    if hero_data:
        modal_data = {
            'stats': hero_data.get('stats'),
            'standings': hero_data.get('standings'),
            'news': hero_data.get('news')
        }
    
    def get_abbrev(sport, team_name):
        return get_team_abbreviation(sport, team_name)
    
    username = session.get('username', '')
    
    return render_template('dashboard.html',
                         selected_sports=selected_sports,
                         favorites={},
                         sports=SPORTS,
                         timeline_events=timeline_events,
                         first_row_events=first_row_events,
                         second_row_events=second_row_events,
                         hero_data=hero_data,
                         modal_data=modal_data,
                         get_abbrev=get_abbrev,
                         username=username,
                         is_public=True)


@app.route('/select-sports')
def select_sports_page():
    """Sport selection page (requires login)"""
    return render_template('sport_selection.html', sports=SPORTS)


@app.route('/select-sports', methods=['POST'])
def select_sports():
    """Handle sport selection"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    selected_sports = request.form.getlist('sports')
    if not selected_sports:
        return redirect(url_for('select_sports_page'))
    
    session['selected_sports'] = selected_sports
    return redirect(url_for('select_favorites'))


@app.route('/favorites')
def select_favorites():
    """Page for selecting favorite teams/players for each sport"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    selected_sports = session.get('selected_sports', [])
    if not selected_sports:
        return redirect(url_for('select_sports_page'))
    
    # Prepare sport data for the template
    sports_data = {}
    for sport_key in selected_sports:
        if sport_key in SPORTS:
            sports_data[sport_key] = SPORTS[sport_key]
    
    return render_template('favorites_selection.html', sports_data=sports_data)


@app.route('/api/suggestions/<sport>')
def get_suggestions(sport):
    """Get autocomplete suggestions for a sport - returns ALL options"""
    query = request.args.get('q', '').lower()
    
    # Start with comprehensive preloaded list
    options = ALL_OPTIONS.get(sport, []).copy()
    
    # Try to get from API if available and merge
    try:
        api_key = os.getenv('SPORTS_API_KEY')
        if api_key:
            client = SportsAPIClient(api_key=api_key)
            
            if SPORTS.get(sport, {}).get('type') == 'team':
                # Get all teams from API
                api_options = client.get_all_teams(sport)
                # Merge with preloaded list (API takes priority)
                all_options = list(set(api_options + options))
                options = sorted(all_options)
            else:
                # Get all players/drivers from API
                api_options = client.get_all_players(sport)
                # Merge with preloaded list (API takes priority)
                all_options = list(set(api_options + options))
                options = sorted(all_options)
    except Exception as e:
        # If API fails, use preloaded list
        pass
    
    # Filter based on query if provided
    if query:
        filtered = [opt for opt in options if query in opt.lower()]
    else:
        # Return all options if no query
        filtered = options
    
    return jsonify({'suggestions': filtered})


@app.route('/save-favorites', methods=['POST'])
def save_favorites():
    """Save user favorites to session and persistent storage"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    selected_sports = session.get('selected_sports', [])
    favorites = {}
    
    for sport_key in selected_sports:
        favorite_key = f'favorite_{sport_key}'
        favorite_value = request.form.get(favorite_key, '').strip()
        if favorite_value:
            favorites[sport_key] = favorite_value
    
    # Save to session
    session['favorites'] = favorites
    session['preferences_set'] = True
    
    # Save to persistent storage using authenticated user_id
    storage = get_preferences_storage()
    storage.save_preferences(
        session['user_id'],
        selected_sports,
        favorites
    )
    
    return redirect(url_for('dashboard'))


@app.route('/preferences')
@login_required
def preferences():
    """Update preferences page (accessible from username click)"""
    selected_sports = session.get('selected_sports', [])
    
    # Prepare sport data for the template
    sports_data = {}
    for sport_key in selected_sports:
        if sport_key in SPORTS:
            sports_data[sport_key] = SPORTS[sport_key]
    
    return render_template('favorites_selection.html', sports_data=sports_data, is_update=True)


@app.route('/dashboard')
@login_required
def dashboard():
    """Cinematic sports dashboard with hero image layout"""
    # Load from session first
    selected_sports = session.get('selected_sports', [])
    favorites = session.get('favorites', {})
    user_id = session.get('user_id')
    
    # If session is empty, try to load from storage
    if not selected_sports and user_id:
        storage = get_preferences_storage()
        saved_prefs = storage.load_preferences(user_id)
        if saved_prefs:
            selected_sports = saved_prefs.get('selected_sports', [])
            favorites = saved_prefs.get('favorites', {})
            # Restore to session
            session['selected_sports'] = selected_sports
            session['favorites'] = favorites
            session['preferences_set'] = True
    
    # If still no preferences, redirect to sport selection
    if not selected_sports:
        return redirect(url_for('select_sports_page'))
    
    # Build timeline: Live → Upcoming → Recent
    timeline_events = []
    
    # Get dummy data (will be replaced with API calls)
    live_events = get_dummy_live_events()
    upcoming_fixtures = get_dummy_fixtures()
    recent_results = get_dummy_results()
    
    # Process live events
    for sport_key in selected_sports:
        if sport_key in live_events:
            for event in live_events[sport_key]:
                event['sport_key'] = sport_key
                event['is_live'] = True
                event['is_favorite'] = _is_favorite_event(event, sport_key, favorites)
                timeline_events.append(event)
    
    # Process upcoming fixtures
    for sport_key in selected_sports:
        if sport_key in upcoming_fixtures:
            for event in upcoming_fixtures[sport_key]:
                event['sport_key'] = sport_key
                event['is_live'] = False
                event['is_favorite'] = _is_favorite_event(event, sport_key, favorites)
                timeline_events.append(event)
    
    # Process recent results
    for sport_key in selected_sports:
        if sport_key in recent_results:
            for event in recent_results[sport_key]:
                event['sport_key'] = sport_key
                event['is_live'] = False
                event['is_completed'] = True
                event['is_favorite'] = _is_favorite_event(event, sport_key, favorites)
                timeline_events.append(event)
    
    # Sort by priority: Live first, then by date
    def get_event_date(event):
        try:
            date_str = event.get('fixture', {}).get('date', '')
            if date_str:
                # Handle various date formats
                if 'T' in date_str:
                    return datetime.fromisoformat(date_str.replace('Z', ''))
                else:
                    return datetime.strptime(date_str, '%Y-%m-%d')
            return datetime.now()
        except:
            return datetime.now()
    
    timeline_events.sort(key=lambda x: (
        0 if x.get('is_live') else 1,  # Live events first
        get_event_date(x)
    ))
    
    # Prioritize favorite events within same category
    timeline_events.sort(key=lambda x: (0 if x.get('is_favorite') else 1), reverse=False)
    
    # Split events into two rows: first row (viewport) and second row (below)
    first_row_events = timeline_events[:8]  # First 8 events in viewport
    second_row_events = timeline_events[8:]  # Remaining events below viewport
    
    # Resolve images for events (async, non-blocking)
    image_resolver = get_image_resolver()
    for event in first_row_events + second_row_events[:10]:  # Limit for performance
        try:
            event['background_image'] = image_resolver.resolve_event_image(event)
        except Exception:
            event['background_image'] = None
    
    # Get additional data for first event (hero)
    hero_data = {}
    if timeline_events:
        first_event = timeline_events[0]
        # Get team name for news/stats
        team_name = None
        if first_event.get('teams', {}).get('home', {}).get('name'):
            team_name = first_event['teams']['home']['name']
        elif first_event.get('teams', {}).get('away', {}).get('name'):
            team_name = first_event['teams']['away']['name']
        
        if team_name:
            hero_data['news'] = get_dummy_news(team_name)
            hero_data['stats'] = get_dummy_stats(team_name)
            hero_data['standings'] = get_dummy_standings(first_event['sport_key'])
    
    # Prepare modal data (for JavaScript to use)
    modal_data = {}
    if hero_data:
        modal_data = {
            'stats': hero_data.get('stats'),
            'standings': hero_data.get('standings'),
            'news': hero_data.get('news')
        }
    
    # Add abbreviation helper function to template context
    def get_abbrev(sport, team_name):
        return get_team_abbreviation(sport, team_name)
    
    username = session.get('username', '')
    
    return render_template('dashboard.html', 
                         selected_sports=selected_sports,
                         favorites=favorites,
                         sports=SPORTS,
                         timeline_events=timeline_events,
                         first_row_events=first_row_events,
                         second_row_events=second_row_events,
                         hero_data=hero_data,
                         modal_data=modal_data,
                         get_abbrev=get_abbrev,
                         username=username,
                         is_public=False)


def _is_favorite_event(event: dict, sport_key: str, favorites: dict) -> bool:
    """Check if event involves user's favorite team/player"""
    favorite = favorites.get(sport_key, '')
    if not favorite:
        return False
    
    # Check team names
    home_team = event.get('teams', {}).get('home', {}).get('name', '')
    away_team = event.get('teams', {}).get('away', {}).get('name', '')
    
    return favorite.lower() in home_team.lower() or favorite.lower() in away_team.lower()


@app.route('/calendar')
@login_required
def calendar():
    """Calendar page showing games on various days with filters"""
    username = session.get('username', '')
    selected_sports = session.get('selected_sports', [])
    
    # Get all games data
    from dummy_data import get_sport_games
    all_games = {}
    for sport_key in selected_sports:
        games_data = get_sport_games(sport_key)
        all_games[sport_key] = games_data
    
    return render_template('calendar.html',
                         selected_sports=selected_sports,
                         sports=SPORTS,
                         all_games=all_games,
                         username=username)


@app.route('/sport/<sport_key>')
def sport_page(sport_key):
    """Individual sport page with tabs for Games, News, Standings, Stats"""
    if sport_key not in SPORTS:
        return redirect(url_for('dashboard'))
    
    sport_info = SPORTS[sport_key]
    username = session.get('username', '')
    is_public = not username
    
    # Get all data for this sport
    from dummy_data import get_sport_games, get_sport_news, get_sport_standings, get_sport_stats, get_dummy_play_by_play
    
    games_data = get_sport_games(sport_key)
    news_data = get_sport_news(sport_key)
    standings_data = get_sport_standings(sport_key)
    stats_data = get_sport_stats(sport_key)
    
    # Get play-by-play for live games
    play_by_play = {}
    for live_game in games_data['live']:
        fixture_id = live_game.get('fixture', {}).get('id')
        if fixture_id:
            play_by_play[fixture_id] = get_dummy_play_by_play(fixture_id, sport_key)
    
    # Helper function for abbreviations
    def get_abbrev(sport, team_name):
        return get_team_abbreviation(sport, team_name)
    
    return render_template('sport_page.html',
                         sport_key=sport_key,
                         sport_info=sport_info,
                         games_data=games_data,
                         news_data=news_data,
                         standings_data=standings_data,
                         stats_data=stats_data,
                         play_by_play=play_by_play,
                         username=username,
                         is_public=is_public,
                         get_abbrev=get_abbrev)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
