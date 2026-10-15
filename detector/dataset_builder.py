import os
import sys
import time
import argparse
import gc

# -------------------------------------------------------------
# Laptop Thermal & Resource Protection:
# Restrict thread thrashing to keep CPU/GPU temperatures safe
# -------------------------------------------------------------
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import torch
torch.set_num_threads(2)

import pandas as pd
from feature_extractor import FeatureExtractor
from utils.constants import FEATURE_NAMES, DATASET_PATH, MODEL_PATH
from utils.models import clear_gpu_cache
from classifier import train_classifier

HUMAN_DIR = "datasets/raw/human"
AI_DIR = "datasets/raw/ai"
OUTPUT_FILE = DATASET_PATH


def balanced_sample_generator(skip_pairs: int = 0):
    """
    Infinite/full generator yielding balanced (text, label) pairs.
    Streams first from AI Generated Essays Dataset.csv, then from AI_Human.csv.
    Maintains a strict 1:1 balance (1 Human, 1 AI).
    """
    pairs_yielded = 0

    # 1. Stream from 'AI Generated Essays Dataset.csv'
    ai_essays_csv = os.path.join(AI_DIR, "AI Generated Essays Dataset.csv")
    if os.path.exists(ai_essays_csv):
        try:
            df = pd.read_csv(ai_essays_csv)
            ai_list = df[df["generated"] == 1]["text"].dropna().tolist()
            human_list = df[df["generated"] == 0]["text"].dropna().tolist()

            for h_text, a_text in zip(human_list, ai_list):
                if pairs_yielded < skip_pairs:
                    pairs_yielded += 1
                    continue
                yield (h_text.strip(), 0)
                yield (a_text.strip(), 1)
                pairs_yielded += 1
        except Exception as e:
            print(f"Warning reading {ai_essays_csv}: {e}")

    # 2. Stream from 'AI_Human.csv' (487,235 rows) in chunks
    ai_human_csv = os.path.join(HUMAN_DIR, "AI_Human.csv")
    if os.path.exists(ai_human_csv):
        print(f"Streaming from '{ai_human_csv}'...")
        chunk_size = 5000
        for chunk in pd.read_csv(ai_human_csv, chunksize=chunk_size):
            h_chunk = chunk[chunk["generated"] == 0.0]["text"].dropna().tolist()
            a_chunk = chunk[chunk["generated"] == 1.0]["text"].dropna().tolist()

            for h_text, a_text in zip(h_chunk, a_chunk):
                if pairs_yielded < skip_pairs:
                    pairs_yielded += 1
                    continue
                yield (h_text.strip(), 0)
                yield (a_text.strip(), 1)
                pairs_yielded += 1


def count_existing_samples() -> int:
    """
    Returns the number of rows currently in features.csv (excluding header).
    """
    if not os.path.exists(OUTPUT_FILE):
        return 0
    try:
        df = pd.read_csv(OUTPUT_FILE)
        return len(df)
    except Exception:
        return 0


def build_and_retrain_continuous(
    max_samples: int = None,
    retrain_every: int = 250,
    batch_size: int = 10,
    delay: float = 0.08
):
    """
    Industrial-grade, resumable dataset builder that extracts features
    and periodically retrains the classifier with GPU thermal safeguards.
    """
    existing_count = count_existing_samples()
    skip_pairs = existing_count // 2

    print("=" * 65)
    print("AI CONTENT DETECTOR - MASSIVE DATASET EXTRACTION PIPELINE")
    print("=" * 65)
    print(f"Target Output: {OUTPUT_FILE}")
    print(f"Existing Samples in CSV: {existing_count} (skipping first {skip_pairs} pairs)")
    print(f"Auto-Retrain Interval: Every {retrain_every} samples")
    print(f"Flush Batch Size: {batch_size} samples")
    if max_samples:
        print(f"Max Samples Target: {max_samples}")
    else:
        print("Max Samples Target: UNLIMITED (processing entire dataset)")
    print("=" * 65)

    print("\nWarming up FeatureExtractor...")
    extractor = FeatureExtractor()

    # If file doesn't exist, create it with headers
    if existing_count == 0:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        columns = FEATURE_NAMES + ["label"]
        pd.DataFrame(columns=columns).to_csv(OUTPUT_FILE, index=False)

    generator = balanced_sample_generator(skip_pairs=skip_pairs)

    buffer = []
    total_processed = existing_count
    session_count = 0
    last_retrain_count = existing_count
    start_time = time.time()

    print("\nStarting extraction loop...\n")

    for text, label in generator:
        if max_samples and total_processed >= max_samples:
            print(f"\nReached specified max_samples limit of {max_samples}.")
            break

        if not text or len(text.split()) < 10:
            continue

        try:
            feats = extractor.extract(text)
            row = dict(zip(FEATURE_NAMES, feats))
            row["label"] = label
            buffer.append(row)
            total_processed += 1
            session_count += 1

            # Console progress
            lbl_str = "AI   " if label == 1 else "Human"
            words = len(text.split())
            elapsed = time.time() - start_time
            speed = session_count / max(1e-3, elapsed)
            print(
                f"[Sample {total_processed:>6}] | Label: {lbl_str} | "
                f"Words: {words:>4} | Speed: {speed:4.2f} texts/sec | "
                f"Session: +{session_count}"
            )

            # Flush batch to CSV
            if len(buffer) >= batch_size:
                df_batch = pd.DataFrame(buffer, columns=FEATURE_NAMES + ["label"])
                df_batch.to_csv(OUTPUT_FILE, mode="a", header=False, index=False)
                buffer.clear()

            # Laptop Thermal Throttle & Memory Guard
            if delay > 0:
                time.sleep(delay)
            if session_count % 10 == 0:
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            if session_count % 50 == 0:
                clear_gpu_cache()
                time.sleep(0.4)  # Cooling breather for laptop fans

            # Auto-retrain periodically
            if total_processed - last_retrain_count >= retrain_every:
                # Flush buffer before training
                if buffer:
                    df_batch = pd.DataFrame(buffer, columns=FEATURE_NAMES + ["label"])
                    df_batch.to_csv(OUTPUT_FILE, mode="a", header=False, index=False)
                    buffer.clear()

                clear_gpu_cache()

                print("\n" + "#" * 65)
                print(f"[AUTO-RETRAIN TRIGGERED] Accumulated {total_processed} samples!")
                print("#" * 65)
                try:
                    train_classifier()
                    last_retrain_count = total_processed
                    print(f"[AUTO-RETRAIN COMPLETE] Model updated at: {MODEL_PATH}\n")
                except Exception as err:
                    print(f"Error during auto-retraining: {err}\n")

                clear_gpu_cache()
                time.sleep(1.0)  # Post-training cooldown

        except Exception as e:
            print(f"Warning: Failed sample extraction ({e}), skipping.")
            continue

    # Final flush
    if buffer:
        df_batch = pd.DataFrame(buffer, columns=FEATURE_NAMES + ["label"])
        df_batch.to_csv(OUTPUT_FILE, mode="a", header=False, index=False)
        buffer.clear()

    # Final Retrain
    print("\n" + "=" * 65)
    print(f"FINAL TRAINING ON FULL DATASET ({total_processed} SAMPLES)")
    print("=" * 65)
    train_classifier()
    clear_gpu_cache()
    print(f"\nAll operations completed! Final model saved to {MODEL_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract features from full datasets and retrain continuously.")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of samples to extract (default: None / Unlimited)")
    parser.add_argument("--retrain-every", type=int, default=250, help="Retrain model every N samples (default: 250)")
    parser.add_argument("--batch-size", type=int, default=10, help="Flush buffer size (default: 10)")
    parser.add_argument("--delay", type=float, default=0.08, help="Throttle delay in seconds between samples (default: 0.08)")
    args = parser.parse_args()

    build_and_retrain_continuous(
        max_samples=args.limit,
        retrain_every=args.retrain_every,
        batch_size=args.batch_size,
        delay=args.delay
    )

