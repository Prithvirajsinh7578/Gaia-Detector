"""
video_preprocessor.py - Video verification, metadata extraction, and corruption detection.
Step 2 of Video AI Detector Pipeline.
"""

import os
import cv2
from utils.video_utils import validate_file_path, get_video_capture
from utils.constants import MAX_FILE_SIZE_MB


class VideoPreprocessor:
    """
    Validates uploaded video files, extracts detailed structural metadata,
    and checks for decodability and corruption.
    """

    def __init__(self, max_file_size_mb: float = MAX_FILE_SIZE_MB, max_duration_sec: float = 1800.0):
        self.max_file_size_mb = max_file_size_mb
        self.max_duration_sec = max_duration_sec

    def preprocess(self, file_path: str) -> dict:
        """
        Validates file existence, format, and decodability.
        Returns a standardized metadata dictionary.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If file size, format, or duration violates constraints.
            IOError: If the video stream is corrupted or cannot be decoded.
        """
        # 1. Path & basic constraints validation
        valid, msg = validate_file_path(file_path)
        if not valid:
            raise ValueError(msg)

        file_size_bytes = os.path.getsize(file_path)
        file_size_mb = round(file_size_bytes / (1024 * 1024), 2)

        # 2. Open stream with OpenCV
        cap = get_video_capture(file_path)

        try:
            # 3. Read structural video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = float(cap.get(cv2.CAP_PROP_FPS))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fourcc_int = int(cap.get(cv2.CAP_PROP_FOURCC))

            # Decode fourcc string
            fourcc_str = "".join([chr((fourcc_int >> 8 * i) & 0xFF) for i in range(4)]).strip()

            # Handle edge cases / missing metadata
            if fps <= 0 or fps > 240:
                fps = 25.0  # Sensible standard fallback for variable frame rates

            duration_sec = 0.0
            if total_frames > 0 and fps > 0:
                duration_sec = round(total_frames / fps, 2)

            # 4. Corruption probe: Attempt reading the very first frame
            ret, first_frame = cap.read()
            if not ret or first_frame is None:
                raise IOError(f"Video file is corrupted or contains no decodable frames: {file_path}")

            actual_h, actual_w = first_frame.shape[:2]
            if width <= 0 or height <= 0:
                width, height = actual_w, actual_h

            # If total_frames was inaccurate in header, estimate from duration or actual read
            if total_frames <= 0:
                total_frames = max(1, int(duration_sec * fps))

            # Duration check
            if duration_sec > self.max_duration_sec:
                raise ValueError(
                    f"Video duration ({duration_sec}s) exceeds maximum allowed limit of {self.max_duration_sec}s."
                )

            filename = os.path.basename(file_path)
            ext = os.path.splitext(filename)[1].lower()

            return {
                "file_path": file_path,
                "filename": filename,
                "extension": ext,
                "file_size_mb": file_size_mb,
                "width": width,
                "height": height,
                "aspect_ratio": f"{width}:{height}",
                "fps": round(fps, 2),
                "total_frames": total_frames,
                "duration_seconds": duration_sec,
                "codec": fourcc_str or "unknown",
                "is_valid": True,
            }

        finally:
            cap.release()
