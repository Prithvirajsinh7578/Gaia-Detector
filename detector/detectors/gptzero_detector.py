"""
gptzero_detector.py - Official GPTZero AI Text Detection API Client.
Integrates GPTZero's commercial enterprise API (v2 endpoint) as an independent external evidence stream.
"""

import os
import time
import requests
from typing import Dict, Any, Optional, List
from pathlib import Path
from .base_detector import BaseTextDetector, DetectorResult

try:
    from dotenv import load_dotenv
    _env_local = Path(__file__).resolve().parent.parent / ".env"
    if _env_local.exists():
        load_dotenv(_env_local)
    else:
        load_dotenv()
except ImportError:
    pass

GPTZERO_ENDPOINT = "https://api.gptzero.me/v2/predict/text"
DEFAULT_TIMEOUT_SEC = 25.0


class GPTZeroTextDetector(BaseTextDetector):
    """
    Dedicated client for GPTZero API v2.
    Handles authentication, error handling, rate limits, schema validation, and score normalization.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: str = GPTZERO_ENDPOINT,
        timeout_seconds: float = DEFAULT_TIMEOUT_SEC
    ):
        self.detector_id = "gptzero_api"
        self.name = "GPTZero Commercial AI Text API"
        self.category = "commercial_api"
        self.api_key = (api_key if api_key is not None else os.getenv("GPTZERO_API_KEY", "")).strip()
        self.endpoint = endpoint
        self.timeout = timeout_seconds

    @property
    def is_configured(self) -> bool:
        """Checks if GPTZero API key is present."""
        return bool(self.api_key)

    def predict(self, text: str, timeout: Optional[float] = None) -> DetectorResult:
        start_time = time.time()
        effective_timeout = timeout or self.timeout

        # 1. Validation for empty text
        if not text or not text.strip():
            return DetectorResult(
                detector_id=self.detector_id,
                name=self.name,
                category=self.category,
                status="skipped",
                ai_probability=0.0,
                human_probability=100.0,
                raw_score=0.0,
                verdict="Invalid / Empty Input",
                confidence="None",
                latency_ms=0.0,
                analyzed_chars=0,
                error_message="Input text was empty."
            )

        # 2. Configuration Guard
        if not self.is_configured:
            return DetectorResult(
                detector_id=self.detector_id,
                name=self.name,
                category=self.category,
                status="unconfigured",
                ai_probability=50.0,
                human_probability=50.0,
                raw_score=0.5,
                verdict="Inconclusive / Uncertain",
                confidence="None",
                latency_ms=0.0,
                analyzed_chars=len(text),
                error_message="GPTZero API key (GPTZERO_API_KEY) is not configured in environment."
            )

        # 3. Minimum text restriction check (GPTZero requires >= 250 characters or ~50 words)
        if len(text.strip()) < 250:
            return DetectorResult(
                detector_id=self.detector_id,
                name=self.name,
                category=self.category,
                status="skipped",
                ai_probability=50.0,
                human_probability=50.0,
                raw_score=0.5,
                verdict="Inconclusive / Uncertain",
                confidence="Low",
                latency_ms=0.0,
                analyzed_chars=len(text),
                error_message="Text length is below GPTZero's minimum requirement of 250 characters."
            )

        # 4. HTTP Request to GPTZero API
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {
            "document": text,
            "version": "2024-01-09"
        }

        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=effective_timeout
            )
            latency_ms = (time.time() - start_time) * 1000.0

            # Handle HTTP errors
            if response.status_code == 401 or response.status_code == 403:
                return DetectorResult(
                    detector_id=self.detector_id,
                    name=self.name,
                    category=self.category,
                    status="failed",
                    ai_probability=50.0,
                    human_probability=50.0,
                    raw_score=0.5,
                    verdict="Inconclusive / Uncertain",
                    confidence="None",
                    latency_ms=latency_ms,
                    analyzed_chars=len(text),
                    error_message=f"GPTZero authentication failed (HTTP {response.status_code}). Verify your API key."
                )

            if response.status_code == 429:
                return DetectorResult(
                    detector_id=self.detector_id,
                    name=self.name,
                    category=self.category,
                    status="failed",
                    ai_probability=50.0,
                    human_probability=50.0,
                    raw_score=0.5,
                    verdict="Inconclusive / Uncertain",
                    confidence="None",
                    latency_ms=latency_ms,
                    analyzed_chars=len(text),
                    error_message="GPTZero API rate limit or quota exceeded (HTTP 429)."
                )

            if not response.ok:
                return DetectorResult(
                    detector_id=self.detector_id,
                    name=self.name,
                    category=self.category,
                    status="failed",
                    ai_probability=50.0,
                    human_probability=50.0,
                    raw_score=0.5,
                    verdict="Inconclusive / Uncertain",
                    confidence="None",
                    latency_ms=latency_ms,
                    analyzed_chars=len(text),
                    error_message=f"GPTZero API returned HTTP error {response.status_code}: {response.text[:200]}"
                )

            # Parse and normalize JSON
            data = response.json()
            return self._parse_response(data, latency_ms, len(text))

        except requests.exceptions.Timeout:
            latency_ms = (time.time() - start_time) * 1000.0
            return DetectorResult(
                detector_id=self.detector_id,
                name=self.name,
                category=self.category,
                status="failed",
                ai_probability=50.0,
                human_probability=50.0,
                raw_score=0.5,
                verdict="Inconclusive / Uncertain",
                confidence="None",
                latency_ms=latency_ms,
                analyzed_chars=len(text),
                error_message=f"GPTZero API request timed out after {effective_timeout}s."
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000.0
            return DetectorResult(
                detector_id=self.detector_id,
                name=self.name,
                category=self.category,
                status="failed",
                ai_probability=50.0,
                human_probability=50.0,
                raw_score=0.5,
                verdict="Inconclusive / Uncertain",
                confidence="None",
                latency_ms=latency_ms,
                analyzed_chars=len(text),
                error_message=f"GPTZero client network or parsing error: {str(e)}"
            )

    def _parse_response(self, data: Dict[str, Any], latency_ms: float, char_count: int) -> DetectorResult:
        """Normalizes GPTZero API v2 JSON response into standardized DetectorResult."""
        documents = data.get("documents", [])
        if not documents:
            return DetectorResult(
                detector_id=self.detector_id,
                name=self.name,
                category=self.category,
                status="failed",
                ai_probability=50.0,
                human_probability=50.0,
                raw_score=0.5,
                verdict="Inconclusive / Uncertain",
                confidence="None",
                latency_ms=latency_ms,
                analyzed_chars=char_count,
                error_message="Malformed GPTZero response: 'documents' array is empty."
            )

        doc = documents[0]
        # completely_generated_prob ranges from 0.0 to 1.0
        ai_prob_raw = float(doc.get("completely_generated_prob", 0.5))
        ai_prob_pct = round(ai_prob_raw * 100.0, 1)
        human_prob_pct = round(max(0.0, 100.0 - ai_prob_pct), 1)

        predicted_class = str(doc.get("predicted_class", "unknown")).lower()
        confidence_cat = str(doc.get("confidence_category", "medium")).capitalize()
        if confidence_cat not in {"High", "Medium", "Low"}:
            confidence_cat = "Medium"

        # Determine verdict
        if predicted_class == "ai" or ai_prob_pct >= 65.0:
            verdict = "Likely AI-generated"
        elif predicted_class == "human" or ai_prob_pct <= 35.0:
            verdict = "Likely Human-written"
        elif predicted_class == "mixed":
            verdict = "Possibly AI-generated"
        else:
            verdict = "Inconclusive / Uncertain"

        indicators = []
        if ai_prob_pct >= 70.0:
            indicators.append(f"GPTZero classified content as AI-generated ({ai_prob_pct}% probability)")
        elif ai_prob_pct <= 30.0:
            indicators.append(f"GPTZero classified content as Human-written ({human_prob_pct}% human probability)")
        else:
            indicators.append(f"GPTZero detected mixed authorship or ambiguous perplexity patterns ({ai_prob_pct}%)")

        burstiness = doc.get("overall_burstiness")
        if burstiness is not None:
            indicators.append(f"GPTZero measured document burstiness at {round(float(burstiness), 2)}")

        return DetectorResult(
            detector_id=self.detector_id,
            name=self.name,
            category=self.category,
            status="success",
            ai_probability=ai_prob_pct,
            human_probability=human_prob_pct,
            raw_score=ai_prob_raw,
            is_calibrated=True,
            verdict=verdict,
            confidence=confidence_cat,
            latency_ms=latency_ms,
            analyzed_chars=char_count,
            indicators=indicators,
            metadata={
                "predicted_class": predicted_class,
                "overall_burstiness": burstiness,
                "sentences_count": len(doc.get("sentences", [])),
                "provider": "GPTZero API v2"
            }
        )
