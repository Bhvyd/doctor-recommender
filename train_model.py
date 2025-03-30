import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Step 1: Load the data
def load_data(train_path, test_path):
    train_data = pd.read_csv(train_path)
    test_data = pd.read_csv(test_path)
    
    # Remove unnamed columns during data loading
    train_data = train_data.loc[:, ~train_data.columns.str.contains('^Unnamed')]
    test_data = test_data.loc[:, ~test_data.columns.str.contains('^Unnamed')]
    
    return train_data, test_data

# Step 3: Train the Model
def train_model(X_train, y_train):
    # Define individual classifiers
    dt_model = DecisionTreeClassifier(random_state=42)
    nb_model = GaussianNB()
    rf_model = RandomForestClassifier(random_state=42)
    knn_model = KNeighborsClassifier()

    # Soft Voting Classifier
    ensemble_model = VotingClassifier(
        estimators=[
            ('decision_tree', dt_model),
            ('naive_bayes', nb_model),
            ('random_forest', rf_model),
            ('knn', knn_model)
        ],
        voting='soft'
    )
    
    # Train the ensemble model
    ensemble_model.fit(X_train, y_train)
    return ensemble_model

# Step 4: Evaluate the Model
def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc * 100:.2f}%")
    print("\nClassification Report:\n", classification_report(y_test, y_pred))
    print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

# Main Function
def main(train_csv, test_csv):
    # Load data
    train_data, test_data = load_data(train_csv, test_csv)
    
    # Separate features and labels
    X_train = train_data.drop('prognosis', axis=1)
    y_train = train_data['prognosis']
    X_test = test_data.drop('prognosis', axis=1)
    y_test = test_data['prognosis']
    
    # Standardize numerical features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    # Train the model
    model = train_model(X_train, y_train)
    
    # Evaluate the model
    evaluate_model(model, X_test, y_test)
    
    # Ensure the 'models' directory exists before saving
    if not os.path.exists("models"):
        os.makedirs("models")
    
    # Save the model
    joblib.dump(model, "models/disease_predictor.pkl")
    print(f"\nModel saved as 'models/disease_predictor.pkl'")

# Example usage
if __name__ == "__main__":
    train_csv_path = "/content/training_data.csv"  # Provide your training CSV file path
    test_csv_path = "/content/test_data.csv"    # Provide your testing CSV file path
    main(train_csv_path, test_csv_path)
