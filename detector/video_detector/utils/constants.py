"""
constants.py - Configuration constants and feature definitions for Video AI Detector.
"""

import os

# Base Directories
VIDEO_DETECTOR_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(VIDEO_DETECTOR_DIR, "models")
DATASETS_DIR = os.path.join(VIDEO_DETECTOR_DIR, "datasets")
RAW_DATASETS_DIR = os.path.join(DATASETS_DIR, "raw")
RAW_AUTHENTIC_DIR = os.path.join(RAW_DATASETS_DIR, "real") if os.path.exists(os.path.join(RAW_DATASETS_DIR, "real")) else os.path.join(RAW_DATASETS_DIR, "authentic")
RAW_AI_DIR = os.path.join(RAW_DATASETS_DIR, "ai") if os.path.exists(os.path.join(RAW_DATASETS_DIR, "ai")) else os.path.join(RAW_DATASETS_DIR, "ai_generated")

# Model & Schema Paths
MODEL_PATH = os.path.join(MODELS_DIR, "video_classifier.pkl")
CALIBRATION_MODEL_PATH = os.path.join(MODELS_DIR, "calibration_model.pkl")
FEATURE_SCHEMA_PATH = os.path.join(MODELS_DIR, "feature_schema.json")
MODEL_METADATA_PATH = os.path.join(MODELS_DIR, "model_metadata.json")
DATASET_PATH = os.path.join(DATASETS_DIR, "video_features.csv")

# Supported Video Extensions
SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".webm", ".avi", ".mkv", ".flv"}

# Video Processing Constraints
MAX_FILE_SIZE_MB = 1000.0
DEFAULT_SAMPLE_FRAMES = 16
MIN_SAMPLE_FRAMES = 4
MAX_SAMPLE_FRAMES = 64
FRAME_TARGET_SIZE = (224, 224)  # Width, Height for visual encoder

# Decision Thresholds
CONFIDENCE_HIGH_THRESHOLD = 0.80
CONFIDENCE_MEDIUM_THRESHOLD = 0.60
UNCERTAIN_LOWER_BOUND = 0.46
UNCERTAIN_UPPER_BOUND = 0.54

# Full Feature List for Video Classification
FEATURE_NAMES = [
    # Handcrafted Visual Spatial Features (Averaged across sampled frames)
    "sharpness_mean",
    "sharpness_std",
    "texture_contrast_mean",
    "texture_contrast_std",
    "texture_energy_mean",
    "color_diversity_mean",
    "color_diversity_std",
    "high_freq_ratio_mean",
    "noise_residual_mean",
    "noise_residual_std",
    "compression_blocking_mean",
    # Deep Visual Embedding Statistics
    "deep_embedding_norm_mean",
    "deep_embedding_dispersion",
    # Temporal & Motion Dynamics Features
    "motion_magnitude_mean",
    "motion_magnitude_std",
    "frame_similarity_mean",
    "frame_similarity_min",
    "frame_similarity_std",
    "flicker_score_mean",
    "flicker_score_max",
    "temporal_inconsistency",
    "appearance_stability",
]

MODEL_VERSION = "1.0.0"
