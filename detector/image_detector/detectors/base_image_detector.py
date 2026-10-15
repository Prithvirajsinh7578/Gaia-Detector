"""
base_image_detector.py - Standardized base interface for all Gaia image detectors.
Ensures every model outputs a standardized, calibrated result schema.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from PIL import Image


@dataclass
class ImageDetectorResult:
    detector_id: str
    model_name: str
    category: str  # "custom_cnn" | "pretrained_transformer" | "complementary_vision" | "commercial_api"
    status: str    # "success" | "error" | "skipped" | "unconfigured"
    ai_probability: float          # 0.0 to 100.0 (or normalized 0.0 to 1.0)
    authentic_probability: float   # 0.0 to 100.0
    verdict: str                   # "Likely AI-generated" | "Likely Authentic" | "Inconclusive"
    confidence: str                # "High" | "Medium" | "Low" | "None"
    latency_ms: float
    raw_scores: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "detector_id": self.detector_id,
            "model_name": self.model_name,
            "category": self.category,
            "status": self.status,
            "ai_probability": round(self.ai_probability, 1),
            "authentic_probability": round(self.authentic_probability, 1),
            "verdict": self.verdict,
            "confidence": self.confidence,
            "latency_ms": round(self.latency_ms, 1),
            "raw_scores": self.raw_scores,
            "error_message": self.error_message,
        }


class BaseImageDetector(ABC):
    """Abstract base class for all image detection models in Gaia Detector."""

    @property
    @abstractmethod
    def detector_id(self) -> str:
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @abstractmethod
    def predict(self, image: Image.Image) -> ImageDetectorResult:
        """Runs inference on a PIL Image and returns an ImageDetectorResult."""
        pass
