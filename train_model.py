import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE

# Load your dataset
X_train = pd.read_csv('path_to_X_train.csv')
y_train = pd.read_csv('path_to_y_train.csv')

# Balance the data using SMOTE
smote = SMOTE(random_state=42)
X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

print(f"Original dataset shape: {X_train.shape}, {y_train.shape}")
print(f"Resampled dataset shape: {X_train_res.shape}, {y_train_res.shape}")

# Define models
models = {
    "Random Forest": RandomForestClassifier(random_state=42),
    "SVM": SVC(),
    "KNN": KNeighborsClassifier(),
    "Logistic Regression": LogisticRegression()
}

# Stratified K-Fold Cross-Validation
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

best_score = 0
best_model = None
best_name = ""

for name, model in models.items():
    print(f"Training {name}...")
    
    # Hyperparameter tuning for Random Forest
    if name == "Random Forest":
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5],
            'min_samples_leaf': [1, 2]
        }
        grid_search = GridSearchCV(model, param_grid, cv=skf, n_jobs=-1)
        grid_search.fit(X_train_res, y_train_res)
        model = grid_search.best_estimator_
        print(f"Best parameters for {name}: {grid_search.best_params_}")

    # Cross-validation and scoring
    scores = cross_val_score(model, X_train_res, y_train_res, cv=skf, scoring='accuracy')
    accuracy = np.mean(scores)
    print(f"{name} Accuracy: {accuracy:.4f}")
    
    if accuracy > best_score:
        best_score = accuracy
        best_model = model
        best_name = name

# Final training on the entire balanced dataset
best_model.fit(X_train_res, y_train_res)

# Evaluation on the training data
y_pred = best_model.predict(X_train_res)
print(f"\nBest Model: {best_name} with Accuracy: {accuracy_score(y_train_res, y_pred):.4f}")
print("\nClassification Report:")
print(classification_report(y_train_res, y_pred))
print("\nConfusion Matrix:")
print(confusion_matrix(y_train_res, y_pred))

# Ensure the 'models' directory exists before saving
if not os.path.exists("models"):
    os.makedirs("models")

# Save the best model
joblib.dump(best_model, "models/disease_predictor.pkl")
print(f"\nModel saved as 'models/disease_predictor.pkl'")
