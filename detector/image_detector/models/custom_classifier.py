"""
custom_classifier.py - Model 1: Custom Deep Transfer-Learning Image Classifier for Gaia Detector.
Based on EfficientNet-B0 with custom binary forensic classification head.
"""

import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights


class GaiaImageClassifier(nn.Module):
    """
    Custom transfer-learning classifier for Gaia Detector.
    Uses an EfficientNet-B0 backbone fine-tuned for generative artifact identification.
    """

    def __init__(self, pretrained: bool = True, dropout_rate: float = 0.3):
        super().__init__()
        weights = EfficientNet_B0_Weights.DEFAULT if pretrained else None
        self.backbone = efficientnet_b0(weights=weights)

        # In EfficientNet, classifier is Sequential(Dropout, Linear(1280, 1000))
        in_features = self.backbone.classifier[1].in_features

        # Replace classification head with specialized forensic layers
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=dropout_rate),
            nn.Linear(in_features, 256),
            nn.SiLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(p=dropout_rate * 0.7),
            nn.Linear(256, 1)  # Binary logit: positive = AI-generated, negative = Authentic
        )

        # Temperature parameter for post-hoc probability calibration
        self.temperature = nn.Parameter(torch.ones(1), requires_grad=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Outputs raw binary logit (shape: [batch_size, 1])."""
        return self.backbone(x)

    def predict_proba(self, x: torch.Tensor) -> torch.Tensor:
        """Outputs calibrated probability of being AI-generated (0.0 to 1.0)."""
        logits = self.forward(x)
        calibrated_logits = logits / self.temperature
        return torch.sigmoid(calibrated_logits).squeeze(-1)

    def set_temperature(self, temp: float):
        """Sets temperature scaling factor for probability calibration."""
        with torch.no_grad():
            self.temperature.copy_(torch.tensor([max(0.01, temp)]))
