"""
evaluation.py - Rigorous Evaluation and Benchmarking Pipeline for Text Detectors.
Evaluates:
1. Custom 18-Feature Random Forest Classifier Alone
2. Pretrained Hugging Face RoBERTa Model Alone
3. Hybrid Multi-Model Ensemble

Computes Accuracy, Precision, Recall, F1-Score, ROC-AUC, FPR, FNR, and Inconclusive Rate.
"""

import os
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
os.environ["OPENBLAS_NUM_THREADS"] = "2"
os.environ["VECLIB_MAXIMUM_THREADS"] = "2"
os.environ["NUMEXPR_NUM_THREADS"] = "2"

import sys
import time
import argparse
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)
from utils.constants import DATASET_PATH, FEATURE_NAMES

AI_DIR = "datasets/raw/ai"
HUMAN_DIR = "datasets/raw/human"


def load_heldout_text_samples(samples_per_class: int = 10) -> List[Dict[str, Any]]:
    """Loads held-out text samples with verifiable ground-truth labels."""
    samples = []

    # 1. Load from AI Generated Essays Dataset.csv if present
    ai_essays_csv = os.path.join(AI_DIR, "AI Generated Essays Dataset.csv")
    if os.path.exists(ai_essays_csv):
        df = pd.read_csv(ai_essays_csv)
        human_texts = df[df["generated"] == 0]["text"].dropna().tolist()
        ai_texts = df[df["generated"] == 1]["text"].dropna().tolist()

        # Take from the tail (held-out)
        for t in human_texts[-samples_per_class:]:
            samples.append({"text": t.strip(), "label": 0, "source": "essay_human"})
        for t in ai_texts[-samples_per_class:]:
            samples.append({"text": t.strip(), "label": 1, "source": "essay_ai"})

    # Fallback to synthetic standard samples if raw CSV is unavailable
    if not samples:
        human_fallbacks = [
            "Yesterday my family and I went to the farmers market on the corner of Elm Street to pick up fresh organic peaches and sourdough bread.",
            "I have been thinking a lot lately about how our habits shape our daily lives in ways we rarely notice until we actively attempt to change them.",
            "The novel's protagonist struggles throughout the middle chapters with feelings of inadequacy and loneliness, which makes her eventual triumph feel earned.",
            "In last week's lab session, our chemistry group struggled to calibrate the spectrophotometer properly, leading to some skewed initial absorbance readings.",
            "Whenever it rains on a Sunday afternoon, I find myself making a hot cup of black tea and reading through old paperback mysteries."
        ]
        ai_fallbacks = [
            "Artificial intelligence in modern pedagogy facilitates individualized instructional pacing, empowering educators to address specific learner deficits with precision.",
            "Sustainable urban development necessitates a comprehensive integration of multimodal transit systems and high-density, energy-efficient architectural paradigms.",
            "Quantum computational frameworks leverage superposition and entanglement to execute complex parallel factorizations far beyond the capabilities of classical Turing architectures.",
            "The symbiotic relationship between cloud-native microservices and container orchestration engines exemplifies modern resilience and horizontal elasticity in software engineering.",
            "Technological advancements in decentralized cryptographic ledgers offer verifiable immutability, thereby redefining contemporary transactional trust protocols."
        ]
        for t in human_fallbacks[:samples_per_class]:
            samples.append({"text": t, "label": 0, "source": "synthetic_human"})
        for t in ai_fallbacks[:samples_per_class]:
            samples.append({"text": t, "label": 1, "source": "synthetic_ai"})

    return samples


def compute_metrics(y_true: List[int], y_pred: List[int], y_prob: List[float]) -> Dict[str, float]:
    """Computes comprehensive binary classification metrics."""
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    try:
        auc = roc_auc_score(y_true, y_prob)
    except Exception:
        auc = 0.5

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

    return {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(auc, 4),
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4)
    }


def run_evaluation(samples_per_class: int = 8):
    print("=" * 65)
    print("GAIA DETECTOR - HYBRID AI TEXT DETECTION EVALUATION PIPELINE")
    print("=" * 65)

    samples = load_heldout_text_samples(samples_per_class=samples_per_class)
    print(f"Loaded {len(samples)} evaluation samples ({samples_per_class} Human, {samples_per_class} AI).\n")

    # Check if live server is running on port 8000 to reuse loaded models
    use_live_server = False
    import urllib.request
    import json
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2) as resp:
            if resp.status == 200:
                use_live_server = True
                print("Connected to live Gaia Text Detector service on http://127.0.0.1:8000")
    except Exception:
        use_live_server = False

    custom_adapter = None
    hf_detector = None
    ensemble = None

    if not use_live_server:
        print("Live server not detected. Initializing local model instances...")
        from detectors.custom_text_adapter import CustomTextAdapter
        from detectors.hf_text_detector import HFTextDetector
        from ensemble import HybridTextEnsemble

        custom_adapter = CustomTextAdapter()
        hf_detector = HFTextDetector()
        ensemble = HybridTextEnsemble()

    y_true = [s["label"] for s in samples]

    custom_probs, custom_preds = [], []
    hf_probs, hf_preds = [], []
    ensemble_probs, ensemble_preds = [], []
    inconclusive_count = 0

    print("\nRunning inference across evaluation benchmark...")
    for i, s in enumerate(samples, 1):
        text = s["text"]
        label = s["label"]
        lbl_str = "AI" if label == 1 else "Human"

        if use_live_server:
            req_data = json.dumps({"text": text}).encode("utf-8")
            req = urllib.request.Request(
                "http://127.0.0.1:8000/detect",
                data=req_data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))

            c_ai_prob = res_json["individual_detectors"]["custom_rf"]["ai_probability"]
            hf_ai_prob = res_json["individual_detectors"]["hf_roberta"]["ai_probability"]
            ens_ai_prob = res_json["probability"]
            ens_verdict = res_json["verdict"]
        else:
            c_res = custom_adapter.predict(text)
            c_ai_prob = c_res.ai_probability

            hf_res = hf_detector.predict(text)
            hf_ai_prob = hf_res.ai_probability

            ens_res = ensemble.combine([c_res, hf_res])
            ens_ai_prob = ens_res.ai_probability
            ens_verdict = ens_res.verdict

        # 1. Custom
        c_prob = c_ai_prob / 100.0
        c_pred = 1 if c_ai_prob >= 50.0 else 0
        custom_probs.append(c_prob)
        custom_preds.append(c_pred)

        # 2. HF
        hf_prob = hf_ai_prob / 100.0
        hf_pred = 1 if hf_ai_prob >= 50.0 else 0
        hf_probs.append(hf_prob)
        hf_preds.append(hf_pred)

        # 3. Ensemble
        ens_prob = ens_ai_prob / 100.0
        if ens_verdict == "Likely AI-generated":
            ens_pred = 1
        elif ens_verdict == "Likely Human-written":
            ens_pred = 0
        else:
            inconclusive_count += 1
            ens_pred = 1 if ens_prob >= 0.50 else 0

        ensemble_probs.append(ens_prob)
        ensemble_preds.append(ens_pred)

        status_str = f"[{i}/{len(samples)}] Actual: {lbl_str.ljust(5)} | Custom: {c_ai_prob:4.1f}% | HF: {hf_ai_prob:4.1f}% | Ensemble: {ens_ai_prob:4.1f}% -> {ens_verdict}"
        print(status_str)

    # Compute Metrics
    c_metrics = compute_metrics(y_true, custom_preds, custom_probs)
    hf_metrics = compute_metrics(y_true, hf_preds, hf_probs)
    ens_metrics = compute_metrics(y_true, ensemble_preds, ensemble_probs)

    print("\n" + "=" * 65)
    print("COMPARATIVE EVALUATION SUMMARY")
    print("=" * 65)
    header = f"{'Metric':<24} | {'Custom Model':<14} | {'HF RoBERTa':<14} | {'Hybrid Ensemble':<14}"
    print(header)
    print("-" * len(header))

    for k in ["accuracy", "precision", "recall", "f1_score", "roc_auc", "false_positive_rate", "false_negative_rate"]:
        print(f"{k:<24} | {c_metrics[k]:<14.4f} | {hf_metrics[k]:<14.4f} | {ens_metrics[k]:<14.4f}")

    inconclusive_pct = (inconclusive_count / len(samples)) * 100.0
    print("-" * len(header))
    print(f"Inconclusive / Uncertain Rate: {inconclusive_pct:.1f}% ({inconclusive_count}/{len(samples)})\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate text detectors")
    parser.add_argument("--samples", type=int, default=8, help="Number of samples per class")
    args = parser.parse_args()
    run_evaluation(samples_per_class=args.samples)
