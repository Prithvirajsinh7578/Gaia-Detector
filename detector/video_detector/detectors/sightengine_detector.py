"""
sightengine_detector.py - Sightengine AI-Generated Video Detection Client.
Integrates Sightengine's commercial GenAI video detection API (models=genai).
Provides independent third-party evidence from multi-generator industrial models.
"""

import os
import time
from pathlib import Path
import requests
import numpy as np
from typing import Dict, Any, Optional, List
from .base_detector import DetectorResult

try:
    from dotenv import load_dotenv
    _env_local = Path(__file__).resolve().parent.parent / ".env"
    if _env_local.exists():
        load_dotenv(_env_local)
    else:
        load_dotenv()
except ImportError:
    pass

SIGHTENGINE_SYNC_ENDPOINT = "https://api.sightengine.com/1.0/video/check-sync.json"
DEFAULT_TIMEOUT_SEC = 45.0


class SightengineVideoDetector:
    """
    Dedicated client for Sightengine's AI-generated video detection service.
    Sends raw video files to the synchronous detection endpoint and standardizes results.
    """

    def __init__(
        self,
        api_user: Optional[str] = None,
        api_secret: Optional[str] = None,
        endpoint: str = SIGHTENGINE_SYNC_ENDPOINT,
        timeout_seconds: float = DEFAULT_TIMEOUT_SEC
    ):
        self.api_user = (api_user if api_user is not None else os.getenv("SIGHTENGINE_API_USER", "")).strip()
        self.api_secret = (api_secret if api_secret is not None else os.getenv("SIGHTENGINE_API_SECRET", "")).strip()
        self.endpoint = endpoint
        self.timeout = timeout_seconds

    @property
    def is_configured(self) -> bool:
        """Checks if both required Sightengine credentials are present in environment."""
        return bool(self.api_user and self.api_secret)

    def predict(
        self,
        video_path: str,
        timeout: Optional[float] = None
    ) -> DetectorResult:
        """
        Submits video to Sightengine synchronous AI-generated video detection API.
        Returns standardized DetectorResult.
        """
        start_time = time.time()
        effective_timeout = timeout or self.timeout

        # 1. Check Configuration Guard
        if not self.is_configured:
            return DetectorResult(
                detector_id="sightengine_api",
                name="Sightengine AI Video Detection API",
                category="commercial_api",
                status="unconfigured",
                ai_probability=50.0,
                raw_score=0.5,
                verdict="Inconclusive",
                confidence="None",
                latency_ms=0.0,
                frames_analyzed=0,
                version="v1.0 (genai)",
                details={"reason": "Missing SIGHTENGINE_API_USER or SIGHTENGINE_API_SECRET"},
                error="API credentials not configured in environment"
            )

        # 2. Check File Existence
        if not os.path.exists(video_path):
            return DetectorResult(
                detector_id="sightengine_api",
                name="Sightengine AI Video Detection API",
                category="commercial_api",
                status="failed",
                ai_probability=50.0,
                raw_score=0.5,
                verdict="Inconclusive",
                confidence="None",
                latency_ms=0.0,
                frames_analyzed=0,
                version="v1.0 (genai)",
                details={},
                error=f"Video file not found: {video_path}"
            )

        # 3. Execute API Request
        try:
            params = {
                "models": "genai",
                "api_user": self.api_user,
                "api_secret": self.api_secret
            }

            with open(video_path, "rb") as video_file:
                files = {"media": video_file}
                response = requests.post(
                    self.endpoint,
                    data=params,
                    files=files,
                    timeout=effective_timeout
                )

            duration_ms = round((time.time() - start_time) * 1000.0, 2)

            # 4. Handle HTTP Status Codes
            if response.status_code == 401 or response.status_code == 403:
                return DetectorResult(
                    detector_id="sightengine_api",
                    name="Sightengine AI Video Detection API",
                    category="commercial_api",
                    status="failed",
                    ai_probability=50.0,
                    raw_score=0.5,
                    verdict="Inconclusive",
                    confidence="None",
                    latency_ms=duration_ms,
                    frames_analyzed=0,
                    version="v1.0 (genai)",
                    details={"http_status": response.status_code},
                    error="Sightengine authentication failed: Invalid API credentials"
                )

            if response.status_code == 429:
                return DetectorResult(
                    detector_id="sightengine_api",
                    name="Sightengine AI Video Detection API",
                    category="commercial_api",
                    status="failed",
                    ai_probability=50.0,
                    raw_score=0.5,
                    verdict="Inconclusive",
                    confidence="None",
                    latency_ms=duration_ms,
                    frames_analyzed=0,
                    version="v1.0 (genai)",
                    details={"http_status": 429},
                    error="Sightengine rate limit or plan quota exceeded"
                )

            if response.status_code != 200:
                return DetectorResult(
                    detector_id="sightengine_api",
                    name="Sightengine AI Video Detection API",
                    category="commercial_api",
                    status="failed",
                    ai_probability=50.0,
                    raw_score=0.5,
                    verdict="Inconclusive",
                    confidence="None",
                    latency_ms=duration_ms,
                    frames_analyzed=0,
                    version="v1.0 (genai)",
                    details={"http_status": response.status_code, "body": response.text[:200]},
                    error=f"Sightengine API returned HTTP {response.status_code}"
                )

            data = response.json()

            # 5. Check API Payload Status
            if data.get("status") != "success":
                err_msg = data.get("error", {}).get("message", "API reported non-success status")
                return DetectorResult(
                    detector_id="sightengine_api",
                    name="Sightengine AI Video Detection API",
                    category="commercial_api",
                    status="failed",
                    ai_probability=50.0,
                    raw_score=0.5,
                    verdict="Inconclusive",
                    confidence="None",
                    latency_ms=duration_ms,
                    frames_analyzed=0,
                    version="v1.0 (genai)",
                    details={"response_payload": data},
                    error=f"Sightengine error: {err_msg}"
                )

            # 6. Parse Frame-Level GenAI Scores
            frames = data.get("data", {}).get("frames", [])
            frame_scores = []

            for f in frames:
                # Sightengine formats score as f['type']['ai_generated']
                type_info = f.get("type", {})
                if "ai_generated" in type_info:
                    frame_scores.append(float(type_info["ai_generated"]))

            if not frame_scores:
                # Check top-level type if frames not present
                top_ai = data.get("type", {}).get("ai_generated")
                if top_ai is not None:
                    frame_scores = [float(top_ai)]

            if not frame_scores:
                return DetectorResult(
                    detector_id="sightengine_api",
                    name="Sightengine AI Video Detection API",
                    category="commercial_api",
                    status="failed",
                    ai_probability=50.0,
                    raw_score=0.5,
                    verdict="Inconclusive",
                    confidence="None",
                    latency_ms=duration_ms,
                    frames_analyzed=0,
                    version="v1.0 (genai)",
                    details={"data": data.get("data", {})},
                    error="Sightengine response did not contain ai_generated scores"
                )

            # 7. Aggregate Frame Scores (Median & Mean)
            median_score = float(np.median(frame_scores))
            mean_score = float(np.mean(frame_scores))
            # 60% median (outlier rejection) + 40% mean
            video_raw_score = 0.60 * median_score + 0.40 * mean_score
            video_raw_score = max(0.0, min(1.0, video_raw_score))
            ai_prob_pct = round(video_raw_score * 100.0, 1)

            # 8. Decision Policy
            if video_raw_score >= 0.55:
                verdict = "Likely AI-generated"
                confidence = "High" if video_raw_score >= 0.80 else ("Medium" if video_raw_score >= 0.65 else "Low")
            elif video_raw_score <= 0.45:
                verdict = "Likely authentic"
                confidence = "High" if video_raw_score <= 0.20 else ("Medium" if video_raw_score <= 0.35 else "Low")
            else:
                verdict = "Inconclusive"
                confidence = "Low"

            return DetectorResult(
                detector_id="sightengine_api",
                name="Sightengine AI Video Detection API",
                category="commercial_api",
                status="success",
                ai_probability=ai_prob_pct,
                raw_score=round(video_raw_score, 4),
                verdict=verdict,
                confidence=confidence,
                latency_ms=duration_ms,
                frames_analyzed=len(frame_scores),
                version="v1.0 (genai)",
                details={
                    "request_id": data.get("request", {}).get("id"),
                    "operations_used": data.get("request", {}).get("operations"),
                    "frame_probabilities": [round(s, 4) for s in frame_scores],
                    "mean_score": round(mean_score, 4),
                    "median_score": round(median_score, 4)
                },
                error=None
            )

        except requests.exceptions.Timeout:
            duration_ms = round((time.time() - start_time) * 1000.0, 2)
            return DetectorResult(
                detector_id="sightengine_api",
                name="Sightengine AI Video Detection API",
                category="commercial_api",
                status="failed",
                ai_probability=50.0,
                raw_score=0.5,
                verdict="Inconclusive",
                confidence="None",
                latency_ms=duration_ms,
                frames_analyzed=0,
                version="v1.0 (genai)",
                details={},
                error=f"Sightengine API request timed out after {effective_timeout}s"
            )

        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000.0, 2)
            return DetectorResult(
                detector_id="sightengine_api",
                name="Sightengine AI Video Detection API",
                category="commercial_api",
                status="failed",
                ai_probability=50.0,
                raw_score=0.5,
                verdict="Inconclusive",
                confidence="None",
                latency_ms=duration_ms,
                frames_analyzed=0,
                version="v1.0 (genai)",
                details={},
                error=f"Sightengine connection error: {str(e)}"
            )
