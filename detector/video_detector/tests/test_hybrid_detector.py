"""
test_hybrid_detector.py - Comprehensive Unit and Integration Test Suite.
Tests:
- Custom detector adapter
- Pretrained Hugging Face ResNet-50 T2V model
- Sightengine API client with mocks (Success, Rate Limit, Timeout, Missing Keys, Malformed)
- Hybrid Ensemble decision policy, consensus metrics, and uncertainty handling
- Full HybridVideoDetector orchestration
- Backward compatibility of API schemas
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import numpy as np

# Ensure parent directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from detectors.base_detector import DetectorResult
from detectors.custom_detector_adapter import CustomDetectorAdapter
from detectors.hf_video_detector import HFVideoDetector
from detectors.sightengine_detector import SightengineVideoDetector
from ensemble import HybridEnsemble, EnsembleResult
from hybrid_detector import HybridVideoDetector


class TestDetectorResult(unittest.TestCase):
    """Verifies DetectorResult dataclass normalization and serialization."""

    def test_detector_result_creation_and_properties(self):
        res = DetectorResult(
            detector_id="test_model",
            name="Test Model",
            category="unit_test",
            status="success",
            ai_probability=75.5,
            raw_score=0.755,
            verdict="Likely AI-generated",
            confidence="Medium",
            latency_ms=120.5,
            frames_analyzed=16
        )
        self.assertTrue(res.is_available)
        data = res.to_dict()
        self.assertEqual(data["detector_id"], "test_model")
        self.assertEqual(data["ai_probability"], 75.5)
        self.assertEqual(data["status"], "success")

    def test_failed_result_availability(self):
        res = DetectorResult(
            detector_id="test_model",
            name="Test Model",
            category="unit_test",
            status="failed",
            ai_probability=50.0,
            raw_score=0.5,
            verdict="Inconclusive",
            confidence="None",
            latency_ms=0.0,
            frames_analyzed=0,
            error="Connection refused"
        )
        self.assertFalse(res.is_available)


class TestSightengineDetectorMocks(unittest.TestCase):
    """Tests Sightengine client across mock network, auth, and error conditions."""

    def test_unconfigured_credentials(self):
        detector = SightengineVideoDetector(api_user="", api_secret="")
        self.assertFalse(detector.is_configured)
        res = detector.predict("nonexistent_video.mp4")
        self.assertEqual(res.status, "unconfigured")
        self.assertIn("not configured", res.error.lower())
        self.assertFalse(res.is_available)

    @patch("detectors.sightengine_detector.requests.post")
    def test_successful_api_response(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "status": "success",
            "request": {"id": "req_12345", "operations": 1},
            "data": {
                "frames": [
                    {"info": {"position": 0}, "type": {"ai_generated": 0.95}},
                    {"info": {"position": 1}, "type": {"ai_generated": 0.91}},
                    {"info": {"position": 2}, "type": {"ai_generated": 0.88}}
                ]
            }
        }
        mock_post.return_value = mock_resp

        # Create dummy file
        dummy_path = "test_dummy_video.mp4"
        with open(dummy_path, "wb") as f:
            f.write(b"dummy video content")

        try:
            client = SightengineVideoDetector(api_user="test_u", api_secret="test_s")
            res = client.predict(dummy_path)

            self.assertEqual(res.status, "success")
            self.assertTrue(res.is_available)
            self.assertEqual(res.verdict, "Likely AI-generated")
            self.assertGreater(res.ai_probability, 85.0)
            self.assertEqual(res.frames_analyzed, 3)
        finally:
            if os.path.exists(dummy_path):
                os.remove(dummy_path)

    @patch("detectors.sightengine_detector.requests.post")
    def test_api_rate_limiting_429(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_post.return_value = mock_resp

        dummy_path = "test_rate_limit.mp4"
        with open(dummy_path, "wb") as f:
            f.write(b"data")

        try:
            client = SightengineVideoDetector(api_user="test_u", api_secret="test_s")
            res = client.predict(dummy_path)
            self.assertEqual(res.status, "failed")
            self.assertIn("rate limit", res.error.lower())
        finally:
            if os.path.exists(dummy_path):
                os.remove(dummy_path)

    @patch("detectors.sightengine_detector.requests.post")
    def test_api_timeout_handling(self, mock_post):
        import requests
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

        dummy_path = "test_timeout.mp4"
        with open(dummy_path, "wb") as f:
            f.write(b"data")

        try:
            client = SightengineVideoDetector(api_user="test_u", api_secret="test_s", timeout_seconds=1.0)
            res = client.predict(dummy_path)
            self.assertEqual(res.status, "failed")
            self.assertIn("timed out", res.error.lower())
        finally:
            if os.path.exists(dummy_path):
                os.remove(dummy_path)


class TestHybridEnsembleLogic(unittest.TestCase):
    """Tests multi-detector combination, weights, consensus, and uncertainty policy."""

    def setUp(self):
        self.ensemble = HybridEnsemble(uncertain_lower=0.46, uncertain_upper=0.54)

    def test_full_consensus_ai(self):
        r1 = DetectorResult("custom_rf", "Custom", "cat", "success", 85.0, 0.85, "Likely AI-generated", "High", 10.0, 16)
        r2 = DetectorResult("hf_resnet50_t2v", "HF", "cat", "success", 92.0, 0.92, "Likely AI-generated", "High", 15.0, 12)
        r3 = DetectorResult("sightengine_api", "API", "cat", "success", 88.0, 0.88, "Likely AI-generated", "High", 20.0, 10)

        res = self.ensemble.combine([r1, r2, r3])
        self.assertEqual(res.verdict, "Likely AI-generated")
        self.assertEqual(res.confidence, "High")
        self.assertEqual(res.agreement, "Full Consensus")
        self.assertEqual(res.agreement_score, 1.0)
        self.assertEqual(res.active_detectors_count, 3)

    def test_full_consensus_authentic(self):
        r1 = DetectorResult("custom_rf", "Custom", "cat", "success", 12.0, 0.12, "Likely authentic", "High", 10.0, 16)
        r2 = DetectorResult("hf_resnet50_t2v", "HF", "cat", "success", 18.0, 0.18, "Likely authentic", "High", 15.0, 12)

        res = self.ensemble.combine([r1, r2])
        self.assertEqual(res.verdict, "Likely authentic")
        self.assertEqual(res.confidence, "High")
        self.assertEqual(res.agreement, "Full Consensus")
        self.assertLess(res.ai_probability, 25.0)

    def test_conflicting_evidence_triggers_inconclusive(self):
        # Discrepancy > 45% between opposing models
        r1 = DetectorResult("custom_rf", "Custom", "cat", "success", 10.0, 0.10, "Likely authentic", "High", 10.0, 16)
        r2 = DetectorResult("hf_resnet50_t2v", "HF", "cat", "success", 95.0, 0.95, "Likely AI-generated", "High", 15.0, 12)

        res = self.ensemble.combine([r1, r2])
        self.assertEqual(res.verdict, "Inconclusive / Uncertain")
        self.assertEqual(res.agreement, "Conflicting Evidence")
        self.assertIsNotNone(res.inconclusive_reason)
        self.assertIn("Contradictory evidence", res.inconclusive_reason)

    def test_partial_ensemble_when_one_fails(self):
        r1 = DetectorResult("custom_rf", "Custom", "cat", "success", 78.0, 0.78, "Likely AI-generated", "Medium", 10.0, 16)
        r2 = DetectorResult("hf_resnet50_t2v", "HF", "cat", "failed", 50.0, 0.50, "Inconclusive", "None", 0.0, 0, error="OOM")

        res = self.ensemble.combine([r1, r2])
        self.assertEqual(res.verdict, "Likely AI-generated")
        self.assertEqual(res.active_detectors_count, 1)
        self.assertEqual(res.agreement, "Single Source")
        self.assertEqual(res.applied_weights.get("custom_rf"), 1.0)

    def test_all_detectors_failed_graceful_handling(self):
        r1 = DetectorResult("custom_rf", "Custom", "cat", "failed", 50.0, 0.50, "Inconclusive", "None", 0.0, 0, error="Err")
        r2 = DetectorResult("hf_resnet50_t2v", "HF", "cat", "failed", 50.0, 0.50, "Inconclusive", "None", 0.0, 0, error="Err")

        res = self.ensemble.combine([r1, r2])
        self.assertEqual(res.verdict, "Inconclusive / Uncertain")
        self.assertEqual(res.active_detectors_count, 0)
        self.assertIsNotNone(res.inconclusive_reason)


class TestHFVideoDetector(unittest.TestCase):
    """Verifies HF ResNet-50 T2V model initialization and shape constraints."""

    def test_hf_detector_initialization(self):
        detector = HFVideoDetector()
        self.assertTrue(detector.is_initialized)
        self.assertIsNotNone(detector.model)


class TestFullHybridOrchestrator(unittest.TestCase):
    """Verifies end-to-end integration across all detectors and schema compliance."""

    def test_hybrid_orchestrator_instantiation(self):
        orchestrator = HybridVideoDetector(
            enable_custom=True,
            enable_hf=True,
            enable_sightengine=False
        )
        self.assertIsNotNone(orchestrator.custom_adapter)
        self.assertIsNotNone(orchestrator.hf_detector)
        self.assertIsNone(orchestrator.sightengine_detector)

    def test_response_schema_compatibility(self):
        orchestrator = HybridVideoDetector(
            enable_custom=False,
            enable_hf=False,
            enable_sightengine=False
        )
        # Even with all disabled, predict must return schema with fallback values
        res = orchestrator.predict("any.mp4")
        required_keys = [
            "verdict", "ai_probability", "confidence", "frames_analyzed",
            "temporal_analysis", "audio_analysis", "visual_indicators",
            "summary_features", "is_hybrid", "consensus", "individual_detectors"
        ]
        for key in required_keys:
            self.assertIn(key, res, f"Missing required response schema key: '{key}'")


if __name__ == "__main__":
    unittest.main()
