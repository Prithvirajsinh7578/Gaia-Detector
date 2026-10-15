import os
import joblib
import pandas as pd
from feature_extractor import FeatureExtractor
from utils.constants import MODEL_PATH, FEATURE_NAMES


class Detector:
    """
    AI Text Detector: Complete prediction pipeline implementing Steps 18, 19, and 20.
    """

    def __init__(self, model_path: str = MODEL_PATH):
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found at '{model_path}'. "
                "Please run 'python classifier.py' first to train and save the model."
            )

        self.model = joblib.load(model_path)
        self.extractor = FeatureExtractor()

    def _calculate_confidence(self, ai_probability: float) -> tuple[str, str]:
        """
        Step 19: Map probability to confidence level and verdict.
        ai_probability is between 0.0 and 1.0 (or 0 to 100%).
        """
        prob_pct = ai_probability * 100.0

        if prob_pct >= 90.0:
            return "High", "Likely AI-generated"
        elif prob_pct >= 70.0:
            return "Medium", "Likely AI-generated"
        elif prob_pct >= 50.0:
            return "Low", "Possibly AI-generated"
        else:
            # Below 50% is Likely Human
            if prob_pct <= 20.0:
                return "High", "Likely Human-written"
            elif prob_pct <= 35.0:
                return "Medium", "Likely Human-written"
            else:
                return "Low", "Likely Human-written"

    def _generate_indicators(self, features: dict, ai_probability: float) -> list[str]:
        """
        Generate heuristic human-readable indicators based on feature thresholds.
        """
        indicators = []
        prob_pct = ai_probability * 100.0

        # AI-leaning indicators
        if features.get("perplexity", 100.0) < 30.0:
            indicators.append("Low perplexity (highly predictable text flow)")

        if features.get("burstiness", 1.0) < 0.38:
            indicators.append("Uniform sentence structure (low burstiness)")

        if features.get("semantic_consistency", 0.0) > 0.38:
            indicators.append("High semantic consistency across transitions")

        if features.get("vocabulary_richness", 0.0) > 0.65:
            indicators.append("Elevated vocabulary richness with formal lexical choices")

        if (
            features.get("grammar_error_rate", 1.0) < 0.02
            and features.get("spelling_error_rate", 1.0) == 0.0
        ):
            indicators.append("Near-flawless grammatical precision")

        if features.get("repetition", 0.0) > 0.40:
            indicators.append("Repetitive structural phrasing across sentences")

        if features.get("passive_sentence_ratio", 0.0) > 0.15:
            indicators.append("Notable use of passive voice constructions")

        # Human-leaning indicators
        if prob_pct < 50.0:
            if features.get("burstiness", 0.0) >= 0.50:
                indicators.append("Dynamic sentence length variation (natural human cadence)")
            if features.get("perplexity", 0.0) >= 45.0:
                indicators.append("High perplexity (creative, unexpected word sequences)")
            if (
                features.get("grammar_error_rate", 0.0) > 0.05
                or features.get("spelling_error_rate", 0.0) > 0.02
            ):
                indicators.append("Colloquial grammar or informal phrasing detected")

        # Fallback if no specific threshold was met
        if not indicators:
            if prob_pct >= 50.0:
                indicators.append("Stylometric patterns align closely with generated AI text")
            else:
                indicators.append("Linguistic patterns align closely with natural human writing")

        return indicators

    def predict(self, text: str) -> dict:
        """
        Steps 18, 19, 20: Complete Prediction Pipeline.

        Input: Raw user text
        Returns: Structured dictionary conforming to Step 20 specification.
        """
        if not text or not text.strip():
            return {
                "probability": 0.0,
                "confidence": "None",
                "verdict": "Invalid / Empty Input",
                "features": {},
                "detailed_features": {},
                "indicators": ["Please provide text for analysis."]
            }

        # Step 18: Preprocess & Extract Features
        raw_features = self.extractor.extract_features(text)
        vector = [raw_features.get(name, 0.0) for name in FEATURE_NAMES]

        # Model Prediction
        df_input = pd.DataFrame([vector], columns=FEATURE_NAMES)
        probabilities = self.model.predict_proba(df_input)[0]
        # Label 1 is AI, Label 0 is Human
        ai_prob = float(probabilities[1])
        prob_percent = round(ai_prob * 100, 1)

        # Step 19: Confidence Calculation
        confidence, verdict = self._calculate_confidence(ai_prob)

        # Step 20: Indicators & Response Formatting
        indicators = self._generate_indicators(raw_features, ai_prob)

        summary_features = {
            "perplexity": round(raw_features.get("perplexity", 0.0), 2),
            "burstiness": round(raw_features.get("burstiness", 0.0), 2),
            "vocabularyRichness": round(raw_features.get("vocabulary_richness", 0.0), 2),
            "sentenceVariation": round(raw_features.get("sentence_variation", 0.0), 2),
            "repetition": round(raw_features.get("repetition", 0.0), 2),
            "ngramScore": round(raw_features.get("ngram", 0.0), 2),
            "semanticConsistency": round(raw_features.get("semantic_consistency", 0.0), 2),
            "stylometry": round(
                (raw_features.get("lexical_density", 0.0) + (raw_features.get("readability", 0.0) / 100.0)) / 2.0, 2
            ),
            "grammarPatterns": round(
                1.0 - min(1.0, raw_features.get("grammar_error_rate", 0.0) * 5.0), 2
            ),
        }

        return {
            "probability": prob_percent,
            "confidence": confidence,
            "verdict": verdict,
            "features": summary_features,
            "detailed_features": raw_features,
            "indicators": indicators,
        }