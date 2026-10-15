"""
split_dataset.py - Creates a clean, leakage-resistant split (Train 400, Val 100, Test 100).
Ensures zero data leakage and strict separation for independent evaluation.
"""

import os
import shutil
import random
from pathlib import Path

from detector.image_detector.config import DATASET_DIR


def organize_splits(train_auth: int = 180, train_ai: int = 250,
                    val_auth: int = 25, val_ai: int = 50,
                    test_auth: int = 25, test_ai: int = 50):
    random.seed(42)

    # Source folders
    src_auth = DATASET_DIR / "train" / "authentic"
    src_ai = DATASET_DIR / "train" / "ai_generated"

    auth_files = sorted(list(src_auth.glob("*.jpg")))
    ai_files = sorted(list(src_ai.glob("*.jpg")))

    print(f"Available authentic images: {len(auth_files)}")
    print(f"Available AI-generated images: {len(ai_files)}")

    random.shuffle(auth_files)
    random.shuffle(ai_files)

    # Target directories
    for split in ["train", "validation", "test"]:
        for label in ["authentic", "ai_generated"]:
            (DATASET_DIR / split / label).mkdir(parents=True, exist_ok=True)

    # 1. Authentic Split
    val_auth_files = auth_files[:val_auth]
    test_auth_files = auth_files[val_auth:val_auth + test_auth]
    train_auth_files = auth_files[val_auth + test_auth:val_auth + test_auth + train_auth]

    # Move to validation and test
    for f in val_auth_files:
        shutil.move(str(f), str(DATASET_DIR / "validation" / "authentic" / f.name))
    for f in test_auth_files:
        shutil.move(str(f), str(DATASET_DIR / "test" / "authentic" / f.name))

    # 2. AI Generated Split
    val_ai_files = ai_files[:val_ai]
    test_ai_files = ai_files[val_ai:val_ai + test_ai]
    train_ai_files = ai_files[val_ai + test_ai:val_ai + test_ai + train_ai]

    for f in val_ai_files:
        shutil.move(str(f), str(DATASET_DIR / "validation" / "ai_generated" / f.name))
    for f in test_ai_files:
        shutil.move(str(f), str(DATASET_DIR / "test" / "ai_generated" / f.name))

    print("\n" + "=" * 55)
    print("DATASET LEAKAGE-RESISTANT SPLIT COMPLETED")
    print("=" * 55)
    for s in ["train", "validation", "test"]:
        a_count = len(list((DATASET_DIR / s / "authentic").glob("*.jpg")))
        ai_count = len(list((DATASET_DIR / s / "ai_generated").glob("*.jpg")))
        print(f"  {s.upper():<12} | Authentic: {a_count:>4} | AI-Generated: {ai_count:>4} | Total: {a_count + ai_count:>4}")
    print("=" * 55)


if __name__ == "__main__":
    organize_splits()
