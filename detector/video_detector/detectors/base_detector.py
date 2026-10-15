"""
base_detector.py - Standardized detector interface and prediction results schema.
Supports uniform reporting across custom ML models, pretrained Hugging Face models,
and external AI detection APIs.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone


@dataclass
class DetectorResult:
    """
    Unified representation of an individual detector's prediction.
    """
    detector_id: str                      # e.g., 'custom_rf', 'hf_resnet50_t2v', 'sightengine_api'
    name: str                             # Human-readable display name
    category: str                         # 'spatial_temporal_rf' | 'deep_visual_t2v' | 'commercial_api'
    status: str                           # 'success' | 'failed' | 'disabled' | 'unconfigured'
    ai_probability: float                 # Normalized score 0.0 to 100.0%
    raw_score: float                      # Internal raw float score [0.0, 1.0]
    verdict: str                          # 'Likely AI-generated' | 'Likely authentic' | 'Inconclusive'
    confidence: str                       # 'High' | 'Medium' | 'Low' | 'None'
    latency_ms: float                     # Processing duration in milliseconds
    frames_analyzed: int                  # Number of frames inspected
    version: str = "1.0.0"                # Model or provider version
    details: Dict[str, Any] = field(default_factory=dict) # Diagnostic metadata
    error: Optional[str] = None           # Failure reason if status != 'success'
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Converts result dataclass to standard JSON-serializable dictionary."""
        return asdict(self)

    @property
    def is_available(self) -> bool:
        """Returns True if detector executed successfully and produced a valid score."""
        return self.status == "success" and self.error is None
