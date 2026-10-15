"""
hf_image_detector.py - Adapter for Model 2: Hugging Face Pretrained AI Image Detector.
Uses umm-maybe/AI-image-detector (Swin Transformer architecture fine-tuned for artificial image cues).
"""

import time
import torch
from PIL import Image
from typing import Optional, Dict, Any
from transformers import AutoImageProcessor, AutoModelForImageClassification

from .base_image_detector import BaseImageDetector, ImageDetectorResult
from detector.image_detector.config import HF_MODEL_2_ID, DEVICE


class HFImageDetectorAdapter(BaseImageDetector):
    """Adapter for umm-maybe/AI-image-detector (Swin Transformer)."""

    def __init__(self, model_id: str = HF_MODEL_2_ID):
        self._detector_id = "hf_swin_detector"
        self._model_name = f"Pretrained Swin AI Detector ({model_id})"
        self._category = "pretrained_transformer"
        self.model_id = model_id
        self.device = torch.device(DEVICE)

        self.processor = None
        self.model = None
        self.is_loaded = False
        self.error_message: Optional[str] = None

        self._load_model()

    @property
    def detector_id(self) -> str:
        return self._detector_id

    @property
    def model_name(self) -> str:
        return self._model_name

    def _load_model(self):
        """Loads processor and weights once."""
        try:
            self.processor = AutoImageProcessor.from_pretrained(self.model_id)
            self.model = AutoModelForImageClassification.from_pretrained(self.model_id)
            self.model.to(self.device)
            self.model.eval()
            self.is_loaded = True
            self.error_message = None
        except Exception as e:
            self.error_message = f"Failed to load HF model {self.model_id}: {e}"
            self.is_loaded = False

    def predict(self, image: Image.Image) -> ImageDetectorResult:
        start_time = time.time()

        if not self.is_loaded or self.model is None or self.processor is None:
            return ImageDetectorResult(
                detector_id=self.detector_id,
                model_name=self.model_name,
                category=self._category,
                status="error",
                ai_probability=50.0,
                authentic_probability=50.0,
                verdict="Inconclusive",
                confidence="None",
                latency_ms=0.0,
                error_message=self.error_message or "Model not loaded."
            )

        try:
            if image.mode != "RGB":
                img = image.convert("RGB")
            else:
                img = image

            inputs = self.processor(images=img, return_tensors="pt").to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.softmax(logits, dim=-1).squeeze(0)

            # Map labels: umm-maybe uses {0: 'artificial', 1: 'human'}
            # We dynamically check id2label to avoid hardcoded index assumptions
            id2label = self.model.config.id2label
            ai_idx = None
            for idx, label in id2label.items():
                lbl_lower = str(label).lower()
                if "art" in lbl_lower or "ai" in lbl_lower or "fake" in lbl_lower or "synth" in lbl_lower:
                    ai_idx = int(idx)
                    break

            if ai_idx is not None:
                ai_prob_val = float(probs[ai_idx].item()) * 100.0
            else:
                # Default to index 0 if not discovered
                ai_prob_val = float(probs[0].item()) * 100.0

            ai_prob = max(0.0, min(100.0, ai_prob_val))
            auth_prob = 100.0 - ai_prob
            latency = (time.time() - start_time) * 1000.0

            if ai_prob >= 62.0:
                verdict = "Likely AI-generated"
                conf = "High" if ai_prob >= 82.0 else "Medium"
            elif ai_prob <= 38.0:
                verdict = "Likely Authentic"
                conf = "High" if ai_prob <= 18.0 else "Medium"
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
                raw_scores={id2label[i]: round(float(probs[i].item()), 4) for i in range(len(probs))}
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
