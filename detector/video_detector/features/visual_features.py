"""
visual_features.py - Spatial handcrafted image statistics and deep visual encoder embeddings.
Step 4 of Video AI Detector Pipeline.
"""

from typing import Dict, Any, List
import cv2
import numpy as np
import torch
import torch.nn as nn
import torchvision.models as models
from torchvision import transforms

from utils.video_utils import device, clear_gpu, rgb_to_gray


class VisualFeatureExtractor:
    """
    Extracts handcrafted visual quality indicators and deep convolutional embeddings
    from video frames.
    """

    def __init__(self, use_deep_encoder: bool = True):
        self.use_deep_encoder = use_deep_encoder
        self.device = device
        self.encoder = None

        if self.use_deep_encoder:
            self._init_encoder()

        # ImageNet normalization transform for deep visual encoder
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def _init_encoder(self):
        """Initializes pretrained MobileNetV3 visual encoder with spatial pooling."""
        try:
            weights = models.MobileNet_V3_Small_Weights.DEFAULT
            base_model = models.mobilenet_v3_small(weights=weights)
            base_model.eval()

            # Sequential feature extractor + global pooling
            self.encoder = nn.Sequential(
                base_model.features,
                nn.AdaptiveAvgPool2d((1, 1)),
                nn.Flatten()
            ).to(self.device)

            for param in self.encoder.parameters():
                param.requires_grad = False

        except Exception as e:
            print(f"Warning: Failed to load deep visual encoder ({e}). Fallback to spatial statistics only.")
            self.encoder = None

    def extract_frame_handcrafted(self, rgb_image: np.ndarray) -> Dict[str, float]:
        """
        Extracts spatial statistical indicators from a single RGB frame:
        - Sharpness (Laplacian variance)
        - Texture contrast & energy
        - Color diversity
        - High-frequency FFT ratio
        - Noise residual
        - Compression blocking artifacts
        """
        gray = rgb_to_gray(rgb_image)
        h, w = gray.shape

        # 1. Sharpness (Laplacian variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = float(laplacian.var())

        # 2. Texture Statistics
        # Local standard deviation filter as texture contrast proxy
        blur_mean = cv2.blur(gray.astype(np.float32), (5, 5))
        blur_sq_mean = cv2.blur((gray.astype(np.float32)) ** 2, (5, 5))
        local_var = np.maximum(0, blur_sq_mean - blur_mean ** 2)
        texture_contrast = float(np.mean(np.sqrt(local_var)))
        # Texture energy (uniformity of intensity)
        hist, _ = np.histogram(gray, bins=32, range=(0, 256), density=True)
        texture_energy = float(np.sum(hist ** 2))

        # 3. Color Diversity (standard deviation across color channels in HSV and RGB)
        hsv = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)
        sat_std = float(np.std(hsv[:, :, 1]))
        val_std = float(np.std(hsv[:, :, 2]))
        color_diversity = float((sat_std + val_std) / 2.0)

        # 4. High-Frequency Spectral Ratio (2D FFT)
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.abs(f_shift)
        total_energy = float(np.sum(magnitude_spectrum) + 1e-6)

        # Mask central low frequencies
        crow, ccol = h // 2, w // 2
        r = min(h, w) // 6
        y, x = np.ogrid[:h, :w]
        mask = (x - ccol) ** 2 + (y - crow) ** 2 > (r ** 2)
        high_freq_energy = float(np.sum(magnitude_spectrum[mask]))
        high_freq_ratio = float(high_freq_energy / total_energy)

        # 5. Noise Residual (Difference from median filtered frame)
        median_filtered = cv2.medianBlur(gray, 3)
        noise_diff = gray.astype(np.float32) - median_filtered.astype(np.float32)
        noise_residual = float(np.std(noise_diff))

        # 6. Compression Blocking Artifacts (Ratio of gradient on 8x8 block boundaries)
        diff_h = np.abs(np.diff(gray.astype(np.float32), axis=0))
        block_edges = diff_h[7::8, :]
        non_block_edges = diff_h[np.mod(np.arange(diff_h.shape[0]), 8) != 7, :]
        blocking_ratio = float(np.mean(block_edges) / (np.mean(non_block_edges) + 1e-5))

        return {
            "sharpness": round(sharpness, 4),
            "texture_contrast": round(texture_contrast, 4),
            "texture_energy": round(texture_energy, 4),
            "color_diversity": round(color_diversity, 4),
            "high_freq_ratio": round(high_freq_ratio, 4),
            "noise_residual": round(noise_residual, 4),
            "compression_blocking": round(blocking_ratio, 4),
        }

    def extract_deep_embeddings(self, rgb_resized_frames: List[np.ndarray]) -> np.ndarray:
        """
        Passes a list of normalized RGB frames (224x224) through the visual encoder.
        Returns a 2D numpy array of shape (num_frames, embedding_dim).
        """
        if self.encoder is None or not rgb_resized_frames:
            # Fallback zero vector if deep encoder is unavailable
            return np.zeros((len(rgb_resized_frames), 576), dtype=np.float32)

        tensor_list = [self.transform(frame) for frame in rgb_resized_frames]
        batch_tensor = torch.stack(tensor_list).to(self.device)

        with torch.no_grad():
            embeddings = self.encoder(batch_tensor)  # (N, 576)
            embeddings_np = embeddings.cpu().numpy()

        del batch_tensor, embeddings
        clear_gpu()

        return embeddings_np
