"""
Smart persistent cache with tiered durations
"""

import json
import time
import os
from typing import Any, Callable
from pathlib import Path

# Cache directory
CACHE_DIR = Path(__file__).parent / "cache_data"
CACHE_DIR.mkdir(exist_ok=True)

# Cache durations (in seconds)
CACHE_DURATIONS = {
    'live_games': 30,           # 30 seconds - needs frequent updates (not using for now)
    'upcoming_games': 86400,    # 24 hours - schedules published in advance, rarely change
    'recent_games': 172800,     # 48 hours - final scores NEVER change
    'standings': 21600,         # 6 hours - only change after games finish
}


def _get_cache_path(key: str) -> Path:
    """Get file path for cache key"""
    return CACHE_DIR / f"{key}.json"


def _read_cache(key: str) -> tuple[Any, float]:
    """
    Read cache from disk
    
    Returns:
        (data, timestamp) or (None, 0) if not found
    """
    cache_file = _get_cache_path(key)
    
    if not cache_file.exists():
        return None, 0
    
    try:
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
            return cache_data['data'], cache_data['timestamp']
    except Exception as e:
        print(f"⚠️  Error reading cache {key}: {e}")
        return None, 0


def _write_cache(key: str, data: Any):
    """Write cache to disk"""
    cache_file = _get_cache_path(key)
    
    try:
        cache_data = {
            'data': data,
            'timestamp': time.time()
        }
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
    except Exception as e:
        print(f"⚠️  Error writing cache {key}: {e}")


def cached_call(key: str, func: Callable, ttl_seconds: int = 3600) -> Any:
    """
    Smart cached function call with persistent storage
    
    Args:
        key: Unique cache key
        func: Function to call if not cached
        ttl_seconds: Time to live in seconds
        
    Returns:
        Cached or fresh result
    """
    now = time.time()
    
    # Try to read from disk
    cached_data, cached_time = _read_cache(key)
    
    # Check if cached and not expired
    if cached_data is not None and (now - cached_time) < ttl_seconds:
        age_minutes = (now - cached_time) / 60
        print(f"✓ Using cached {key} (age: {age_minutes:.1f}m, ttl: {ttl_seconds/60:.0f}m)")
        return cached_data
    
    # Cache expired or missing - fetch fresh data
    print(f"⟳ Fetching fresh {key} (cache expired or missing)")
    result = func()
    
    # Write to disk
    _write_cache(key, result)
    
    return result


def get_cache_info() -> dict:
    """Get info about all cached items"""
    info = {}
    now = time.time()
    
    for cache_file in CACHE_DIR.glob("*.json"):
        key = cache_file.stem
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                age_seconds = now - cache_data['timestamp']
                info[key] = {
                    'age_seconds': age_seconds,
                    'age_minutes': age_seconds / 60,
                    'age_hours': age_seconds / 3600,
                    'timestamp': cache_data['timestamp']
                }
        except:
            pass
    
    return info


def clear_cache(pattern: str = None):
    """
    Clear cached data
    
    Args:
        pattern: If provided, only clear keys matching pattern
    """
    if pattern:
        for cache_file in CACHE_DIR.glob(f"*{pattern}*.json"):
            cache_file.unlink()
            print(f"🗑️  Cleared cache: {cache_file.stem}")
    else:
        for cache_file in CACHE_DIR.glob("*.json"):
            cache_file.unlink()
        print("🗑️  Cleared all cache")


def prime_cache(fetch_functions: dict):
    """
    Pre-warm cache with data (for app startup)
    
    Args:
        fetch_functions: Dict of {key: (function, ttl)} to pre-fetch
    """
    print("\n🔥 Warming cache...")
    
    for key, (func, ttl) in fetch_functions.items():
        # Check if already cached and fresh
        cached_data, cached_time = _read_cache(key)
        if cached_data and (time.time() - cached_time) < ttl:
            print(f"  ✓ {key} already cached")
            continue
        
        # Fetch and cache
        print(f"  ⟳ Fetching {key}...")
        try:
            result = func()
            _write_cache(key, result)
            print(f"    ✓ Cached {key}")
        except Exception as e:
            print(f"    ⚠️  Error: {e}")
    
    print("✓ Cache warmed!\n")

