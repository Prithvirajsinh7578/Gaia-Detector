"""
custom_image_adapter.py - Adapter for Model 1 (Gaia Custom Image Classifier).
Handles preprocessing, device allocation, inference, calibration, and standardized reporting.
"""

import time
import json
import torch
import torchvision.transforms as T
from PIL import Image
from pathlib import Path
from typing import Optional

from .base_image_detector import BaseImageDetector, ImageDetectorResult
from detector.image_detector.models.custom_classifier import GaiaImageClassifier
from detector.image_detector.config import (
    CHECKPOINT_PATH, METADATA_PATH, DEVICE, IMAGE_SIZE
)


class CustomImageDetectorAdapter(BaseImageDetector):
    """Adapter for Gaia Custom-Trained EfficientNet-B0 Image Classifier."""

    def __init__(self, checkpoint_path: Optional[Path] = None, metadata_path: Optional[Path] = None):
        self._detector_id = "gaia_custom_image"
        self._model_name = "Gaia Custom EfficientNet-B0 Classifier"
        self._category = "custom_cnn"
        self.device = torch.device(DEVICE)

        self.checkpoint_path = checkpoint_path or CHECKPOINT_PATH
        self.metadata_path = metadata_path or METADATA_PATH

        self.model: Optional[GaiaImageClassifier] = None
        self.metadata: dict = {}
        self.is_loaded: bool = False
        self.error_message: Optional[str] = None

        # Standard Preprocessing Pipeline
        self.transform = T.Compose([
            T.Resize(IMAGE_SIZE),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        self._load_model()

    @property
    def detector_id(self) -> str:
        return self._detector_id

    @property
    def model_name(self) -> str:
        return self._model_name

    def _load_model(self):
        """Loads trained weights and calibration metadata if available."""
        if not self.checkpoint_path.exists():
            self.error_message = f"Checkpoint not found at {self.checkpoint_path}"
            return

        try:
            model = GaiaImageClassifier(pretrained=False)
            state_dict = torch.load(self.checkpoint_path, map_location=self.device)
            model.load_state_dict(state_dict)
            model.to(self.device)
            model.eval()

            # Load metadata
            if self.metadata_path.exists():
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
                temp = self.metadata.get("calibration", {}).get("temperature", 1.0)
                model.set_temperature(temp)

            self.model = model
            self.is_loaded = True
            self.error_message = None
        except Exception as e:
            self.error_message = f"Failed to load custom model weights: {e}"
            self.is_loaded = False

    def predict(self, image: Image.Image) -> ImageDetectorResult:
        start_time = time.time()

        if not self.is_loaded or self.model is None:
            # Fallback when weights are not yet trained or loaded
            return ImageDetectorResult(
                detector_id=self.detector_id,
                model_name=self.model_name,
                category=self._category,
                status="unconfigured" if not self.checkpoint_path.exists() else "error",
                ai_probability=50.0,
                authentic_probability=50.0,
                verdict="Inconclusive",
                confidence="None",
                latency_ms=0.0,
                error_message=self.error_message or "Model checkpoint not initialized."
            )

        try:
            # Ensure RGB
            if image.mode != "RGB":
                img = image.convert("RGB")
            else:
                img = image

            tensor = self.transform(img).unsqueeze(0).to(self.device)

            with torch.no_grad():
                prob = self.model.predict_proba(tensor).item()

            ai_prob = max(0.0, min(100.0, prob * 100.0))
            auth_prob = 100.0 - ai_prob
            latency = (time.time() - start_time) * 1000.0

            # Determine verdict and confidence
            if ai_prob >= 65.0:
                verdict = "Likely AI-generated"
                conf = "High" if ai_prob >= 85.0 else "Medium"
            elif ai_prob <= 35.0:
                verdict = "Likely Authentic"
                conf = "High" if ai_prob <= 15.0 else "Medium"
            else:
                verdict = "Inconclusive"
                conf = "Low"

            return ImageDetectorResult(
                detector_id=self.detector_id,
                model_name=self.model_name,
                category=self._category,
                status="success",
                ai_probability=ai_prob,
                authentic_probability=auth_prob,
                verdict=verdict,
                confidence=conf,
                latency_ms=latency,
                raw_scores={"calibrated_prob": round(prob, 4)}
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000.0
            return ImageDetectorResult(
                detector_id=self.detector_id,
                model_name=self.model_name,
                category=self._category,
                status="error",
                ai_probability=50.0,
                authentic_probability=50.0,
                verdict="Inconclusive",
                confidence="None",
                latency_ms=latency,
                error_message=str(e)
            )
