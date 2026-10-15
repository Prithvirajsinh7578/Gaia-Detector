"""
dataset_builder.py - Automated video-to-feature dataset generator and synthetic benchmark synthesizer.
Steps 7 & 8 of Video AI Detector Pipeline.
"""

import os
import time
import argparse
import numpy as np
import pandas as pd
import cv2

from video_preprocessor import VideoPreprocessor
from frame_extractor import FrameExtractor
from feature_extractor import VideoFeatureExtractor
from classifier import VideoClassifier
from utils.constants import (
    RAW_AUTHENTIC_DIR,
    RAW_AI_DIR,
    DATASET_PATH,
    FEATURE_NAMES
)
from utils.video_utils import clear_gpu


def create_sample_video(
    output_path: str,
    is_ai: bool,
    num_frames: int = 40,
    fps: int = 25,
    width: int = 320,
    height: int = 240
):
    """
    Synthesizes a test video file with authentic or synthetic generation signatures.

    Authentic characteristics:
    - Natural high-frequency edge textures and organic motion gradients.
    - Consistent perspective shift and camera motion.

    AI characteristics:
    - Overly smooth local textures, high-frequency spectral attenuation.
    - Temporal flickering, warping, or latent morphing between frames.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Base canvas
    np.random.seed(abs(hash(output_path)) % (2**32))

    # Background texture pattern
    bg = np.random.randint(60, 180, (height, width, 3), dtype=np.uint8)

    for i in range(num_frames):
        frame = bg.copy()
        t = i / float(num_frames)

        if not is_ai:
            # --- AUTHENTIC VIDEO SIGNATURES ---
            # 1. Natural textured noise
            grain = np.random.normal(0, 10, (height, width, 3)).astype(np.int16)
            frame = np.clip(frame.astype(np.int16) + grain, 0, 255).astype(np.uint8)

            # 2. Moving sharp natural object (rigid translation)
            center_x = int(50 + (width - 100) * t)
            center_y = int(height // 2 + 20 * np.sin(2 * np.pi * t))
            cv2.rectangle(frame, (center_x - 30, center_y - 30), (center_x + 30, center_y + 30), (40, 200, 70), -1)
            cv2.circle(frame, (center_x, center_y), 15, (255, 255, 255), 2)
        else:
            # --- AI-GENERATED VIDEO SIGNATURES ---
            # 1. Overly smoothed textures (bilateral / Gaussian blur)
            frame = cv2.GaussianBlur(frame, (9, 9), 0)

            # 2. Latent morphing & inconsistent boundary warping
            warp_radius = int(25 + 15 * np.sin(6 * np.pi * t))  # pulsating/warping shape
            center_x = int(50 + (width - 100) * t)
            center_y = int(height // 2 + 10 * np.cos(4 * np.pi * t))
            cv2.circle(frame, (center_x, center_y), warp_radius, (220, 80, 160), -1)

            # 3. High-frequency flicker artifact
            if i % 3 == 0:
                frame = np.clip(frame.astype(np.float32) * 1.15, 0, 255).astype(np.uint8)

        out.write(frame)

    out.release()


def generate_benchmark_dataset(num_authentic: int = 15, num_ai: int = 15):
    """
    Generates a localized benchmark video library for immediate training and verification.
    """
    print(f"Synthesizing test benchmark: {num_authentic} Authentic + {num_ai} AI videos...")

    for i in range(num_authentic):
        v_path = os.path.join(RAW_AUTHENTIC_DIR, f"authentic_sample_{i+1:03d}.mp4")
        if not os.path.exists(v_path):
            create_sample_video(v_path, is_ai=False, num_frames=35 + (i * 2))

    for i in range(num_ai):
        v_path = os.path.join(RAW_AI_DIR, f"ai_sample_{i+1:03d}.mp4")
        if not os.path.exists(v_path):
            create_sample_video(v_path, is_ai=True, num_frames=35 + (i * 2))

    print(f"Benchmark video dataset ready in '{os.path.dirname(RAW_AUTHENTIC_DIR)}'.")


class VideoDatasetBuilder:
    """
    Batch feature extraction pipeline converting raw labeled videos
    into structured tabular datasets for model training.
    """

    def __init__(
        self,
        output_file: str = DATASET_PATH,
        sample_frames_per_video: int = 16
    ):
        self.output_file = output_file
        self.preprocessor = VideoPreprocessor()
        self.frame_extractor = FrameExtractor(num_frames=sample_frames_per_video)
        self.feature_extractor = VideoFeatureExtractor()

    def process_directory(self, dir_path: str, label: int) -> list:
        """Processes all videos in a directory, extracting features for each valid file."""
        if not os.path.exists(dir_path):
            return []

        rows = []
        video_files = [
            f for f in os.listdir(dir_path)
            if os.path.splitext(f)[1].lower() in {".mp4", ".mov", ".webm", ".avi", ".mkv"}
        ]

        print(f"\nProcessing '{dir_path}' ({len(video_files)} videos, label={label})...")

        for idx, filename in enumerate(video_files, 1):
            file_path = os.path.join(dir_path, filename)
            try:
                # 1. Preprocess & validate
                meta = self.preprocessor.preprocess(file_path)

                # 2. Extract frames
                frames = self.frame_extractor.extract_frames(file_path, meta)

                # 3. Extract features
                feats_dict, vec, _ = self.feature_extractor.extract_features(frames)

                row = {
                    "video_id": filename,
                    **feats_dict,
                    "label": label
                }
                rows.append(row)
                lbl_name = "AI   " if label == 1 else "Human"
                print(f"  [{idx:>3}/{len(video_files)}] Extracted: {filename:<26} | Label: {lbl_name} | Frames: {len(frames)}")

            except Exception as e:
                print(f"  [Warning] Failed to process {filename}: {e}")
                continue

            clear_gpu()

        return rows

    def build_dataset(self, auto_train: bool = True):
        """Constructs full balanced dataset and triggers model training."""
        auth_rows = self.process_directory(RAW_AUTHENTIC_DIR, label=0)
        ai_rows = self.process_directory(RAW_AI_DIR, label=1)

        all_rows = auth_rows + ai_rows
        if not all_rows:
            print("No video features extracted. Please ensure raw video folders contain files.")
            return

        cols = ["video_id"] + FEATURE_NAMES + ["label"]
        df = pd.DataFrame(all_rows)[cols]

        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        df.to_csv(self.output_file, index=False)
        print(f"\nSuccessfully wrote {len(df)} samples to '{self.output_file}'.")

        if auto_train:
            classifier = VideoClassifier()
            classifier.train(self.output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video AI Detector Dataset Builder")
    parser.add_argument("--synthesize", action="store_true", help="Synthesize sample benchmark videos for testing")
    parser.add_argument("--train", action="store_true", help="Automatically train classifier after feature extraction")
    args = parser.parse_args()

    if args.synthesize or (not os.path.exists(RAW_AUTHENTIC_DIR) and not os.path.exists(RAW_AI_DIR)):
        generate_benchmark_dataset(num_authentic=20, num_ai=20)

    builder = VideoDatasetBuilder()
    builder.build_dataset(auto_train=True)
