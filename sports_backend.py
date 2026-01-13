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

# ======================
# NEW SPORTS
# ======================

# ==========================================
# CRICKET (ICC iCalendar + Cricsheet)
# ==========================================

def get_cricket_fixtures(team_filter=None):
    """Get upcoming cricket matches from ICC iCalendar feed"""
    try:
        from icalendar import Calendar
        from datetime import datetime as dt
        
        ical_url = "https://ics.ecal.com/ecal-sub/6965fee2b0ce3d0002b9d47f/ICC%20Cricket.ics"
        r = requests.get(ical_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        
        cal = Calendar.from_ical(r.text)
        matches = []
        now = dt.now()
        
        for component in cal.walk():
            if component.name == "VEVENT":
                summary = str(component.get('summary', ''))
                if team_filter and team_filter not in summary:
                    continue
                
                dtstart = component.get('dtstart')
                location = str(component.get('location', ''))
                description = str(component.get('description', ''))
                start_dt = dtstart.dt if dtstart else None
                
                if start_dt and hasattr(start_dt, 'replace'):
                    if start_dt.tzinfo is None:
                        from datetime import timezone
                        start_dt = start_dt.replace(tzinfo=timezone.utc)
                    
                    if start_dt > now.replace(tzinfo=start_dt.tzinfo):
                        teams = []
                        summary_clean = summary.replace('🏏 ', '').strip()
                        if ':' in summary_clean:
                            match_part = summary_clean.split(':', 1)[1].strip()
                            if ' v ' in match_part:
                                teams = [t.strip() for t in match_part.split(' v ')]
                            elif ' vs ' in match_part:
                                teams = [t.strip() for t in match_part.split(' vs ')]
                        
                        match_type = ""
                        if "T20 International" in description:
                            match_type = "T20I"
                        elif "One-Day International" in description or "ODI" in description:
                            match_type = "ODI"
                        elif "Test" in description:
                            match_type = "Test"
                        
                        matches.append({
                            "match": f"{teams[0]} vs {teams[1]}" if len(teams) == 2 else summary_clean,
                            "teams": teams,
                            "venue": location.replace('\\,', ','),
                            "date": start_dt.strftime('%Y-%m-%d'),
                            "start_time": start_dt.isoformat(),
                            "match_type": match_type,
                            "status": "Upcoming",
                            "source": "ical"
                        })
        return matches
    except Exception as e:
        print(f"Error fetching cricket fixtures: {e}")
        return []


def get_cricket_results(days=7, team_filter=None):
    """Get recent cricket results from Cricsheet"""
    import zipfile, io, json
    
    try:
        cricsheet_url = f"https://cricsheet.org/downloads/recently_played_{days}_json.zip"
        r = requests.get(cricsheet_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        r.raise_for_status()
        
        matches = []
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            json_files = [f for f in z.namelist() if f.endswith('.json')]
            
            for filename in json_files[:50]:
                try:
                    with z.open(filename) as f:
                        match_data = json.load(f)
                        info = match_data.get('info', {})
                        teams = info.get('teams', [])
                        
                        if team_filter and not any(team_filter in team for team in teams):
                            continue
                        
                        outcome = info.get('outcome', {})
                        winner = outcome.get('winner', '')
                        by_info = outcome.get('by', {})
                        
                        result_str = ""
                        if winner:
                            if 'runs' in by_info:
                                result_str = f"{winner} won by {by_info['runs']} runs"
                            elif 'wickets' in by_info:
                                result_str = f"{winner} won by {by_info['wickets']} wickets"
                            else:
                                result_str = f"{winner} won"
                        
                        innings = match_data.get('innings', [])
                        scores = {}
                        for inning in innings:
                            team = inning.get('team', '')
                            overs = inning.get('overs', [])
                            total_runs = total_wickets = 0
                            for over in overs:
                                for delivery in over.get('deliveries', []):
                                    total_runs += delivery.get('runs', {}).get('total', 0)
                                    if 'wickets' in delivery:
                                        total_wickets += len(delivery['wickets'])
                            scores[team] = f"{total_runs}/{total_wickets}"
                        
                        matches.append({
                            "match": f"{teams[0]} vs {teams[1]}" if len(teams) == 2 else "Unknown",
                            "teams": teams,
                            "status": "Complete",
                            "result": result_str,
                            "winner": winner,
                            "scores": scores,
                            "match_type": info.get('match_type', '').upper(),
                            "venue": info.get('venue', ''),
                            "date": info.get('dates', [''])[0],
                            "source": "cricsheet"
                        })
                except:
                    continue
        return matches
    except Exception as e:
        print(f"Error fetching cricket results: {e}")
        return []


# ==========================================
# TENNIS (ESPN API)
# ==========================================

def get_tennis_matches(tour="atp"):
    """Get tennis matches from ESPN (ATP or WTA)"""
    url = f"{ESPN_BASE}/tennis/{tour}/scoreboard"
    return fetch_json(url)


def get_tennis_rankings(tour="atp"):
    """Get tennis rankings from ESPN"""
    url = f"{ESPN_BASE}/tennis/{tour}/rankings"
    return fetch_json(url)


# ==========================================
# GOLF (ESPN API)
# ==========================================

def get_golf_tournament():
    """Get current golf tournament from ESPN PGA"""
    url = f"{ESPN_BASE}/golf/pga/scoreboard"
    return fetch_json(url)


# ==========================================
# FORMULA 1 (FastF1)
# ==========================================

def get_f1_schedule(season="current"):
    """Get F1 season schedule using FastF1"""
    try:
        import fastf1
        from datetime import datetime as dt
        
        if season == "current":
            season = dt.now().year
        
        schedule = fastf1.get_event_schedule(season)
        races = []
        
        for idx, event in schedule.iterrows():
            races.append({
                "round": event["RoundNumber"],
                "race_name": event["EventName"],
                "country": event["Country"],
                "location": event["Location"],
                "date": event["EventDate"].strftime("%Y-%m-%d") if hasattr(event["EventDate"], 'strftime') else str(event["EventDate"]),
                "circuit": event["Location"],
                "season": season
            })
        return races
    except Exception as e:
        print(f"Error fetching F1 schedule: {e}")
        return []


def get_f1_next_race():
    """Get next upcoming F1 race"""
    try:
        import fastf1
        from datetime import datetime as dt
        
        schedule = fastf1.get_event_schedule(dt.now().year)
        now = dt.now()
        
        for idx, event in schedule.iterrows():
            event_date = event["EventDate"]
            if hasattr(event_date, 'to_pydatetime'):
                event_date = event_date.to_pydatetime()
            if hasattr(event_date, 'replace') and event_date.tzinfo:
                event_date = event_date.replace(tzinfo=None)
            
            if event_date > now:
                return {
                    "round": event["RoundNumber"],
                    "race_name": event["EventName"],
                    "country": event["Country"],
                    "location": event["Location"],
                    "date": event["EventDate"].strftime("%Y-%m-%d") if hasattr(event["EventDate"], 'strftime') else str(event["EventDate"]),
                    "circuit": event["Location"],
                }
        return None
    except:
        return None


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
