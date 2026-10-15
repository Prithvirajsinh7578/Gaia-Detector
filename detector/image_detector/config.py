"""
config.py - Centralized configuration for Gaia Image Detection System.
"""

from pathlib import Path
import os
import torch

# Base directories
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
DATA_DIR = BASE_DIR / "data"
DATASET_DIR = DATA_DIR / "dataset"
MODELS_DIR = BASE_DIR / "models"
CHECKPOINT_PATH = MODELS_DIR / "gaia_image_classifier.pt"
METADATA_PATH = MODELS_DIR / "model_metadata.json"

# Device configuration
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
USE_AMP = DEVICE == "cuda"

# Dataset settings
KAGGLE_DATASET_HANDLE = "tristanzhang32/ai-generated-images-vs-real-images"
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
NUM_WORKERS = 0  # 0 for safe multiprocessing on Windows

# Model 1 (Custom Classifier) Hyperparameters
MODEL_NAME = "efficientnet_b0"
LEARNING_RATE = 2e-4
WEIGHT_DECAY = 1e-4
NUM_EPOCHS = 6
EARLY_STOPPING_PATIENCE = 3

# Pretrained Models
HF_MODEL_2_ID = "umm-maybe/AI-image-detector"           # Swin Transformer
HF_MODEL_3_ID = "Ateeqq/ai-vs-human-image-detector"     # SigLIP Vision Transformer

# Ensemble thresholds & weights
# Default fallback weights if calibration data is sparse
DEFAULT_WEIGHTS = {
    "custom_model": 0.40,
    "hf_model_2": 0.35,
    "hf_model_3": 0.25,
}

# Classification Decision Boundaries
AI_THRESHOLD = 62.0          # Prob >= 62% -> LIKELY_AI_GENERATED
HUMAN_THRESHOLD = 38.0       # Prob <= 38% -> LIKELY_AUTHENTIC
DISCREPANCY_LIMIT = 45.0     # Discrepancy > 45% between detectors -> INCONCLUSIVE
