import math
import torch
from utils.models import gpt2_tokenizer as tokenizer, gpt2_model as model, device

# Put model in evaluation mode
model.eval()


def calculate_perplexity(text: str) -> float:
    """
    Calculate GPT-2 perplexity for a given text safely with thermal and VRAM protection.
    """
    if not text or not text.strip():
        return 0.0

    # Limit to 512 tokens to prevent O(N^2) quadratic attention spikes and TDR timeouts on laptop GPUs
    encodings = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    input_ids = encodings.input_ids.to(device)
    attention_mask = encodings.attention_mask.to(device)

    with torch.no_grad():
        outputs = model(
            input_ids,
            attention_mask=attention_mask,
            labels=input_ids
        )
        loss = outputs.loss.item()

    # Free tensor references from GPU memory immediately
    del input_ids, attention_mask, outputs

    try:
        perplexity = math.exp(min(loss, 50.0))
    except OverflowError:
        perplexity = 1000.0

    return round(perplexity, 4)