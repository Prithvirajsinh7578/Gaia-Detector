import os
import gc
import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
from sentence_transformers import SentenceTransformer
import language_tool_python

# Determine acceleration hardware safely
device = "cuda" if (torch.cuda.is_available() and torch.cuda.device_count() > 0) else "cpu"

if device == "cuda":
    try:
        gpu_name = torch.cuda.get_device_name(0)
        total_vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"[Hardware Acceleration] Active GPU: {gpu_name} ({total_vram_gb:.1f} GB VRAM)")

        # Safe Laptop GPU Memory & Stability Guard:
        # Cap PyTorch allocation to 65% of VRAM so Windows DWM & desktop compositor never starve.
        try:
            torch.cuda.set_per_process_memory_fraction(0.65, 0)
        except Exception:
            pass
        torch.backends.cudnn.benchmark = False
    except Exception as e:
        print(f"[Hardware Acceleration] CUDA initialization fallback: {e}")
        device = "cpu"
else:
    print("[Hardware Acceleration] GPU not detected or disabled, running on CPU.")

# GPT-2
gpt2_tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2").to(device)
gpt2_model.eval()

# Sentence Transformer
sentence_model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
sentence_model.eval()

# LanguageTool
language_tool = language_tool_python.LanguageTool("en-US")


def clear_gpu_cache():
    """Safely flush VRAM cache and collect garbage to keep GPU thermals & memory stable."""
    if device == "cuda":
        torch.cuda.empty_cache()
    gc.collect()