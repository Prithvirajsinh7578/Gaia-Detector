"""
test_image_detector.py - Automated unit and integration tests for Gaia Image Detection System.
Tests safe decoding, error handling, individual adapters, ensemble logic, and schema compliance.
"""

import io
import pytest
import numpy as np
from PIL import Image

from detector.image_detector.detectors.base_image_detector import ImageDetectorResult
from detector.image_detector.detectors.custom_image_adapter import CustomImageDetectorAdapter
from detector.image_detector.detectors.hf_image_detector import HFImageDetectorAdapter
from detector.image_detector.detectors.complementary_image_detector import ComplementaryImageDetectorAdapter
from detector.image_detector.ensemble import ImageEnsembleDetector, extract_visual_forensic_features


@pytest.fixture
def sample_pil_image():
    """Generates a synthetic test image."""
    arr = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
    return Image.fromarray(arr)


@pytest.fixture
def blank_image():
    """Generates a solid color image."""
    return Image.new("RGB", (224, 224), color=(128, 128, 128))


def test_visual_forensic_features(sample_pil_image):
    """Verifies that quantitative forensic feature extraction returns expected numeric keys."""
    features = extract_visual_forensic_features(sample_pil_image)
    assert isinstance(features, dict)
    assert "Sharpness Score" in features
    assert "High-Freq Energy %" in features
    assert "Texture Entropy" in features
    assert "Global Contrast" in features
    assert all(isinstance(v, (int, float)) for v in features.values())


def test_custom_adapter_initialization():
    """Verifies that CustomImageDetectorAdapter initializes with standardized attributes."""
    adapter = CustomImageDetectorAdapter()
    assert adapter.detector_id == "gaia_custom_image"
    assert "EfficientNet" in adapter.model_name
    assert adapter._category == "custom_cnn"


def test_custom_adapter_prediction(sample_pil_image):
    """Verifies custom adapter inference returns a compliant ImageDetectorResult."""
    adapter = CustomImageDetectorAdapter()
    res = adapter.predict(sample_pil_image)
    assert isinstance(res, ImageDetectorResult)
    assert 0.0 <= res.ai_probability <= 100.0
    assert 0.0 <= res.authentic_probability <= 100.0
    assert res.verdict in ["Likely AI-generated", "Likely Authentic", "Inconclusive"]
    assert res.status in ["success", "error", "unconfigured"]


def test_hf_adapter_prediction(sample_pil_image):
    """Verifies Model 2 (Swin Transformer) returns compliant schema."""
    adapter = HFImageDetectorAdapter()
    res = adapter.predict(sample_pil_image)
    assert isinstance(res, ImageDetectorResult)
    assert 0.0 <= res.ai_probability <= 100.0
    assert res.status in ["success", "error"]


def test_complementary_adapter_prediction(sample_pil_image):
    """Verifies Model 3 (SigLIP / API) returns compliant schema."""
    adapter = ComplementaryImageDetectorAdapter()
    res = adapter.predict(sample_pil_image)
    assert isinstance(res, ImageDetectorResult)
    assert 0.0 <= res.ai_probability <= 100.0
    assert res.status in ["success", "error"]


def test_ensemble_prediction_structure(sample_pil_image):
    """Verifies complete ensemble returns expected Gaia backend dictionary."""
    ensemble = ImageEnsembleDetector()
    res = ensemble.predict(sample_pil_image)

    assert res["content_type"] == "image"
    assert res["prediction"] in ["LIKELY_AI_GENERATED", "LIKELY_AUTHENTIC", "INCONCLUSIVE"]
    assert "confidence" in res
    assert "processing_time_sec" in res
    assert "summary" in res
    assert "evidence" in res
    assert "details" in res
    assert "consensus" in res["details"]
    assert "individual_detectors" in res["details"]
    assert "features" in res["details"]

    # Check individual detectors presence
    ind = res["details"]["individual_detectors"]
    assert "model_1_custom" in ind
    assert "model_2_hf_swin" in ind
    assert "model_3_complementary" in ind


def test_inconclusive_handling_on_divergence(monkeypatch, sample_pil_image):
    """Verifies that high model discrepancy (>45%) correctly triggers INCONCLUSIVE classification."""
    ensemble = ImageEnsembleDetector()

    # Mock Model 1 to return 95% AI, and Model 2 to return 5% AI (divergence = 90%)
    mock_res_1 = ImageDetectorResult(
        detector_id="gaia_custom_image",
        model_name="Custom",
        category="custom_cnn",
        status="success",
        ai_probability=95.0,
        authentic_probability=5.0,
        verdict="Likely AI-generated",
        confidence="High",
        latency_ms=10.0
    )
    mock_res_2 = ImageDetectorResult(
        detector_id="hf_swin_detector",
        model_name="Swin",
        category="pretrained_transformer",
        status="success",
        ai_probability=5.0,
        authentic_probability=95.0,
        verdict="Likely Authentic",
        confidence="High",
        latency_ms=10.0
    )

    monkeypatch.setattr(ensemble.model_1, "predict", lambda img: mock_res_1)
    monkeypatch.setattr(ensemble.model_2, "predict", lambda img: mock_res_2)

    res = ensemble.predict(sample_pil_image)
    assert res["prediction"] == "INCONCLUSIVE"
    assert res["details"]["consensus"]["agreement"] == "Conflicting Evidence"
    assert res["details"]["consensus"]["discrepancy"] >= 45.0
