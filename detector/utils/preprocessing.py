import re
from collections import Counter
from utils.nlp import nlp


def normalize_text(text: str) -> str:
    """
    Normalize whitespace and convert text to lowercase.
    """
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = text.lower()
    return text


def sentence_split(text: str):
    """
    Split text into sentences.
    """
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]


def word_tokenize(text: str):
    """
    Tokenize text into words while ignoring punctuation and spaces.
    """
    doc = nlp(text)

    return [
        token.text
        for token in doc
        if not token.is_space and not token.is_punct
    ]


def preprocess(text: str):
    """
    Complete preprocessing pipeline.
    Returns all processed representations needed later.
    """

    normalized = normalize_text(text)
    doc = nlp(normalized)

    sentences = [sent.text.strip() for sent in doc.sents]
    words = [token.text for token in doc if not token.is_space and not token.is_punct]

    sentence_lengths = []
    for sentence in doc.sents:
        length = sum(
            1
            for token in sentence
            if not token.is_space
            and not token.is_punct
        )
        sentence_lengths.append(length)

    pos_counts = Counter(token.pos_ for token in doc if not token.is_space)

    return {
        "normalized_text": normalized,
        "sentences": sentences,
        "words": words,
        "doc": doc,
        "sentence_lengths": sentence_lengths,
        "pos_counts": pos_counts
    }