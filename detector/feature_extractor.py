from utils.preprocessing import preprocess

from features.perplexity import calculate_perplexity
from features.burstiness import calculate_burstiness
from features.vocabulary import vocabulary_richness
from features.sentence_variation import sentence_variation
from features.repetition import repetition_score
from features.ngram import ngram_score
from features.semantic import semantic_consistency
from features.stylometry import stylometry_features
from features.grammar import grammar_score


from utils.constants import FEATURE_NAMES

class FeatureExtractor:

    def __init__(self):
        pass

    def extract_features(self, text):

        processed = preprocess(text)

        features = {}

        features["perplexity"] = calculate_perplexity(
            processed["normalized_text"]
        )

        features["burstiness"] = calculate_burstiness(
            processed["sentence_lengths"]
        )

        features["vocabulary_richness"] = vocabulary_richness(
            processed["words"]
        )

        features["sentence_variation"] = sentence_variation(
            processed["sentence_lengths"]
        )

        features["repetition"] = repetition_score(
            processed["words"]
        )

        features["ngram"] = ngram_score(
            processed["words"]
        )

        features["semantic_consistency"] = semantic_consistency(
            processed["sentences"]
        )

        features.update(
            stylometry_features(
                processed["doc"],
                processed["words"],
                processed["pos_counts"]
            )
        )

        features.update(
            grammar_score(
                processed["doc"]
            )
        )

        return features

    def extract(self, text):

        features = self.extract_features(text)

        return [
            features.get(name, 0.0)
            for name in FEATURE_NAMES
        ]