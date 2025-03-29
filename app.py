import streamlit as st
from disease_mappers import predict_disease, symptoms_list

st.title("Doctor Recommender System")

# Dropdown or checkbox for symptoms
st.subheader("Select Your Symptoms")

selected_symptoms = st.multiselect("Choose your symptoms", symptoms_list)

if st.button("Predict Disease"):
    if not selected_symptoms:
        st.warning("Please select at least one symptom.")
    else:
        predicted_disease = predict_disease(selected_symptoms)
        st.success(f"Predicted Disease: {predicted_disease}")
