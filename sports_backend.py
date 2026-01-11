import requests
from datetime import datetime, timedelta

HEADERS = {
    "User-Agent": "sports-data-client/1.0"
}

# ======================
# ESPN-BASED LEAGUES
# ======================

ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports"

ESPN_LEAGUES = {
    "nba": "basketball/nba",
    "nfl": "football/nfl",
    "nhl": "hockey/nhl",
}

def fetch_json(url, params=None):
    r = requests.get(url, params=params, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()

def espn_scoreboard(league, date=None):
    path = ESPN_LEAGUES[league]
    url = f"{ESPN_BASE}/{path}/scoreboard"

    params = {}
    if date:
        params["dates"] = date.strftime("%Y%m%d")

    data = fetch_json(url, params)

    games = []
    for event in data.get("events", []):
        comp = event["competitions"][0]
        status_info = comp["status"]["type"]
        status = status_info["description"]
        
        # Determine if game is live
        is_live = status_info["state"] == "in"

        teams = {}
        for c in comp["competitors"]:
            teams[c["homeAway"]] = {
                "team": c["team"]["displayName"],
                "score": c.get("score"),
                "logo": c["team"].get("logo"),  # Team logo URL
                "abbreviation": c["team"].get("abbreviation"),
            }

        games.append({
            "id": event["id"],
            "date": event["date"],
            "status": status,
            "is_live": is_live,
            "home": teams.get("home"),
            "away": teams.get("away"),
        })

    return games

def espn_standings(league):
    """
    Get FULL standings from ESPN's real standings API (not scoreboard)
    Returns ALL teams with division-based rankings
    """
    path = ESPN_LEAGUES[league]
    url = f"https://site.api.espn.com/apis/v2/sports/{path}/standings"
    data = fetch_json(url)
    
    all_teams = []
    
    # Iterate through all divisions/conferences and assign division ranks
    for division in data.get("children", []):
        entries = division.get("standings", {}).get("entries", [])
        division_name = division.get("name", "")
        
        # Sort entries by wins within this division (ESPN usually provides them sorted)
        division_teams = []
        for rank, entry in enumerate(entries, 1):
            team_info = entry.get("team", {})
            
            # Extract wins, losses, winPercent from stats array
            stats_dict = {}
            for stat in entry.get("stats", []):
                stats_dict[stat.get("name")] = stat.get("value")
            
            # Get logo from logos array (use first logo)
            logo_url = None
            logos = team_info.get("logos", [])
            if logos and len(logos) > 0:
                logo_url = logos[0].get("href")
            
            division_teams.append({
                "team": team_info.get("displayName", ""),
                "abbreviation": team_info.get("abbreviation", ""),
                "logo": logo_url,
                "wins": int(stats_dict.get("wins", 0)),
                "losses": int(stats_dict.get("losses", 0)),
                "winPercent": stats_dict.get("winPercent", 0),
                "division": division_name,
                "divisionRank": rank  # Rank within division
            })
        
        # Sort by wins within division to ensure correct ranking
        division_teams.sort(key=lambda x: x["wins"], reverse=True)
        
        # Reassign ranks after sorting
        for idx, team in enumerate(division_teams, 1):
            team["divisionRank"] = idx
        
        all_teams.extend(division_teams)
    
    # Sort all teams by wins for overall display order (but keep divisionRank)
    standings = sorted(all_teams, key=lambda x: x["wins"], reverse=True)
    return standings

def espn_game_stats(league, game_id):
    path = ESPN_LEAGUES[league]
    url = f"{ESPN_BASE}/{path}/summary"
    data = fetch_json(url, {"event": game_id})

    stats = {}
    for team in data.get("boxscore", {}).get("teams", []):
        stats[team["team"]["displayName"]] = {
            s["label"]: s["value"] for s in team.get("statistics", [])
        }

    return stats

# ======================
# HELPER FUNCTIONS FOR DATE RANGES
# ======================

def espn_recent_games(league, days_back=7):
    """Get games from the past X days"""
    games = []
    today = datetime.now()
    
    for i in range(days_back):
        date = today - timedelta(days=i)
        try:
            day_games = espn_scoreboard(league, date)
            games.extend(day_games)
        except:
            pass  # Skip days with no games or errors
    
    return games

def espn_upcoming_games(league, days_ahead=7):
    """Get games for the next X days"""
    games = []
    today = datetime.now()
    
    for i in range(days_ahead):
        date = today + timedelta(days=i)
        try:
            day_games = espn_scoreboard(league, date)
            games.extend(day_games)
        except:
            pass  # Skip days with no games or errors
    
    return games

def espn_live_games(league):
    """Get only games that are currently live"""
    games = espn_scoreboard(league)
    return [g for g in games if g.get("is_live")]

# ======================
# MLB STATS API
# ======================

MLB_BASE = "https://statsapi.mlb.com/api/v1"

def mlb_schedule(date=None):
    params = {
        "sportId": 1,
        "hydrate": "team,linescore",
    }
    if date:
        params["date"] = date.strftime("%Y-%m-%d")

    data = fetch_json(f"{MLB_BASE}/schedule", params)

    games = []
    for d in data.get("dates", []):
        for g in d.get("games", []):
            # Determine if game is live
            status = g["status"]["detailedState"]
            is_live = status in ["In Progress", "Live"]
            
            games.append({
                "id": g["gamePk"],
                "date": g["gameDate"],
                "status": status,
                "is_live": is_live,
                "home": {
                    "team": g["teams"]["home"]["team"]["name"],
                    "abbreviation": g["teams"]["home"]["team"].get("abbreviation", ""),
                    "score": g["teams"]["home"].get("score"),
                },
                "away": {
                    "team": g["teams"]["away"]["team"]["name"],
                    "abbreviation": g["teams"]["away"]["team"].get("abbreviation", ""),
                    "score": g["teams"]["away"].get("score"),
                },
            })

    return games

def mlb_standings():
    params = {
        "leagueId": "103,104",  # AL, NL
        "season": datetime.utcnow().year,
    }
    data = fetch_json(f"{MLB_BASE}/standings", params)

    standings = []
    for record in data.get("records", []):
        division = record.get("division", {}).get("name", "")
        for team in record.get("teamRecords", []):
            standings.append({
                "team": team["team"]["name"],
                "abbreviation": team["team"].get("abbreviation", ""),
                "wins": team["wins"],
                "losses": team["losses"],
                "winPercent": team.get("leagueRecord", {}).get("pct", "0"),
                "gamesBack": team.get("gamesBack", "0"),
                "division": division,
            })

    return standings

def mlb_game_stats(game_id):
    data = fetch_json(f"{MLB_BASE}/game/{game_id}/boxscore")

    stats = {}
    for side in ["home", "away"]:
        team = data["teams"][side]
        stats[team["team"]["name"]] = team["teamStats"]["batting"]

    return stats

def mlb_recent_games(days_back=7):
    """Get MLB games from the past X days"""
    games = []
    today = datetime.now()
    
    for i in range(days_back):
        date = today - timedelta(days=i)
        try:
            day_games = mlb_schedule(date)
            games.extend(day_games)
        except:
            pass
    
    return games

def mlb_upcoming_games(days_ahead=7):
    """Get MLB games for the next X days"""
    games = []
    today = datetime.now()
    
    for i in range(days_ahead):
        date = today + timedelta(days=i)
        try:
            day_games = mlb_schedule(date)
            games.extend(day_games)
        except:
            pass
    
    return games

def mlb_live_games():
    """Get only MLB games that are currently live"""
    games = mlb_schedule()
    return [g for g in games if g.get("is_live")]

# ======================
# UNIFIED API
# ======================

def get_live_games(sport):
    """Get live games for any sport"""
    if sport in ESPN_LEAGUES:
        return espn_live_games(sport)
    elif sport == "mlb":
        return mlb_live_games()
    return []

def get_upcoming_games(sport, days=7):
    """Get upcoming games for any sport"""
    if sport in ESPN_LEAGUES:
        return espn_upcoming_games(sport, days)
    elif sport == "mlb":
        return mlb_upcoming_games(days)
    return []

def get_recent_games(sport, days=7):
    """Get recent games for any sport"""
    if sport in ESPN_LEAGUES:
        return espn_recent_games(sport, days)
    elif sport == "mlb":
        return mlb_recent_games(days)
    return []

def get_standings(sport):
    """Get standings for any sport"""
    if sport in ESPN_LEAGUES:
        return espn_standings(sport)
    elif sport == "mlb":
        return mlb_standings()
    return []

# ======================
# MAIN DEMO
# ======================

if __name__ == "__main__":
    print("="*60)
    print("TESTING ENHANCED SPORTS BACKEND")
    print("="*60)

    # Test NBA
    print("\n" + "="*60)
    print("NBA - Live Games")
    live = get_live_games("nba")
    if live:
        for g in live[:2]:
            print(f"🔴 LIVE: {g['away']['team']} @ {g['home']['team']} - {g['away'].get('score', 0)}-{g['home'].get('score', 0)}")
    else:
        print("No live games")

    print("\nNBA - Upcoming Games (next 3 days)")
    upcoming = get_upcoming_games("nba", days=3)
    for g in upcoming[:3]:
        live_indicator = "🔴 " if g.get('is_live') else ""
        print(f"{live_indicator}{g['status']}: {g['away']['team']} @ {g['home']['team']}")

    print("\nNBA - Standings (Top 5)")
    standings = get_standings("nba")
    for s in standings[:5]:
        logo = "🏀" if s.get('logo') else ""
        print(f"{logo} {s['team']} ({s.get('abbreviation', 'N/A')}) - {s['wins']}-{s['losses']} ({s.get('division', 'N/A')})")

    # Test NFL
    print("\n" + "="*60)
    print("NFL - Upcoming Games (next 7 days)")
    nfl_games = get_upcoming_games("nfl", days=7)
    for g in nfl_games[:3]:
        print(f"{g['status']}: {g['away']['team']} @ {g['home']['team']}")

    # Test MLB
    print("\n" + "="*60)
    print("MLB - Recent Games (last 3 days)")
    mlb_recent = get_recent_games("mlb", days=3)
    for g in mlb_recent[:3]:
        print(f"{g['status']}: {g['away']['team']} @ {g['home']['team']}")

    print("\n✅ All tests complete!")
