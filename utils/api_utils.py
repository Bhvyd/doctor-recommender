import json
import os

# Function to load cached data from a JSON file
def load_cache(cache_file):
    """Load cache from a JSON file"""
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    return {}

# Function to save data to a cache file in JSON format
def save_cache(cache_file, data):
    """Save data to a JSON cache file"""
    with open(cache_file, 'w') as f:
        json.dump(data, f, indent=4)

# Optional: Function to clear cache (if needed for any reason)
def clear_cache(cache_file):
    """Clear the cache file"""
    if os.path.exists(cache_file):
        os.remove(cache_file)

