"""
custom_detector_adapter.py - Adapter wrapping existing custom Spatial-Temporal Video Detector.
Maintains full backwards compatibility and preserves all custom ML components.
"""

import time
from typing import Dict, Any, Optional, List
from .base_detector import DetectorResult
from detector import VideoDetector
from utils.constants import MODEL_VERSION


class CustomDetectorAdapter:
    """
    Adapter encapsulating the user's custom trained VideoDetector.
    Produces standardized DetectorResult representations without modifying
    any of the underlying feature extraction or model logic.
    """

    def __init__(self, detector: Optional[VideoDetector] = None):
        if detector is not None:
            self._detector = detector
        else:
            self._detector = VideoDetector()

    @property
    def detector(self) -> VideoDetector:
        return self._detector

    def predict(self, video_path: str, preloaded_frames=None) -> DetectorResult:
        """
        Executes prediction using custom spatial-temporal pipeline.
        Returns standardized DetectorResult.
        """
        start_time = time.time()
        try:
            # Execute existing custom prediction pipeline
            pred = self._detector.predict(video_path)
            duration_ms = round((time.time() - start_time) * 1000.0, 2)

            return DetectorResult(
                detector_id="custom_rf",
                name="Custom Spatial-Temporal Ensemble",
                category="spatial_temporal_rf",
                status="success",
                ai_probability=float(pred.get("ai_probability", 50.0)),
                raw_score=float(pred.get("raw_score", pred.get("ai_probability", 50.0) / 100.0)),
                verdict=pred.get("verdict", "Inconclusive / Uncertain"),
                confidence=pred.get("confidence", "Low"),
                latency_ms=duration_ms,
                frames_analyzed=pred.get("frames_analyzed", 0),
                version=MODEL_VERSION,
                details={
                    "summary_features": pred.get("summary_features", {}),
                    "visual_indicators": pred.get("visual_indicators", []),
                    "video_metadata": pred.get("video_metadata", {})
                },
                error=None
            )

        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000.0, 2)
            return DetectorResult(
                detector_id="custom_rf",
                name="Custom Spatial-Temporal Ensemble",
                category="spatial_temporal_rf",
                status="failed",
                ai_probability=50.0,
                raw_score=0.5,
                verdict="Inconclusive",
                confidence="None",
                latency_ms=duration_ms,
                frames_analyzed=0,
                version=MODEL_VERSION,
                details={},
                error=f"Custom detector execution failed: {str(e)}"
            )
