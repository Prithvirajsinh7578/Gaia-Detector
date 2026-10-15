from collections import Counter


def repetition_score(words):
    """
    Calculates repetition using:
    - repeated words
    - repeated bigrams
    - repeated trigrams

    Returns a normalized score between 0 and 1.
    """

    if len(words) < 2:
        return 0.0

    # Normalize to lowercase
    words = [word.lower() for word in words]

    total_words = len(words)

    # -------------------------
    # Word repetition
    # -------------------------

    word_counts = Counter(words)

    repeated_words = sum(
        count - 1
        for count in word_counts.values()
        if count > 1
    )

    # -------------------------
    # Bigram repetition
    # -------------------------

    bigrams = list(zip(words[:-1], words[1:]))

    bigram_counts = Counter(bigrams)

    repeated_bigrams = sum(
        count - 1
        for count in bigram_counts.values()
        if count > 1
    )

    # -------------------------
    # Trigram repetition
    # -------------------------

    trigrams = list(zip(words[:-2], words[1:-1], words[2:]))

    trigram_counts = Counter(trigrams)

    repeated_trigrams = sum(
        count - 1
        for count in trigram_counts.values()
        if count > 1
    )

    # -------------------------
    # Combined score
    # -------------------------

    score = (
        repeated_words
        + repeated_bigrams
        + repeated_trigrams
    ) / total_words

    return round(score, 4)