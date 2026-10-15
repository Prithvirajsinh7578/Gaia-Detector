"""
hf_video_detector.py - Pretrained Hugging Face Text-to-Video AI Detector.
Integrates gaetanbrison/deepfake-detector-resnet50-t2v-sora-veo2.
Specialized for detecting modern generative text-to-video diffusion and autoregressive outputs.
"""

import os
import time
import cv2
import numpy as np
import torch
import torch.nn as nn
import torchvision.models as models
from torchvision import transforms
from typing import Dict, Any, Optional, List
from huggingface_hub import hf_hub_download

from .base_detector import DetectorResult
from utils.video_utils import device as default_device, clear_gpu

# Default repository constants
HF_MODEL_REPO = "gaetanbrison/deepfake-detector-resnet50-t2v-sora-veo2"
HF_WEIGHTS_FILE = "ckpt_best.pt"


class HFVideoDetector:
    """
    Inference engine for gaetanbrison/deepfake-detector-resnet50-t2v-sora-veo2.
    Evaluates frame-level deep visual artifacts from generative models (Sora, Veo2, etc.).
    """

    def __init__(
        self,
        repo_id: str = HF_MODEL_REPO,
        weights_filename: str = HF_WEIGHTS_FILE,
        device: Optional[str] = None,
        default_sample_frames: int = 12
    ):
        self.repo_id = repo_id
        self.weights_filename = weights_filename
        self.device = torch.device(device if device else (default_device if torch.cuda.is_available() else "cpu"))
        self.default_sample_frames = default_sample_frames
        self.model: Optional[nn.Module] = None
        self.is_initialized = False
        self.init_error: Optional[str] = None

        # Standard ImageNet normalization expected by ResNet50 backbone
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        # Initialize model at startup
        self._load_model()

    def _load_model(self):
        """
        Downloads (or loads from HF cache) and instantiates the ResNet-50 architecture.
        Loads once during service startup.
        """
        try:
            print(f"[HF Video Detector] Loading weights from '{self.repo_id}' on {self.device}...")
            ckpt_path = hf_hub_download(
                repo_id=self.repo_id,
                filename=self.weights_filename
            )

            state = torch.load(ckpt_path, map_location="cpu", weights_only=False)

            # Build ResNet50 with 2-class binary head (0: Real, 1: AI-generated)
            model = models.resnet50(weights=None)
            model.fc = nn.Linear(2048, 2)

            raw_state = state.get("model", state)
            clean_state = {
                k.replace("backbone.", ""): v
                for k, v in raw_state.items()
            }
            model.load_state_dict(clean_state)
            model.to(self.device)
            model.eval()

            for param in model.parameters():
                param.requires_grad = False

            self.model = model
            self.is_initialized = True
            print("[HF Video Detector] Model successfully loaded and warmed up.")

        except Exception as e:
            self.is_initialized = False
            self.init_error = f"Failed to load HF model: {str(e)}"
            print(f"[HF Video Detector] Notice: {self.init_error}")

    def _sample_frames_from_video(
        self,
        video_path: str,
        num_frames: int
    ) -> List[np.ndarray]:
        """
        Uniformly extracts RGB frames (resized to 224x224) across the video timeline.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video stream from {video_path}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            cap.release()
            raise ValueError("Video contains zero readable frames.")

        num_samples = min(num_frames, total_frames)
        indices = np.linspace(0, total_frames - 1, num_samples, dtype=int)
        frames_224 = []

        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
            ret, frame = cap.read()
            if ret and frame is not None:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb_resized = cv2.resize(rgb, (224, 224), interpolation=cv2.INTER_AREA)
                frames_224.append(rgb_resized)

        cap.release()
        return frames_224

    def predict(
        self,
        video_path: str,
        num_frames: Optional[int] = None,
        preloaded_frames_224: Optional[List[np.ndarray]] = None
    ) -> DetectorResult:
        """
        Executes multi-frame inference using the pretrained ResNet-50 model.
        Aggregates frame probabilities into a robust video-level score.
        """
        start_time = time.time()

        if not self.is_initialized or self.model is None:
            return DetectorResult(
                detector_id="hf_resnet50_t2v",
                name="HF Pretrained ResNet50 (Sora/Veo2 T2V)",
                category="deep_visual_t2v",
                status="failed",
                ai_probability=50.0,
                raw_score=0.5,
                verdict="Inconclusive",
                confidence="None",
                latency_ms=0.0,
                frames_analyzed=0,
                version=HF_MODEL_REPO,
                details={},
                error=self.init_error or "Model is not initialized."
            )

        if not os.path.exists(video_path) and not preloaded_frames_224:
            return DetectorResult(
                detector_id="hf_resnet50_t2v",
                name="HF Pretrained ResNet50 (Sora/Veo2 T2V)",
                category="deep_visual_t2v",
                status="failed",
                ai_probability=50.0,
                raw_score=0.5,
                verdict="Inconclusive",
                confidence="None",
                latency_ms=0.0,
                frames_analyzed=0,
                version=HF_MODEL_REPO,
                details={},
                error=f"Video file not found: {video_path}"
            )

        try:
            # 1. Obtain uniform frames (224x224 RGB)
            target_num_frames = num_frames or self.default_sample_frames
            if preloaded_frames_224:
                frames_224 = preloaded_frames_224
            else:
                frames_224 = self._sample_frames_from_video(video_path, target_num_frames)

            if not frames_224:
                raise ValueError("No frames could be extracted from the video.")

            # 2. Batch Tensor Transformation
            tensor_list = [self.transform(f) for f in frames_224]
            batch_tensor = torch.stack(tensor_list).to(self.device)

            # 3. Model Forward Pass
            with torch.no_grad():
                logits = self.model(batch_tensor)  # (N, 2)
                # Class 1 = AI-generated, Class 0 = Real
                probs = torch.softmax(logits, dim=-1)[:, 1].cpu().numpy()

            del batch_tensor, logits
            clear_gpu()

            # 4. Robust Frame Aggregation (Median & Trimmed Mean)
            # Avoids single-frame outlier dominance
            frame_probs = [float(p) for p in probs]
            median_score = float(np.median(frame_probs))
            mean_score = float(np.mean(frame_probs))
            std_score = float(np.std(frame_probs))
            max_score = float(np.max(frame_probs))
            min_score = float(np.min(frame_probs))

            # Aggregated video AI score: 60% median (outlier rejection) + 40% mean
            video_raw_score = 0.60 * median_score + 0.40 * mean_score
            video_raw_score = max(0.0, min(1.0, video_raw_score))
            ai_prob_pct = round(video_raw_score * 100.0, 1)

            # 5. Decision Policy & Confidence Assessment
            if video_raw_score >= 0.58:
                verdict = "Likely AI-generated"
                if video_raw_score >= 0.85:
                    confidence = "High"
                elif video_raw_score >= 0.65:
                    confidence = "Medium"
                else:
                    confidence = "Low"
            elif video_raw_score <= 0.42:
                verdict = "Likely authentic"
                if video_raw_score <= 0.15:
                    confidence = "High"
                elif video_raw_score <= 0.35:
                    confidence = "Medium"
                else:
                    confidence = "Low"
            else:
                verdict = "Inconclusive"
                confidence = "Low"

            duration_ms = round((time.time() - start_time) * 1000.0, 2)

            return DetectorResult(
                detector_id="hf_resnet50_t2v",
                name="HF Pretrained ResNet50 (Sora/Veo2 T2V)",
                category="deep_visual_t2v",
                status="success",
                ai_probability=ai_prob_pct,
                raw_score=round(video_raw_score, 4),
                verdict=verdict,
                confidence=confidence,
                latency_ms=duration_ms,
                frames_analyzed=len(frames_224),
                version=self.repo_id,
                details={
                    "frame_probabilities": [round(p, 4) for p in frame_probs],
                    "median_score": round(median_score, 4),
                    "mean_score": round(mean_score, 4),
                    "dispersion_std": round(std_score, 4),
                    "min_frame_score": round(min_score, 4),
                    "max_frame_score": round(max_score, 4),
                    "hardware_device": str(self.device),
                    "specialization": "T2V generative artifacts (Sora, Veo2, etc.)"
                },
                error=None
            )

        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000.0, 2)
            clear_gpu()
            return DetectorResult(
                detector_id="hf_resnet50_t2v",
                name="HF Pretrained ResNet50 (Sora/Veo2 T2V)",
                category="deep_visual_t2v",
                status="failed",
                ai_probability=50.0,
                raw_score=0.5,
                verdict="Inconclusive",
                confidence="None",
                latency_ms=duration_ms,
                frames_analyzed=0,
                version=self.repo_id,
                details={},
                error=f"HF Video Detector inference error: {str(e)}"
            )
