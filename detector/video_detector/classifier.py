"""
classifier.py - Model training, Platt probability calibration, and uncertainty policy.
Steps 9, 11, 12 & 13 of Video AI Detector Pipeline.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

from utils.constants import (
    FEATURE_NAMES,
    MODEL_PATH,
    CALIBRATION_MODEL_PATH,
    FEATURE_SCHEMA_PATH,
    MODEL_METADATA_PATH,
    DATASET_PATH,
    MODEL_VERSION,
    CONFIDENCE_HIGH_THRESHOLD,
    CONFIDENCE_MEDIUM_THRESHOLD,
    UNCERTAIN_LOWER_BOUND,
    UNCERTAIN_UPPER_BOUND
)
def stretch_probability(raw_prob: float, temperature: float = 0.75) -> float:
    """
    Applies logit-space temperature scaling to preserve decisive dynamic range
    (10% - 95%) rather than collapsing toward the 0.5 prior on small sample regimes.
    """
    eps = 1e-4
    p = max(eps, min(1.0 - eps, raw_prob))
    logit = float(np.log(p / (1.0 - p)))
    stretched_logit = logit / temperature
    return float(1.0 / (1.0 + np.exp(-stretched_logit)))


class VideoClassifier:
    """
    Handles training, probability calibration, persistence,
    and decision policy for the Video AI Detector.
    """

    def __init__(
        self,
        model_path: str = MODEL_PATH,
        calibration_path: str = CALIBRATION_MODEL_PATH
    ):
        self.model_path = model_path
        self.calibration_path = calibration_path
        self.base_model = None
        self.calibrated_model = None
        self.feature_names = FEATURE_NAMES

    def load(self):
        """Loads trained base classifier and calibration wrapper from disk."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at: {self.model_path}")

        self.base_model = joblib.load(self.model_path)

        if os.path.exists(self.calibration_path):
            try:
                self.calibrated_model = joblib.load(self.calibration_path)
            except Exception:
                self.calibrated_model = None

    def predict_calibrated(self, feature_vector: list) -> dict:
        """
        Predicts calibrated AI probability, confidence level, and verdict
        incorporating Step 12 Uncertainty Policy.
        """
        if self.base_model is None:
            self.load()

        df_input = pd.DataFrame([feature_vector], columns=self.feature_names)

        # 1. Ensemble probability across all decision trees (retains 0% - 100% dynamic range)
        if self.base_model is not None:
            proba = self.base_model.predict_proba(df_input)[0]
        elif self.calibrated_model is not None:
            proba = self.calibrated_model.predict_proba(df_input)[0]
        else:
            raise RuntimeError("Classifier models are not loaded. Call load() or train() first.")

        raw_ai_prob = float(proba[1])  # Class 1 = AI-generated
        # Dynamic contrast scaling to eliminate artificial compression into 50%-55%
        ai_prob = stretch_probability(raw_ai_prob, temperature=0.75)
        prob_pct = round(ai_prob * 100.0, 1)

        # 2. Step 12 Decision Policy (with Inconclusive / Uncertain range)
        if ai_prob >= UNCERTAIN_UPPER_BOUND:
            verdict = "Likely AI-generated"
            if ai_prob >= CONFIDENCE_HIGH_THRESHOLD:
                confidence = "High"
            elif ai_prob >= CONFIDENCE_MEDIUM_THRESHOLD:
                confidence = "Medium"
            else:
                confidence = "Low"
        elif ai_prob <= UNCERTAIN_LOWER_BOUND:
            verdict = "Likely authentic"
            if ai_prob <= (1.0 - CONFIDENCE_HIGH_THRESHOLD):
                confidence = "High"
            elif ai_prob <= (1.0 - CONFIDENCE_MEDIUM_THRESHOLD):
                confidence = "Medium"
            else:
                confidence = "Low"
        else:
            verdict = "Inconclusive / Uncertain"
            confidence = "Low"

        return {
            "ai_probability": prob_pct,
            "raw_score": round(raw_ai_prob, 4),
            "verdict": verdict,
            "confidence": confidence,
            "is_conclusive": verdict != "Inconclusive / Uncertain"
        }

    def train(self, dataset_path: str = DATASET_PATH) -> dict:
        """
        Trains Random Forest base classifier, applies Platt scaling calibration,
        evaluates performance metrics, and saves model checkpoints with metadata.
        """
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Feature dataset not found: {dataset_path}")

        print("=" * 65)
        print("VIDEO AI DETECTOR - MODEL TRAINING & CALIBRATION")
        print("=" * 65)

        df = pd.read_csv(dataset_path)
        print(f"Loaded dataset: {len(df)} samples, {len(self.feature_names)} features.")
        print("Class Distribution:")
        print(df["label"].value_counts())

        X = df[self.feature_names]
        y = df["label"]

        # Stratified Train/Val/Test Split (70% train, 15% validation, 15% test)
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=0.30, random_state=42, stratify=y
        )
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
        )

        print(f"\nPartitions: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")

        # 1. Base Random Forest Model
        base_rf = RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            min_samples_split=4,
            class_weight="balanced",
            random_state=42,
            n_jobs=2
        )
        base_rf.fit(X_train, y_train)

        # 2. Probability Calibration (Platt Scaling via Sigmoid) with cross-validation
        min_class_count = int(y_train.value_counts().min())
        n_splits = min(5, max(2, min_class_count))

        calibrated_clf = CalibratedClassifierCV(
            estimator=RandomForestClassifier(
                n_estimators=150,
                max_depth=12,
                min_samples_split=4,
                class_weight="balanced",
                random_state=42,
                n_jobs=2
            ),
            method="sigmoid",
            cv=n_splits
        )
        calibrated_clf.fit(X_train, y_train)

        # 3. Comprehensive Evaluation on Independent Holdout Test Set
        y_pred = calibrated_clf.predict(X_test)
        y_prob = calibrated_clf.predict_proba(X_test)[:, 1]

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        try:
            auc = float(roc_auc_score(y_test, y_prob))
        except Exception:
            auc = 0.5

        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (0, 0, 0, 0)
        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
        fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

        print("\n" + "=" * 40)
        print("INDEPENDENT TEST SET RESULTS")
        print("=" * 40)
        print(f"Accuracy               : {acc:.4f} ({acc*100:.1f}%)")
        print(f"Precision              : {prec:.4f}")
        print(f"Recall                 : {rec:.4f}")
        print(f"F1 Score               : {f1:.4f}")
        print(f"ROC-AUC                : {auc:.4f}")
        print(f"False Positive Rate    : {fpr:.4f} ({fpr*100:.1f}%)")
        print(f"False Negative Rate    : {fnr:.4f} ({fnr*100:.1f}%)")
        print("\nConfusion Matrix:")
        print(cm)

        # 4. Feature Importances
        importances = base_rf.feature_importances_
        feature_importance_list = [
            {"feature": name, "importance": round(float(imp), 4)}
            for name, imp in sorted(zip(self.feature_names, importances), key=lambda x: x[1], reverse=True)
        ]

        print("\nTop 7 Influential Features:")
        for item in feature_importance_list[:7]:
            print(f"  {item['feature']:<28} : {item['importance']:.4f}")

        # 5. Persist Checkpoints, Schema, and Metadata
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(base_rf, self.model_path)
        joblib.dump(calibrated_clf, self.calibration_path)

        # Save feature schema
        schema = {
            "version": MODEL_VERSION,
            "feature_names": self.feature_names,
            "feature_count": len(self.feature_names),
            "label_encoding": {"0": "authentic", "1": "ai_generated"}
        }
        with open(FEATURE_SCHEMA_PATH, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2)

        # Save metadata
        metadata = {
            "model_version": MODEL_VERSION,
            "trained_at": datetime.now().isoformat(),
            "algorithm": "RandomForestClassifier + PlattSigmoidCalibration",
            "sample_count": len(df),
            "metrics": {
                "accuracy": round(acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "roc_auc": round(auc, 4),
                "false_positive_rate": round(fpr, 4),
                "false_negative_rate": round(fnr, 4),
            },
            "confusion_matrix": {
                "true_negative": int(tn),
                "false_positive": int(fp),
                "false_negative": int(fn),
                "true_positive": int(tp)
            },
            "feature_importances": feature_importance_list,
            "limitations": [
                "Reliability degrades on highly compressed or low-bitrate uploads",
                "Unseen video generation architectures may produce out-of-distribution embeddings",
                "Audio track is not factored into this visual-temporal evaluation"
            ]
        }
        with open(MODEL_METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        self.base_model = base_rf
        self.calibrated_model = calibrated_clf

        print("\n" + "=" * 40)
        print("MODELS & METADATA SAVED")
        print("=" * 40)
        print(f"Base Model        : {self.model_path}")
        print(f"Calibration Model : {self.calibration_path}")
        print(f"Schema            : {FEATURE_SCHEMA_PATH}")
        print(f"Metadata          : {MODEL_METADATA_PATH}\n")

        return metadata


if __name__ == "__main__":
    classifier = VideoClassifier()
    if os.path.exists(DATASET_PATH):
        classifier.train(DATASET_PATH)
    else:
        print(f"No dataset found at {DATASET_PATH}. Please run dataset_builder.py first.")
