"""
temporal_analyzer.py - Coordinates inter-frame temporal analysis, optical flow, and embedding trajectory.
Step 5 of Video AI Detector Pipeline.
"""

from typing import List, Dict, Any
import numpy as np
from frame_extractor import FrameSample
from features.temporal_features import (
    compute_optical_flow_stats,
    compute_flicker_score,
    compute_appearance_stability
)
from utils.video_utils import rgb_to_gray


class TemporalAnalyzer:
    """
    Analyses how visual information, motion vectors, and deep feature representations
    evolve across sampled frames.
    """

    def __init__(self):
        pass

    def analyze_sequence(
        self,
        frames: List[FrameSample],
        deep_embeddings: np.ndarray = None
    ) -> Dict[str, float]:
        """
        Executes sequential temporal analysis across the sampled video frames.

        Args:
            frames: Uniformly sampled FrameSample instances.
            deep_embeddings: Optional (N, D) array of frame embeddings from visual encoder.

        Returns:
            Dictionary containing aggregated temporal features.
        """
        if len(frames) < 2:
            return {
                "motion_magnitude_mean": 0.0,
                "motion_magnitude_std": 0.0,
                "frame_similarity_mean": 1.0,
                "frame_similarity_min": 1.0,
                "frame_similarity_std": 0.0,
                "flicker_score_mean": 0.0,
                "flicker_score_max": 0.0,
                "temporal_inconsistency": 0.0,
                "appearance_stability": 1.0,
            }

        motion_means = []
        motion_stds = []
        flicker_scores = []
        appearance_stabilities = []

        # 1. Pixel & Optical Flow Dynamics
        for i in range(len(frames) - 1):
            prev_gray = rgb_to_gray(frames[i].rgb_resized)
            curr_gray = rgb_to_gray(frames[i + 1].rgb_resized)

            m_mean, m_std = compute_optical_flow_stats(prev_gray, curr_gray)
            flicker = compute_flicker_score(prev_gray, curr_gray)
            stability = compute_appearance_stability(prev_gray, curr_gray)

            motion_means.append(m_mean)
            motion_stds.append(m_std)
            flicker_scores.append(flicker)
            appearance_stabilities.append(stability)

        # 2. Deep Embedding Trajectory & Cosine Similarities
        cos_sims = []
        embedding_deltas = []

        if deep_embeddings is not None and len(deep_embeddings) >= 2:
            # Normalize embeddings for cosine similarity
            norms = np.linalg.norm(deep_embeddings, axis=1, keepdims=True) + 1e-7
            normalized_emb = deep_embeddings / norms

            for i in range(len(deep_embeddings) - 1):
                # Cosine similarity between consecutive frames
                sim = float(np.dot(normalized_emb[i], normalized_emb[i + 1]))
                cos_sims.append(max(-1.0, min(1.0, sim)))

                # Delta vector
                delta = deep_embeddings[i + 1] - deep_embeddings[i]
                embedding_deltas.append(np.linalg.norm(delta))

        # Defaults if deep embeddings were not provided or empty
        if not cos_sims:
            cos_sims = [1.0]
        if not embedding_deltas:
            embedding_deltas = [0.0]

        return {
            "motion_magnitude_mean": round(float(np.mean(motion_means)), 4),
            "motion_magnitude_std": round(float(np.mean(motion_stds)), 4),
            "frame_similarity_mean": round(float(np.mean(cos_sims)), 4),
            "frame_similarity_min": round(float(np.min(cos_sims)), 4),
            "frame_similarity_std": round(float(np.std(cos_sims)), 4),
            "flicker_score_mean": round(float(np.mean(flicker_scores)), 4),
            "flicker_score_max": round(float(np.max(flicker_scores)), 4),
            "temporal_inconsistency": round(float(np.std(embedding_deltas)), 4),
            "appearance_stability": round(float(np.mean(appearance_stabilities)), 4),
        }
