import torch
import torch.nn.functional as F
from utils.models import sentence_model as model


def semantic_consistency(sentences):
    """
    Computes semantic consistency by averaging cosine similarity
    between consecutive sentence embeddings with safety batching.
    """
    if not sentences or len(sentences) < 2:
        return 0.0

    # Limit to first 20 sentences for consistent throughput and low VRAM
    sentences_sample = sentences[:20]

    with torch.no_grad():
        # Small batch size prevents GPU kernel queue saturation
        embeddings = model.encode(
            sentences_sample,
            batch_size=8,
            convert_to_tensor=True,
            show_progress_bar=False
        )

        sims = F.cosine_similarity(embeddings[:-1], embeddings[1:], dim=1)
        average_similarity = sims.mean().item()

    del embeddings, sims

    return round(float(average_similarity), 4)