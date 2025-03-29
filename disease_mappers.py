import joblib
import numpy as np

# Load the model
model = joblib.load("models/disease_predictor.pkl")

def predict_disease(symptoms):
    # Load the list of symptoms
    symptoms_list = joblib.load("models/symptoms_list.pkl")

    # Create a binary symptoms vector
    symptoms_vector = np.zeros(len(symptoms_list))
    for symptom in symptoms:
        if symptom in symptoms_list:
            symptoms_vector[symptoms_list.index(symptom)] = 1

    # Predict disease
    disease = model.predict([symptoms_vector])[0]
    return disease

# Load the list of symptoms
symptoms_list = joblib.load("models/symptoms_list.pkl")
