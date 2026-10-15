"""
train.py - Training pipeline for Model 1 (Gaia Custom EfficientNet-B0 Classifier).
Includes dataset validation, training augmentations, mixed precision, early stopping,
checkpoint saving, and validation-based probability calibration.
"""

import os
import sys
import time
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as T
from pathlib import Path
from PIL import Image
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

from detector.image_detector.models.custom_classifier import GaiaImageClassifier
from detector.image_detector.config import (
    DATASET_DIR, CHECKPOINT_PATH, METADATA_PATH, DEVICE, USE_AMP,
    IMAGE_SIZE, BATCH_SIZE, NUM_EPOCHS, LEARNING_RATE, WEIGHT_DECAY,
    EARLY_STOPPING_PATIENCE
)


class ImageFolderBinaryDataset(Dataset):
    """Loads images labeled 1 for ai_generated and 0 for authentic."""

    def __init__(self, root_dir: Path, transform=None):
        self.samples = []
        self.transform = transform

        ai_dir = root_dir / "ai_generated"
        auth_dir = root_dir / "authentic"

        if ai_dir.exists():
            for p in ai_dir.glob("*.jpg"):
                self.samples.append((str(p), 1.0))
        if auth_dir.exists():
            for p in auth_dir.glob("*.jpg"):
                self.samples.append((str(p), 0.0))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        try:
            with Image.open(path) as img:
                img = img.convert("RGB")
                if self.transform:
                    img = self.transform(img)
                return img, torch.tensor(label, dtype=torch.float32)
        except Exception:
            # Fallback to zero tensor if image fails
            blank = torch.zeros((3, IMAGE_SIZE[0], IMAGE_SIZE[1]), dtype=torch.float32)
            return blank, torch.tensor(label, dtype=torch.float32)


def calibrate_temperature(model: GaiaImageClassifier, val_loader: DataLoader, device: torch.device) -> float:
    """Finds optimal temperature scaling factor on validation logits to minimize NLL."""
    model.eval()
    logits_list = []
    labels_list = []

    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(device)
            out = model(images).squeeze(-1)
            logits_list.append(out.cpu())
            labels_list.append(labels)

    logits = torch.cat(logits_list)
    labels = torch.cat(labels_list)

    # Simple grid search over temperature values 0.5 to 3.0
    best_temp = 1.0
    best_loss = float("inf")
    criterion = nn.BCEWithLogitsLoss()

    for temp in [0.5, 0.7, 0.85, 1.0, 1.15, 1.3, 1.5, 1.8, 2.0, 2.5]:
        loss = criterion(logits / temp, labels).item()
        if loss < best_loss:
            best_loss = loss
            best_temp = temp

    return round(best_temp, 3)


def train_custom_model():
    print("=" * 60)
    print("GAIA DETECTOR — MODEL 1 TRAINING PIPELINE")
    print(f"Device: {DEVICE.upper()} | Mixed Precision: {USE_AMP}")
    print("=" * 60)

    train_dir = DATASET_DIR / "train"
    val_dir = DATASET_DIR / "validation"

    # Data Transforms
    train_transform = T.Compose([
        T.Resize(IMAGE_SIZE),
        T.RandomHorizontalFlip(p=0.5),
        T.RandomRotation(degrees=10),
        T.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    val_transform = T.Compose([
        T.Resize(IMAGE_SIZE),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    train_dataset = ImageFolderBinaryDataset(train_dir, transform=train_transform)
    val_dataset = ImageFolderBinaryDataset(val_dir, transform=val_transform)

    if len(train_dataset) == 0:
        raise RuntimeError(f"Train dataset is empty in {train_dir}. Please run download_subset.py first.")

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    print(f"Dataset Loaded: {len(train_dataset)} training samples | {len(val_dataset)} validation samples.")

    # Initialize model
    device = torch.device(DEVICE)
    model = GaiaImageClassifier(pretrained=True, dropout_rate=0.3).to(device)

    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=NUM_EPOCHS, eta_min=1e-6)
    scaler = torch.amp.GradScaler("cuda", enabled=USE_AMP)

    best_val_loss = float("inf")
    patience_counter = 0
    history = []

    print("\nStarting Training...")
    start_train_time = time.time()

    for epoch in range(1, NUM_EPOCHS + 1):
        epoch_start = time.time()
        model.train()
        train_loss = 0.0

        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            with torch.amp.autocast("cuda", enabled=USE_AMP):
                logits = model(images).squeeze(-1)
                loss = criterion(logits, labels)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            train_loss += loss.item() * len(labels)

        scheduler.step()
        train_loss /= len(train_dataset)

        # Validation
        model.eval()
        val_loss = 0.0
        all_preds = []
        all_probs = []
        all_labels = []

        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.to(device)

                with torch.amp.autocast("cuda", enabled=USE_AMP):
                    logits = model(images).squeeze(-1)
                    loss = criterion(logits, labels)

                val_loss += loss.item() * len(labels)
                probs = torch.sigmoid(logits)
                preds = (probs >= 0.5).long()

                all_probs.extend(probs.cpu().tolist())
                all_preds.extend(preds.cpu().tolist())
                all_labels.extend(labels.cpu().tolist())

        val_loss /= len(val_dataset)
        val_acc = accuracy_score(all_labels, all_preds)
        val_f1 = f1_score(all_labels, all_preds, zero_division=0)
        try:
            val_auc = roc_auc_score(all_labels, all_probs)
        except Exception:
            val_auc = 0.5

        epoch_time = time.time() - epoch_start
        print(f"Epoch {epoch:02d}/{NUM_EPOCHS:02d} [{epoch_time:.1f}s] | "
              f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | "
              f"Val Acc: {val_acc * 100:.2f}% | Val F1: {val_f1:.4f} | Val AUC: {val_auc:.4f}")

        history.append({
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "val_loss": round(val_loss, 4),
            "val_accuracy": round(val_acc, 4),
            "val_f1": round(val_f1, 4),
            "val_auc": round(val_auc, 4),
        })

        # Checkpoint saving
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), CHECKPOINT_PATH)
            print(f"  -> Saved new best model checkpoint to {CHECKPOINT_PATH.name}")
        else:
            patience_counter += 1
            if patience_counter >= EARLY_STOPPING_PATIENCE:
                print(f"Early stopping triggered at epoch {epoch}.")
                break

    total_training_sec = time.time() - start_train_time
    print(f"\nTraining completed in {total_training_sec:.1f}s.")

    # Load best checkpoint and perform calibration
    print("\nPerforming post-hoc probability calibration on validation split...")
    best_state = torch.load(CHECKPOINT_PATH, map_location=device)
    model.load_state_dict(best_state)
    optimal_temperature = calibrate_temperature(model, val_loader, device)
    model.set_temperature(optimal_temperature)
    print(f"Calibrated Optimal Temperature: {optimal_temperature}")

    # Save comprehensive metadata
    metadata = {
        "model_name": "Gaia Custom EfficientNet-B0 Classifier",
        "architecture": "efficientnet_b0",
        "trained_date": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "total_training_time_sec": round(total_training_sec, 2),
        "dataset": "tristanzhang32/ai-generated-images-vs-real-images",
        "train_samples": len(train_dataset),
        "validation_samples": len(val_dataset),
        "best_val_loss": round(best_val_loss, 4),
        "calibration": {
            "method": "temperature_scaling",
            "temperature": optimal_temperature,
        },
        "history": history,
        "input_resolution": list(IMAGE_SIZE),
        "normalization": {
            "mean": [0.485, 0.456, 0.406],
            "std": [0.229, 0.224, 0.225],
        }
    }

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Model metadata saved to: {METADATA_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    train_custom_model()
