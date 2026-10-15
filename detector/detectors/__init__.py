"""
detectors/__init__.py - Expose all text detector components.
"""

from .base_detector import BaseTextDetector, DetectorResult
from .custom_text_adapter import CustomTextAdapter
from .hf_text_detector import HFTextDetector
from .gptzero_detector import GPTZeroTextDetector

__all__ = [
    "BaseTextDetector",
    "DetectorResult",
    "CustomTextAdapter",
    "HFTextDetector",
    "GPTZeroTextDetector"
]
