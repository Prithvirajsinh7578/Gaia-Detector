from collections import Counter


def vocabulary_richness(words):
    """
    Computes Type-Token Ratio (TTR).

    Vocabulary Richness = Unique Words / Total Words
    """

    if not words:
        return 0.0

    # Convert all words to lowercase
    normalized_words = [word.lower() for word in words]

    total_words = len(normalized_words)
    unique_words = len(set(normalized_words))

    richness = unique_words / total_words

    return round(richness, 4)