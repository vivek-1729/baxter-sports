#!/usr/bin/env python3
"""Remove all API-Sports.io references from app.py"""

with open('app.py', 'r') as f:
    lines = f.readlines()

# Remove imports
lines = [l for l in lines if 'sports_backend' not in l and 'smart_cache' not in l and 'CacheDuration' not in l]

output = []
skip_until = None

for i, line in enumerate(lines):
    # Skip if we're in a block to remove
    if skip_until and i < skip_until:
        continue
    skip_until = None
    
    # Replace get_data_with_cache with direct dummy calls
    if 'get_data_with_cache' in line:
        indent = len(line) - len(line.lstrip())
        if 'live_events[sport_key]' in lines[i-1] if i > 0 else False:
            output.append(' ' * indent + "live_events[sport_key] = get_dummy_live_events().get(sport_key, [])\n")
        elif 'upcoming_fixtures[sport_key]' in lines[i-1] if i > 0 else False:
            output.append(' ' * indent + "upcoming_fixtures[sport_key] = get_dummy_fixtures().get(sport_key, [])\n")
        elif 'recent_results[sport_key]' in lines[i-1] if i > 0 else False:
            output.append(' ' * indent + "recent_results[sport_key] = get_dummy_results().get(sport_key, [])\n")
        elif "'standings']" in line:
            output.append(' ' * indent + "hero_data['standings'] = get_dummy_standings(sport_key)\n")
        # Skip the get_data_with_cache block
        depth = 0
        for j in range(i, len(lines)):
            if '(' in lines[j]:
                depth += lines[j].count('(') - lines[j].count(')')
            if depth == 0:
                skip_until = j + 1
                break
        continue
    
    # Remove cache_fixture_smart calls
    if 'cache_fixture_smart' in line:
        continue
    
    # Remove cache_manager calls
    if 'cache_manager.' in line:
        continue
    
    # Remove USE_API checks
    if 'if USE_API' in line or 'if not USE_API' in line:
        # Skip entire if/else block
        for j in range(i+1, len(lines)):
            if lines[j].strip() and not lines[j].strip().startswith(('#', 'try', 'except', 'else')):
                if lines[j][0] not in (' ', '\t'):
                    skip_until = j
                    break
        output.append(lines[i].replace('if USE_API:', 'if False:  # API disabled').replace('if not USE_API:', 'if True:  # Using dummy data'))
        continue
    
    # Remove API/cache initialization
    if any(x in line for x in ['api_client =', 'cache_manager =', 'USE_API =', 'api_client.', 'from sports_backend']):
        continue
    
    output.append(line)

with open('app.py', 'w') as f:
    f.writelines(output)

print("✓ Cleaned app.py")

