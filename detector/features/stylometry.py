import string
import textstat

from utils.nlp import nlp


def stylometry_features(doc, words, pos_counts):
    """
    Extract stylometric features.
    """

    if not words:
        return {
            "avg_word_length": 0.0,
            "punctuation_density": 0.0,
            "readability": 0.0,
            "pronoun_ratio": 0.0,
            "adverb_ratio": 0.0,
            "lexical_density": 0.0,
        }

    text = doc.text

    total_words = len(words)

    # -----------------------------------
    # Average Word Length
    # -----------------------------------

    avg_word_length = (
        sum(len(word) for word in words)
        / total_words
    )

    # -----------------------------------
    # Punctuation Density
    # -----------------------------------

    punctuation_count = sum(
        1
        for token in doc
        if token.is_punct
    )

    punctuation_density = (
        punctuation_count / total_words
    )

    # -----------------------------------
    # Readability
    # -----------------------------------

    try:
        readability = textstat.flesch_reading_ease(text)
    except Exception:
        readability = 0.0

    # -----------------------------------
    # Pronouns
    # -----------------------------------

    pronouns = pos_counts.get("PRON", 0)

    pronoun_ratio = pronouns / total_words

    # -----------------------------------
    # Adverbs
    # -----------------------------------

    adverbs = pos_counts.get("ADV", 0)

    adverb_ratio = adverbs / total_words

    # -----------------------------------
    # Lexical Density
    # -----------------------------------

    content_words = sum(pos_counts.get(pos, 0) for pos in ["NOUN", "VERB", "ADJ", "ADV"])

    lexical_density = (
        content_words / total_words
    )



    return {

        "avg_word_length":
            round(avg_word_length, 4),

        "punctuation_density":
            round(punctuation_density, 4),

        "readability":
            round(readability, 4),

        "pronoun_ratio":
            round(pronoun_ratio, 4),

        "adverb_ratio":
            round(adverb_ratio, 4),

        "lexical_density":
            round(lexical_density, 4),
    }