"""
evaluate.py - Independent evaluation of Model 1, Model 2, Model 3, and the Three-Model Ensemble.
Evaluates strictly on the held-out test split (DATASET_DIR / "test") without data leakage.
"""

import os
import sys
import time
import json
import torch
import numpy as np
from pathlib import Path
from PIL import Image
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix
)

from detector.image_detector.ensemble import ImageEnsembleDetector
from detector.image_detector.config import DATASET_DIR, BASE_DIR

OUTPUT_REPORT_PATH = BASE_DIR / "evaluation_report.json"


def evaluate_system():
    print("=" * 65)
    print("GAIA DETECTOR — INDEPENDENT BENCHMARK EVALUATION")
    print("Evaluating Model 1, Model 2, Model 3 & Ensemble on Held-Out Test Set")
    print("=" * 65)

    test_dir = DATASET_DIR / "test"
    test_auth_dir = test_dir / "authentic"
    test_ai_dir = test_dir / "ai_generated"

    test_samples = []  # (path, true_label: 1 for AI, 0 for Authentic)
    for p in sorted(list(test_ai_dir.glob("*.jpg"))):
        test_samples.append((p, 1))
    for p in sorted(list(test_auth_dir.glob("*.jpg"))):
        test_samples.append((p, 0))

    if not test_samples:
        raise RuntimeError(f"No test images found in {test_dir}.")

    y_true = [s[1] for s in test_samples]
    total_samples = len(test_samples)
    ai_samples = sum(y_true)
    auth_samples = total_samples - ai_samples

    print(f"Independent Test Set Size: {total_samples} images")
    print(f"Class Distribution: {ai_samples} AI-Generated | {auth_samples} Authentic Photography/Art\n")

    # Initialize Ensemble
    print("Initializing Image Ensemble Models...")
    ensemble = ImageEnsembleDetector()

    # Track metrics for each model
    results_m1_probs, results_m1_preds, latencies_m1 = [], [], []
    results_m2_probs, results_m2_preds, latencies_m2 = [], [], []
    results_m3_probs, results_m3_preds, latencies_m3 = [], [], []
    results_ens_probs, results_ens_verdicts, latencies_ens = [], [], []

    print("Running Inference across test images...")
    start_all = time.time()

    for idx, (img_path, true_lbl) in enumerate(test_samples, 1):
        try:
            with Image.open(img_path) as img:
                img_rgb = img.convert("RGB")

                # Model 1
                r1 = ensemble.model_1.predict(img_rgb)
                results_m1_probs.append(r1.ai_probability / 100.0)
                results_m1_preds.append(1 if r1.ai_probability >= 50.0 else 0)
                latencies_m1.append(r1.latency_ms)

                # Model 2
                r2 = ensemble.model_2.predict(img_rgb)
                results_m2_probs.append(r2.ai_probability / 100.0)
                results_m2_preds.append(1 if r2.ai_probability >= 50.0 else 0)
                latencies_m2.append(r2.latency_ms)

                # Model 3
                r3 = ensemble.model_3.predict(img_rgb)
                results_m3_probs.append(r3.ai_probability / 100.0)
                results_m3_preds.append(1 if r3.ai_probability >= 50.0 else 0)
                latencies_m3.append(r3.latency_ms)

                # Full Ensemble
                t0_ens = time.time()
                ens_res = ensemble.predict(img_rgb)
                latencies_ens.append((time.time() - t0_ens) * 1000.0)

                pred_verdict = ens_res["prediction"]
                results_ens_verdicts.append(pred_verdict)
                ai_p = ens_res["details"]["ai_probability"] / 100.0
                results_ens_probs.append(ai_p)

        except Exception as e:
            print(f"Error on {img_path.name}: {e}")

        if idx % 25 == 0 or idx == total_samples:
            print(f"  Processed {idx}/{total_samples} test images...")

    def compute_metrics(y_true, y_pred, y_prob, latencies):
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred, zero_division=0)
        rec = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        try:
            auc = roc_auc_score(y_true, y_prob)
        except Exception:
            auc = 0.5

        return {
            "accuracy": round(float(acc) * 100.0, 2),
            "precision": round(float(prec) * 100.0, 2),
            "recall": round(float(rec) * 100.0, 2),
            "f1_score": round(float(f1), 4),
            "roc_auc": round(float(auc), 4),
            "confusion_matrix": {"TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp)},
            "false_positive_rate": round(float(fpr) * 100.0, 2),
            "false_negative_rate": round(float(fnr) * 100.0, 2),
            "mean_latency_ms": round(float(np.mean(latencies)), 1),
        }

    m1_metrics = compute_metrics(y_true, results_m1_preds, results_m1_probs, latencies_m1)
    m2_metrics = compute_metrics(y_true, results_m2_preds, results_m2_probs, latencies_m2)
    m3_metrics = compute_metrics(y_true, results_m3_preds, results_m3_probs, latencies_m3)

    # Ensemble metrics (with inconclusive handling)
    inconclusive_count = sum(1 for v in results_ens_verdicts if v == "INCONCLUSIVE")
    inconclusive_rate = (inconclusive_count / total_samples) * 100.0

    # Binary evaluation for definitive predictions
    definitive_indices = [i for i, v in enumerate(results_ens_verdicts) if v != "INCONCLUSIVE"]
    if definitive_indices:
        def_y_true = [y_true[i] for i in definitive_indices]
        def_y_pred = [1 if results_ens_verdicts[i] == "LIKELY_AI_GENERATED" else 0 for i in definitive_indices]
        def_y_prob = [results_ens_probs[i] for i in definitive_indices]
        def_latencies = [latencies_ens[i] for i in definitive_indices]
        ens_metrics = compute_metrics(def_y_true, def_y_pred, def_y_prob, def_latencies)
        ens_metrics["coverage_rate"] = round(100.0 - inconclusive_rate, 2)
        ens_metrics["inconclusive_rate"] = round(inconclusive_rate, 2)
        ens_metrics["inconclusive_count"] = inconclusive_count
    else:
        ens_metrics = {"inconclusive_rate": 100.0, "coverage_rate": 0.0}

    report = {
        "evaluation_dataset": "Held-Out Test Set (Tristan Zhang AI vs Real)",
        "total_test_images": total_samples,
        "classes": {"ai_generated": ai_samples, "authentic": auth_samples},
        "model_1_custom": {
            "name": ensemble.model_1.model_name,
            "architecture": "EfficientNet-B0 (Transfer Learning)",
            "metrics": m1_metrics,
        },
        "model_2_hf_swin": {
            "name": ensemble.model_2.model_name,
            "architecture": "Swin-V2 Transformer",
            "license": "Apache 2.0",
            "metrics": m2_metrics,
        },
        "model_3_complementary": {
            "name": ensemble.model_3.model_name,
            "architecture": "SigLIP Vision Transformer",
            "license": "Apache 2.0",
            "metrics": m3_metrics,
        },
        "three_model_ensemble": {
            "name": "Gaia 3-Model Weighted Image Consensus",
            "metrics": ens_metrics,
        }
    }

    with open(OUTPUT_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Print Summary Table
    print("\n" + "=" * 65)
    print("GAIA DETECTOR — IMAGE SYSTEM BENCHMARK RESULTS")
    print("=" * 65)
    header = f"{'Model':<28} | {'Acc (%)':<8} | {'Prec (%)':<8} | {'Recall (%)':<10} | {'F1':<6} | {'AUC':<6} | {'Lat (ms)'}"
    print(header)
    print("-" * len(header))
    print(f"{'Model 1 (Custom EfficientNet)':<28} | {m1_metrics['accuracy']:<8.1f} | {m1_metrics['precision']:<8.1f} | {m1_metrics['recall']:<10.1f} | {m1_metrics['f1_score']:<6.3f} | {m1_metrics['roc_auc']:<6.3f} | {m1_metrics['mean_latency_ms']}")
    print(f"{'Model 2 (Swin Transformer)':<28} | {m2_metrics['accuracy']:<8.1f} | {m2_metrics['precision']:<8.1f} | {m2_metrics['recall']:<10.1f} | {m2_metrics['f1_score']:<6.3f} | {m2_metrics['roc_auc']:<6.3f} | {m2_metrics['mean_latency_ms']}")
    print(f"{'Model 3 (SigLIP Transformer)':<28} | {m3_metrics['accuracy']:<8.1f} | {m3_metrics['precision']:<8.1f} | {m3_metrics['recall']:<10.1f} | {m3_metrics['f1_score']:<6.3f} | {m3_metrics['roc_auc']:<6.3f} | {m3_metrics['mean_latency_ms']}")
    if "accuracy" in ens_metrics:
        print(f"{'Three-Model Ensemble':<28} | {ens_metrics['accuracy']:<8.1f} | {ens_metrics['precision']:<8.1f} | {ens_metrics['recall']:<10.1f} | {ens_metrics['f1_score']:<6.3f} | {ens_metrics['roc_auc']:<6.3f} | {ens_metrics['mean_latency_ms']}")
        print(f"  * Ensemble Coverage: {ens_metrics['coverage_rate']}% | Inconclusive Rate: {ens_metrics['inconclusive_rate']}%")
    print("=" * 65)
    print(f"Detailed JSON report saved to: {OUTPUT_REPORT_PATH}")
    return report


if __name__ == "__main__":
    evaluate_system()
