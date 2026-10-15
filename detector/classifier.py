import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)
from utils.constants import FEATURE_NAMES, MODEL_PATH, DATASET_PATH

def load_dataset():
    df = pd.read_csv(DATASET_PATH)
    X = df[FEATURE_NAMES]
    y = df["label"]
    return X, y

def train_classifier():
    print("Loading dataset...")
    X, y = load_dataset()
    print(f"Total samples: {len(X)}")
    print(f"Number of features: {len(FEATURE_NAMES)}")
    print("\nClass distribution:")
    print(y.value_counts())

    # --------------------------------
    # Train / Test Split
    # --------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )
    print("\nDataset split:")
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")

    # --------------------------------
    # Create Model
    # --------------------------------
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        n_jobs=4
    )

    # --------------------------------
    # Train
    # --------------------------------
    print("\nTraining Random Forest...")
    model.fit(X_train, y_train)
    print("Training completed.")

    # --------------------------------
    # Evaluate
    # --------------------------------
    y_pred = model.predict(X_test)
    
    print("\n========== MODEL RESULTS ==========")
    print(f"Accuracy : {accuracy_score(y_test, y_pred):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred):.4f}")
    print(f"Recall   : {recall_score(y_test, y_pred):.4f}")
    print(f"F1 Score : {f1_score(y_test, y_pred):.4f}")
    
    print("\n========== CLASSIFICATION REPORT ==========")
    print(classification_report(y_test, y_pred))
    
    print("========== CONFUSION MATRIX ==========")
    print(confusion_matrix(y_test, y_pred))
    
    # --------------------------------
    # Feature Importance
    # --------------------------------
    print("\n========== FEATURE IMPORTANCE ==========")
    importances = model.feature_importances_
    
    feature_importances = list(zip(FEATURE_NAMES, importances))
    feature_importances.sort(key=lambda x: x[1], reverse=True)
    
    for name, importance in feature_importances:
        print(f"{name.ljust(25)} {importance:.4f}")

    # --------------------------------
    # Step 17: Save Model
    # --------------------------------
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    file_size_kb = os.path.getsize(MODEL_PATH) / 1024
    print("\n========== MODEL SAVED ==========")
    print(f"Path: {MODEL_PATH}")
    print(f"Size: {file_size_kb:.2f} KB")

    return model

if __name__ == "__main__":
    train_classifier()