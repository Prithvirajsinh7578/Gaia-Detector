"""
video_utils.py - Utility helpers for video I/O, device management, and array processing.
"""

import os
import gc
import cv2
import numpy as np
import torch
from utils.constants import SUPPORTED_EXTENSIONS, MAX_FILE_SIZE_MB

# Hardware Acceleration Setup
device = "cuda" if torch.cuda.is_available() else "cpu"

if device == "cuda":
    gpu_name = torch.cuda.get_device_name(0)
    vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    print(f"[Video Acceleration] Active GPU: {gpu_name} ({vram_gb:.1f} GB VRAM)")
    try:
        # Prevent VRAM starvation on laptop GPUs
        torch.cuda.set_per_process_memory_fraction(0.65, 0)
    except Exception:
        pass
    torch.backends.cudnn.benchmark = False
else:
    print("[Video Acceleration] GPU not detected, utilizing CPU inference.")


def clear_gpu():
    """Safely flush PyTorch CUDA cache and invoke Python garbage collection."""
    if device == "cuda":
        torch.cuda.empty_cache()
    gc.collect()


def validate_file_path(file_path: str) -> tuple[bool, str]:
    """
    Validates that the file exists, has a supported video extension,
    and does not exceed the maximum allowed file size.
    """
    if not os.path.exists(file_path):
        return False, f"File does not exist: {file_path}"

    if not os.path.isfile(file_path):
        return False, f"Path is not a regular file: {file_path}"

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return False, f"Unsupported video extension '{ext}'. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"

    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f"File size ({size_mb:.1f} MB) exceeds maximum allowed limit of {MAX_FILE_SIZE_MB} MB."

    if size_mb == 0:
        return False, "File is empty (0 bytes)."

    return True, "File path is valid."


def get_video_capture(file_path: str) -> cv2.VideoCapture:
    """
    Safely opens a video file using OpenCV VideoCapture.
    Raises IOError if the file cannot be opened.
    """
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        cap.release()
        raise IOError(f"OpenCV could not open video stream: {file_path}")
    return cap


def bgr_to_rgb(frame: np.ndarray) -> np.ndarray:
    """Converts a BGR image array (OpenCV default) to RGB."""
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


def rgb_to_gray(frame: np.ndarray) -> np.ndarray:
    """Converts an RGB image array to single-channel Grayscale."""
    return cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
