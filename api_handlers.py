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

def get_nearby_doctors(latitude, longitude, disease):
    # Google Places API URL for finding doctors nearby
    places_url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
        f"location={latitude},{longitude}&radius=5000&keyword={disease}+doctor&key=YOUR_GOOGLE_API_KEY"
    )
    
    response = requests.get(places_url)
    data = response.json()
    
    doctors = []
    if response.status_code == 200 and data.get("status") == "OK":
        for result in data.get("results", []):
            doctors.append({
                "name": result.get("name"),
                "address": result.get("vicinity"),
                "rating": result.get("rating", "N/A"),
                "specialization": disease  # Assuming the disease name as specialization
            })
    return doctors
