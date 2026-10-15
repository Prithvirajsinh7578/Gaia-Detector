from collections import Counter


def ngram_score(words):
    """
    Calculates an N-gram diversity score.

    Combines:
    - unigram diversity
    - bigram diversity
    - trigram diversity

    Returns a value between 0 and 1.
    """

    if len(words) < 3:
        return 0.0

    words = [w.lower() for w in words]

    # -----------------------
    # Unigrams
    # -----------------------

    unigrams = words

    unigram_ratio = len(set(unigrams)) / len(unigrams)

    # -----------------------
    # Bigrams
    # -----------------------

    bigrams = list(zip(words[:-1], words[1:]))

    bigram_ratio = len(set(bigrams)) / len(bigrams)

    # -----------------------
    # Trigrams
    # -----------------------

    trigrams = list(zip(words[:-2], words[1:-1], words[2:]))

    trigram_ratio = len(set(trigrams)) / len(trigrams)

    # -----------------------
    # Final Score
    # -----------------------

    score = (
        unigram_ratio +
        bigram_ratio +
        trigram_ratio
    ) / 3

    return round(score, 4)