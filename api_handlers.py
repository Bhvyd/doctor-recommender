import requests
from utils.api_utils import load_cache, save_cache
from config import GOOGLE_API_KEY

CACHE_FILE = "location_cache.json"

def autocomplete_location(query):
    """Autocomplete location using Google Places API"""
    cache = load_cache(CACHE_FILE)
    if query in cache:
        return cache[query]

    url = f"https://maps.googleapis.com/maps/api/place/autocomplete/json?input={query}&types=(regions)&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and data.get("status") == "OK":
        predictions = [item["description"] for item in data["predictions"]]
        cache[query] = predictions
        save_cache(CACHE_FILE, cache)
        return predictions
    else:
        print("Error:", data.get("status", "Unknown error"))
        return []

def get_nearby_doctors(latitude, longitude):
    """Get top 10 doctors near the given coordinates"""
    url = (f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
           f"location={latitude},{longitude}&radius=5000&keyword=doctor&key={GOOGLE_API_KEY}")
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and data.get("status") == "OK":
        doctors = []
        for place in data.get("results", [])[:10]:
            doctors.append({
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "rating": place.get("rating", "N/A")
            })
        return doctors
    else:
        print("Error:", data.get("status", "Unknown error"))
        return []
