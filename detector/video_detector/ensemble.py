"""
ensemble.py - Multi-Source Hybrid Ensemble Engine for Video AI Detection.
Integrates custom spatial-temporal classifier, pretrained Hugging Face ResNet-50 T2V model,
and Sightengine GenAI detection API into a unified, calibrated decision framework.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import numpy as np

from detectors.base_detector import DetectorResult


# Default calibrated weights across available detector configurations
DEFAULT_WEIGHTS = {
    # 3 active detectors
    ("custom_rf", "hf_resnet50_t2v", "sightengine_api"): {
        "custom_rf": 0.35,
        "hf_resnet50_t2v": 0.35,
        "sightengine_api": 0.30
    },
    # 2 active detectors (Custom + HF)
    ("custom_rf", "hf_resnet50_t2v"): {
        "custom_rf": 0.50,
        "hf_resnet50_t2v": 0.50
    },
    # 2 active detectors (Custom + API)
    ("custom_rf", "sightengine_api"): {
        "custom_rf": 0.50,
        "sightengine_api": 0.50
    },
    # 2 active detectors (HF + API)
    ("hf_resnet50_t2v", "sightengine_api"): {
        "hf_resnet50_t2v": 0.55,
        "sightengine_api": 0.45
    },
    # 1 active detector
    ("custom_rf",): {"custom_rf": 1.0},
    ("hf_resnet50_t2v",): {"hf_resnet50_t2v": 1.0},
    ("sightengine_api",): {"sightengine_api": 1.0}
}


@dataclass
class EnsembleResult:
    """
    Unified output of the Hybrid Video AI Detection Ensemble.
    """
    verdict: str                               # 'Likely AI-generated' | 'Likely authentic' | 'Inconclusive / Uncertain'
    ai_probability: float                      # Calibrated ensemble AI score [0.0, 100.0%]
    confidence: str                            # 'High' | 'Medium' | 'Low'
    agreement: str                             # 'Full Consensus' | 'Majority Agreement' | 'Conflicting Evidence' | 'Single Source'
    agreement_score: float                     # Fraction of detectors agreeing with final verdict [0.0, 1.0]
    active_detectors_count: int                # Number of detectors that successfully ran
    total_detectors_count: int                 # Total detectors configured in pipeline
    individual_results: Dict[str, Dict[str, Any]] # Standardized result per detector
    ensemble_strategy: str                     # e.g., 'calibrated_weighted_consensus'
    applied_weights: Dict[str, float]          # Weights assigned to each detector
    inconclusive_reason: Optional[str] = None  # Explanation if verdict is Inconclusive
    visual_indicators: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verdict": self.verdict,
            "ai_probability": self.ai_probability,
            "confidence": self.confidence,
            "agreement": self.agreement,
            "agreement_score": round(self.agreement_score, 2),
            "active_detectors_count": self.active_detectors_count,
            "total_detectors_count": self.total_detectors_count,
            "individual_results": self.individual_results,
            "ensemble_strategy": self.ensemble_strategy,
            "applied_weights": self.applied_weights,
            "inconclusive_reason": self.inconclusive_reason,
            "visual_indicators": self.visual_indicators,
            "limitations": self.limitations
        }


class HybridEnsemble:
    """
    Coordinates multi-evidence fusion, agreement checks, and calibrated uncertainty policy.
    """

    def __init__(
        self,
        uncertain_lower: float = 0.46,
        uncertain_upper: float = 0.54,
        confidence_high: float = 0.80,
        confidence_med: float = 0.60,
        conflict_discrepancy_threshold: float = 0.45
    ):
        self.uncertain_lower = uncertain_lower
        self.uncertain_upper = uncertain_upper
        self.confidence_high = confidence_high
        self.confidence_med = confidence_med
        self.conflict_discrepancy_threshold = conflict_discrepancy_threshold

    def _determine_weights(self, available_ids: List[str]) -> Dict[str, float]:
        """Resolves calibrated weights based on the set of available detectors."""
        tuple_key = tuple(sorted(available_ids))
        for key, weights in DEFAULT_WEIGHTS.items():
            if tuple(sorted(key)) == tuple_key:
                return weights

        # Fallback: uniform weighting if combination is unusual
        uniform_weight = 1.0 / max(1, len(available_ids))
        return {did: uniform_weight for did in available_ids}

    def combine(self, detector_results: List[DetectorResult]) -> EnsembleResult:
        """
        Combines outputs from all evaluated detectors into a robust ensemble verdict.
        """
        total_count = len(detector_results)
        active_results = [r for r in detector_results if r.is_available]
        available_ids = [r.detector_id for r in active_results]
        individual_dict = {r.detector_id: r.to_dict() for r in detector_results}

        # 1. Handle case where zero detectors succeeded
        if not active_results:
            return EnsembleResult(
                verdict="Inconclusive / Uncertain",
                ai_probability=50.0,
                confidence="Low",
                agreement="Zero Evidence",
                agreement_score=0.0,
                active_detectors_count=0,
                total_detectors_count=total_count,
                individual_results=individual_dict,
                ensemble_strategy="fallback",
                applied_weights={},
                inconclusive_reason="All configured detection components failed or were unconfigured.",
                visual_indicators=["No detector was able to process this file."],
                limitations=["Check network connection, local model weights, and video codecs."]
            )

        # 2. Assign Weights based on available detector set
        weights = self._determine_weights(available_ids)

        # 3. Calculate Weighted Ensemble Score
        weighted_score = sum(
            (r.raw_score * weights.get(r.detector_id, 0.0))
            for r in active_results
        )
        weighted_score = max(0.0, min(1.0, weighted_score))
        ensemble_pct = round(weighted_score * 100.0, 1)

        # 4. Assess Inter-Detector Agreement & Contradiction
        verdicts = [r.verdict for r in active_results]
        raw_scores = [r.raw_score for r in active_results]
        max_score = max(raw_scores)
        min_score = min(raw_scores)
        score_spread = max_score - min_score

        ai_votes = sum(1 for v in verdicts if "AI-generated" in v)
        real_votes = sum(1 for v in verdicts if "authentic" in v)
        num_active = len(active_results)

        is_contradictory = (
            num_active >= 2 and
            ai_votes >= 1 and
            real_votes >= 1 and
            score_spread >= self.conflict_discrepancy_threshold
        )

        if num_active == 1:
            agreement_label = "Single Source"
            agreement_ratio = 1.0
        elif is_contradictory:
            agreement_label = "Conflicting Evidence"
            agreement_ratio = max(ai_votes, real_votes) / float(num_active)
        elif ai_votes == num_active or real_votes == num_active:
            agreement_label = "Full Consensus"
            agreement_ratio = 1.0
        else:
            agreement_label = "Majority Agreement"
            agreement_ratio = max(ai_votes, real_votes) / float(num_active)

        # 5. Step 12 Decision Policy (Handling Inconclusive Conditions)
        inconclusive_reason = None

        if is_contradictory:
            # When detectors strongly contradict each other, output Inconclusive
            verdict = "Inconclusive / Uncertain"
            confidence = "Low"
            conflicting_names = [r.name for r in active_results]
            inconclusive_reason = (
                f"Contradictory evidence between independent models (score spread: {round(score_spread*100, 1)}%). "
                f"One detector flagged synthetic patterns while another verified authentic motion."
            )
        elif weighted_score >= self.uncertain_upper:
            verdict = "Likely AI-generated"
            if weighted_score >= self.confidence_high and agreement_ratio >= 0.67:
                confidence = "High"
            elif weighted_score >= self.confidence_med:
                confidence = "Medium"
            else:
                confidence = "Low"
        elif weighted_score <= self.uncertain_lower:
            verdict = "Likely authentic"
            if weighted_score <= (1.0 - self.confidence_high) and agreement_ratio >= 0.67:
                confidence = "High"
            elif weighted_score <= (1.0 - self.confidence_med):
                confidence = "Medium"
            else:
                confidence = "Low"
        else:
            verdict = "Inconclusive / Uncertain"
            confidence = "Low"
            inconclusive_reason = (
                f"Ensemble probability ({ensemble_pct}%) falls within the borderline threshold window "
                f"[{round(self.uncertain_lower*100, 1)}% - {round(self.uncertain_upper*100, 1)}%]."
            )

        # 6. Aggregate Indicators from all active models
        indicators = []
        for r in active_results:
            # Custom indicators
            if r.detector_id == "custom_rf":
                custom_inds = r.details.get("visual_indicators", [])
                indicators.extend(custom_inds[:3])
            # HF ResNet50 T2V indicator
            elif r.detector_id == "hf_resnet50_t2v":
                if r.raw_score >= 0.70:
                    indicators.append("Deep residual visual features match text-to-video diffusion signatures (Sora/Veo2)")
                elif r.raw_score <= 0.30:
                    indicators.append("Deep visual texture consistency matches natural camera sensor patterns")
            # Sightengine API indicator
            elif r.detector_id == "sightengine_api":
                if r.raw_score >= 0.65:
                    indicators.append("Sightengine GenAI commercial model detected synthetic frame patterns")
                elif r.raw_score <= 0.35:
                    indicators.append("Sightengine GenAI model verified authentic camera capture")

        if not indicators:
            if "AI-generated" in verdict:
                indicators.append("Spatial-temporal motion patterns align with generated AI video models")
            elif "authentic" in verdict:
                indicators.append("Visual texture cadence and temporal consistency align with authentic camera footage")
            else:
                indicators.append("Subtle or conflicting visual cues observed across evaluation frames")

        # Deduplicate indicators
        unique_indicators = list(dict.fromkeys(indicators))

        # 7. Limitations & Disclaimers
        limitations = [
            "Predictions reflect visual-temporal cues; audio tracks are not analyzed.",
            "Heavy compression or social media re-encoding can degrade detection confidence.",
        ]
        if num_active < total_count:
            unavail = [r.name for r in detector_results if not r.is_available]
            limitations.append(f"Operating with partial ensemble: {', '.join(unavail)} not active.")

        return EnsembleResult(
            verdict=verdict,
            ai_probability=ensemble_pct,
            confidence=confidence,
            agreement=agreement_label,
            agreement_score=agreement_ratio,
            active_detectors_count=num_active,
            total_detectors_count=total_count,
            individual_results=individual_dict,
            ensemble_strategy="calibrated_weighted_consensus",
            applied_weights=weights,
            inconclusive_reason=inconclusive_reason,
            visual_indicators=unique_indicators,
            limitations=limitations
        )
