import requests
import streamlit as st
from disease_mappers import predict_disease, symptoms_list
from api_handlers import autocomplete_location, get_nearby_doctors



# Streamlit UI Setup
st.title("Doctor Recommender System")

# Symptom Selection
st.subheader("Select Your Symptoms")
selected_symptoms = st.multiselect("Choose your symptoms", symptoms_list)

# Location Selection
st.subheader("Select Your Location")

# State, City, Locality Inputs
state = st.text_input("Enter State:")
city = None
locality = None

if state:
    cities = autocomplete_location(state)
    city = st.selectbox("Select City", cities) if cities else None

if city:
    locality_query = f"{city}, {state}"
    localities = autocomplete_location(locality_query)
    locality = st.selectbox("Select Locality", localities) if localities else None

# Disease Prediction and Doctor Recommendation
if st.button("Predict Disease and Find Doctors"):
    if not selected_symptoms:
        st.warning("Please select at least one symptom.")
    elif not (state and city and locality):
        st.warning("Please provide your full location.")
    else:
        # Predict disease based on selected symptoms using disease_mappers.py
        predicted_disease = predict_disease(selected_symptoms)
        st.success(f"Predicted Disease: {predicted_disease}")

        # Use the selected location to get coordinates via Geocoding API
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={locality},{city},{state}&key=YOUR_GOOGLE_API_KEY"
        geocode_response = requests.get(geocode_url)
        geocode_data = geocode_response.json()

        if geocode_response.status_code == 200 and geocode_data.get("status") == "OK":
            location = geocode_data["results"][0]["geometry"]["location"]
            latitude, longitude = location["lat"], location["lng"]

            # Fetch nearby doctors using these coordinates
            doctors = get_nearby_doctors(latitude, longitude)
            if doctors:
                st.subheader("Top 10 Nearby Doctors:")
                for doctor in doctors:
                    st.write(f"**{doctor['name']}** - {doctor['address']} (Rating: {doctor['rating']})")
            else:
                st.warning("No doctors found nearby.")
        else:
            st.error("Unable to fetch coordinates for the given location.")
