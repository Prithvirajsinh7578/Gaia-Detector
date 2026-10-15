import statistics
from utils.nlp import nlp


def sentence_variation(sentence_lengths):
    """
    Calculates sentence length variation statistics.

    Returns a normalized variation score.
    """

    if len(sentence_lengths) < 2:
        return 0.0

    avg_length = statistics.mean(sentence_lengths)

    variance = statistics.variance(sentence_lengths)

    shortest = min(sentence_lengths)

    longest = max(sentence_lengths)

    if avg_length == 0:
        return 0.0

    # Normalize variation
    variation_score = variance / avg_length

    return round(variation_score, 4)