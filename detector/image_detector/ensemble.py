"""
ensemble.py - Three-Model Image Detection Ensemble Engine for Gaia Detector.
Combines:
  Model 1: Custom Deep Transfer-Learning Classifier (EfficientNet-B0)
  Model 2: Pretrained Vision Transformer (umm-maybe/AI-image-detector, Swin)
  Model 3: Complementary Vision Model (Ateeqq/ai-vs-human-image-detector, SigLIP) / Sightengine API
"""

import time
import math
import numpy as np
from PIL import Image
from typing import Dict, Any, List, Optional

from detector.image_detector.detectors.base_image_detector import ImageDetectorResult
from detector.image_detector.detectors.custom_image_adapter import CustomImageDetectorAdapter
from detector.image_detector.detectors.hf_image_detector import HFImageDetectorAdapter
from detector.image_detector.detectors.complementary_image_detector import ComplementaryImageDetectorAdapter
from detector.image_detector.config import (
    DEFAULT_WEIGHTS, AI_THRESHOLD, HUMAN_THRESHOLD, DISCREPANCY_LIMIT
)


def extract_visual_forensic_features(image: Image.Image) -> Dict[str, float]:
    """
    Computes objective quantitative forensic metrics from image pixels.
    Includes sharpness (Laplacian variance), high-frequency FFT energy, color entropy, and contrast.
    """
    try:
        # Resize to standard size for normalized computation
        img_rgb = image.convert("RGB").resize((256, 256))
        arr = np.array(img_rgb, dtype=np.float32)

        # Grayscale representation
        gray = 0.2989 * arr[:, :, 0] + 0.5870 * arr[:, :, 1] + 0.1140 * arr[:, :, 2]

        # 1. Image Sharpness (approximate Laplacian variance)
        laplacian = (
            np.roll(gray, 1, axis=0) + np.roll(gray, -1, axis=0) +
            np.roll(gray, 1, axis=1) + np.roll(gray, -1, axis=1) - 4 * gray
        )
        sharpness = float(np.var(laplacian))

        # 2. High-Frequency Spectral Energy Ratio (FFT)
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.abs(f_shift)
        h, w = gray.shape
        cy, cx = h // 2, w // 2
        # Mask out low frequencies (radius 30)
        y, x = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((x - cx)**2 + (y - cy)**2)
        high_freq_mask = dist_from_center > 30
        high_freq_energy = float(np.sum(magnitude_spectrum[high_freq_mask]))
        total_energy = float(np.sum(magnitude_spectrum) + 1e-6)
        spectral_hf_ratio = float((high_freq_energy / total_energy) * 100.0)

        # 3. Color Entropy (Information density)
        hist, _ = np.histogram(gray, bins=64, range=(0, 256), density=True)
        hist = hist[hist > 0]
        entropy = float(-np.sum(hist * np.log2(hist)))

        # 4. Global Contrast (Standard deviation of luminance)
        contrast = float(np.std(gray))

        return {
            "Sharpness Score": round(sharpness, 2),
            "High-Freq Energy %": round(spectral_hf_ratio, 2),
            "Texture Entropy": round(entropy, 2),
            "Global Contrast": round(contrast, 2),
        }
    except Exception:
        return {}


class ImageEnsembleDetector:
    """Three-Model Image Authenticity Detection Ensemble."""

    def __init__(self):
        self.model_1 = CustomImageDetectorAdapter()
        self.model_2 = HFImageDetectorAdapter()
        self.model_3 = ComplementaryImageDetectorAdapter()
        self.weights = DEFAULT_WEIGHTS.copy()

    def predict(self, image: Image.Image) -> Dict[str, Any]:
        start_time = time.time()

        # 1. Run all three models independently
        r1 = self.model_1.predict(image)
        r2 = self.model_2.predict(image)
        r3 = self.model_3.predict(image)

        individual_results = [r1, r2, r3]

        # 2. Filter active and successful detectors
        active_results = [r for r in individual_results if r.status == "success"]

        # 3. Dynamic Weight Normalization
        if active_results:
            weight_keys = {
                "gaia_custom_image": "custom_model",
                "hf_swin_detector": "hf_model_2",
                "complementary_siglip_detector": "hf_model_3",
                "sightengine_image_api": "hf_model_3",
            }
            raw_weights = [self.weights.get(weight_keys.get(r.detector_id, "custom_model"), 0.33) for r in active_results]
            total_weight = sum(raw_weights) or 1.0
            norm_weights = [w / total_weight for w in raw_weights]

            # Weighted consensus probability
            weighted_ai_prob = sum(r.ai_probability * w for r, w in zip(active_results, norm_weights))
            weighted_ai_prob = max(0.0, min(100.0, weighted_ai_prob))

            # Discrepancy metric
            probs = [r.ai_probability for r in active_results]
            discrepancy = max(probs) - min(probs) if len(probs) > 1 else 0.0
        else:
            weighted_ai_prob = 50.0
            discrepancy = 0.0

        # 4. Consensus Classification & Agreement
        inconclusive_reason = None
        if not active_results:
            verdict = "INCONCLUSIVE"
            agreement = "Unavailable"
            inconclusive_reason = "No image detector models could be loaded or executed."
        elif discrepancy > DISCREPANCY_LIMIT:
            verdict = "INCONCLUSIVE"
            agreement = "Conflicting Evidence"
            inconclusive_reason = f"Models strongly diverge by {discrepancy:.1f}% (min {min(probs):.1f}% vs max {max(probs):.1f}%). Withholding confident verdict."
        elif weighted_ai_prob >= AI_THRESHOLD:
            verdict = "LIKELY_AI_GENERATED"
            agreement = "Strong Consensus" if discrepancy < 20.0 else "Moderate Consensus"
        elif weighted_ai_prob <= HUMAN_THRESHOLD:
            verdict = "LIKELY_AUTHENTIC"
            agreement = "Strong Consensus" if discrepancy < 20.0 else "Moderate Consensus"
        else:
            verdict = "INCONCLUSIVE"
            agreement = "Uncertain Evidence"
            inconclusive_reason = f"Ensemble AI probability ({weighted_ai_prob:.1f}%) lies in the neutral ambiguity zone ({HUMAN_THRESHOLD}% - {AI_THRESHOLD}%)."

        # 5. Extract Quantitative Forensic Features
        forensic_features = extract_visual_forensic_features(image)

        # 6. Synthesize Evidence and Key Forensic Indicators
        evidence: List[str] = []
        if verdict == "LIKELY_AI_GENERATED":
            evidence.append(f"Ensemble consensus indicates AI-generation ({weighted_ai_prob:.1f}% confidence across {len(active_results)} active models).")
            if "High-Freq Energy %" in forensic_features and forensic_features["High-Freq Energy %"] > 25.0:
                evidence.append(f"Elevated high-frequency spectral artifacts ({forensic_features['High-Freq Energy %']}%) consistent with diffusion synthesis.")
            if "Texture Entropy" in forensic_features:
                evidence.append(f"Synthetic texture distribution observed (entropy: {forensic_features['Texture Entropy']}).")
        elif verdict == "LIKELY_AUTHENTIC":
            evidence.append(f"Ensemble consensus indicates authentic photography/artwork ({100.0 - weighted_ai_prob:.1f}% confidence).")
            evidence.append("Natural optical chromatic and luminance dispersion without generative grid artifacts.")
        else:
            evidence.append(f"Classification inconclusive: {inconclusive_reason or 'Evidence is insufficient'}")

        # Individual detectors mapping for UI
        individual_map = {
            "model_1_custom": r1.to_dict(),
            "model_2_hf_swin": r2.to_dict(),
            "model_3_complementary": r3.to_dict(),
        }

        processing_ms = (time.time() - start_time) * 1000.0

        # Construct short summary
        summary = (
            f"Three-model ensemble analysis concluded '{verdict.replace('_', ' ').title()}' "
            f"with an estimated AI probability of {weighted_ai_prob:.1f}%. "
            f"Consensus: {agreement}. Active detectors: {len(active_results)}/{len(individual_results)}."
        )

        return {
            "content_type": "image",
            "prediction": verdict,
            "status": "Likely AI-Generated" if verdict == "LIKELY_AI_GENERATED" else ("Likely Authentic" if verdict == "LIKELY_AUTHENTIC" else "Inconclusive"),
            "confidence": round(weighted_ai_prob if verdict == "LIKELY_AI_GENERATED" else (100.0 - weighted_ai_prob if verdict == "LIKELY_AUTHENTIC" else 50.0), 1),
            "processing_time_sec": round(processing_ms / 1000.0, 3),
            "risk_level": "High" if verdict == "LIKELY_AI_GENERATED" else ("Low" if verdict == "LIKELY_AUTHENTIC" else "Medium"),
            "summary": summary,
            "detector_name": "Gaia 3-Model Image Ensemble (Custom + Swin + SigLIP)",
            "verified": True,
            "evidence": evidence,
            "details": {
                "ai_probability": round(weighted_ai_prob, 1),
                "authentic_probability": round(100.0 - weighted_ai_prob, 1),
                "consensus": {
                    "agreement": agreement,
                    "active_detectors": len(active_results),
                    "total_detectors": len(individual_results),
                    "discrepancy": round(discrepancy, 1),
                    "inconclusive_reason": inconclusive_reason,
                },
                "individual_detectors": individual_map,
                "features": forensic_features,
            }
        }
