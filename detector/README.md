# Gaia Detector: Hybrid AI-Generated Text Detection System

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-green.svg)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-CUDA%20Accelerated-orange.svg)](https://pytorch.org/)
[![Transformers](https://img.shields.io/badge/HuggingFace-RoBERTa-yellow.svg)](https://huggingface.co/openai-community/roberta-base-openai-detector)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

---

## 1. Architectural Overview

Gaia Detector's Text Detection subsystem has been upgraded from a single engineered-feature Random Forest model into an industrial-grade **Hybrid Multi-Model Ensemble**. Rather than relying on a single heuristic or a single deep learning checkpoint, the hybrid system synthesizes three independent streams of evidence:

```
                                  Input Text
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│  Custom Detector │        │ Pretrained HF    │        │ Commercial API   │
│  (18 Features +  │        │ (RoBERTa Base    │        │ (GPTZero API v2  │
│  Random Forest)  │        │ OpenAI Detector) │        │  Optional Client)│
└────────┬─────────┘        └────────┬─────────┘        └────────┬─────────┘
         │                           │                           │
         │ Feature Vector (18)       │ Sliding Window (512 tok)  │ External REST
         │ Stylometric/Perplexity    │ Token Distribution        │ Multidimensional
         ▼                           ▼                           ▼
┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│  DetectorResult  │        │  DetectorResult  │        │  DetectorResult  │
│  Score: [0, 100] │        │  Score: [0, 100] │        │  Score: [0, 100] │
└────────┬─────────┘        └────────┬─────────┘        └────────┬─────────┘
         │                           │                           │
         └───────────────────────────┼───────────────────────────┘
                                     ▼
                   ┌───────────────────────────────────┐
                   │    Hybrid Multi-Model Ensemble    │
                   │  - Dynamic Weight Normalization   │
                   │  - Cross-Model Consensus Meter    │
                   │  - High-Divergence Conflict Guard │
                   │  - Short-Text Confidence Penalty  │
                   └─────────────────┬─────────────────┘
                                     ▼
                   ┌───────────────────────────────────┐
                   │          Final Verdict            │
                   │  - Likely AI-Generated (>=65%)    │
                   │  - Likely Human-Written (<=35%)   │
                   │  - Inconclusive / Uncertain       │
                   └───────────────────────────────────┘
```

---

## 2. Detection Components

### Component A: Preserved 18-Feature Custom Classifier
- **Model Architecture**: Scikit-Learn `RandomForestClassifier` (`models/classifier.pkl`) trained on engineered linguistic distributions.
- **Independence**: Operates 100% locally and can run independently even if external models or networks are unavailable.
- **Engineered Feature Schema (18 Exact Features)**:
  1. `perplexity`: Cross-entropy exponentiation computed via Hugging Face `gpt2`.
  2. `burstiness`: Standard deviation of inter-sentence perplexity (variance of writing complexity).
  3. `vocabulary_richness`: Distinct vocabulary ratio (Type-Token Ratio / TTR).
  4. `sentence_variation`: Standard deviation of sentence lengths in tokens.
  5. `repetition`: Multi-gram phrase duplication density across the document.
  6. `ngram`: Bigram/trigram transition probability score.
  7. `semantic_consistency`: Mean cosine similarity across adjacent sentence embeddings using `sentence-transformers/all-MiniLM-L6-v2`.
  8. `avg_word_length`: Mean characters per token.
  9. `punctuation_density`: Ratio of punctuation marks to total token count.
  10. `readability`: Flesch Reading Ease score.
  11. `pronoun_ratio`: Frequency of personal/demonstrative pronouns.
  12. `adverb_ratio`: Frequency of modifier adverbs.
  13. `lexical_density`: Ratio of content words (nouns, verbs, adjectives) to grammatical tokens.
  14. `grammar_error_rate`: Syntax and inflection error frequency via spaCy dependency parsing.
  15. `spelling_error_rate`: Orthographic error frequency.
  16. `passive_sentence_ratio`: Proportion of passive grammatical constructions.
  17. `question_ratio`: Proportion of interrogative sentences.
  18. `exclamation_ratio`: Proportion of exclamatory sentences.

### Component B: Pretrained Hugging Face Transformer
- **Model Checkpoint**: `openai-community/roberta-base-openai-detector`
- **Architecture**: RoBERTa-base sequence classification head (12 layers, 768 hidden dimensions, 125M parameters).
- **Why Selected**:
  - Open-weights, commercially permissive (MIT License), locally hostable without recurring API costs.
  - Native token-level contextual representations that capture subtle autoregressive generation patterns invisible to hand-crafted surface heuristics.
- **Label Mapping Inversion**:
  - The checkpoint maps index `0 -> "Fake"` (AI-generated) and index `1 -> "Real"` (Human-written).
  - The adapter strictly maps `probs[0]` to `ai_probability` and `probs[1]` to `human_probability`.
- **Long-Text Chunking & Aggregation**:
  - Input text exceeding 512 tokens is chunked with a sliding window of 450 tokens and 64 tokens of overlap.
  - Chunk predictions are aggregated using an interquartile trimmed median-mean strategy to prevent local artifacts from dominating document-level classification.

### Component C: External Commercial API (GPTZero API v2)
- **Integration**: `https://api.gptzero.me/v2/predict/text`
- **Features**: Multi-tiered scan measuring document burstiness, perplexity, and paragraph-level synthesis.
- **Privacy & Execution**:
  - Only executes if `GPTZERO_API_KEY` is configured in environment variables.
  - Fully decoupled: If unconfigured, disabled, or if network timeouts/rate limits occur, the system falls back gracefully to the local hybrid pipeline without crashing or stalling.

---

## 3. Decision Policy & Inconclusive Verdict

The ensemble does NOT force a false binary decision. It supports a ternary outcome:
1. **Likely AI-generated**: Calibrated ensemble probability $\ge 65.0\%$, supported by model consensus.
2. **Likely Human-written**: Calibrated ensemble probability $\le 35.0\%$, supported by model consensus.
3. **Inconclusive / Uncertain**: Triggered when:
   - **Borderline Score**: Score is between $35.0\%$ and $65.0\%$.
   - **Severe Disagreement**: Maximum discrepancy between active detectors exceeds $45.0\%$ (e.g., Custom detects $98\%$ AI but RoBERTa detects $10\%$ AI).
   - **Short Text**: Text is under 250 characters or 35 words (insufficient statistical support).
   - **Language Limitation**: Input language is unsupported or outside model evaluation domain.

---

## 4. Setup & Installation

### Requirements
- Python 3.10, 3.11, 3.12, or 3.13
- CUDA-compatible GPU (e.g., NVIDIA GTX 1650 / RTX 3060+) recommended, with automatic CPU fallback.
- Virtual environment at `detector/venv`

### Installation
```powershell
cd d:\MIne\CO4\AWTSE\detector
.\venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Environment Configuration
Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```

Contents of `.env`:
```ini
# Server Configuration
PORT=8000
HOST=127.0.0.1
DEBUG=False

# Hardware Acceleration (cuda or cpu)
DEVICE=cuda

# Hugging Face Pretrained Model
HF_MODEL_NAME=openai-community/roberta-base-openai-detector
ENABLE_HF_DETECTOR=true

# Commercial GPTZero API (Optional)
# Leave empty to run 100% locally with zero external network calls
GPTZERO_API_KEY=
GPTZERO_API_URL=https://api.gptzero.me/v2/predict/text
GPTZERO_TIMEOUT_SECONDS=25
ENABLE_GPTZERO_API=false

# Hybrid Ensemble Weights (Auto-normalized if an engine is inactive)
WEIGHT_CUSTOM_RF=0.35
WEIGHT_HF_ROBERTA=0.35
WEIGHT_GPTZERO_API=0.30

# Decision Thresholds
THRESHOLD_AI_LIKELY=0.65
THRESHOLD_HUMAN_LIKELY=0.35
```

---

## 5. Execution Commands

### 1. Start the Live Server & Web Interface
```powershell
cd d:\MIne\CO4\AWTSE\detector
.\venv\Scripts\python.exe app.py
```
Open your browser to:
- **Interactive Web UI**: `http://127.0.0.1:8000/`
- **Health Check**: `http://127.0.0.1:8000/health`
- **Active Models**: `http://127.0.0.1:8000/models`
- **API Documentation**: `http://127.0.0.1:8000/docs`

### 2. Run Comprehensive Automated Tests
```powershell
cd d:\MIne\CO4\AWTSE\detector
.\venv\Scripts\python.exe -m unittest tests/test_hybrid_text_detector.py
```

### 3. Run Benchmark Evaluation Pipeline
```powershell
cd d:\MIne\CO4\AWTSE\detector
.\venv\Scripts\python.exe evaluation.py --samples 5
```

---

## 6. API Usage Example

### Request
```bash
curl -X POST "http://127.0.0.1:8000/detect" \
     -H "Content-Type: application/json" \
     -d '{"text": "Yesterday evening, I went out for a long walk in the rain through the neighborhood park. I got completely drenched, but the fresh smell of wet earth and pine trees was really calming."}'
```

### Response
```json
{
  "probability": 38.6,
  "confidence": "Low",
  "verdict": "Inconclusive / Uncertain",
  "features": {
    "perplexity": 39.1,
    "burstiness": 0.04,
    "vocabularyRichness": 0.91,
    "sentenceVariation": 0.03,
    "repetition": 0.09,
    "ngramScore": 0.97,
    "semanticConsistency": 0.49,
    "stylometry": 0.70,
    "grammarPatterns": 0.85
  },
  "detailed_features": {
    "perplexity": 39.1014,
    "burstiness": 0.0429,
    "vocabulary_richness": 0.9091,
    "sentence_variation": 0.0303,
    "repetition": 0.0909,
    "ngram": 0.9697,
    "semantic_consistency": 0.4888,
    "avg_word_length": 4.4545,
    "punctuation_density": 0.1212,
    "readability": 82.4148,
    "pronoun_ratio": 0.0606,
    "adverb_ratio": 0.0606,
    "lexical_density": 0.5758,
    "grammar_error_rate": 0.0303,
    "spelling_error_rate": 0.0606,
    "passive_sentence_ratio": 0.0,
    "question_ratio": 0.0,
    "exclamation_ratio": 0.0
  },
  "indicators": [
    "Uniform sentence structure (low burstiness)",
    "High semantic consistency across transitions",
    "RoBERTa token distribution aligns with natural human prose (76.8% human probability)"
  ],
  "hybrid_pipeline": true,
  "consensus": {
    "agreement": "Majority Agreement",
    "active_detectors": 2,
    "total_detectors": 3,
    "discrepancy": 30.8,
    "inconclusive_reason": "Borderline score (38.6%): Insufficient polarity to confirm AI or Human authorship."
  },
  "individual_detectors": {
    "custom_rf": {
      "detector_id": "custom_rf",
      "name": "Custom 18-Feature Random Forest Ensemble",
      "ai_probability": 54.0,
      "verdict": "Possibly AI-generated",
      "latency_ms": 15683.1
    },
    "hf_roberta": {
      "detector_id": "hf_roberta",
      "name": "Pretrained RoBERTa AI Text Classifier",
      "ai_probability": 23.2,
      "verdict": "Likely Human-written",
      "latency_ms": 1374.9
    },
    "gptzero_api": {
      "detector_id": "gptzero_api",
      "name": "GPTZero Commercial AI Text API",
      "status": "unconfigured",
      "ai_probability": 50.0,
      "verdict": "Inconclusive / Uncertain"
    }
  }
}
```

---

## 7. Known Limitations & Operational Guidance

1. **Pretrained Generator Scope**:
   - `roberta-base-openai-detector` was fine-tuned on outputs from GPT-2 (1.5B) in 2019. Modern frontier LLMs (GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro) produce tokens with higher natural entropy that can partially evade early RoBERTa detectors. The hybrid ensemble mitigates this by weighing against the 18 stylometric features and GPTZero.
2. **Short Text Uncertainty**:
   - Texts under 250 characters lack the statistical volume necessary for stable perplexity variance, n-gram repetition, or sentence length diversity. The ensemble enforces an automatic inconclusive state or confidence penalty for brief submissions.
3. **Privacy & Data Transmission**:
   - By default, all analysis is performed **100% locally** on your machine. Text is NEVER transmitted to external servers unless `ENABLE_GPTZERO_API=true` is explicitly set with a valid user-supplied `GPTZERO_API_KEY`.
