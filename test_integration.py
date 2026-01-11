#!/usr/bin/env python3
"""
Test script to verify the hybrid data integration is working correctly
"""

from hybrid_data import get_live_data, get_upcoming_data, get_recent_data, get_standings_data

print("="*60)
print("TESTING HYBRID DATA INTEGRATION")
print("="*60)

# Test each sport
sports = ['nba', 'nfl', 'nhl', 'mlb']

for sport in sports:
    print(f"\n{sport.upper()}:")
    print("-" * 40)
    
    # Test live games
    try:
        live = get_live_data()
        live_count = len(live.get(sport, []))
        if live_count > 0:
            print(f"  ✓ {live_count} live game(s)")
            # Show first live game
            game = live[sport][0]
            home = game['teams']['home']['name']
            away = game['teams']['away']['name']
            print(f"    🔴 {away} @ {home}")
        else:
            print(f"  • No live games")
    except Exception as e:
        print(f"  ❌ Error getting live games: {e}")
    
    # Test upcoming games
    try:
        upcoming = get_upcoming_data()
        upcoming_count = len(upcoming.get(sport, []))
        if upcoming_count > 0:
            print(f"  ✓ {upcoming_count} upcoming game(s)")
            # Show first upcoming game
            game = upcoming[sport][0]
            home = game['teams']['home']['name']
            away = game['teams']['away']['name']
            status = game['fixture']['status']['long']
            print(f"    📅 {away} @ {home} - {status}")
        else:
            print(f"  • No upcoming games")
    except Exception as e:
        print(f"  ❌ Error getting upcoming games: {e}")
    
    # Test recent games
    try:
        recent = get_recent_data()
        recent_count = len(recent.get(sport, []))
        if recent_count > 0:
            print(f"  ✓ {recent_count} recent game(s)")
            # Show first recent game with score
            game = recent[sport][0]
            home = game['teams']['home']['name']
            away = game['teams']['away']['name']
            home_score = game['goals']['home']
            away_score = game['goals']['away']
            if home_score is not None and away_score is not None:
                print(f"    ✅ {away} {away_score} - {home_score} {home}")
        else:
            print(f"  • No recent games")
    except Exception as e:
        print(f"  ❌ Error getting recent games: {e}")
    
    # Test standings
    try:
        standings = get_standings_data(sport)
        if standings and standings[0].get('league', {}).get('standings'):
            teams = standings[0]['league']['standings'][0]
            print(f"  ✓ Standings: {len(teams)} teams")
            # Show top 3
            for i, team in enumerate(teams[:3]):
                team_name = team['team']['name']
                wins = team.get('wins', 0)
                losses = team.get('losses', 0)
                print(f"    {i+1}. {team_name} ({wins}-{losses})")
        else:
            print(f"  • No standings data")
    except Exception as e:
        print(f"  ❌ Error getting standings: {e}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
print()
print("✅ If you see data above, real API is working!")
print("✅ If you see 'No data', that's okay (off-season or no games today)")
print("✅ If you see errors, check your internet connection")
print()
print("🚀 Ready to run: python3 app.py")

