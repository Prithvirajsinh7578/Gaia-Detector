# utils/constants.py

FEATURE_NAMES = [
    "perplexity",
    "burstiness",
    "vocabulary_richness",
    "sentence_variation",
    "repetition",
    "ngram",
    "semantic_consistency",
    "avg_word_length",
    "punctuation_density",
    "readability",
    "pronoun_ratio",
    "adverb_ratio",
    "lexical_density",
    "grammar_error_rate",
    "spelling_error_rate",
    "passive_sentence_ratio",
    "question_ratio",
    "exclamation_ratio",
]

import os

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(_BASE_DIR, "models", "classifier.pkl")
DATASET_PATH = os.path.join(_BASE_DIR, "datasets", "features.csv")
