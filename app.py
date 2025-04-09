import streamlit as st
import requests
from config import GOOGLE_API_KEY
from api_handlers import autocomplete_location
from disease_mappers import predict_disease, symptoms_list
from doctor_mappers import disease_specialization_map

# Streamlit App Title and Configuration
st.set_page_config(page_title="DocFinder", page_icon="🏥", layout="centered")
st.title("🏥 DocFinder")
st.markdown("Find the best doctors near you based on your symptoms.")

# Add a custom CSS for styling and centering elements
st.markdown("""
    <style>
        /* Left-align the page title and content */
        .css-18e3th9 {
            text-align: left;
        }

        /* Remove the deploy button and three dots in the top right corner */
        .css-1v3fvcr {
            display: none !important;
        }
        .css-1d391kg {
            display: none !important;
        }

        /* Left-align buttons and inputs */
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            padding: 12px 24px;
            font-size: 16px;
            border-radius: 8px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            border: none;
            cursor: pointer;
            display: inline-block;
            text-align: left;
            margin-left: 0;
        }

        .stButton>button:hover {
            background-color: #45a049;
        }

        .stTextInput input {
            border-radius: 12px;
            padding: 12px;
            font-size: 16px;
            width: 100%;  /* Full width for left-aligned input */
            margin-left: 0;
        }

        .stMultiselect div {
            border-radius: 12px;
            padding: 12px;
            width: 100%;  /* Full width for left-aligned multiselect */
            margin-left: 0;
        }

        /* Left-align the doctor cards */
        .doctor-card {
            border: 2px solid #1a1a1a;
            padding: 15px;
            border-radius: 12px;
            margin: 8px 0;
            background-color: #1f2430;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
            width: 100%;  /* Full width for left-aligned cards */
            margin-left: 0;
            text-align: left;
        }

        .doctor-card h4 {
            color: #64ffda;
            margin: 10px 0;
        }

        .doctor-card p {
            font-size: 16px;
            color: #ffffff;
        }

        .doctor-card a {
            color: #a855f7;
            text-decoration: none;
        }

        /* Left-align the disease prediction box */
        .predicted-disease-box {
            border-radius: 10px;
            padding: 15px;
            background-color: #2e3b47;
            color: #ffffff;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
            width: 100%;  /* Full width for left-aligned prediction box */
            margin-left: 0;
            text-align: left;
        }

        .predicted-disease-box h3 {
            color: #64ffda;
        }

        .predicted-disease-box p {
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)


# Initialize session state for symptom and location tracking
if 'symptoms' not in st.session_state:
    st.session_state.symptoms = []
if 'location' not in st.session_state:
    st.session_state.location = ""
if 'predicted_disease' not in st.session_state:
    st.session_state.predicted_disease = None
if 'nearby_doctors' not in st.session_state:
    st.session_state.nearby_doctors = []

# Dropdown for Symptom Selection
st.subheader("📝 Select Your Symptoms")
# Replace underscores with spaces for display purposes
formatted_symptoms_list = [symptom.replace('_', ' ') for symptom in symptoms_list]
selected_symptoms = st.multiselect("Choose your symptoms", formatted_symptoms_list, key="symptoms", max_selections=5)

# Layout for Address Input with Autocomplete in columns
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("📍 Enter Your Address")
    location = st.text_input("Start typing your address:", key="location")

# Initialize variables
latitude, longitude = None, None
selected_location = None
max_distance = 5

# Clear results when symptoms or location are changed (reset state)
if st.session_state.symptoms != selected_symptoms:
    st.session_state.predicted_disease = None
    st.session_state.nearby_doctors = []

if st.session_state.location != location:
    st.session_state.predicted_disease = None
    st.session_state.nearby_doctors = []

# Autocomplete Location
if location:
    locations = autocomplete_location(location + ", India")
    if locations:
        selected_location = st.selectbox("🔍 Select Location", locations)
        st.success(f"**Selected Location:** {selected_location}")
    else:
        st.error("❌ No suggestions found. Please check the address.")

# Function to get latitude and longitude from the address
def get_lat_long_from_address(address):
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_API_KEY}"
    response = requests.get(geocode_url)
    result = response.json()
    if result['status'] == 'OK':
        latitude = result['results'][0]['geometry']['location']['lat']
        longitude = result['results'][0]['geometry']['location']['lng']
        return latitude, longitude
    else:
        st.error("Unable to fetch latitude and longitude from the address.")
        return None, None

# Function to search for doctors near the given latitude and longitude using Google Places API
def get_nearby_doctors_google_api(latitude, longitude, max_distance):
    if latitude is None or longitude is None:
        st.error("Invalid location data")
        return []

    google_places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius={max_distance * 1000}&type=doctor&key={GOOGLE_API_KEY}"
    response = requests.get(google_places_url)
    results = response.json().get('results', [])

    doctors = []
    for place in results:
        name = place.get('name')
        address = place.get('vicinity')
        place_id = place.get('place_id')
        rating = place.get('rating', 'N/A')
        doctors.append({
            'name': name,
            'location': address,
            'place_id': place_id,
            'rating': rating
        })
    
    # Sort doctors by rating in descending order (highest rating first)
    doctors = sorted(doctors, key=lambda x: x['rating'] if x['rating'] != 'N/A' else 0, reverse=True)
    
    return doctors

# Function to create a styled card for each doctor
def display_doctor_card(name, location, place_id, source, rating=None):
    google_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
    st.markdown(f"""
        <div class="doctor-card">
            <h4> {name} 🩺</h4>
            <p><b>Address:</b> {location}</p>
            <p><b>Rating:</b> {rating if rating != 'N/A' else 'N/A'}</p>
            <p><b>🌐 Source:</b> {source}</p>
            <a href="{google_url}" target="_blank"><b>🔗 View Profile on Google</b></a>
        </div>
    """, unsafe_allow_html=True)

# Button to Predict Disease and Find Doctors
if st.button("🚑 Predict Disease and Find Doctors"):
    if not selected_symptoms:
        st.warning("⚠️ Please select at least one symptom.")
    elif not selected_location:
        st.warning("⚠️ Please enter a valid address and select from suggestions.")
    else:
        predicted_disease = predict_disease(selected_symptoms)
        # Get the specializations for the predicted disease
        specializations = disease_specialization_map.get(predicted_disease, ["General Practitioner"])

        # Remove "General Practitioner" if it's the only one
        if len(specializations) == 1 and "General Practitioner" in specializations:
            specializations = []

        # Show disease prediction in a nice box
        st.markdown(f"""
            <div class="predicted-disease-box">
                <h3>Predicted Disease: {predicted_disease}</h3>
                <p><strong>Need to refer to:</strong> {', '.join(specializations) if specializations else 'General Doctor'}</p>
            </div>
        """, unsafe_allow_html=True)

        # Fetch the latitude and longitude of the selected location
        latitude, longitude = get_lat_long_from_address(selected_location)

        # Fetch nearby doctors using Google Places API
        nearby_doctors = get_nearby_doctors_google_api(latitude, longitude, max_distance)

        # Store results in session_state
        st.session_state.predicted_disease = predicted_disease
        st.session_state.nearby_doctors = nearby_doctors

        if nearby_doctors:
            st.subheader("🏥 Nearby Doctors (Sorted by Rating):")
            nearby_doctors_sorted = sorted(nearby_doctors, key=lambda x: x['rating'] if x['rating'] != 'N/A' else 0, reverse=True)
            for doctor in nearby_doctors[:10]:
                display_doctor_card(doctor['name'], doctor['location'], doctor['place_id'], "Google Places", doctor.get('rating'))
        else:
            st.warning("⚠️ No nearby doctors found.")
