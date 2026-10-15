"""
hybrid_detector.py - Master Orchestrator for Hybrid AI Text Detection System.
Coordinates:
1. Preserved Custom 18-Feature Random Forest Classifier
2. Pretrained Hugging Face RoBERTa Sequence Classifier
3. External Commercial GPTZero API
4. Calibrated Multi-Source Ensemble Combiner
"""

import os
import time
from typing import Dict, Any, Optional, List
from pathlib import Path

try:
    from dotenv import load_dotenv
    _env_local = Path(__file__).resolve().parent / ".env"
    if _env_local.exists():
        load_dotenv(_env_local)
    else:
        load_dotenv()
except ImportError:
    pass

from detectors.base_detector import DetectorResult
from detectors.custom_text_adapter import CustomTextAdapter
from detectors.hf_text_detector import HFTextDetector
from detectors.gptzero_detector import GPTZeroTextDetector
from ensemble import HybridTextEnsemble, EnsembleResult


class HybridTextDetector:
    """
    End-to-End Hybrid AI Text Detection Pipeline.
    Integrates multiple independent evidence streams into a calibrated detection system.
    """

    def __init__(
        self,
        enable_custom: bool = True,
        enable_hf: bool = True,
        enable_gptzero: bool = True,
        gptzero_api_key: Optional[str] = None
    ):
        self.enable_custom = enable_custom
        self.enable_hf = enable_hf
        self.enable_gptzero = enable_gptzero

        # 1. Custom Model Adapter (18-feature Random Forest)
        if self.enable_custom:
            self.custom_adapter = CustomTextAdapter()
        else:
            self.custom_adapter = None

        # 2. Pretrained Hugging Face Model
        if self.enable_hf:
            self.hf_detector = HFTextDetector()
        else:
            self.hf_detector = None

        # 3. GPTZero Commercial API Client
        if self.enable_gptzero:
            self.gptzero_detector = GPTZeroTextDetector(api_key=gptzero_api_key)
        else:
            self.gptzero_detector = None

        # 4. Ensemble Combiner
        self.ensemble = HybridTextEnsemble()

    def configure_gptzero(self, api_key: str, enabled: bool = True):
        """Dynamically configure and enable GPTZero API credentials at runtime."""
        self.enable_gptzero = enabled
        if enabled:
            self.gptzero_detector = GPTZeroTextDetector(api_key=api_key.strip())
        else:
            self.gptzero_detector = None

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Executes hybrid multi-detector inference pipeline.

        Args:
            text: Input raw text string.

        Returns:
            Structured hybrid prediction dictionary conforming to existing and upgraded API contracts.
        """
        start_time = time.time()

        if not text or not text.strip():
            return {
                "probability": 0.0,
                "confidence": "None",
                "verdict": "Invalid / Empty Input",
                "features": {},
                "detailed_features": {},
                "indicators": ["Please provide text for analysis."],
                "hybrid_pipeline": True,
                "consensus": {
                    "agreement": "None",
                    "active_detectors": 0,
                    "total_detectors": 0,
                    "discrepancy": 0.0,
                    "inconclusive_reason": "Empty input"
                },
                "individual_detectors": {}
            }

        is_short_text = (len(text.split()) < 30) or (len(text) < 150)
        results: List[DetectorResult] = []

        # 1. Run Custom Classifier
        if self.enable_custom and self.custom_adapter:
            results.append(self.custom_adapter.predict(text))

        # 2. Run Pretrained Hugging Face Model
        if self.enable_hf and self.hf_detector:
            results.append(self.hf_detector.predict(text))

        # 3. Run GPTZero External API
        if self.enable_gptzero and self.gptzero_detector:
            results.append(self.gptzero_detector.predict(text))

        # 4. Combine via Calibrated Ensemble
        ensemble_res = self.ensemble.combine(results, is_short_text=is_short_text)
        total_latency_ms = (time.time() - start_time) * 1000.0

        # Extract preserved custom feature summaries for backward compatibility
        custom_metadata = ensemble_res.component_results.get("custom_rf", {}).get("metadata", {})
        summary_features = custom_metadata.get("features", {})
        detailed_features = custom_metadata.get("detailed_features", {})

        return {
            # Backward-compatible fields
            "probability": round(ensemble_res.ai_probability, 1),
            "confidence": ensemble_res.confidence,
            "verdict": ensemble_res.verdict,
            "features": summary_features,
            "detailed_features": detailed_features,
            "indicators": ensemble_res.summary_indicators,

            # Upgraded Hybrid Multi-Source Diagnostics
            "hybrid_pipeline": True,
            "text_length_chars": len(text),
            "text_word_count": len(text.split()),
            "is_short_text": is_short_text,
            "total_latency_ms": round(total_latency_ms, 1),
            "consensus": {
                "agreement": ensemble_res.consensus_status,
                "active_detectors": ensemble_res.active_detectors_count,
                "total_detectors": ensemble_res.total_detectors_count,
                "discrepancy": round(ensemble_res.discrepancy, 1),
                "inconclusive_reason": ensemble_res.inconclusive_reason
            },
            "individual_detectors": ensemble_res.component_results,
            "weights_used": ensemble_res.weights_used
        }
