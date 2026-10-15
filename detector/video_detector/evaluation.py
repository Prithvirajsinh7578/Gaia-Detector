"""
evaluation.py - Multi-Source Evaluation Pipeline for Hybrid Video AI Detection.
Measures performance for:
1. Custom Spatial-Temporal Classifier alone
2. Pretrained Hugging Face ResNet-50 T2V model alone
3. Sightengine Commercial API (when credentials present)
4. Calibrated Hybrid Ensemble
"""

import os
import glob
import json
import argparse
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    brier_score_loss
)

from hybrid_detector import HybridVideoDetector
from utils.constants import DATASET_PATH, FEATURE_NAMES, RAW_AUTHENTIC_DIR, RAW_AI_DIR


def compute_metrics(y_true: List[int], probabilities: List[float], threshold: float = 0.50) -> Dict[str, Any]:
    """Computes comprehensive binary classification and calibration metrics."""
    y_true_arr = np.array(y_true)
    y_prob_arr = np.array(probabilities)
    y_pred_arr = (y_prob_arr >= threshold).astype(int)

    acc = float(accuracy_score(y_true_arr, y_pred_arr))
    prec = float(precision_score(y_true_arr, y_pred_arr, zero_division=0))
    rec = float(recall_score(y_true_arr, y_pred_arr, zero_division=0))
    f1 = float(f1_score(y_true_arr, y_pred_arr, zero_division=0))

    try:
        auc = float(roc_auc_score(y_true_arr, y_prob_arr))
    except Exception:
        auc = 0.5

    brier = float(brier_score_loss(y_true_arr, y_prob_arr))
    cm = confusion_matrix(y_true_arr, y_pred_arr)
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
    else:
        tn, fp, fn, tp = 0, 0, 0, 0

    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

    return {
        "sample_count": len(y_true),
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(auc, 4),
        "brier_score": round(brier, 4),
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
        "confusion_matrix": {
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "true_positive": int(tp)
        }
    }


def evaluate_hybrid_pipeline(
    max_videos_per_class: int = 20,
    enable_custom: bool = True,
    enable_hf: bool = True,
    enable_sightengine: bool = False
) -> Dict[str, Any]:
    """
    Evaluates Custom alone, HF alone, and Ensemble side-by-side on held-out evaluation videos.
    """
    print("=" * 65)
    print("HYBRID VIDEO AI DETECTOR - SYSTEM EVALUATION PIPELINE")
    print("=" * 65)

    real_videos = sorted(glob.glob(os.path.join(RAW_AUTHENTIC_DIR, "*.*")))[:max_videos_per_class]
    ai_videos = sorted(glob.glob(os.path.join(RAW_AI_DIR, "*.*")))[:max_videos_per_class]

    if not real_videos or not ai_videos:
        print(f"Notice: Raw evaluation videos not found in {RAW_AUTHENTIC_DIR} and {RAW_AI_DIR}.")
        return {}

    print(f"Evaluating on {len(real_videos)} authentic and {len(ai_videos)} AI-generated videos...")

    detector = HybridVideoDetector(
        enable_custom=enable_custom,
        enable_hf=enable_hf,
        enable_sightengine=enable_sightengine
    )

    y_true = []
    scores_custom = []
    scores_hf = []
    scores_ensemble = []
    verdicts_ensemble = []

    test_items = [(p, 0) for p in real_videos] + [(p, 1) for p in ai_videos]

    for idx, (path, label) in enumerate(test_items, 1):
        filename = os.path.basename(path)
        print(f"[{idx}/{len(test_items)}] Processing {filename}...", end=" ", flush=True)

        res = detector.predict(path)
        y_true.append(label)

        ind = res.get("individual_detectors", {})

        # Custom score
        c_score = ind.get("custom_rf", {}).get("raw_score", 0.5) if "custom_rf" in ind else 0.5
        scores_custom.append(c_score)

        # HF score
        hf_score = ind.get("hf_resnet50_t2v", {}).get("raw_score", 0.5) if "hf_resnet50_t2v" in ind else 0.5
        scores_hf.append(hf_score)

        # Ensemble score & verdict
        ens_prob = res.get("ai_probability", 50.0) / 100.0
        scores_ensemble.append(ens_prob)
        verdicts_ensemble.append(res.get("verdict", "Inconclusive"))

        print(f"Custom={c_score*100:.1f}%, HF={hf_score*100:.1f}%, Ens={ens_prob*100:.1f}% -> {res.get('verdict')}")

    # Compute Comparative Metrics
    metrics_custom = compute_metrics(y_true, scores_custom) if enable_custom else None
    metrics_hf = compute_metrics(y_true, scores_hf) if enable_hf else None
    metrics_ensemble = compute_metrics(y_true, scores_ensemble)

    # Inconclusive analysis
    inconclusive_count = sum(1 for v in verdicts_ensemble if "Inconclusive" in v)
    conclusive_count = len(verdicts_ensemble) - inconclusive_count

    report = {
        "evaluation_dataset": {
            "real_videos": len(real_videos),
            "ai_videos": len(ai_videos),
            "total_evaluated": len(test_items)
        },
        "detectors_evaluated": {
            "custom_rf": enable_custom,
            "hf_resnet50_t2v": enable_hf,
            "sightengine_api": enable_sightengine
        },
        "comparative_metrics": {
            "custom_alone": metrics_custom,
            "hf_model_alone": metrics_hf,
            "hybrid_ensemble": metrics_ensemble
        },
        "uncertainty_policy_analysis": {
            "inconclusive_verdicts": inconclusive_count,
            "conclusive_verdicts": conclusive_count,
            "inconclusive_rate": round(inconclusive_count / len(test_items), 4)
        }
    }

    print("\n" + "=" * 65)
    print("COMPARATIVE EVALUATION SUMMARY")
    print("=" * 65)
    print(f"{'Metric':<24} | {'Custom Model':<14} | {'HF ResNet50':<14} | {'Hybrid Ensemble':<14}")
    print("-" * 72)
    for m in ["accuracy", "precision", "recall", "f1_score", "roc_auc", "false_positive_rate", "false_negative_rate"]:
        c_val = f"{metrics_custom[m]:.4f}" if metrics_custom else "N/A"
        h_val = f"{metrics_hf[m]:.4f}" if metrics_hf else "N/A"
        e_val = f"{metrics_ensemble[m]:.4f}"
        print(f"{m:<24} | {c_val:<14} | {h_val:<14} | {e_val:<14}")
    print("-" * 72)
    print(f"Inconclusive / Uncertain Rate: {round(inconclusive_count / len(test_items) * 100, 1)}% ({inconclusive_count}/{len(test_items)})\n")

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Hybrid Video AI Detector")
    parser.add_argument("--samples", type=int, default=15, help="Max samples per class to evaluate")
    parser.add_argument("--sightengine", action="store_true", help="Include Sightengine API in evaluation")
    args = parser.parse_args()

    evaluate_hybrid_pipeline(
        max_videos_per_class=args.samples,
        enable_custom=True,
        enable_hf=True,
        enable_sightengine=args.sightengine
    )
