"""
frame_extractor.py - Uniform temporal frame sampling with timestamp tracking and normalization.
Step 3 of Video AI Detector Pipeline.
"""

from typing import List, Dict, Any, Tuple
import cv2
import numpy as np
from utils.constants import DEFAULT_SAMPLE_FRAMES, MIN_SAMPLE_FRAMES, MAX_SAMPLE_FRAMES, FRAME_TARGET_SIZE
from utils.video_utils import get_video_capture, bgr_to_rgb


class FrameSample:
    """Represents an extracted video frame with timing and resolution metadata."""

    def __init__(
        self,
        frame_idx: int,
        timestamp_ms: float,
        rgb_original: np.ndarray,
        rgb_resized: np.ndarray
    ):
        self.frame_idx = frame_idx
        self.timestamp_ms = round(timestamp_ms, 2)
        self.timestamp_sec = round(timestamp_ms / 1000.0, 3)
        self.rgb_original = rgb_original  # Original resolution RGB
        self.rgb_resized = rgb_resized    # Normalized target size (224x224) RGB

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_idx": self.frame_idx,
            "timestamp_ms": self.timestamp_ms,
            "timestamp_sec": self.timestamp_sec,
            "original_shape": self.rgb_original.shape,
            "resized_shape": self.rgb_resized.shape,
        }


class FrameExtractor:
    """
    Uniform temporal sampling engine that extracts a representative sequence
    of frames spanning the entire video duration.
    """

    def __init__(
        self,
        num_frames: int = DEFAULT_SAMPLE_FRAMES,
        target_size: Tuple[int, int] = FRAME_TARGET_SIZE
    ):
        self.num_frames = max(MIN_SAMPLE_FRAMES, min(MAX_SAMPLE_FRAMES, num_frames))
        self.target_size = target_size

    def calculate_sampling_indices(self, total_frames: int) -> List[int]:
        """
        Calculates uniform integer frame indices spanning from start to end of video.
        Ensures no duplicate frames and stays strictly within [0, total_frames - 1].
        """
        if total_frames <= 0:
            return [0]

        if total_frames <= self.num_frames:
            # If video has fewer frames than target sample count, sample all available frames
            return list(range(total_frames))

        # Uniform temporal intervals across the entire video duration
        indices = np.linspace(0, total_frames - 1, num=self.num_frames, dtype=int)
        # Deduplicate and maintain order
        unique_indices = sorted(list(set(indices.tolist())))
        return unique_indices

    def extract_frames(self, file_path: str, metadata: dict = None) -> List[FrameSample]:
        """
        Extracts uniformly sampled frames from the target video file.

        Returns:
            List[FrameSample]: Array of extracted frames with timestamps and RGB representations.
        """
        cap = get_video_capture(file_path)

        try:
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = float(cap.get(cv2.CAP_PROP_FPS))
            if fps <= 0:
                fps = 25.0

            if metadata and "total_frames" in metadata:
                total_frames = max(total_frames, metadata["total_frames"])

            target_indices = self.calculate_sampling_indices(total_frames)
            target_set = set(target_indices)

            samples: List[FrameSample] = []
            current_frame_idx = 0

            # Read sequentially or seek to index
            while cap.isOpened() and len(samples) < len(target_indices):
                ret, bgr_frame = cap.read()
                if not ret or bgr_frame is None:
                    break

                if current_frame_idx in target_set:
                    # Timestamp in milliseconds
                    ts_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
                    if ts_ms <= 0:
                        ts_ms = (current_frame_idx / fps) * 1000.0

                    rgb_orig = bgr_to_rgb(bgr_frame)
                    rgb_res = cv2.resize(
                        rgb_orig,
                        self.target_size,
                        interpolation=cv2.INTER_AREA
                    )

                    sample = FrameSample(
                        frame_idx=current_frame_idx,
                        timestamp_ms=ts_ms,
                        rgb_original=rgb_orig,
                        rgb_resized=rgb_res
                    )
                    samples.append(sample)

                current_frame_idx += 1

                # If reached beyond the maximum target index, stop reading
                if current_frame_idx > target_indices[-1]:
                    break

            if not samples:
                raise IOError(f"No valid frames could be decoded from {file_path}")

            return samples

        finally:
            cap.release()
