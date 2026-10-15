from utils.nlp import nlp
from utils.models import language_tool


def grammar_score(doc):
    """
    Extract grammar-related features.

    Returns a dictionary.
    """

    text = doc.text

    words = [
        token.text
        for token in doc
        if not token.is_punct and not token.is_space
    ]

    total_words = max(1, len(words))

    sentences = list(doc.sents)

    total_sentences = max(1, len(sentences))

    # -----------------------------------
    # LanguageTool (optimized sample window)
    # -----------------------------------
    sample_text = text[:800]
    sample_words = max(1, len(sample_text.split()))

    try:
        matches = language_tool.check(sample_text)
    except Exception:
        matches = []

    grammar_errors = 0
    spelling_errors = 0

    for match in matches:

        rule = getattr(match, "rule_issue_type", None)

        if rule is None:
            rule = getattr(match, "ruleIssueType", "")
        if rule == "misspelling":
            spelling_errors += 1
        else:
            grammar_errors += 1

    grammar_error_rate = grammar_errors / sample_words

    spelling_error_rate = spelling_errors / sample_words

    # -----------------------------------
    # Passive Voice
    # -----------------------------------

    passive_sentences = 0

    for sentence in sentences:

        if any(
            token.dep_ == "nsubjpass"
            for token in sentence
        ):
            passive_sentences += 1

    passive_sentence_ratio = (
        passive_sentences / total_sentences
    )

    # -----------------------------------
    # Sentence Types
    # -----------------------------------

    questions = 0
    exclamations = 0

    for sentence in sentences:

        sentence_text = sentence.text.strip()

        if sentence_text.endswith("?"):
            questions += 1

        if sentence_text.endswith("!"):
            exclamations += 1

    question_ratio = questions / total_sentences

    exclamation_ratio = exclamations / total_sentences

    return {

        "grammar_error_rate":
            round(grammar_error_rate, 4),

        "spelling_error_rate":
            round(spelling_error_rate, 4),

        "passive_sentence_ratio":
            round(passive_sentence_ratio, 4),

        "question_ratio":
            round(question_ratio, 4),

        "exclamation_ratio":
            round(exclamation_ratio, 4),
    }
