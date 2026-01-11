# API Integration Plan - Real Data vs Dummy Data

## 📊 Data Comparison

### ✅ **CAN REPLACE** (sports_backend.py has real data)

| Dummy Function | Real API Function | Sports Available | Status |
|----------------|-------------------|------------------|--------|
| `get_dummy_fixtures()` | `get_upcoming_games(sport, days)` | NBA, NFL, NHL, MLB | ✅ Ready |
| `get_dummy_results()` | `get_recent_games(sport, days)` | NBA, NFL, NHL, MLB | ✅ Ready |
| `get_dummy_live_events()` | `get_live_games(sport)` | NBA, NFL, NHL, MLB | ✅ Ready |
| `get_dummy_standings()` | `get_standings(sport)` | NBA, NFL, NHL, MLB | ✅ Ready |

### ❌ **CANNOT REPLACE YET** (need different solution)

| Dummy Function | What It Provides | Alternative |
|----------------|------------------|-------------|
| `get_dummy_news()` | Team news articles | Use NewsAPI or RSS later |
| `get_dummy_stats()` | Individual team stats | Can extract from `espn_game_stats()` |
| `get_dummy_play_by_play()` | Live play-by-play | ESPN has this, need separate endpoint |

### ⚠️ **UNSUPPORTED SPORTS** (no API available)

- Cricket, Formula 1, Tennis, Golf
- Will continue using dummy data for these

---

## 🔄 Data Structure Mapping

### Current Dummy Format vs Real API Format

**Dummy Data Structure:**
```python
{
    'fixture': {
        'id': 1001,
        'date': '2024-01-10T19:00:00',
        'status': {'short': 'NS'},
        'venue': {'name': 'Stadium', 'city': 'City'}
    },
    'league': {'name': 'NFL', 'country': 'USA'},
    'teams': {
        'home': {'id': 1, 'name': 'Team A', 'logo': ''},
        'away': {'id': 2, 'name': 'Team B', 'logo': ''}
    },
    'goals': {'home': None, 'away': None}
}
```

**Real API Structure:**
```python
{
    'id': '12345',
    'date': '2024-01-10T19:00:00',
    'status': 'Scheduled',
    'is_live': False,
    'home': {
        'team': 'Team A',
        'score': None,
        'logo': 'https://...',
        'abbreviation': 'TEA'
    },
    'away': {
        'team': 'Team B',
        'score': None,
        'logo': 'https://...',
        'abbreviation': 'TEB'
    }
}
```

**⚠️ MISMATCH!** - Need adapter/transformer

---

## 🛠️ Integration Strategy

### **Phase 1: Create Data Adapter**
Create `api_adapter.py` to transform ESPN/MLB data → dummy data format

```python
def transform_game_to_dummy_format(game, sport):
    """Convert real API game to dummy format"""
    return {
        'fixture': {
            'id': game['id'],
            'date': game['date'],
            'status': {'short': 'LIVE' if game['is_live'] else 'NS'},
        },
        'league': {'name': sport.upper()},
        'teams': {
            'home': {
                'name': game['home']['team'],
                'logo': game['home'].get('logo', ''),
            },
            'away': {
                'name': game['away']['team'],
                'logo': game['away'].get('logo', ''),
            }
        },
        'goals': {
            'home': game['home'].get('score'),
            'away': game['away'].get('score')
        },
        'sport_key': sport
    }
```

### **Phase 2: Create Hybrid Data Source**
Update functions to use real data when available, dummy data as fallback

```python
from sports_backend import get_live_games, get_upcoming_games, get_recent_games, get_standings
from api_adapter import transform_games, transform_standings

REAL_DATA_SPORTS = ['nba', 'nfl', 'nhl', 'mlb']

def get_games_data():
    """Get games with real API for supported sports"""
    all_games = {}
    
    for sport in selected_sports:
        if sport in REAL_DATA_SPORTS:
            # Use real API
            try:
                raw_games = get_upcoming_games(sport, days=7)
                all_games[sport] = transform_games(raw_games, sport)
            except:
                # Fallback to dummy
                all_games[sport] = get_dummy_fixtures().get(sport, [])
        else:
            # Use dummy for unsupported sports
            all_games[sport] = get_dummy_fixtures().get(sport, [])
    
    return all_games
```

### **Phase 3: Gradual Rollout**
1. ✅ **Start with live games** (most important)
2. ✅ **Add upcoming/recent games**
3. ✅ **Add standings**
4. ⏳ **Keep dummy data for news** (integrate later)
5. ⏳ **Keep dummy data for unsupported sports**

---

## 📝 Implementation Checklist

### Step 1: Create Adapter ✅
- [ ] Create `api_adapter.py`
- [ ] Add `transform_game()` function
- [ ] Add `transform_standings()` function
- [ ] Test transformations

### Step 2: Update Dashboard Route ✅
- [ ] Replace `get_dummy_fixtures()` with hybrid function
- [ ] Replace `get_dummy_results()` with hybrid function
- [ ] Replace `get_dummy_live_events()` with hybrid function
- [ ] Keep `get_dummy_news()` for now
- [ ] Keep `get_dummy_stats()` for now

### Step 3: Update Live Games Route ✅
- [ ] Same changes as dashboard
- [ ] Test live game detection

### Step 4: Update Sport Pages ✅
- [ ] Replace game data with real API
- [ ] Keep play-by-play as dummy (for now)

### Step 5: Testing ✅
- [ ] Test NBA games
- [ ] Test NFL games
- [ ] Test NHL games
- [ ] Test MLB games
- [ ] Verify fallback to dummy works
- [ ] Test with no internet connection

---

## 🎯 Expected Results After Integration

### For NBA, NFL, NHL, MLB:
- ✅ **Real live scores** when games are active
- ✅ **Real upcoming games** (accurate schedule)
- ✅ **Real recent results** (actual scores)
- ✅ **Real standings** (current win-loss records)
- ✅ **Team logos** (official ESPN/MLB logos)
- ❌ **Dummy news** (until we add NewsAPI)

### For Cricket, F1, Tennis, Golf:
- ❌ **All dummy data** (no API available)
- ✅ **UI still works** (seamless experience)

---

## 🚀 Next Steps

1. **Create `api_adapter.py`** - Transform real API → dummy format
2. **Test adapter** - Ensure data structure matches
3. **Update app.py** - Replace dummy calls with hybrid calls
4. **Test thoroughly** - Verify both real and dummy data work
5. **Deploy** - Real sports data live!

---

## 💡 Future Enhancements

### Near Term:
- Add **NewsAPI** integration for real news
- Extract **team stats** from game stats
- Add **player stats** from ESPN

### Long Term:
- Find APIs for Cricket, F1, Tennis, Golf
- Add **play-by-play** for live games
- Add **injury reports**
- Add **betting odds**

---

## ⚠️ Important Notes

- **Error Handling**: Always have dummy data fallback
- **Rate Limiting**: ESPN/MLB are free but may have limits
- **Caching**: Consider caching to reduce API calls
- **Testing**: Test with both live data and dummy fallback
- **User Experience**: Should be seamless whether real or dummy data

