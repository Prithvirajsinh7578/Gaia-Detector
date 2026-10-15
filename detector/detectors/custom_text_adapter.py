"""
custom_text_adapter.py - Adapter for the Preserved Custom-Trained Text Classifier.
Integrates the 18-feature Random Forest model without modifying underlying logic or saved weights.
"""

import time
from typing import Dict, Any, Optional
from .base_detector import BaseTextDetector, DetectorResult
from detector import Detector
from utils.constants import MODEL_PATH, FEATURE_NAMES


class CustomTextAdapter(BaseTextDetector):
    """
    Adapter wrapping the existing custom 18-feature Random Forest classifier.
    Preserves exact feature ordering, preprocessing, model weights, and thresholds.
    """

    def __init__(self, model_path: str = MODEL_PATH):
        self.detector_id = "custom_rf"
        self.name = "Custom 18-Feature Random Forest Ensemble"
        self.category = "custom_model"
        self.model_path = model_path
        self._underlying_detector = Detector(model_path=model_path)

    def predict(self, text: str) -> DetectorResult:
        start_time = time.time()

        if not text or not text.strip():
            return DetectorResult(
                detector_id=self.detector_id,
                name=self.name,
                category=self.category,
                status="skipped",
                ai_probability=0.0,
                human_probability=100.0,
                raw_score=0.0,
                verdict="Invalid / Empty Input",
                confidence="None",
                latency_ms=0.0,
                analyzed_chars=0,
                error_message="Input text was empty."
            )

        try:
            raw_res = self._underlying_detector.predict(text)
            latency_ms = (time.time() - start_time) * 1000.0

            prob_ai = float(raw_res.get("probability", 50.0))
            prob_human = max(0.0, 100.0 - prob_ai)

            return DetectorResult(
                detector_id=self.detector_id,
                name=self.name,
                category=self.category,
                status="success",
                ai_probability=prob_ai,
                human_probability=prob_human,
                raw_score=prob_ai / 100.0,
                is_calibrated=True,
                verdict=raw_res.get("verdict", "Inconclusive / Uncertain"),
                confidence=raw_res.get("confidence", "Medium"),
                latency_ms=latency_ms,
                analyzed_chars=len(text),
                indicators=raw_res.get("indicators", []),
                metadata={
                    "features": raw_res.get("features", {}),
                    "detailed_features": raw_res.get("detailed_features", {}),
                    "feature_count": len(FEATURE_NAMES)
                }
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000.0
            return DetectorResult(
                detector_id=self.detector_id,
                name=self.name,
                category=self.category,
                status="failed",
                ai_probability=50.0,
                human_probability=50.0,
                raw_score=0.5,
                verdict="Inconclusive / Uncertain",
                confidence="None",
                latency_ms=latency_ms,
                analyzed_chars=len(text),
                error_message=f"Custom classifier inference error: {str(e)}"
            )
