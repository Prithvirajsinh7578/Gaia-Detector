"""
temporal_features.py - Optical flow, frame-to-frame similarity, and temporal stability metrics.
Step 5 of Video AI Detector Pipeline.
"""

from typing import List, Dict, Any
import cv2
import numpy as np
from utils.video_utils import rgb_to_gray


def compute_optical_flow_stats(prev_gray: np.ndarray, curr_gray: np.ndarray) -> tuple[float, float]:
    """
    Computes dense optical flow (Farneback algorithm) between two grayscale frames.
    Returns (mean_motion_magnitude, std_motion_magnitude).
    """
    # Downscale for fast and robust optical flow estimation
    small_prev = cv2.resize(prev_gray, (160, 120), interpolation=cv2.INTER_AREA)
    small_curr = cv2.resize(curr_gray, (160, 120), interpolation=cv2.INTER_AREA)

    flow = cv2.calcOpticalFlowFarneback(
        small_prev,
        small_curr,
        None,
        pyr_scale=0.5,
        levels=2,
        winsize=11,
        iterations=2,
        poly_n=5,
        poly_sigma=1.1,
        flags=0
    )

    magnitude = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)
    mean_mag = float(np.mean(magnitude))
    std_mag = float(np.std(magnitude))

    return mean_mag, std_mag


def compute_flicker_score(prev_gray: np.ndarray, curr_gray: np.ndarray) -> float:
    """
    Measures abrupt lighting and regional intensity instability (flicker)
    between consecutive frames using normalized histogram intersection distance.
    """
    hist_prev = cv2.calcHist([prev_gray], [0], None, [32], [0, 256])
    hist_curr = cv2.calcHist([curr_gray], [0], None, [32], [0, 256])

    cv2.normalize(hist_prev, hist_prev, alpha=1.0, norm_type=cv2.NORM_L1)
    cv2.normalize(hist_curr, hist_curr, alpha=1.0, norm_type=cv2.NORM_L1)

    # Chi-square or Bhattacharyya distance between intensity histograms
    diff = np.sum(np.abs(hist_curr - hist_prev))
    return float(diff)


def compute_appearance_stability(prev_gray: np.ndarray, curr_gray: np.ndarray) -> float:
    """
    Computes visual structural appearance consistency between consecutive frames
    using normalized cross-correlation / structural similarity proxy.
    """
    small_prev = cv2.resize(prev_gray, (112, 112), interpolation=cv2.INTER_AREA).astype(np.float32)
    small_curr = cv2.resize(curr_gray, (112, 112), interpolation=cv2.INTER_AREA).astype(np.float32)

    # Normalized cross correlation score [-1.0, 1.0]
    p_mean = np.mean(small_prev)
    c_mean = np.mean(small_curr)

    p_norm = small_prev - p_mean
    c_norm = small_curr - c_mean

    denom = np.sqrt(np.sum(p_norm ** 2) * np.sum(c_norm ** 2)) + 1e-6
    correlation = float(np.sum(p_norm * c_norm) / denom)

    # Normalize into [0.0, 1.0] range
    return float(max(0.0, min(1.0, (correlation + 1.0) / 2.0)))
