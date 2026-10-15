"""
detectors package for Hybrid AI Video Detection System.
Exposes standardized adapters for custom, pretrained, and external API detectors.
"""

from .base_detector import DetectorResult
from .custom_detector_adapter import CustomDetectorAdapter
from .hf_video_detector import HFVideoDetector
from .sightengine_detector import SightengineVideoDetector

__all__ = [
    "DetectorResult",
    "CustomDetectorAdapter",
    "HFVideoDetector",
    "SightengineVideoDetector"
]
