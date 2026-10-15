"""
hybrid_detector.py - Master Orchestrator for the Hybrid AI Video Detection System.
Coordinates:
1. Custom Spatial-Temporal Classifier
2. Pretrained Hugging Face ResNet-50 T2V Model
3. Sightengine Commercial GenAI Detection API
4. Calibrated Hybrid Ensemble Engine
"""

import os
import time
from typing import Dict, Any, Optional, List

from detectors.base_detector import DetectorResult
from detectors.custom_detector_adapter import CustomDetectorAdapter
from detectors.hf_video_detector import HFVideoDetector
from detectors.sightengine_detector import SightengineVideoDetector
from ensemble import HybridEnsemble, EnsembleResult
from utils.constants import (
    MODEL_VERSION,
    UNCERTAIN_LOWER_BOUND,
    UNCERTAIN_UPPER_BOUND,
    CONFIDENCE_HIGH_THRESHOLD,
    CONFIDENCE_MEDIUM_THRESHOLD
)


class HybridVideoDetector:
    """
    End-to-End Hybrid AI Video Detection Pipeline.
    Integrates multiple independent evidence streams into a calibrated detection system.
    """

    def __init__(
        self,
        enable_custom: bool = True,
        enable_hf: bool = True,
        enable_sightengine: bool = True,
        sightengine_api_user: Optional[str] = None,
        sightengine_api_secret: Optional[str] = None
    ):
        self.enable_custom = enable_custom
        self.enable_hf = enable_hf
        self.enable_sightengine = enable_sightengine

        # 1. Custom Model Adapter
        if self.enable_custom:
            self.custom_adapter = CustomDetectorAdapter()
        else:
            self.custom_adapter = None

        # 2. Hugging Face Pretrained Model
        if self.enable_hf:
            self.hf_detector = HFVideoDetector()
        else:
            self.hf_detector = None

        # 3. Sightengine API Client
        if self.enable_sightengine:
            self.sightengine_detector = SightengineVideoDetector(
                api_user=sightengine_api_user,
                api_secret=sightengine_api_secret
            )
        else:
            self.sightengine_detector = None

        # 4. Ensemble Combiner
        self.ensemble = HybridEnsemble(
            uncertain_lower=UNCERTAIN_LOWER_BOUND,
            uncertain_upper=UNCERTAIN_UPPER_BOUND,
            confidence_high=CONFIDENCE_HIGH_THRESHOLD,
            confidence_med=CONFIDENCE_MEDIUM_THRESHOLD
        )

    def configure_sightengine(self, api_user: str, api_secret: str, enabled: bool = True):
        """Dynamically configure and enable Sightengine API credentials."""
        self.enable_sightengine = enabled
        if enabled:
            self.sightengine_detector = SightengineVideoDetector(
                api_user=api_user.strip(),
                api_secret=api_secret.strip()
            )
        else:
            self.sightengine_detector = None

    def predict(self, video_path: str) -> Dict[str, Any]:
        """
        Executes hybrid multi-detector inference pipeline.

        Args:
            video_path: Local filesystem path to video file.

        Returns:
            Structured hybrid prediction dictionary conforming to API contracts.
        """
        start_time = time.time()
        detector_results: List[DetectorResult] = []

        # 1. Execute Custom Classifier
        custom_pred_raw = None
        if self.enable_custom and self.custom_adapter:
            try:
                res_custom = self.custom_adapter.predict(video_path)
                detector_results.append(res_custom)
                custom_pred_raw = self.custom_adapter.detector
            except Exception as e:
                detector_results.append(
                    DetectorResult(
                        detector_id="custom_rf",
                        name="Custom Spatial-Temporal Ensemble",
                        category="spatial_temporal_rf",
                        status="failed",
                        ai_probability=50.0,
                        raw_score=0.5,
                        verdict="Inconclusive",
                        confidence="None",
                        latency_ms=0.0,
                        frames_analyzed=0,
                        error=str(e)
                    )
                )

        # 2. Execute Hugging Face Pretrained Model
        if self.enable_hf and self.hf_detector:
            try:
                res_hf = self.hf_detector.predict(video_path)
                detector_results.append(res_hf)
            except Exception as e:
                detector_results.append(
                    DetectorResult(
                        detector_id="hf_resnet50_t2v",
                        name="HF Pretrained ResNet50 (Sora/Veo2 T2V)",
                        category="deep_visual_t2v",
                        status="failed",
                        ai_probability=50.0,
                        raw_score=0.5,
                        verdict="Inconclusive",
                        confidence="None",
                        latency_ms=0.0,
                        frames_analyzed=0,
                        error=str(e)
                    )
                )

        # 3. Execute Sightengine API (if configured)
        if self.enable_sightengine and self.sightengine_detector:
            try:
                res_se = self.sightengine_detector.predict(video_path)
                detector_results.append(res_se)
            except Exception as e:
                detector_results.append(
                    DetectorResult(
                        detector_id="sightengine_api",
                        name="Sightengine AI Video Detection API",
                        category="commercial_api",
                        status="failed",
                        ai_probability=50.0,
                        raw_score=0.5,
                        verdict="Inconclusive",
                        confidence="None",
                        latency_ms=0.0,
                        frames_analyzed=0,
                        error=str(e)
                    )
                )

        # 4. Multi-Evidence Ensemble Fusion
        ensemble_res: EnsembleResult = self.ensemble.combine(detector_results)
        total_duration_ms = round((time.time() - start_time) * 1000.0, 2)

        # Extract underlying metadata & diagnostics from custom detector if available
        custom_details = {}
        for r in detector_results:
            if r.detector_id == "custom_rf" and r.is_available:
                custom_details = r.details
                break

        # Frame diagnostics for deep inspection
        frame_analysis = []
        if self.custom_adapter and hasattr(self.custom_adapter.detector, "feature_extractor"):
            pass

        # 5. Build Unified Structured Response
        return {
            # Core Top-Level Schema (fully backwards-compatible with existing UI & clients)
            "verdict": ensemble_res.verdict,
            "ai_probability": ensemble_res.ai_probability,
            "confidence": ensemble_res.confidence,
            "frames_analyzed": max([r.frames_analyzed for r in detector_results] + [0]),
            "temporal_analysis": "completed",
            "audio_analysis": "not_performed",
            "video_metadata": custom_details.get("video_metadata", {}),
            "visual_indicators": ensemble_res.visual_indicators,
            "summary_features": custom_details.get("summary_features", {}),

            # Hybrid Specific Extensions
            "is_hybrid": True,
            "pipeline_type": "hybrid_multi_model_ensemble",
            "model_version": MODEL_VERSION,
            "total_latency_ms": total_duration_ms,

            # Consensus & Evidence Diagnostics
            "consensus": {
                "agreement": ensemble_res.agreement,
                "agreement_score": round(ensemble_res.agreement_score, 2),
                "active_detectors": ensemble_res.active_detectors_count,
                "total_detectors": ensemble_res.total_detectors_count,
                "applied_weights": ensemble_res.applied_weights,
                "inconclusive_reason": ensemble_res.inconclusive_reason
            },

            # Individual Detector Breakdown
            "individual_detectors": {
                r.detector_id: r.to_dict()
                for r in detector_results
            },

            # Limitations & System Information
            "limitations": ensemble_res.limitations
        }

    # Alias for analyze
    analyze = predict
