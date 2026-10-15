"""
base_detector.py - Unified Data Contract and Base Class for Text Detectors.
Standardizes outputs across Custom Model, Pretrained Hugging Face Models, and External APIs.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod


@dataclass
class DetectorResult:
    """
    Standardized result contract for all text detection evidence sources.
    Guarantees strict schema compatibility across local and remote inference engines.
    """
    detector_id: str
    name: str
    category: str  # 'custom_model', 'pretrained_hf', 'commercial_api'
    status: str    # 'success', 'unconfigured', 'failed', 'skipped'
    ai_probability: float  # 0.0 to 100.0 percent
    raw_score: float       # 0.0 to 1.0
    human_probability: float = 0.0  # 0.0 to 100.0 percent
    is_calibrated: bool = False
    verdict: str = "Inconclusive / Uncertain"
    confidence: str = "Low"  # 'High', 'Medium', 'Low', 'None'
    latency_ms: float = 0.0
    analyzed_tokens: int = 0
    analyzed_chars: int = 0
    indicators: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "detector_id": self.detector_id,
            "name": self.name,
            "category": self.category,
            "status": self.status,
            "ai_probability": round(self.ai_probability, 1),
            "human_probability": round(self.human_probability, 1),
            "raw_score": round(self.raw_score, 4),
            "is_calibrated": self.is_calibrated,
            "verdict": self.verdict,
            "confidence": self.confidence,
            "latency_ms": round(self.latency_ms, 1),
            "analyzed_tokens": self.analyzed_tokens,
            "analyzed_chars": self.analyzed_chars,
            "indicators": self.indicators,
            "metadata": self.metadata,
            "error_message": self.error_message
        }


class BaseTextDetector(ABC):
    """
    Abstract interface that all individual detector modules must implement.
    """

    @abstractmethod
    def predict(self, text: str) -> DetectorResult:
        """
        Analyzes input text and produces a standardized DetectorResult.
        """
        pass
