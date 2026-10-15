"""
detector.py - Core orchestrator for the Video AI Detection pipeline.
Step 14 of Video AI Detector Pipeline.
"""

from typing import Dict, Any, List
from video_preprocessor import VideoPreprocessor
from frame_extractor import FrameExtractor
from feature_extractor import VideoFeatureExtractor
from classifier import VideoClassifier
from utils.constants import (
    MODEL_PATH,
    MODEL_VERSION,
    DEFAULT_SAMPLE_FRAMES
)
from utils.video_utils import clear_gpu


class VideoDetector:
    """
    End-to-end Video AI Content Detector.
    Coordinates file validation, uniform frame sampling, spatial & deep feature extraction,
    temporal motion analysis, calibrated probability calculation, and indicator generation.
    """

    def __init__(
        self,
        model_path: str = MODEL_PATH,
        num_sample_frames: int = DEFAULT_SAMPLE_FRAMES
    ):
        self.preprocessor = VideoPreprocessor()
        self.frame_extractor = FrameExtractor(num_frames=num_sample_frames)
        self.feature_extractor = VideoFeatureExtractor(use_deep_encoder=True)
        self.classifier = VideoClassifier(model_path=model_path)
        self.classifier.load()

    def _generate_indicators(
        self,
        features: Dict[str, float],
        prob_pct: float
    ) -> List[str]:
        """
        Derives human-interpretable visual and temporal indicators based on feature thresholds.
        """
        indicators = []

        # 1. AI-leaning indicators
        if features.get("high_freq_ratio_mean", 1.0) < 0.12:
            indicators.append("Overly smoothed high-frequency spectrum (diffusion synthesis signature)")

        if features.get("flicker_score_max", 0.0) > 0.45:
            indicators.append("Temporal luminance flickering detected across frame intervals")

        if features.get("temporal_inconsistency", 0.0) > 0.35:
            indicators.append("Unnatural embedding trajectory variance (latent space morphing)")

        if features.get("frame_similarity_min", 1.0) < 0.50:
            indicators.append("Abrupt intra-shot visual incoherence or morphing artifacts")

        if features.get("texture_contrast_mean", 100.0) < 18.0:
            indicators.append("Subdued local texture contrast (synthetic rendering smoothing)")

        if features.get("motion_magnitude_std", 0.0) > 4.5:
            indicators.append("Erratic optical flow motion dispersion across object boundaries")

        # 2. Authentic-leaning indicators
        if prob_pct <= 40.0:
            if features.get("high_freq_ratio_mean", 0.0) >= 0.18:
                indicators.append("Organic high-frequency edge detail and natural sensor noise")
            if features.get("appearance_stability", 0.0) >= 0.70:
                indicators.append("Rigid physical perspective continuity and stable optical flow")
            if features.get("flicker_score_max", 1.0) < 0.30:
                indicators.append("Smooth illumination transitions consistent with optical camera sensors")

        # Fallback if no specific threshold triggered
        if not indicators:
            if prob_pct >= 50.0:
                indicators.append("Spatial-temporal motion patterns align closely with generated AI video models")
            else:
                indicators.append("Visual texture cadence and temporal consistency align with authentic camera footage")

        return indicators

    def predict(self, file_path: str) -> Dict[str, Any]:
        """
        Executes complete video prediction pipeline.

        Args:
            file_path: Path to the target video file.

        Returns:
            Structured prediction dictionary matching the Video AI Detector specification.
        """
        # 1. Validate & extract metadata
        metadata = self.preprocessor.preprocess(file_path)

        # 2. Extract uniformly spaced frames across complete duration
        frames = self.frame_extractor.extract_frames(file_path, metadata)

        # 3. Extract spatial visual features + temporal flow metrics
        features_dict, feature_vector, frame_diagnostics = self.feature_extractor.extract_features(frames)

        # 4. Predict calibrated probability & verdict
        classification = self.classifier.predict_calibrated(feature_vector)

        # 5. Generate descriptive indicators
        indicators = self._generate_indicators(features_dict, classification["ai_probability"])

        clear_gpu()

        return {
            "verdict": classification["verdict"],
            "ai_probability": classification["ai_probability"],
            "confidence": classification["confidence"],
            "frames_analyzed": len(frames),
            "temporal_analysis": "completed",
            "audio_analysis": "not_performed",
            "video_metadata": metadata,
            "visual_indicators": indicators,
            "frame_analysis": frame_diagnostics,
            "summary_features": {
                "sharpness": features_dict.get("sharpness_mean", 0.0),
                "textureContrast": features_dict.get("texture_contrast_mean", 0.0),
                "highFreqRatio": features_dict.get("high_freq_ratio_mean", 0.0),
                "motionMagnitude": features_dict.get("motion_magnitude_mean", 0.0),
                "frameSimilarity": features_dict.get("frame_similarity_mean", 0.0),
                "flickerScore": features_dict.get("flicker_score_mean", 0.0),
                "temporalConsistency": round(1.0 - min(1.0, features_dict.get("temporal_inconsistency", 0.0)), 3),
                "appearanceStability": features_dict.get("appearance_stability", 0.0),
            },
            "model_version": MODEL_VERSION,
            "limitations": [
                "Predictions may degrade on heavily recompressed or downscaled video clips",
                "Unseen generation models or artistic animation styles may yield inconclusive scores",
                "Audio track is not currently factored into visual-temporal verification"
            ]
        }

    # Alias for analyze
    analyze = predict

