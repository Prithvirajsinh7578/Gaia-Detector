"""
download_subset.py - Direct high-speed selective downloader for Kaggle AI vs Real dataset.
Handles direct signed GCS streaming and automatic single-file zip decompression.
"""

import os
import io
import sys
import time
import zipfile
import hashlib
import requests
import concurrent.futures
from pathlib import Path
from PIL import Image

from detector.image_detector.config import DATASET_DIR

BASE_URL = "https://www.kaggle.com/api/v1/datasets/download/tristanzhang32/ai-generated-images-vs-real-images"

# Target counts per split (Balanced 50/50 AI vs Authentic)
TARGETS = {
    "train": {"fake": 250, "real": 250},
    "validation": {"fake": 75, "real": 75},
    "test": {"fake": 75, "real": 75},
}


def compute_file_hash(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def extract_and_validate(raw_bytes: bytes) -> bytes | None:
    """Handles optional zip compression and validates image integrity."""
    img_bytes = raw_bytes
    if raw_bytes.startswith(b"PK"):
        try:
            with zipfile.ZipFile(io.BytesIO(raw_bytes)) as z:
                names = z.namelist()
                if names:
                    img_bytes = z.read(names[0])
        except Exception:
            return None

    try:
        with Image.open(io.BytesIO(img_bytes)) as img:
            img.verify()
        with Image.open(io.BytesIO(img_bytes)) as img:
            img.convert("RGB")
        return img_bytes
    except Exception:
        return None


def fetch_image_from_kaggle(remote_path: str, session: requests.Session) -> tuple[str, bytes | None]:
    try:
        r = session.get(BASE_URL, params={"fileName": remote_path, "datasetVersionNumber": 2}, timeout=15)
        if r.status_code == 200 and len(r.content) > 1024:
            valid_bytes = extract_and_validate(r.content)
            return remote_path, valid_bytes
    except Exception:
        pass
    return remote_path, None


def download_dataset_subset(max_workers: int = 16):
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    seen_hashes = set()
    session = requests.Session()

    # Pre-index existing files
    for split in ["train", "validation", "test"]:
        for label in ["authentic", "ai_generated"]:
            target_dir = DATASET_DIR / split / label
            target_dir.mkdir(parents=True, exist_ok=True)
            for f in target_dir.glob("*.jpg"):
                try:
                    seen_hashes.add(compute_file_hash(f.read_bytes()))
                except Exception:
                    pass

    # Ranges to prevent data leakage between train, val, and test
    ranges = {
        "train": {"fake": (1, 250), "real": (1, 250)},
        "validation": {"fake": (251, 325), "real": (251, 325)},
        "test": {"fake": (326, 400), "real": (326, 400)},
    }

    print(f"Downloading balanced dataset subset into: {DATASET_DIR}")

    for split, categories in TARGETS.items():
        for cat, target_count in categories.items():
            label = "ai_generated" if cat == "fake" else "authentic"
            target_dir = DATASET_DIR / split / label
            existing_files = list(target_dir.glob("*.jpg"))

            if len(existing_files) >= target_count:
                print(f"[{split}/{label}] Already has {len(existing_files)} images (target: {target_count}). Skipping.")
                continue

            needed = target_count - len(existing_files)
            start_num, end_num = ranges[split][cat]
            remote_prefix = "train" if split != "test" else "test"
            remote_paths = [f"{remote_prefix}/{cat}/{i:04d}.jpg" for i in range(start_num, end_num + 1)]

            print(f"[{split}/{label}] Downloading {needed} images from {remote_prefix}/{cat}/...")
            saved = 0
            t0 = time.time()

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(fetch_image_from_kaggle, p, session): p for p in remote_paths}
                for fut in concurrent.futures.as_completed(futures):
                    p, content = fut.result()
                    if content:
                        fhash = compute_file_hash(content)
                        if fhash in seen_hashes:
                            continue
                        seen_hashes.add(fhash)

                        save_path = target_dir / f"{split}_{cat}_{len(existing_files) + saved + 1:04d}.jpg"
                        with open(save_path, "wb") as f:
                            f.write(content)
                        saved += 1
                        if saved % 25 == 0 or saved == needed:
                            rate = saved / max(0.1, time.time() - t0)
                            print(f"  [{split}/{label}] Saved {saved}/{needed} ({rate:.1f} img/s)")

            print(f"[{split}/{label}] Completed: {saved} verified images written.")

    # Final Audit Summary
    print("\n" + "=" * 55)
    print("GAIA IMAGE DATASET SUMMARY")
    print("=" * 55)
    total_imgs = 0
    for s in ["train", "validation", "test"]:
        auth_c = len(list((DATASET_DIR / s / "authentic").glob("*.jpg")))
        ai_c = len(list((DATASET_DIR / s / "ai_generated").glob("*.jpg")))
        total_imgs += auth_c + ai_c
        print(f"  Split: {s.upper():<12} | Authentic: {auth_c:>4} | AI-Generated: {ai_c:>4} | Total: {auth_c + ai_c:>4}")
    print("-" * 55)
    print(f"Total Dataset Images: {total_imgs}")
    print(f"Target Directory: {DATASET_DIR}")
    print("=" * 55)


if __name__ == "__main__":
    download_dataset_subset(max_workers=16)
