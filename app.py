"""
Flask application for Sports Dashboard
Handles user preferences for sports and favorite teams/players
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from hybrid_data import get_live_data, get_upcoming_data, get_recent_data, get_timeline_data, get_standings_data, get_news_data, get_stats_data, get_sport_games
from dummy_data import get_dummy_play_by_play, get_sport_news, get_sport_standings, get_sport_stats
from image_resolver import get_image_resolver
from preferences_storage import get_preferences_storage
from team_abbreviations import get_team_abbreviation
from user_auth import register_user, authenticate_user, get_user_by_id
from smart_cache import prime_cache, CACHE_DURATIONS
from datetime import datetime, timedelta, timezone
from functools import wraps

# Import safe date parser
try:
    from api_adapter import parse_datetime_safe
except ImportError:
    # Fallback if api_adapter not available
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
import os
import uuid
import hybrid_data

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.permanent_session_lifetime = timedelta(days=30)  # Remember login for 30 days

# Flag to track if cache has been warmed
_cache_warmed = False

# ========== HELPER FUNCTIONS FOR HERO DATA ==========

def get_game_time_with_timezone(game_date_str):
    """Generate game time with timezone from date string"""
    try:
        game_date = datetime.fromisoformat(game_date_str.replace('Z', '+00:00'))
        # Format as "7:30 PM PST"
        return game_date.strftime('%I:%M %p PST')
    except:
        return "7:30 PM PST"  # Default fallback

def get_broadcast_network(sport_key):
    """Get broadcast network based on sport"""
    networks = {
        'nfl': 'ESPN',
        'nba': 'TNT',
        'nhl': 'NBC',
        'mlb': 'MLB Network',
        'cricket': 'Star Sports',
        'formula1': 'ESPN',
        'tennis': 'Tennis Channel',
        'golf': 'Golf Channel'
    }
    return networks.get(sport_key, 'ESPN')

def get_game_preview(home_team, away_team, sport_key):
    """Generate dummy game preview text"""
    previews = [
        f"{home_team} looking to extend their win streak as they face division rival {away_team}. Key matchups in all areas of the game will determine the outcome.",
        f"High-stakes showdown as {home_team} hosts {away_team}. Both teams enter this game riding momentum from recent victories.",
        f"{away_team} travels to face {home_team} in what promises to be an intense battle. Playoff implications loom large for both squads.",
        f"Classic rivalry renewed as {home_team} takes on {away_team}. Expect a physical, hard-fought contest from start to finish."
    ]
    import random
    return random.choice(previews)

def get_team_news(team_name):
    """Generate dummy team news"""
    news_items = [
        f"{team_name}'s star player scored 35+ points in their last game, leading the team to victory.",
        f"Coach confirms all key players are healthy and ready for tonight's matchup.",
        f"{team_name} has won 4 of their last 5 games, showing strong form heading into this contest.",
        f"Team practices new defensive schemes to counter opponent's offensive strategies."
    ]
    import random
    return random.choice(news_items)

def get_game_recap(home_team, away_team, home_score, away_score):
    """Generate dummy game recap"""
    winner = home_team if home_score > away_score else away_team
    loser = away_team if home_score > away_score else home_team
    recaps = [
        f"{winner} rallied in the 4th quarter with clutch performances to seal the victory. Key defensive stops with under 3 minutes remaining proved decisive. Final stats show {winner} dominated in rebounds and assists.",
        f"In a closely contested battle, {winner} emerged victorious over {loser}. The game was tied going into the final period before {winner} pulled away. Star players delivered when it mattered most.",
        f"{winner} controlled the pace from start to finish, never trailing in this dominant performance against {loser}. Stellar defense held opponents to season-low scoring totals.",
        f"Comeback complete! {winner} overcame a double-digit deficit to defeat {loser}. The momentum shift came in the 3rd quarter and {winner} never looked back."
    ]
    import random
    return random.choice(recaps)

def get_game_highlights():
    """Generate dummy highlight items with timestamps"""
    highlights = [
        {"title": "Opening tip-off and fast break", "time": "1st Q - 11:45"},
        {"title": "Three-pointer to tie the game", "time": "2nd Q - 6:23"},
        {"title": "Incredible defensive stop", "time": "3rd Q - 8:12"},
        {"title": "Clutch basket in final minute", "time": "4th Q - 0:47"},
        {"title": "Game-winning free throws", "time": "4th Q - 0:03"},
        {"title": "Post-game celebration", "time": "Final"}
    ]
    return highlights

def warm_cache():
    """Pre-fetch data to warm cache before first user visit"""
    global _cache_warmed
    if _cache_warmed:
        return
    
    try:
        print("\n" + "="*60)
        print("🚀 Starting cache warm-up...")
        print("="*60)
        
        # Define what to pre-fetch (only long-lived cache)
        cache_warmup = {
            'upcoming_games_all': (hybrid_data.get_upcoming_data, CACHE_DURATIONS['upcoming_games']),
            'recent_games_all': (hybrid_data.get_recent_data, CACHE_DURATIONS['recent_games']),
        }
        
        prime_cache(cache_warmup)
        print("="*60)
        print("✅ Cache warmed! First page load will be instant!")
        print("="*60 + "\n")
        _cache_warmed = True
    except Exception as e:
        print(f"⚠️  Cache warm-up failed: {e}")
        print("   (App will still work, just slower on first load)")
        _cache_warmed = True  # Mark as attempted to avoid retrying

# Warm cache before first request
@app.before_request
def warm_cache_once():
    """Run cache warming only once on first request"""
    warm_cache()

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
    
    # Build timeline with real API data (with dummy fallback)
    # SIMPLE LAYOUT: First row = upcoming, Second row = past
    live_events = get_live_data()
    # Use smart timeline data that re-categorizes games based on current time
    upcoming_fixtures, recent_results = get_timeline_data()
    
    # Helper function to get event date
    def get_event_date(event):
        try:
            date_str = event.get('fixture', {}).get('date', '')
            if date_str:
                return parse_datetime_safe(date_str)
            return datetime.now(timezone.utc)
        except:
            return datetime.now(timezone.utc)
    
    # FIRST ROW: Live + Upcoming games (sorted by date, soonest first)
    first_row_events = []
    for sport_key in selected_sports:
        # Add live events
        if sport_key in live_events:
            for event in live_events[sport_key]:
                event['sport_key'] = sport_key
                event['is_live'] = True
                first_row_events.append(event)
        
        # Add upcoming events
        if sport_key in upcoming_fixtures:
            for event in upcoming_fixtures[sport_key]:
                event['sport_key'] = sport_key
                event['is_live'] = False
                first_row_events.append(event)
    
    # Sort first row: Live first, then by date (soonest first)
    first_row_events.sort(key=lambda e: (0 if e.get('is_live') else 1, get_event_date(e)))
    
    # SECOND ROW: Recent/Past games (sorted by date, most recent first)
    second_row_events = []
    for sport_key in selected_sports:
        if sport_key in recent_results:
            for event in recent_results[sport_key]:
                event['sport_key'] = sport_key
                event['is_live'] = False
                event['is_completed'] = True
                second_row_events.append(event)
    
    # Sort second row: Most recent games first
    second_row_events.sort(key=lambda e: get_event_date(e), reverse=True)
    
    # Combine for template (first event from first row used for hero)
    timeline_events = first_row_events + second_row_events
    
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
            hero_data['news'] = get_news_data(team_name)
            hero_data['stats'] = get_stats_data(team_name, first_event['sport_key'])  # Pass sport_key for real data!
            hero_data['standings'] = get_standings_data(first_event['sport_key'])
    
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


@app.route('/api/hero-data', methods=['POST'])
def get_hero_data():
    """Get hero data (stats, news, standings) for a specific event - prioritizes user's favorite team"""
    try:
        event = request.json.get('event', {})
        if not event:
            return jsonify({'error': 'No event data provided'}), 400
        
        home_team = event.get('teams', {}).get('home', {}).get('name')
        away_team = event.get('teams', {}).get('away', {}).get('name')
        sport_key = event.get('sport_key')
        
        if not sport_key or (not home_team and not away_team):
            return jsonify({'error': 'Missing team or sport information'}), 400
        
        # Determine which team to show stats for (prioritize user's favorite)
        team_name = None
        user_favorites = session.get('favorites', {}).get(sport_key, [])
        
        # Check if either team is the user's favorite
        for fav in user_favorites:
            fav_lower = fav.lower()
            if home_team and fav_lower in home_team.lower():
                team_name = home_team
                break
            elif away_team and fav_lower in away_team.lower():
                team_name = away_team
                break
        
        # If no favorite found, default to home team, then away team
        if not team_name:
            team_name = home_team or away_team
        
        # Get hero data
        hero_data = {
            'stats': get_stats_data(team_name, sport_key),
            'home_team_stats': get_stats_data(home_team, sport_key),  # Stats for home team
            'away_team_stats': get_stats_data(away_team, sport_key),  # Stats for away team
            'standings': get_standings_data(sport_key),
            'news': get_news_data(team_name),
            'selected_team': team_name,  # Let frontend know which team we selected
            'game_time': get_game_time_with_timezone(event.get('fixture', {}).get('date', '')),
            'network': get_broadcast_network(sport_key)
        }
        
        # Add conditional data based on game status
        if event.get('is_completed'):
            hero_data['recap'] = get_game_recap(
                home_team, away_team,
                event.get('goals', {}).get('home', 0),
                event.get('goals', {}).get('away', 0)
            )
            hero_data['highlights'] = get_game_highlights()
        else:
            hero_data['preview'] = get_game_preview(home_team, away_team, sport_key)
            hero_data['team_news'] = get_team_news(team_name)
        
        return jsonify(hero_data)
        
    except Exception as e:
        print(f"Error in /api/hero-data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/standings', methods=['POST'])
def get_standings():
    """Get full standings for a sport (all divisions)"""
    try:
        sport_key = request.json.get('sport_key')
        if not sport_key:
            return jsonify({'error': 'No sport_key provided'}), 400
        
        # Get standings data
        standings_data = get_standings_data(sport_key)
        
        return jsonify(standings_data)
        
    except Exception as e:
        print(f"Error in /api/standings: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


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
    
    # Build timeline with SIMPLE LAYOUT: First row = upcoming, Second row = past
    # Get real API data (with dummy fallback)
    live_events = get_live_data()
    # Use smart timeline data that re-categorizes games based on current time
    upcoming_fixtures, recent_results = get_timeline_data()
    
    # Helper function to get event date
    def get_event_date(event):
        try:
            date_str = event.get('fixture', {}).get('date', '')
            if date_str:
                return parse_datetime_safe(date_str)
            return datetime.now(timezone.utc)
        except:
            return datetime.now(timezone.utc)
    
    # FIRST ROW: Live + Upcoming games (favorites first, then by date)
    first_row_events = []
    for sport_key in selected_sports:
        # Add live events
        if sport_key in live_events:
            for event in live_events[sport_key]:
                event['sport_key'] = sport_key
                event['is_live'] = True
                event['is_favorite'] = _is_favorite_event(event, sport_key, favorites)
                first_row_events.append(event)
        
        # Add upcoming events
        if sport_key in upcoming_fixtures:
            for event in upcoming_fixtures[sport_key]:
                event['sport_key'] = sport_key
                event['is_live'] = False
                event['is_favorite'] = _is_favorite_event(event, sport_key, favorites)
                first_row_events.append(event)
    
    # Sort first row: Live first, then favorites, then by date (soonest first)
    first_row_events.sort(key=lambda e: (
        0 if e.get('is_live') else 1,
        0 if e.get('is_favorite') else 1,
        get_event_date(e)
    ))
    
    # SECOND ROW: Recent/Past games (favorites first, then most recent)
    second_row_events = []
    for sport_key in selected_sports:
        if sport_key in recent_results:
            for event in recent_results[sport_key]:
                event['sport_key'] = sport_key
                event['is_live'] = False
                event['is_completed'] = True
                event['is_favorite'] = _is_favorite_event(event, sport_key, favorites)
                second_row_events.append(event)
    
    # Sort second row: Favorites first, then most recent
    second_row_events.sort(key=lambda e: (
        0 if e.get('is_favorite') else 1,
        -get_event_date(e).timestamp()
    ))
    
    # Combine for hero data selection (first event from either row)
    timeline_events = first_row_events + second_row_events
    
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
        
        # Get team name for news/stats - prioritize user's favorite team
        home_team = first_event.get('teams', {}).get('home', {}).get('name')
        away_team = first_event.get('teams', {}).get('away', {}).get('name')
        sport_key = first_event.get('sport_key')
        
        team_name = None
        if sport_key:
            user_favorites = favorites.get(sport_key, [])
            
            # Check if either team is the user's favorite
            for fav in user_favorites:
                fav_lower = fav.lower()
                if home_team and fav_lower in home_team.lower():
                    team_name = home_team
                    break
                elif away_team and fav_lower in away_team.lower():
                    team_name = away_team
                    break
        
        # If no favorite found, default to home team, then away team
        if not team_name:
            team_name = home_team or away_team
        
        if team_name and sport_key:
            hero_data['news'] = get_news_data(team_name)
            hero_data['stats'] = get_stats_data(team_name, sport_key)
            hero_data['standings'] = get_standings_data(sport_key)
            
            # Add additional hero data
            hero_data['game_time'] = get_game_time_with_timezone(first_event.get('fixture', {}).get('date', ''))
            hero_data['network'] = get_broadcast_network(sport_key)
    
    # Get both teams' stats for display
    home_team_stats = None
    away_team_stats = None
    if timeline_events:
        first_event = timeline_events[0]
        home_team = first_event.get('teams', {}).get('home', {}).get('name')
        away_team = first_event.get('teams', {}).get('away', {}).get('name')
        sport_key = first_event.get('sport_key')
        
        if home_team and sport_key:
            home_team_stats = get_stats_data(home_team, sport_key)
        if away_team and sport_key:
            away_team_stats = get_stats_data(away_team, sport_key)
            
            if first_event.get('is_completed'):
                # Completed game - add recap and highlights
                hero_data['recap'] = get_game_recap(
                    home_team, away_team,
                    first_event.get('goals', {}).get('home', 0),
                    first_event.get('goals', {}).get('away', 0)
                )
                hero_data['highlights'] = get_game_highlights()
            else:
                # Upcoming game - add preview and team news
                hero_data['preview'] = get_game_preview(home_team, away_team, sport_key)
                hero_data['team_news'] = get_team_news(team_name)
    
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
                         home_team_stats=home_team_stats,
                         away_team_stats=away_team_stats,
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
    
    # Get all games data (using hybrid data - reuses dashboard cache!)
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
    
    # Get all data for this sport (using hybrid data)
    
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
