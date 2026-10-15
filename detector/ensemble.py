"""
ensemble.py - Calibrated Hybrid Multi-Source Text Detection Ensemble.
Combines:
1. Preserved Custom Random Forest Classifier (18 engineered features)
2. Pretrained Hugging Face RoBERTa Deepfake/AI Detector
3. External Commercial GPTZero API

Applies dynamic weight re-normalization, inter-detector consensus scoring,
conflict detection (divergence >= 45%), short-text uncertainty guards, and indicator aggregation.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from detectors.base_detector import DetectorResult

# Calibrated Default Weights
DEFAULT_WEIGHTS = {
    "custom_rf": 0.35,
    "hf_roberta": 0.35,
    "gptzero_api": 0.30
}

# Conservative Decision Policy Thresholds
AI_VERDICT_THRESHOLD = 65.0         # >= 65% is Likely AI-generated
HUMAN_VERDICT_THRESHOLD = 35.0      # <= 35% is Likely Human-written
CONFLICT_DISCREPANCY_THRESHOLD = 45.0  # Divergence >= 45% triggers Inconclusive


@dataclass
class EnsembleResult:
    """Standardized multi-model consensus prediction payload."""
    ai_probability: float
    human_probability: float
    verdict: str
    confidence: str
    consensus_status: str
    discrepancy: float
    active_detectors_count: int
    total_detectors_count: int
    inconclusive_reason: Optional[str]
    summary_indicators: List[str]
    component_results: Dict[str, Any]
    weights_used: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ai_probability": round(self.ai_probability, 1),
            "human_probability": round(self.human_probability, 1),
            "verdict": self.verdict,
            "confidence": self.confidence,
            "consensus_status": self.consensus_status,
            "discrepancy": round(self.discrepancy, 1),
            "active_detectors": self.active_detectors_count,
            "total_detectors": self.total_detectors_count,
            "inconclusive_reason": self.inconclusive_reason,
            "indicators": self.summary_indicators,
            "individual_detectors": self.component_results,
            "weights_used": self.weights_used
        }


class HybridTextEnsemble:
    """
    Orchestrates evidence aggregation from all active text detectors.
    Implements dynamic weighting, consensus calculation, and conservative conflict policy.
    """

    def __init__(
        self,
        ai_threshold: float = AI_VERDICT_THRESHOLD,
        human_threshold: float = HUMAN_VERDICT_THRESHOLD,
        conflict_threshold: float = CONFLICT_DISCREPANCY_THRESHOLD,
        base_weights: Optional[Dict[str, float]] = None
    ):
        self.ai_threshold = ai_threshold
        self.human_threshold = human_threshold
        self.conflict_threshold = conflict_threshold
        self.base_weights = base_weights or DEFAULT_WEIGHTS.copy()

    def combine(
        self,
        detector_results: List[DetectorResult],
        is_short_text: bool = False
    ) -> EnsembleResult:
        """
        Combines outputs of available detectors into a calibrated final verdict.
        """
        total_count = len(detector_results)
        active_results = [r for r in detector_results if r.status == "success"]
        component_dict = {r.detector_id: r.to_dict() for r in detector_results}

        # 1. Fallback if no detector succeeded
        if not active_results:
            return EnsembleResult(
                ai_probability=50.0,
                human_probability=50.0,
                verdict="Inconclusive / Uncertain",
                confidence="None",
                consensus_status="Unavailable",
                discrepancy=0.0,
                active_detectors_count=0,
                total_detectors_count=total_count,
                inconclusive_reason="All detection modules were unavailable or failed inference.",
                summary_indicators=["No active detector produced a valid score."],
                component_results=component_dict,
                weights_used={}
            )

        # 2. Dynamic Weight Normalization for Active Detectors
        active_weights_sum = sum(self.base_weights.get(r.detector_id, 0.2) for r in active_results)
        normalized_weights = {}
        for r in active_results:
            base_w = self.base_weights.get(r.detector_id, 0.2)
            normalized_weights[r.detector_id] = round(base_w / active_weights_sum, 4)

        # 3. Calculate Weighted Ensemble AI Probability
        weighted_ai_prob = sum(
            r.ai_probability * normalized_weights[r.detector_id]
            for r in active_results
        )
        weighted_ai_prob = max(0.0, min(100.0, weighted_ai_prob))
        human_prob = max(0.0, min(100.0, 100.0 - weighted_ai_prob))

        # 4. Measure Inter-Model Discrepancy
        probs = [r.ai_probability for r in active_results]
        discrepancy = (max(probs) - min(probs)) if len(probs) > 1 else 0.0

        # 5. Determine Consensus Status
        if len(active_results) == 1:
            consensus_status = "Single Source"
        elif discrepancy < 18.0:
            consensus_status = "Full Consensus"
        elif discrepancy < self.conflict_threshold:
            consensus_status = "Majority Agreement"
        else:
            consensus_status = "Conflicting Evidence"

        # 6. Apply Conservative Uncertainty & Decision Policy
        inconclusive_reason = None
        verdict = "Inconclusive / Uncertain"
        confidence = "Medium"

        # Conflict Trigger
        if len(active_results) > 1 and discrepancy >= self.conflict_threshold:
            verdict = "Inconclusive / Uncertain"
            confidence = "Low"
            inconclusive_reason = (
                f"Conflicting Evidence: Individual models strongly disagree by {discrepancy:.1f}% "
                f"(min {min(probs):.1f}% vs max {max(probs):.1f}%). Withholding confident decision."
            )

        # Short Text Guard
        elif is_short_text:
            if weighted_ai_prob >= 75.0:
                verdict = "Possibly AI-generated"
                confidence = "Low"
            elif weighted_ai_prob <= 25.0:
                verdict = "Likely Human-written"
                confidence = "Low"
            else:
                verdict = "Inconclusive / Uncertain"
                confidence = "Low"
            inconclusive_reason = "Short text alert: Input contains limited tokens, reducing statistical power."

        # Borderline Interval [35%, 65%]
        elif self.human_threshold < weighted_ai_prob < self.ai_threshold:
            verdict = "Inconclusive / Uncertain"
            confidence = "Low"
            inconclusive_reason = f"Borderline score ({weighted_ai_prob:.1f}%): Insufficient polarity to confirm AI or Human authorship."

        # Confident Verdicts
        elif weighted_ai_prob >= self.ai_threshold:
            verdict = "Likely AI-generated"
            confidence = "High" if consensus_status == "Full Consensus" else "Medium"

        elif weighted_ai_prob <= self.human_threshold:
            verdict = "Likely Human-written"
            confidence = "High" if consensus_status == "Full Consensus" else "Medium"

        # 7. Aggregate Explanatory Indicators
        indicators = []
        for r in active_results:
            for ind in r.indicators:
                if ind not in indicators and len(indicators) < 8:
                    indicators.append(ind)

        # Prepend consensus summary indicator
        if consensus_status == "Conflicting Evidence":
            indicators.insert(0, f"Caution: Multi-detector discrepancy observed ({discrepancy:.1f}% divergence)")
        elif consensus_status == "Full Consensus":
            indicators.insert(0, f"High Multi-Detector Agreement: All active models unanimously aligned on verdict")

        return EnsembleResult(
            ai_probability=weighted_ai_prob,
            human_probability=human_prob,
            verdict=verdict,
            confidence=confidence,
            consensus_status=consensus_status,
            discrepancy=discrepancy,
            active_detectors_count=len(active_results),
            total_detectors_count=total_count,
            inconclusive_reason=inconclusive_reason,
            summary_indicators=indicators,
            component_results=component_dict,
            weights_used=normalized_weights
        )
