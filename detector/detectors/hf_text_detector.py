"""
hf_text_detector.py - Dedicated Pretrained Transformer AI Text Detector Module.
Integrates RoBERTa AI-detection architecture (e.g. openai-community/roberta-base-openai-detector)
with overlapping window chunking, verified class-mapping, GPU/CPU acceleration, and long-text aggregation.
"""

import os
import time
import math
import torch
import numpy as np
from typing import Dict, Any, Optional, List
from pathlib import Path

from .base_detector import BaseTextDetector, DetectorResult

# Safe environment default
DEFAULT_MODEL_REPO = "openai-community/roberta-base-openai-detector"
MAX_SEQ_LENGTH = 512
CHUNK_SIZE = 480
CHUNK_STRIDE = 360  # 120 token overlap


class HFTextDetector(BaseTextDetector):
    """
    Dedicated Pretrained Transformer AI Text Detection Engine.
    Handles tokenization, sliding-window chunking, verified label mapping, and score aggregation.
    """

    def __init__(
        self,
        model_id: str = DEFAULT_MODEL_REPO,
        device: Optional[str] = None
    ):
        self.detector_id = "hf_roberta"
        self.name = "Pretrained RoBERTa AI Text Classifier"
        self.category = "pretrained_hf"
        self.model_id = os.getenv("HF_TEXT_MODEL_REPO", model_id).strip()

        # Hardware selection
        if device:
            self.device = device
        else:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.tokenizer = None
        self.model = None
        self.is_initialized = False
        self.initialization_error = None
        self.ai_class_index = 0  # 0 is 'Fake' (AI) in openai-community/roberta-base-openai-detector
        self.human_class_index = 1

        self._load_model()

    def _load_model(self):
        """Loads model and tokenizer once with local caching and label verification."""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification

            print(f"[HF Text Detector] Loading tokenizer & model from '{self.model_id}' on {self.device}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_id)
            self.model.to(self.device)
            self.model.eval()

            # Verify and adapt to the model's exact label2id mapping
            id2label = getattr(self.model.config, "id2label", {0: "Fake", 1: "Real"})
            label2id = getattr(self.model.config, "label2id", {"Fake": 0, "Real": 1})

            # Check where AI/Fake maps
            for idx, label_name in id2label.items():
                lbl = str(label_name).lower()
                if lbl in {"fake", "ai", "chatgpt", "generated", "machine"}:
                    self.ai_class_index = int(idx)
                elif lbl in {"real", "human", "authentic", "original"}:
                    self.human_class_index = int(idx)

            print(f"[HF Text Detector] Model successfully loaded on {self.device}. "
                  f"AI class index: {self.ai_class_index} ('{id2label.get(self.ai_class_index, 'Fake')}'), "
                  f"Human class index: {self.human_class_index} ('{id2label.get(self.human_class_index, 'Real')}')")
            self.is_initialized = True

        except Exception as e:
            self.initialization_error = str(e)
            self.is_initialized = False
            print(f"[HF Text Detector] Model initialization failed / pending: {e}")

    def _chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Tokenizes text and divides it into overlapping windows if it exceeds MAX_SEQ_LENGTH.
        Returns list of token input dictionaries.
        """
        encoded = self.tokenizer(
            text,
            return_tensors="pt",
            add_special_tokens=True,
            truncation=False
        )

        input_ids = encoded["input_ids"][0]
        attention_mask = encoded["attention_mask"][0]
        total_tokens = len(input_ids)

        if total_tokens <= MAX_SEQ_LENGTH:
            return [{
                "input_ids": input_ids.unsqueeze(0),
                "attention_mask": attention_mask.unsqueeze(0),
                "token_count": total_tokens
            }]

        chunks = []
        start_idx = 0
        while start_idx < total_tokens:
            end_idx = min(start_idx + CHUNK_SIZE, total_tokens)
            chunk_ids = input_ids[start_idx:end_idx]
            chunk_mask = attention_mask[start_idx:end_idx]

            # Ensure special tokens [CLS] / [SEP] boundary safety
            cls_token = input_ids[0].unsqueeze(0)
            sep_token = input_ids[-1].unsqueeze(0)

            # Pad / format if needed
            if chunk_ids[0] != cls_token[0]:
                chunk_ids = torch.cat([cls_token, chunk_ids])
                chunk_mask = torch.cat([torch.tensor([1]), chunk_mask])
            if chunk_ids[-1] != sep_token[0]:
                chunk_ids = torch.cat([chunk_ids, sep_token])
                chunk_mask = torch.cat([chunk_mask, torch.tensor([1])])

            # Truncate if special tokens pushed it slightly over 512
            chunk_ids = chunk_ids[:MAX_SEQ_LENGTH].unsqueeze(0)
            chunk_mask = chunk_mask[:MAX_SEQ_LENGTH].unsqueeze(0)

            chunks.append({
                "input_ids": chunk_ids,
                "attention_mask": chunk_mask,
                "token_count": len(chunk_ids[0])
            })

            if end_idx >= total_tokens:
                break
            start_idx += CHUNK_STRIDE

        return chunks

    def predict(self, text: str) -> DetectorResult:
        start_time = time.time()

        if not text or not text.strip():
            return DetectorResult(
                detector_id=self.detector_id,
                name=self.name,
                category=self.category,
                status="skipped",
                ai_probability=0.0,
                human_probability=100.0,
                raw_score=0.0,
                verdict="Invalid / Empty Input",
                confidence="None",
                latency_ms=0.0,
                analyzed_chars=0,
                error_message="Input text was empty."
            )

        if not self.is_initialized or self.model is None:
            # Try lazy re-initialization if weights finished downloading
            self._load_model()

        if not self.is_initialized or self.model is None:
            return DetectorResult(
                detector_id=self.detector_id,
                name=self.name,
                category=self.category,
                status="failed",
                ai_probability=50.0,
                human_probability=50.0,
                raw_score=0.5,
                verdict="Inconclusive / Uncertain",
                confidence="None",
                latency_ms=(time.time() - start_time) * 1000.0,
                analyzed_chars=len(text),
                error_message=f"Pretrained weights unavailable or downloading: {self.initialization_error}"
            )

        try:
            chunks = self._chunk_text(text)
            chunk_ai_scores = []
            total_tokens = sum(c["token_count"] for c in chunks)

            with torch.no_grad():
                for c in chunks:
                    input_ids = c["input_ids"].to(self.device)
                    attention_mask = c["attention_mask"].to(self.device)

                    outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                    logits = outputs.logits[0]
                    probs = torch.softmax(logits, dim=-1)

                    # Extract AI probability
                    ai_score = float(probs[self.ai_class_index].item())
                    chunk_ai_scores.append(ai_score)

                    del input_ids, attention_mask, outputs

            # Aggregate chunk predictions: Robust median-mean blend
            if len(chunk_ai_scores) == 1:
                aggregated_score = chunk_ai_scores[0]
            else:
                median_score = float(np.median(chunk_ai_scores))
                mean_score = float(np.mean(chunk_ai_scores))
                aggregated_score = (0.6 * median_score) + (0.4 * mean_score)

            ai_prob_pct = round(aggregated_score * 100.0, 1)
            human_prob_pct = round(max(0.0, 100.0 - ai_prob_pct), 1)

            # Assign calibrated verdict and confidence
            is_short = (len(text.split()) < 30) or (len(text) < 150)
            if ai_prob_pct >= 75.0:
                verdict = "Likely AI-generated"
                confidence = "High" if not is_short else "Low"
            elif ai_prob_pct <= 25.0:
                verdict = "Likely Human-written"
                confidence = "High" if not is_short else "Low"
            elif ai_prob_pct >= 55.0:
                verdict = "Possibly AI-generated"
                confidence = "Medium" if not is_short else "Low"
            else:
                verdict = "Inconclusive / Uncertain"
                confidence = "Low"

            indicators = []
            if ai_prob_pct >= 65.0:
                indicators.append(f"RoBERTa transformer detected synthetic token sequences ({ai_prob_pct}% probability)")
            elif ai_prob_pct <= 35.0:
                indicators.append(f"RoBERTa token distribution aligns with natural human prose ({human_prob_pct}% human probability)")
            else:
                indicators.append("RoBERTa token representation borders statistical neutrality")

            if len(chunks) > 1:
                indicators.append(f"Document chunking active: evaluated {len(chunks)} overlapping windows across {total_tokens} tokens")
            if is_short:
                indicators.append("Short text caveat: limited token length reduces transformer discrimination power")

            latency_ms = (time.time() - start_time) * 1000.0

            return DetectorResult(
                detector_id=self.detector_id,
                name=self.name,
                category=self.category,
                status="success",
                ai_probability=ai_prob_pct,
                human_probability=human_prob_pct,
                raw_score=aggregated_score,
                is_calibrated=True,
                verdict=verdict,
                confidence=confidence,
                latency_ms=latency_ms,
                analyzed_tokens=total_tokens,
                analyzed_chars=len(text),
                indicators=indicators,
                metadata={
                    "model_id": self.model_id,
                    "device": self.device,
                    "chunks_count": len(chunks),
                    "chunk_ai_scores": [round(s, 4) for s in chunk_ai_scores],
                    "is_short_text": is_short,
                    "ai_class_label": "Fake/AI"
                }
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000.0
            return DetectorResult(
                detector_id=self.detector_id,
                name=self.name,
                category=self.category,
                status="failed",
                ai_probability=50.0,
                human_probability=50.0,
                raw_score=0.5,
                verdict="Inconclusive / Uncertain",
                confidence="None",
                latency_ms=latency_ms,
                analyzed_chars=len(text),
                error_message=f"HF RoBERTa inference exception: {str(e)}"
            )
