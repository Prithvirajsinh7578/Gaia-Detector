"""
complementary_image_detector.py - Adapter for Model 3: Complementary AI Image Detector.
Uses Ateeqq/ai-vs-human-image-detector (SigLIP vision transformer) with optional Sightengine API support.
"""

import os
import io
import time
import torch
import requests
from PIL import Image
from typing import Optional, Dict, Any
from transformers import AutoImageProcessor, AutoModelForImageClassification

from .base_image_detector import BaseImageDetector, ImageDetectorResult
from detector.image_detector.config import HF_MODEL_3_ID, DEVICE


class ComplementaryImageDetectorAdapter(BaseImageDetector):
    """Adapter for Model 3 (SigLIP Vision Transformer with optional Sightengine GenAI fallback)."""

    def __init__(self, model_id: str = HF_MODEL_3_ID):
        self._detector_id = "complementary_siglip_detector"
        self._model_name = f"Complementary SigLIP AI Detector ({model_id})"
        self._category = "complementary_vision"
        self.model_id = model_id
        self.device = torch.device(DEVICE)

        # Sightengine commercial credentials if present
        self.api_user = os.getenv("SIGHTENGINE_API_USER", "").strip()
        self.api_secret = os.getenv("SIGHTENGINE_API_SECRET", "").strip()

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
        """Loads processor and weights for Model 3."""
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

    def _call_sightengine_api(self, image: Image.Image) -> Optional[float]:
        """Calls Sightengine GenAI API if configured."""
        if not self.api_user or not self.api_secret:
            return None

        try:
            buf = io.BytesIO()
            image.save(buf, format="JPEG")
            buf.seek(0)

            params = {
                "models": "genai",
                "api_user": self.api_user,
                "api_secret": self.api_secret
            }
            files = {"media": ("image.jpg", buf, "image/jpeg")}
            r = requests.post("https://api.sightengine.com/1.0/check.json", files=files, data=params, timeout=12)
            if r.status_code == 200:
                data = r.json()
                if "type" in data and "ai_generated" in data["type"]:
                    return float(data["type"]["ai_generated"]) * 100.0
        except Exception:
            pass
        return None

    def predict(self, image: Image.Image) -> ImageDetectorResult:
        start_time = time.time()

        # Check commercial API first if configured
        api_prob = self._call_sightengine_api(image)
        if api_prob is not None:
            latency = (time.time() - start_time) * 1000.0
            verdict = "Likely AI-generated" if api_prob >= 60.0 else ("Likely Authentic" if api_prob <= 40.0 else "Inconclusive")
            return ImageDetectorResult(
                detector_id="sightengine_image_api",
                model_name="Sightengine Commercial GenAI API",
                category="commercial_api",
                status="success",
                ai_probability=api_prob,
                authentic_probability=100.0 - api_prob,
                verdict=verdict,
                confidence="High" if (api_prob >= 80 or api_prob <= 20) else "Medium",
                latency_ms=latency,
                raw_scores={"sightengine_genai": round(api_prob, 2)}
            )

        # Fallback to local SigLIP model
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
                error_message=self.error_message or "Model 3 not initialized."
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

            # Map labels: Ateeqq uses {0: 'ai', 1: 'hum'}
            id2label = self.model.config.id2label
            ai_idx = None
            for idx, label in id2label.items():
                lbl_lower = str(label).lower()
                if "ai" in lbl_lower or "fake" in lbl_lower or "art" in lbl_lower:
                    ai_idx = int(idx)
                    break

            if ai_idx is not None:
                ai_prob_val = float(probs[ai_idx].item()) * 100.0
            else:
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
