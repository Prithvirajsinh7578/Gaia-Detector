import statistics
from utils.nlp import nlp


def calculate_burstiness(sentence_lengths):
    """
    Calculates burstiness as:
        standard deviation / mean sentence length
    """

    if len(sentence_lengths) < 2:
        return 0.0

    mean_length = statistics.mean(sentence_lengths)

    if mean_length == 0:
        return 0.0

    std_dev = statistics.stdev(sentence_lengths)

    burstiness = std_dev / mean_length

    return round(burstiness, 4)