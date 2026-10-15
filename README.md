# Gaia Detector — Multi-Modal AI Authenticity Detection System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.2+-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8.1+-646CFF?logo=vite&logoColor=white)](https://vite.dev)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.6+-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.13-3776AB?logo=python&logoColor=white)](https://python.org)

**Gaia Detector** is an enterprise-grade, multi-modal content authenticity detection application designed to inspect **Text**, **Documents** (PDF, DOCX, TXT), **Images**, and **Videos** to estimate whether their content is AI-generated (synthetic) or authentic human-created.

Gaia employs a **multi-source ensemble architecture** that combines preserved custom-trained machine learning classifiers (extracting domain-specific handcrafted features), pretrained deep learning transformer models from Hugging Face, and optional commercial verification APIs with calibrated statistical decision boundaries.

---

## 1. System Architecture

```
                             ┌───────────────────────────────────────────────┐
                             │       User Interface (Browser / Client)       │
                             └───────────────────────┬───────────────────────┘
                                                     │ HTTP / REST / Multipart
                                                     ▼
                             ┌───────────────────────────────────────────────┐
                             │      React 19 + Vite 8 Frontend (:5173)       │
                             │   - Multi-Modal Authenticity Workbench        │
                             │   - Real-time Diagnostic Visualization        │
                             │   - Framer Motion Dynamic Telemetry           │
                             └───────────────────────┬───────────────────────┘
                                                     │ Proxy / Direct API
                                                     ▼
                             ┌───────────────────────────────────────────────┐
                             │          FastAPI Unified Backend (:8000)      │
                             │   ├── Auth Guard & Rate Limiting              │
                             │   ├── MongoDB Atlas Async Storage (motor)     │
                             │   └── Google Drive Private Cloud Archival     │
                             └───────┬───────────────┬───────────────┬───────┘
                                     │               │               │
            ┌────────────────────────┘               │               └────────────────────────┐
            ▼                                        ▼                                        ▼
┌─────────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
│   Hybrid Text Detector  │      │   Hybrid Video Detector │      │  Image & Document Engine│
├─────────────────────────┤      ├─────────────────────────┤      ├─────────────────────────┤
│ • 18-Feature Custom RF  │      │ • 21-Feature Spatio-    │      │ • Zero-Shot CLIP Vision │
│   (Perplexity, Burst,   │      │   Temporal Custom RF    │      │   (ViT-B/32 Authenticity│
│    Vocabulary Richness, │      │ • HuggingFace ResNet50  │      │ • PDFPlumber & Docx     │
│    Stylometry, Grammar) │      │   (T2V Video Artifacts) │      │   Text Extraction Layer │
│ • RoBERTa Transformer   │      │ • Sightengine Video API │      │ • Text Route Forwarding │
│ • GPTZero API Adapter   │      │ • Calibrated Temporal   │      │                         │
│ • Consensus Combiner    │      │   Confidence Combiner   │      │                         │
└─────────────────────────┘      └─────────────────────────┘      └─────────────────────────┘
```

---

## 2. Supported Detection Modalities

| Modality | Accepted Formats | Underlying Detection Pipeline | Key Metrics & Indicators |
| :--- | :--- | :--- | :--- |
| **Text** | Raw text, copy-paste | Hybrid: 18-Feature Random Forest + RoBERTa Sequence Classifier + GPTZero API | Perplexity, burstiness, vocabulary richness, sentence variation, stylometry, n-grams |
| **Documents** | `.pdf`, `.docx`, `.txt`, `.md`, `.csv` | Multi-page text extraction (`pdfplumber` / `python-docx`) forwarded to Hybrid Text Ensemble | Extracted character count, page analysis, token entropy, linguistic flow consistency |
| **Images** | `.png`, `.jpg`, `.jpeg`, `.webp` | Zero-shot visual classification via Hugging Face CLIP (`openai/clip-vit-base-patch32`) | Visual synthetic score, prompt alignment, artifact detection |
| **Videos** | `.mp4`, `.mov`, `.avi`, `.webm` | Hybrid: 21-Feature Spatio-Temporal RF (OpenCV + scikit-learn) + HuggingFace T2V + Sightengine | Frame variance, temporal stability, edge coherence, spatial entropy, frame sampling |

---

## 3. Repository Structure

```
Gaia-Detector/
├── backend/                         # Unified FastAPI Backend
│   ├── app/
│   │   ├── core/                   # Configuration, Database & Google Drive manager
│   │   ├── middleware/             # Auth guards & security middleware
│   │   ├── models/                 # Pydantic schemas (detection, user, report)
│   │   ├── routers/                # API route definitions (auth, detect, upload, history, report)
│   │   └── services/               # Core multi-modal orchestrator (ai_detector.py)
│   ├── tests/                      # Automated test suite (test_backend.py, verify_live.py)
│   ├── main.py                     # Backend application entry point (:8000)
│   ├── requirements.txt            # Python dependencies
│   └── .env.example                # Backend environment variable template
│
├── frontend/                        # Production React 19 + Vite 8 Frontend
│   ├── src/
│   │   ├── components/             # Reusable UI components (UploadDemo, DetectionPreview, etc.)
│   │   ├── pages/                  # Landing, Upload Workbench, Dashboard, History, Report, Auth
│   │   ├── services/               # Centralized API service client (api.js)
│   │   ├── constants/              # Route constants and format definitions
│   │   └── App.jsx                 # Client entry point and React Router configuration
│   ├── package.json                # Frontend dependencies & npm scripts
│   ├── vite.config.js              # Vite server & reverse proxy configuration
│   └── .env.example                # Frontend environment variable template
│
├── detector/                        # Preserved Custom Machine Learning Detectors
│   ├── hybrid_detector.py          # Master Text Hybrid Pipeline (Custom RF + RoBERTa + GPTZero)
│   ├── detector.py                 # Core 18-feature text prediction pipeline
│   ├── classifier.py               # Random Forest training and serialization script
│   ├── feature_extractor.py        # 18-feature extraction pipeline orchestrator
│   ├── features/                   # Perplexity, burstiness, stylometry, vocabulary, grammar
│   ├── models/                     # Serialized text classifier (classifier.pkl)
│   └── video_detector/             # Spatio-Temporal Video Detection Module
│       ├── hybrid_detector.py      # Master Video Hybrid Pipeline (Custom RF + HF + Sightengine)
│       ├── predict.py              # Spatio-temporal video inference pipeline
│       ├── train.py                # Spatio-temporal Random Forest training script
│       ├── features/               # Visual spatial & temporal feature extractors
│       └── models/                 # Serialized video classifier (video_classifier.pkl)
│
├── .gitignore                       # Repository-wide ignore file (caches, models, venv, secrets)
└── README.md                        # Project documentation (this file)
```

---

## 4. Quickstart & Installation

### Prerequisites
- **Python 3.11+** (compatible with Python 3.13 and 3.14)
- **Node.js 18+** and **npm 9+**
- (Optional) NVIDIA GPU with CUDA support for accelerated transformer inference

---

### Step 1: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate Python virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install backend and detector dependencies
pip install -r requirements.txt
pip install -r ../detector/requirements.txt

# Configure environment variables
cp .env.example .env
```

To run the backend automated test suite:
```bash
python -m pytest tests/test_backend.py -v
```

Start the FastAPI server:
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API is now running at `http://127.0.0.1:8000`. Interactive documentation is available at `http://127.0.0.1:8000/docs`.

---

### Step 2: Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```
The frontend is now accessible at `http://localhost:5173`. API calls are automatically routed to the FastAPI backend via Vite reverse proxy.

To build the frontend for production:
```bash
npm run build
```

---

## 5. Environment Configuration

### Backend (`backend/.env`)
```ini
# Application Environment
APP_ENV=development
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
SECRET_KEY=your-secure-random-secret-key-at-least-32-chars

# CORS Allowed Origins
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

# Optional Database & Storage (Gracefully skipped if unconfigured)
MONGODB_URI=
MONGODB_DB_NAME=gaia_detector
GOOGLE_DRIVE_FOLDER_ID=
GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON=

# Optional Commercial APIs
GPTZERO_API_KEY=
SIGHTENGINE_API_USER=
SIGHTENGINE_API_SECRET=
HF_TOKEN=
```

### Frontend (`frontend/.env`)
```ini
# Leave blank for local development to use Vite reverse proxy
VITE_API_BASE_URL=
```

---

## 6. API Reference

| Endpoint | Method | Content-Type | Payload / Params | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/health` | `GET` | — | None | System liveness, database & cloud storage diagnostic status |
| `/ready` | `GET` | — | None | Readiness probe for dependent infrastructure |
| `/detect/text` | `POST` | `application/json` | `{"text": "..."}` | Analyzes text via 18-Feature RF + RoBERTa + GPTZero hybrid |
| `/detect/document` | `POST` | `multipart/form-data` | `file`: PDF/DOCX/TXT file | Extracts structure & text, runs hybrid authenticity verification |
| `/detect/image` | `POST` | `multipart/form-data` | `file`: Image file | Zero-shot visual authenticity classification (CLIP ViT) |
| `/detect/video` | `POST` | `multipart/form-data` | `file`: Video file | 21-feature spatio-temporal video detection + HF + Sightengine |
| `/auth/register` | `POST` | `application/json` | `{"name": "...", "email": "...", "password": "..."}` | User registration |
| `/auth/login` | `POST` | `application/json` | `{"email": "...", "password": "..."}` | Issues secure httpOnly JWT authentication cookie |
| `/history` | `GET` | — | Bearer / Cookie auth | Retrieves detection scan history from MongoDB Atlas |

---

## 7. Model Details & Training

### Custom Text Classifier
- **Features**: 18 numerical features (GPT-2 perplexity, burstiness, vocabulary richness, sentence variation, lexical density, repetition, stylometry, grammar error rate).
- **Architecture**: `RandomForestClassifier` with probability calibration.
- **Model Checkpoint**: `detector/models/classifier.pkl`.
- **Training**: Run `python detector/classifier.py` to retrain with updated feature matrices.

### Custom Video Classifier
- **Features**: 21 spatio-temporal features across sampled frames (spatial variance, edge energy, frequency entropy, inter-frame structural similarity SSIM, temporal optical flow variance).
- **Architecture**: Balanced `RandomForestClassifier` with isotonic probability calibration.
- **Model Checkpoint**: `detector/video_detector/models/video_classifier.pkl` & `calibration_model.pkl`.
- **Training**: Run `python detector/video_detector/train.py` to retrain from video datasets.

---

## 8. License

This project is licensed under the MIT License. All detector code and frontend components are intended for content authenticity research and verification.
