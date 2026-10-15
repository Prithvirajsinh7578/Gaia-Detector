"""
feature_extractor.py - Master feature extraction engine aggregating spatial and temporal signals.
Step 6 of Video AI Detector Pipeline.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from scipy.stats import trim_mean
from frame_extractor import FrameSample
from features.visual_features import VisualFeatureExtractor
from temporal_analyzer import TemporalAnalyzer
from utils.constants import FEATURE_NAMES


class VideoFeatureExtractor:
    """
    Combines spatial frame-level statistics, deep visual encoder embeddings,
    and temporal motion dynamics into a standardized, fixed-dimension feature vector.
    """

    def __init__(self, use_deep_encoder: bool = True):
        self.visual_extractor = VisualFeatureExtractor(use_deep_encoder=use_deep_encoder)
        self.temporal_analyzer = TemporalAnalyzer()

    def extract_features(
        self,
        frames: List[FrameSample]
    ) -> Tuple[Dict[str, float], List[float], List[Dict[str, Any]]]:
        """
        Extracts and aggregates features across the sampled frames of a video.

        Args:
            frames: Uniformly sampled FrameSample instances.

        Returns:
            Tuple of:
            - features_dict: Key-value dictionary of all aggregated features.
            - feature_vector: Numerical array ordered strictly by FEATURE_NAMES.
            - frame_diagnostics: Frame-level visual statistics for report inspection.
        """
        if not frames:
            raise ValueError("Cannot extract features from an empty frame sequence.")

        # 1. Frame-level handcrafted spatial features
        frame_diagnostics: List[Dict[str, Any]] = []
        handcrafted_list: List[Dict[str, float]] = []

        for f in frames:
            # Use original resolution RGB for high-fidelity spatial analysis
            stats = self.visual_extractor.extract_frame_handcrafted(f.rgb_original)
            handcrafted_list.append(stats)

            frame_diag = {
                "frame_idx": f.frame_idx,
                "timestamp_sec": f.timestamp_sec,
                **stats
            }
            frame_diagnostics.append(frame_diag)

        # Aggregate spatial statistics across all sampled frames with outlier resilience
        def agg(key: str) -> tuple[float, float]:
            vals = [item[key] for item in handcrafted_list]
            if len(vals) >= 6:
                # Trim 12.5% from tails to suppress sudden watermarks, logos, or credit screens
                center_val = float(trim_mean(vals, 0.125))
            else:
                center_val = float(np.mean(vals))
            return center_val, float(np.std(vals))

        sharp_m, sharp_s = agg("sharpness")
        text_cont_m, text_cont_s = agg("texture_contrast")
        text_eng_m, _ = agg("texture_energy")
        col_div_m, col_div_s = agg("color_diversity")
        hfreq_m, _ = agg("high_freq_ratio")
        noise_m, noise_s = agg("noise_residual")
        block_m, _ = agg("compression_blocking")

        # 2. Deep Visual Embeddings
        resized_rgbs = [f.rgb_resized for f in frames]
        deep_embeddings = self.visual_extractor.extract_deep_embeddings(resized_rgbs)

        # Deep embedding statistics
        norms = np.linalg.norm(deep_embeddings, axis=1)
        deep_norm_mean = float(np.mean(norms))
        deep_dispersion = float(np.mean(np.std(deep_embeddings, axis=0)))

        # 3. Inter-Frame Temporal Analysis
        temporal_stats = self.temporal_analyzer.analyze_sequence(
            frames=frames,
            deep_embeddings=deep_embeddings
        )

        # 4. Construct unified feature dictionary
        features_dict: Dict[str, float] = {
            "sharpness_mean": round(sharp_m, 4),
            "sharpness_std": round(sharp_s, 4),
            "texture_contrast_mean": round(text_cont_m, 4),
            "texture_contrast_std": round(text_cont_s, 4),
            "texture_energy_mean": round(text_eng_m, 4),
            "color_diversity_mean": round(col_div_m, 4),
            "color_diversity_std": round(col_div_s, 4),
            "high_freq_ratio_mean": round(hfreq_m, 4),
            "noise_residual_mean": round(noise_m, 4),
            "noise_residual_std": round(noise_s, 4),
            "compression_blocking_mean": round(block_m, 4),
            "deep_embedding_norm_mean": round(deep_norm_mean, 4),
            "deep_embedding_dispersion": round(deep_dispersion, 4),
            **temporal_stats
        }

        # Vector ordered according to canonical FEATURE_NAMES schema
        feature_vector: List[float] = [
            features_dict.get(fname, 0.0) for fname in FEATURE_NAMES
        ]

        return features_dict, feature_vector, frame_diagnostics
