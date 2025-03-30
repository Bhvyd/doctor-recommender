import streamlit as st
import requests
from config import GOOGLE_API_KEY
from api_handlers import autocomplete_location
from disease_mappers import predict_disease, symptoms_list
from doctor_mappers import disease_specialization_map

st.title("Doctor Recommender System")

# Dropdown or checkbox for symptoms
st.subheader("Select Your Symptoms")
selected_symptoms = st.multiselect("Choose your symptoms", symptoms_list)

# Address input for autocompletion
address = st.text_input("Enter Address:")

# Initialize variables
latitude, longitude = None, None
selected_location = None

# Autocomplete location based on entered address
if address:
    locations = autocomplete_location(address + ", India")
    if locations:
        selected_location = st.selectbox("Select Location", locations)
        st.write(f"Selected: {selected_location}")
    else:
        st.error("No suggestions found. Please check the address.")

# Button to predict disease and find doctors
if st.button("Predict Disease and Find Doctors"):
    if not selected_symptoms:
        st.warning("Please select at least one symptom.")
    elif not selected_location:
        st.warning("Please enter a valid address and select from suggestions.")
    else:
        # Predict the disease based on selected symptoms
        predicted_disease = predict_disease(selected_symptoms)
        st.success(f"Predicted Disease: {predicted_disease}")

        # Map the predicted disease to the most relevant medical specialization
        specialization = disease_specialization_map.get(predicted_disease, "General Practitioner")
        st.write(f"Looking for doctors with specialization: {specialization}")

        # Use the selected location directly for geocoding
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={selected_location}&key={GOOGLE_API_KEY}"
        try:
            geocode_response = requests.get(geocode_url)
            geocode_data = geocode_response.json()

            if geocode_response.status_code == 200 and geocode_data.get("status") == "OK":
                location = geocode_data["results"][0]["geometry"]["location"]
                latitude, longitude = location["lat"], location["lng"]
                st.success(f"Location Coordinates: Latitude: {latitude}, Longitude: {longitude}")
            else:
                st.error("Geocoding failed.")
                st.error(f"Status: {geocode_data.get('status')}")
                st.error(f"Error Message: {geocode_data.get('error_message', 'No error message available')}")

        except Exception as e:
            st.error(f"Error while fetching coordinates: {e}")

# Check if coordinates were successfully fetched
if latitude is not None and longitude is not None:
    try:
        def get_nearby_doctors(lat, lng, keyword):
            url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&rankby=distance&keyword={keyword}&key={GOOGLE_API_KEY}"
            response = requests.get(url)
            return response.json().get("results", [])

        # Primary search for specialized doctors
        doctors = get_nearby_doctors(latitude, longitude, specialization)
        st.write("Doctor API Primary Response:", doctors)  # Debug: print the returned doctor list

        # Fallback to general search if no specialized doctors found
        if not doctors:
            st.warning(f"No specialized {specialization} doctors found nearby. Trying a broader search...")
            broader_keywords = ["doctor", "clinic", "hospital", "healthcare"]
            for keyword in broader_keywords:
                doctors = get_nearby_doctors(latitude, longitude, keyword)
                st.write(f"Doctor API Response for '{keyword}':", doctors)
                if doctors:
                    break

        # Final check and display
        if doctors:
            st.subheader(f"Nearby Healthcare Facilities (Ordered by Distance):")
            for doctor in doctors[:10]:
                name = doctor.get("name", "Unknown")
                address = doctor.get("vicinity", "Address not available")
                rating = doctor.get("rating", "N/A")
                st.write(f"**{name}** - {address} (Rating: {rating})")
        else:
            st.warning("No doctors or healthcare facilities found nearby, even after fallback attempts.")
    except Exception as e:
        st.error(f"Error while fetching nearby doctors: {e}")
else:
    st.error("Unable to fetch coordinates for the given location.")