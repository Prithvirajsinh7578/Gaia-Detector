"""
test_hybrid_text_detector.py - Comprehensive Unit and Integration Test Suite.
Verifies:
- Custom 18-feature Random Forest model preservation
- Hugging Face RoBERTa tokenizer, chunking, and label mapping
- GPTZero commercial API client (mocked: success, auth error, rate limit, timeout, unconfigured)
- Hybrid multi-model ensemble weighting, consensus, and conflict policies
- FastAPI endpoint contracts and backward compatibility
"""

import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
os.environ["OPENBLAS_NUM_THREADS"] = "2"

import sys
import unittest
from unittest.mock import patch, MagicMock

# Ensure detector root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from detectors.base_detector import DetectorResult
from detectors.custom_text_adapter import CustomTextAdapter
from detectors.hf_text_detector import HFTextDetector
from detectors.gptzero_detector import GPTZeroTextDetector
from ensemble import HybridTextEnsemble, EnsembleResult
from utils.constants import FEATURE_NAMES


class TestHybridTextDetector(unittest.TestCase):
    """Test suite covering all components of the hybrid text detection architecture."""

    def setUp(self):
        self.sample_text = (
            "Artificial intelligence is transforming education by enabling personalized learning "
            "experiences. Modern generative language models generate coherent academic text, "
            "requiring robust statistical and stylometric evaluation to verify authenticity."
        )

    # 1. Custom Model Adapter & 18 Features
    def test_custom_detector_adapter(self):
        adapter = CustomTextAdapter()
        res = adapter.predict(self.sample_text)

        self.assertIsInstance(res, DetectorResult)
        self.assertEqual(res.detector_id, "custom_rf")
        self.assertEqual(res.status, "success")
        self.assertTrue(0.0 <= res.ai_probability <= 100.0)
        self.assertIn(res.verdict, ["Likely AI-generated", "Likely Human-written", "Possibly AI-generated", "Inconclusive / Uncertain"])

        # Verify all 18 features are preserved in metadata
        detailed_feats = res.metadata.get("detailed_features", {})
        for name in FEATURE_NAMES:
            self.assertIn(name, detailed_feats, f"Missing feature '{name}' from custom extraction!")

    def test_custom_feature_schema(self):
        self.assertEqual(len(FEATURE_NAMES), 18)
        self.assertEqual(FEATURE_NAMES[0], "perplexity")
        self.assertEqual(FEATURE_NAMES[1], "burstiness")
        self.assertEqual(FEATURE_NAMES[-1], "exclamation_ratio")

    def test_empty_and_short_text_handling(self):
        adapter = CustomTextAdapter()
        empty_res = adapter.predict("")
        self.assertEqual(empty_res.status, "skipped")
        self.assertEqual(empty_res.verdict, "Invalid / Empty Input")

    # 2. Pretrained Hugging Face RoBERTa
    def test_hf_detector_label_mapping(self):
        detector = HFTextDetector()
        # Verify AI class index is 0 ('Fake') and Human is 1 ('Real') for roberta-base-openai-detector
        self.assertEqual(detector.ai_class_index, 0)
        self.assertEqual(detector.human_class_index, 1)

    def test_hf_detector_chunking_logic(self):
        detector = HFTextDetector()
        if detector.tokenizer:
            # Generate a document with 1200 words (~1500 tokens) to trigger multi-chunk windowing
            long_doc = "Artificial intelligence and statistical modeling. " * 300
            chunks = detector._chunk_text(long_doc)
            self.assertGreater(len(chunks), 1)
            for c in chunks:
                self.assertLessEqual(c["token_count"], 512)

    # 3. GPTZero Commercial API Client (Mocked)
    def test_gptzero_unconfigured(self):
        # Empty API key
        detector = GPTZeroTextDetector(api_key="")
        res = detector.predict(self.sample_text)
        self.assertEqual(res.status, "unconfigured")
        self.assertEqual(res.verdict, "Inconclusive / Uncertain")

    @patch("requests.post")
    def test_gptzero_success_parsing(self, mock_post):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "documents": [
                {
                    "completely_generated_prob": 0.88,
                    "overall_burstiness": 0.32,
                    "predicted_class": "ai",
                    "confidence_category": "high",
                    "sentences": [{"sentence": "Test sentence", "perplexity": 15.2}]
                }
            ]
        }
        mock_post.return_value = mock_response

        detector = GPTZeroTextDetector(api_key="mock_test_key_12345")
        # Ensure text is >= 250 characters
        long_sample = self.sample_text + " Extra padding text to exceed the 250 character limit for GPTZero analysis."
        res = detector.predict(long_sample)

        self.assertEqual(res.status, "success")
        self.assertEqual(res.ai_probability, 88.0)
        self.assertEqual(res.verdict, "Likely AI-generated")
        self.assertEqual(res.confidence, "High")

    @patch("requests.post")
    def test_gptzero_auth_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.text = "Invalid API key"
        mock_post.return_value = mock_response

        detector = GPTZeroTextDetector(api_key="invalid_key")
        long_sample = self.sample_text + " Extra padding text to exceed the 250 character limit."
        res = detector.predict(long_sample)

        self.assertEqual(res.status, "failed")
        self.assertIn("authentication failed", res.error_message.lower())

    @patch("requests.post")
    def test_gptzero_rate_limit(self, mock_post):
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 429
        mock_response.text = "Rate limit reached"
        mock_post.return_value = mock_response

        detector = GPTZeroTextDetector(api_key="mock_key")
        long_sample = self.sample_text + " Extra padding text to exceed the 250 character limit."
        res = detector.predict(long_sample)

        self.assertEqual(res.status, "failed")
        self.assertIn("rate limit", res.error_message.lower())

    @patch("requests.post")
    def test_gptzero_timeout(self, mock_post):
        import requests
        mock_post.side_effect = requests.exceptions.Timeout("Read timeout")

        detector = GPTZeroTextDetector(api_key="mock_key")
        long_sample = self.sample_text + " Extra padding text to exceed the 250 character limit."
        res = detector.predict(long_sample)

        self.assertEqual(res.status, "failed")
        self.assertIn("timed out", res.error_message.lower())

    # 4. Ensemble Combination & Decision Policies
    def test_ensemble_all_three_detectors(self):
        ensemble = HybridTextEnsemble()
        r1 = DetectorResult("custom_rf", "Custom RF", "custom_model", "success", 85.0, 0.85)
        r2 = DetectorResult("hf_roberta", "HF RoBERTa", "pretrained_hf", "success", 80.0, 0.80)
        r3 = DetectorResult("gptzero_api", "GPTZero API", "commercial_api", "success", 90.0, 0.90)

        res = ensemble.combine([r1, r2, r3])
        self.assertIsInstance(res, EnsembleResult)
        # Expected: 85*0.35 + 80*0.35 + 90*0.30 = 29.75 + 28.0 + 27.0 = 84.75%
        self.assertAlmostEqual(res.ai_probability, 84.8, places=1)
        self.assertEqual(res.verdict, "Likely AI-generated")
        self.assertEqual(res.consensus_status, "Full Consensus")
        self.assertIsNone(res.inconclusive_reason)

    def test_ensemble_conflict_triggers_inconclusive(self):
        ensemble = HybridTextEnsemble()
        # Model 1 says 10% (Human), Model 2 says 90% (AI) -> Discrepancy = 80% (>= 45% threshold)
        r1 = DetectorResult("custom_rf", "Custom RF", "custom_model", "success", 10.0, 0.10)
        r2 = DetectorResult("hf_roberta", "HF RoBERTa", "pretrained_hf", "success", 90.0, 0.90)

        res = ensemble.combine([r1, r2])
        self.assertEqual(res.verdict, "Inconclusive / Uncertain")
        self.assertEqual(res.consensus_status, "Conflicting Evidence")
        self.assertIsNotNone(res.inconclusive_reason)
        self.assertIn("Conflicting Evidence", res.inconclusive_reason)

    def test_ensemble_single_detector_fallback(self):
        ensemble = HybridTextEnsemble()
        r1 = DetectorResult("custom_rf", "Custom RF", "custom_model", "success", 20.0, 0.20)
        r2 = DetectorResult("hf_roberta", "HF RoBERTa", "pretrained_hf", "failed", 50.0, 0.50)
        r3 = DetectorResult("gptzero_api", "GPTZero API", "commercial_api", "unconfigured", 50.0, 0.50)

        res = ensemble.combine([r1, r2, r3])
        # Only custom_rf is active, weight must re-normalize to 1.0 (100%)
        self.assertEqual(res.ai_probability, 20.0)
        self.assertEqual(res.verdict, "Likely Human-written")
        self.assertEqual(res.consensus_status, "Single Source")
        self.assertEqual(res.weights_used.get("custom_rf"), 1.0)

    # 5. Backward Compatibility & Endpoints
    def test_api_compatibility_schema(self):
        from hybrid_detector import HybridTextDetector
        detector = HybridTextDetector(enable_custom=True, enable_hf=False, enable_gptzero=False)
        result = detector.predict(self.sample_text)

        # Existing response keys must be present
        self.assertIn("probability", result)
        self.assertIn("confidence", result)
        self.assertIn("verdict", result)
        self.assertIn("features", result)
        self.assertIn("detailed_features", result)
        self.assertIn("indicators", result)

        # Upgraded hybrid keys must be present
        self.assertTrue(result.get("hybrid_pipeline"))
        self.assertIn("consensus", result)
        self.assertIn("individual_detectors", result)


if __name__ == "__main__":
    unittest.main()
