"""
app.py - FastAPI application and rich interactive web interface for Hybrid Video AI Detector.
Coordinates Custom Classifier, HF ResNet-50 T2V Model, and Sightengine Commercial API.
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from dotenv import load_dotenv
    _env_local = Path(__file__).resolve().parent / ".env"
    if _env_local.exists():
        load_dotenv(_env_local)
    else:
        load_dotenv()
except ImportError:
    pass

from hybrid_detector import HybridVideoDetector
from detector import VideoDetector
from utils.constants import MODEL_PATH, MODEL_VERSION
from utils.video_utils import device

# Global hybrid detector instance
_hybrid_detector = None


def get_detector() -> HybridVideoDetector:
    global _hybrid_detector
    if _hybrid_detector is None:
        print("[Server] Initializing Hybrid Video Detector (Custom RF + HF ResNet-50 + Sightengine)...")
        _hybrid_detector = HybridVideoDetector()
    return _hybrid_detector


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up hybrid detector on server launch
    try:
        get_detector()
    except Exception as e:
        print(f"[Server] Notice during hybrid detector startup: {e}")
    yield


app = FastAPI(
    title="Hybrid Video AI Content Detector API",
    description="Multi-model ensemble combining custom spatial-temporal metrics, HF ResNet-50 T2V deepfake detection, and Sightengine commercial GenAI API",
    version=MODEL_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    detector = get_detector()
    return {
        "status": "healthy",
        "service": "Hybrid Video AI Content Detector",
        "hardware_acceleration": device,
        "hybrid_pipeline": True,
        "detector_loaded": detector is not None,
        "model_version": MODEL_VERSION
    }


@app.get("/models")
def list_models():
    """Returns active status of all 3 detection engines."""
    detector = get_detector()
    return {
        "hybrid_pipeline": True,
        "models": {
            "custom_rf": {
                "name": "Custom Spatial-Temporal Ensemble",
                "status": "active" if detector.custom_adapter else "disabled",
                "version": MODEL_VERSION
            },
            "hf_resnet50_t2v": {
                "name": "HF Pretrained ResNet50 (Sora/Veo2 T2V)",
                "status": "active" if (detector.hf_detector and detector.hf_detector.is_initialized) else "failed",
                "repo": "gaetanbrison/deepfake-detector-resnet50-t2v-sora-veo2"
            },
            "sightengine_api": {
                "name": "Sightengine AI Video Detection API",
                "status": "active" if (detector.sightengine_detector and detector.sightengine_detector.is_configured) else "unconfigured",
                "model": "genai"
            }
        }
    }


class SightengineConfigRequest(BaseModel):
    api_user: str
    api_secret: str
    enabled: bool = True


@app.get("/config/sightengine")
def get_sightengine_config():
    detector = get_detector()
    se = detector.sightengine_detector if detector else None
    configured = se.is_configured if se else False
    user = se.api_user if se else ""
    masked_user = (user[:2] + "****" + user[-2:]) if len(user) > 4 else ("****" if user else "")
    return {
        "is_configured": configured,
        "api_user_masked": masked_user,
        "enabled": detector.enable_sightengine if detector else False
    }


@app.post("/config/sightengine")
def set_sightengine_config(cfg: SightengineConfigRequest):
    user = cfg.api_user.strip()
    secret = cfg.api_secret.strip()
    enabled = cfg.enabled

    detector = get_detector()
    detector.configure_sightengine(user, secret, enabled=enabled)

    # Persist into .env file
    env_file = Path(__file__).parent / ".env"
    try:
        lines = []
        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
        
        user_written = False
        secret_written = False
        enabled_written = False
        new_lines = []
        for line in lines:
            if line.startswith("SIGHTENGINE_API_USER="):
                new_lines.append(f"SIGHTENGINE_API_USER={user}\n")
                user_written = True
            elif line.startswith("SIGHTENGINE_API_SECRET="):
                new_lines.append(f"SIGHTENGINE_API_SECRET={secret}\n")
                secret_written = True
            elif line.startswith("ENABLE_SIGHTENGINE_API="):
                new_lines.append(f"ENABLE_SIGHTENGINE_API={'true' if enabled else 'false'}\n")
                enabled_written = True
            else:
                new_lines.append(line)
        if not user_written:
            new_lines.append(f"SIGHTENGINE_API_USER={user}\n")
        if not secret_written:
            new_lines.append(f"SIGHTENGINE_API_SECRET={secret}\n")
        if not enabled_written:
            new_lines.append(f"ENABLE_SIGHTENGINE_API={'true' if enabled else 'false'}\n")

        with open(env_file, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        os.environ["SIGHTENGINE_API_USER"] = user
        os.environ["SIGHTENGINE_API_SECRET"] = secret
        os.environ["ENABLE_SIGHTENGINE_API"] = "true" if enabled else "false"
    except Exception as e:
        print(f"[Config] Error writing .env: {e}")

    return {
        "status": "success",
        "is_configured": detector.sightengine_detector.is_configured if detector.sightengine_detector else False,
        "models": list_models()["models"]
    }


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.post("/analyze")
async def analyze_video_file(file: UploadFile = File(...)):
    """
    Accepts an uploaded video file (MP4, MOV, WebM, etc.),
    runs multi-evidence hybrid analysis (Custom + HF + Sightengine),
    and returns a calibrated ensemble verdict.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No video file provided.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in {".mp4", ".mov", ".webm", ".avi", ".mkv"}:
        raise HTTPException(status_code=400, detail=f"Unsupported format '{ext}'. Upload MP4, MOV, or WebM.")

    detector = get_detector()

    # Save to safe temporary file for processing
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_video:
        temp_path = temp_video.name
        shutil.copyfileobj(file.file, temp_video)

    try:
        result = detector.predict(temp_path)
        result["filename"] = file.filename
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hybrid video analysis error: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


@app.get("/", response_class=HTMLResponse)
def index():
    html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hybrid Video AI Content Detector | Multi-Evidence Vision Engine</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎬</text></svg>">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #060911;
            --bg-card: rgba(15, 23, 42, 0.75);
            --bg-card-hover: rgba(22, 33, 62, 0.85);
            --border: rgba(255, 255, 255, 0.08);
            --border-highlight: rgba(139, 92, 246, 0.35);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #8b5cf6;
            --primary-glow: rgba(139, 92, 246, 0.4);
            --accent: #06b6d4;
            --ai-red: #f43f5e;
            --ai-red-glow: rgba(244, 63, 94, 0.35);
            --human-green: #10b981;
            --human-green-glow: rgba(16, 185, 129, 0.35);
            --uncertain-amber: #f59e0b;
            --uncertain-amber-glow: rgba(245, 158, 11, 0.35);
            --radius-lg: 20px;
            --radius-md: 12px;
            --radius-sm: 8px;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            background-color: var(--bg-base);
            background-image: 
                radial-gradient(at 0% 0%, rgba(139, 92, 246, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(6, 182, 212, 0.12) 0px, transparent 50%);
            background-attachment: fixed;
            color: var(--text-main);
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        header {
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            backdrop-filter: blur(12px);
            background: rgba(6, 9, 17, 0.8);
            position: sticky;
            top: 0;
            z-index: 50;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 20px;
            font-weight: 800;
            letter-spacing: -0.5px;
            color: #fff;
        }

        .logo-icon {
            width: 38px;
            height: 38px;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            border-radius: var(--radius-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            box-shadow: 0 0 20px var(--primary-glow);
        }

        .hardware-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border);
            padding: 6px 14px;
            border-radius: 999px;
            font-size: 13px;
            color: var(--text-muted);
        }

        .pulse-dot {
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
            box-shadow: 0 0 10px #10b981;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(0.85); }
        }

        main {
            flex: 1;
            max-width: 1360px;
            width: 100%;
            margin: 0 auto;
            padding: 36px 24px 60px;
        }

        .hero {
            text-align: center;
            margin-bottom: 36px;
        }

        .hero h1 {
            font-size: 38px;
            font-weight: 800;
            letter-spacing: -1px;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, var(--primary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero p {
            color: var(--text-muted);
            font-size: 15px;
            max-width: 720px;
            margin: 0 auto;
            line-height: 1.6;
        }

        .grid-layout {
            display: grid;
            grid-template-columns: 1.05fr 1.35fr;
            gap: 28px;
        }

        @media (max-width: 1024px) {
            .grid-layout { grid-template-columns: 1fr; }
        }

        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 28px;
            backdrop-filter: blur(16px);
            box-shadow: 0 12px 36px rgba(0, 0, 0, 0.4);
        }

        /* Upload Zone */
        .drop-zone {
            border: 2px dashed rgba(139, 92, 246, 0.35);
            border-radius: var(--radius-md);
            padding: 44px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: rgba(139, 92, 246, 0.02);
            position: relative;
        }

        .drop-zone:hover, .drop-zone.dragover {
            border-color: var(--primary);
            background: rgba(139, 92, 246, 0.08);
            transform: translateY(-2px);
        }

        .drop-icon {
            font-size: 42px;
            margin-bottom: 12px;
        }

        .drop-text {
            font-size: 16px;
            font-weight: 600;
            color: #fff;
            margin-bottom: 6px;
        }

        .drop-subtext {
            font-size: 13px;
            color: var(--text-muted);
        }

        input[type="file"] { display: none; }

        .video-preview-wrapper {
            margin-top: 20px;
            border-radius: var(--radius-md);
            overflow: hidden;
            border: 1px solid var(--border);
            background: #000;
            display: none;
            max-height: 280px;
        }

        video { width: 100%; height: 260px; object-fit: contain; }

        .action-btn {
            width: 100%;
            margin-top: 20px;
            padding: 15px;
            border-radius: var(--radius-md);
            border: none;
            background: linear-gradient(135deg, var(--primary) 0%, #6366f1 100%);
            color: #fff;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 4px 20px var(--primary-glow);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        .action-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 6px 26px rgba(139, 92, 246, 0.6);
        }

        .action-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        /* Results Display */
        .verdict-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 22px;
            padding-bottom: 18px;
            border-bottom: 1px solid var(--border);
        }

        .verdict-badge {
            padding: 7px 18px;
            border-radius: 999px;
            font-size: 13.5px;
            font-weight: 800;
            letter-spacing: 0.3px;
            text-transform: uppercase;
        }

        .verdict-ai {
            background: rgba(244, 63, 94, 0.15);
            color: var(--ai-red);
            border: 1px solid var(--ai-red);
            box-shadow: 0 0 20px var(--ai-red-glow);
        }

        .verdict-human {
            background: rgba(16, 185, 129, 0.15);
            color: var(--human-green);
            border: 1px solid var(--human-green);
            box-shadow: 0 0 20px var(--human-green-glow);
        }

        .verdict-uncertain {
            background: rgba(245, 158, 11, 0.15);
            color: var(--uncertain-amber);
            border: 1px solid var(--uncertain-amber);
            box-shadow: 0 0 20px var(--uncertain-amber-glow);
        }

        /* Consensus Banner */
        .consensus-banner {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border);
            padding: 10px 16px;
            border-radius: var(--radius-sm);
            margin-bottom: 20px;
            font-size: 13.5px;
        }

        .consensus-pill {
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 12px;
        }

        .consensus-full { background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.4); }
        .consensus-majority { background: rgba(139, 92, 246, 0.2); color: #a78bfa; border: 1px solid rgba(139, 92, 246, 0.4); }
        .consensus-conflict { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }

        .inconclusive-alert {
            background: rgba(245, 158, 11, 0.08);
            border-left: 4px solid var(--uncertain-amber);
            padding: 12px 14px;
            border-radius: 4px;
            font-size: 13px;
            color: #fde68a;
            margin-bottom: 20px;
            display: none;
            line-height: 1.5;
        }

        /* Detector Breakdown 3-Card Grid */
        .detectors-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-bottom: 22px;
        }

        @media (max-width: 640px) {
            .detectors-grid { grid-template-columns: 1fr; }
        }

        .detector-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 14px 12px;
            transition: all 0.2s ease;
        }

        .detector-card:hover {
            border-color: var(--border-highlight);
            background: rgba(255, 255, 255, 0.04);
        }

        .d-title {
            font-size: 11.5px;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }

        .d-score {
            font-size: 22px;
            font-weight: 800;
            color: #fff;
            margin-bottom: 4px;
        }

        .d-badge {
            display: inline-block;
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 999px;
        }

        .cfg-pill-btn {
            background: rgba(139, 92, 246, 0.2);
            color: #c4b5fd;
            border: 1px solid rgba(139, 92, 246, 0.4);
            border-radius: 999px;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 8px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .cfg-pill-btn:hover {
            background: var(--primary);
            color: #fff;
            transform: scale(1.05);
        }

        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(8px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }

        .modal-card {
            background: #0f172a;
            border: 1px solid var(--border-highlight);
            border-radius: var(--radius-lg);
            width: 90%;
            max-width: 480px;
            padding: 28px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
            animation: modalIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }

        @keyframes modalIn {
            from { opacity: 0; transform: scale(0.95) translateY(10px); }
            to { opacity: 1; transform: scale(1) translateY(0); }
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .modal-header h3 {
            font-size: 18px;
            font-weight: 800;
            color: #fff;
        }

        .modal-close-btn {
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-size: 24px;
            cursor: pointer;
            line-height: 1;
        }

        .modal-close-btn:hover {
            color: #fff;
        }

        .cfg-input {
            width: 100%;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 10px 14px;
            color: #fff;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            outline: none;
            transition: border 0.2s;
            box-sizing: border-box;
        }

        .cfg-input:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 2px var(--primary-glow);
        }

        .modal-btn {
            padding: 9px 18px;
            border-radius: var(--radius-sm);
            font-weight: 700;
            font-size: 13px;
            cursor: pointer;
            border: none;
            transition: all 0.2s;
        }

        .modal-btn-cancel {
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-muted);
        }

        .modal-btn-cancel:hover {
            background: rgba(255, 255, 255, 0.15);
            color: #fff;
        }

        .modal-btn-save {
            background: linear-gradient(135deg, var(--primary), var(--accent));
            color: #fff;
        }

        .modal-btn-save:hover {
            box-shadow: 0 0 15px var(--primary-glow);
            transform: translateY(-1px);
        }

        .meter-container {
            display: flex;
            align-items: center;
            gap: 24px;
            margin-bottom: 22px;
            padding: 18px;
            background: rgba(255, 255, 255, 0.02);
            border-radius: var(--radius-md);
            border: 1px solid var(--border);
        }

        .circular-gauge {
            width: 100px;
            height: 100px;
            position: relative;
            flex-shrink: 0;
        }

        .circular-gauge svg {
            width: 100%;
            height: 100%;
            transform: rotate(-90deg);
        }

        .gauge-bg {
            fill: none;
            stroke: rgba(255, 255, 255, 0.08);
            stroke-width: 8;
        }

        .gauge-fill {
            fill: none;
            stroke: var(--primary);
            stroke-width: 8;
            stroke-linecap: round;
            stroke-dasharray: 283;
            stroke-dashoffset: 283;
            transition: stroke-dashoffset 1s ease, stroke 0.3s ease;
        }

        .gauge-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }

        .gauge-text span:first-child {
            font-size: 20px;
            font-weight: 800;
            display: block;
        }

        .gauge-subtext {
            font-size: 10px;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 700;
        }

        .meter-info h3 {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .meter-info p {
            font-size: 13px;
            color: var(--text-muted);
            line-height: 1.5;
        }

        /* Features */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-bottom: 22px;
        }

        .feature-box {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            padding: 10px;
            border-radius: var(--radius-sm);
            text-align: center;
        }

        .feature-label {
            font-size: 11px;
            color: var(--text-muted);
            margin-bottom: 4px;
        }

        .feature-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 13.5px;
            font-weight: 700;
            color: #fff;
        }

        /* Indicators */
        .indicators-section h4 {
            font-size: 13.5px;
            font-weight: 700;
            margin-bottom: 10px;
            color: #e2e8f0;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .indicator-item {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            font-size: 13px;
            line-height: 1.5;
            padding: 8px 12px;
            background: rgba(255, 255, 255, 0.02);
            border-radius: var(--radius-sm);
            margin-bottom: 8px;
            border-left: 3px solid var(--primary);
        }

        /* JSON Output */
        .json-toggle {
            margin-top: 18px;
            font-size: 13px;
            color: var(--primary);
            cursor: pointer;
            text-decoration: underline;
            font-weight: 600;
        }

        pre {
            background: #090d16;
            padding: 16px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border);
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: #a5b4fc;
            max-height: 260px;
            overflow-y: auto;
            margin-top: 12px;
            display: none;
        }

        /* Spinner */
        .spinner {
            width: 18px;
            height: 18px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <header>
        <div class="logo">
            <div class="logo-icon">🎬</div>
            <span>Hybrid Video AI Detector</span>
        </div>
        <div class="hardware-badge">
            <div class="pulse-dot"></div>
            <span id="hardwareStatus">Hardware: GPU Accelerated</span>
        </div>
    </header>

    <main>
        <div class="hero">
            <h1>Hybrid Video AI Content Detector</h1>
            <p>Multi-source verification fusing custom spatial-temporal metrics, pretrained ResNet-50 T2V deepfake detection, and Sightengine commercial GenAI API.</p>
        </div>

        <div class="grid-layout">
            <!-- Left: Video Input -->
            <div class="card">
                <h2 style="font-size: 20px; font-weight: 800; margin-bottom: 18px;">Upload Target Video</h2>
                
                <div class="drop-zone" id="dropZone" onclick="document.getElementById('videoInput').click()">
                    <div class="drop-icon">🎥</div>
                    <div class="drop-text">Drag & drop video clip here</div>
                    <div class="drop-subtext">Supports MP4, MOV, WebM, AVI (up to 1GB)</div>
                    <input type="file" id="videoInput" accept="video/mp4,video/quicktime,video/webm,video/x-msvideo" onchange="handleFileSelect(this.files)">
                </div>

                <div class="video-preview-wrapper" id="previewWrapper">
                    <video id="videoPreview" controls></video>
                </div>

                <div id="fileInfo" style="margin-top: 12px; font-size: 13px; color: var(--text-muted); display: none;"></div>

                <button class="action-btn" id="analyzeBtn" onclick="analyzeVideo()" disabled>
                    <span>⚡ Run Hybrid AI Video Detection</span>
                </button>
            </div>

            <!-- Right: Analysis Results -->
            <div class="card" id="resultsCard">
                <div class="verdict-header">
                    <div>
                        <div style="font-size: 12px; color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Ensemble Detection Verdict</div>
                        <div style="font-size: 22px; font-weight: 800; margin-top: 2px;" id="verdictText">Awaiting Video</div>
                    </div>
                    <div class="verdict-badge verdict-uncertain" id="verdictBadge">Ready</div>
                </div>

                <!-- Consensus Banner -->
                <div class="consensus-banner" id="consensusBanner" style="display: none;">
                    <div><strong>Multi-Model Agreement:</strong> <span id="consensusText">--</span></div>
                    <span class="consensus-pill" id="consensusPill">--</span>
                </div>

                <!-- Inconclusive Alert -->
                <div class="inconclusive-alert" id="inconclusiveAlert"></div>

                <!-- Individual Detectors 3-Card Grid -->
                <div class="detectors-grid">
                    <!-- Detector 1: Custom -->
                    <div class="detector-card" id="cardCustom">
                        <div class="d-title">Custom Ensemble</div>
                        <div class="d-score" id="dScoreCustom">--%</div>
                        <div class="d-badge" id="dBadgeCustom" style="background: rgba(255,255,255,0.06); color: var(--text-muted);">Pending</div>
                    </div>
                    <!-- Detector 2: HF ResNet50 -->
                    <div class="detector-card" id="cardHf">
                        <div class="d-title">HF ResNet-50 (T2V)</div>
                        <div class="d-score" id="dScoreHf">--%</div>
                        <div class="d-badge" id="dBadgeHf" style="background: rgba(255,255,255,0.06); color: var(--text-muted);">Pending</div>
                    </div>
                    <!-- Detector 3: Sightengine -->
                    <div class="detector-card" id="cardSe">
                        <div class="d-title" style="display: flex; justify-content: space-between; align-items: center;">
                            <span>Sightengine API</span>
                            <button class="cfg-pill-btn" onclick="openSightengineModal(event)" title="Configure API Credentials">⚙️ Config</button>
                        </div>
                        <div class="d-score" id="dScoreSe">--%</div>
                        <div class="d-badge" id="dBadgeSe" style="background: rgba(255,255,255,0.06); color: var(--text-muted);">Checking...</div>
                    </div>
                </div>

                <div class="meter-container">
                    <div class="circular-gauge">
                        <svg viewBox="0 0 100 100">
                            <circle class="gauge-bg" cx="50" cy="50" r="45"></circle>
                            <circle class="gauge-fill" id="gaugeFill" cx="50" cy="50" r="45"></circle>
                        </svg>
                        <div class="gauge-text">
                            <span id="probValue">0%</span>
                            <span class="gauge-subtext">AI Score</span>
                        </div>
                    </div>
                    <div class="meter-info">
                        <h3 id="confidenceLabel">Confidence: Pending</h3>
                        <p id="analysisSummary">Upload a video file to execute calibrated multi-model hybrid analysis across spatial, temporal, and pretrained deep visual networks.</p>
                    </div>
                </div>

                <div class="features-grid">
                    <div class="feature-box">
                        <div class="feature-label">Frames Inspected</div>
                        <div class="feature-value" id="fFrames">--</div>
                    </div>
                    <div class="feature-box">
                        <div class="feature-label">Active Models</div>
                        <div class="feature-value" id="fActive">--</div>
                    </div>
                    <div class="feature-box">
                        <div class="feature-label">Total Latency</div>
                        <div class="feature-value" id="fLatency">-- ms</div>
                    </div>
                    <div class="feature-box">
                        <div class="feature-label">Temporal Flow</div>
                        <div class="feature-value" id="fStability">--</div>
                    </div>
                </div>

                <div class="indicators-section">
                    <h4>Multi-Source Detection Indicators</h4>
                    <div id="indicatorsList">
                        <div class="indicator-item" style="border-left-color: var(--text-muted);">
                            No analysis performed yet.
                        </div>
                    </div>
                </div>

                <div class="json-toggle" onclick="toggleJson()">View Raw JSON Output</div>
                <pre id="jsonViewer"></pre>
            </div>
        </div>
    </main>

    <!-- Modal for Sightengine API Configuration -->
    <div class="modal-overlay" id="configModal" onclick="closeModalOnBg(event)">
        <div class="modal-card">
            <div class="modal-header">
                <h3>⚙️ Configure Sightengine Video API</h3>
                <button class="modal-close-btn" onclick="closeSightengineModal()">&times;</button>
            </div>
            <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 16px; line-height: 1.5;">
                Sightengine performs industrial multi-generator AI video detection. Enter your API credentials from your <a href="https://dashboard.sightengine.com/" target="_blank" style="color: var(--accent); text-decoration: underline;">Sightengine Dashboard</a>.
            </p>
            <div style="margin-bottom: 14px;">
                <label style="font-size: 12px; font-weight: 700; color: #cbd5e1; display: block; margin-bottom: 6px;">API User ID</label>
                <input type="text" id="apiUserInput" placeholder="e.g. 1082498274" class="cfg-input">
            </div>
            <div style="margin-bottom: 18px;">
                <label style="font-size: 12px; font-weight: 700; color: #cbd5e1; display: block; margin-bottom: 6px;">API Secret</label>
                <input type="password" id="apiSecretInput" placeholder="e.g. 8fG2xK9L..." class="cfg-input">
            </div>
            <div style="font-size: 11.5px; color: #64748b; margin-bottom: 18px; line-height: 1.4;">
                💡 Don't have credentials? Sign up at <a href="https://sightengine.com/" target="_blank" style="color: var(--primary); text-decoration: underline;">sightengine.com</a> for free trial calls. Keys are saved securely to your local <code>.env</code> file.
            </div>
            <div style="display: flex; gap: 10px; justify-content: flex-end;">
                <button class="modal-btn modal-btn-cancel" onclick="closeSightengineModal()">Cancel</button>
                <button class="modal-btn modal-btn-save" id="saveApiBtn" onclick="saveSightengineConfig()">Save & Activate</button>
            </div>
        </div>
    </div>

    <script>
        let selectedFile = null;

        // Fetch health
        fetch('/health').then(r => r.json()).then(data => {
            const el = document.getElementById('hardwareStatus');
            el.textContent = `Hardware: ${data.hardware_acceleration.toUpperCase()} | Hybrid v${data.model_version}`;
        }).catch(() => {});

        // Drag & drop handlers
        const dropZone = document.getElementById('dropZone');
        ['dragenter', 'dragover'].forEach(name => {
            dropZone.addEventListener(name, (e) => {
                e.preventDefault();
                dropZone.classList.add('dragover');
            });
        });
        ['dragleave', 'drop'].forEach(name => {
            dropZone.addEventListener(name, (e) => {
                e.preventDefault();
                dropZone.classList.remove('dragover');
            });
        });
        dropZone.addEventListener('drop', (e) => {
            if (e.dataTransfer.files.length) {
                handleFileSelect(e.dataTransfer.files);
            }
        });

        function handleFileSelect(files) {
            if (!files || !files.length) return;
            selectedFile = files[0];

            const preview = document.getElementById('videoPreview');
            const wrapper = document.getElementById('previewWrapper');
            const info = document.getElementById('fileInfo');
            const btn = document.getElementById('analyzeBtn');

            preview.src = URL.createObjectURL(selectedFile);
            wrapper.style.display = 'block';

            const sizeMb = (selectedFile.size / (1024 * 1024)).toFixed(2);
            info.textContent = `Selected: ${selectedFile.name} (${sizeMb} MB)`;
            info.style.display = 'block';

            btn.disabled = false;
        }

        async function analyzeVideo() {
            if (!selectedFile) return;

            const btn = document.getElementById('analyzeBtn');
            btn.disabled = true;
            btn.innerHTML = '<div class="spinner"></div><span>Running Multi-Source Hybrid Models...</span>';

            const formData = new FormData();
            formData.append('file', selectedFile);

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.detail || 'Analysis request failed');
                }

                const data = await response.json();
                renderResults(data);

            } catch (err) {
                alert(`Error: ${err.message}`);
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<span>⚡ Run Hybrid AI Video Detection</span>';
            }
        }

        function renderResults(data) {
            const prob = data.ai_probability;
            const verdict = data.verdict;
            const confidence = data.confidence;

            document.getElementById('verdictText').textContent = verdict;
            const badge = document.getElementById('verdictBadge');
            badge.className = 'verdict-badge';

            const fill = document.getElementById('gaugeFill');
            const offset = 283 - (283 * (prob / 100));
            fill.style.strokeDashoffset = offset;

            if (verdict === 'Likely AI-generated') {
                badge.classList.add('verdict-ai');
                badge.textContent = `AI-Generated (${confidence} Conf.)`;
                fill.style.stroke = '#f43f5e';
            } else if (verdict === 'Likely authentic') {
                badge.classList.add('verdict-human');
                badge.textContent = `Authentic (${confidence} Conf.)`;
                fill.style.stroke = '#10b981';
            } else {
                badge.classList.add('verdict-uncertain');
                badge.textContent = `Inconclusive (${confidence} Conf.)`;
                fill.style.stroke = '#f59e0b';
            }

            document.getElementById('probValue').textContent = `${prob}%`;
            document.getElementById('confidenceLabel').textContent = `Confidence: ${confidence}`;
            
            const meta = data.video_metadata || {};
            const dur = meta.duration_seconds ? `${meta.duration_seconds}s` : 'clip';
            const res = (meta.width && meta.height) ? `${meta.width}x${meta.height}` : 'video';
            document.getElementById('analysisSummary').textContent = 
                `Analyzed ${data.frames_analyzed} frames across ${dur} (${res}). Consensus: ${data.consensus?.agreement || 'Standard'}.`;

            // Consensus Banner
            const banner = document.getElementById('consensusBanner');
            const pill = document.getElementById('consensusPill');
            const alertBox = document.getElementById('inconclusiveAlert');
            if (data.consensus) {
                banner.style.display = 'flex';
                document.getElementById('consensusText').textContent = 
                    `${data.consensus.active_detectors}/${data.consensus.total_detectors} Models Active`;
                pill.textContent = data.consensus.agreement;
                pill.className = 'consensus-pill';
                if (data.consensus.agreement === 'Full Consensus') pill.classList.add('consensus-full');
                else if (data.consensus.agreement === 'Majority Agreement') pill.classList.add('consensus-majority');
                else pill.classList.add('consensus-conflict');

                if (data.consensus.inconclusive_reason) {
                    alertBox.style.display = 'block';
                    alertBox.innerHTML = `<strong>Inconclusive Notice:</strong> ${data.consensus.inconclusive_reason}`;
                } else {
                    alertBox.style.display = 'none';
                }
            }

            // Individual Detector Cards
            const indDetectors = data.individual_detectors || {};
            
            // 1. Custom
            const cDet = indDetectors.custom_rf;
            if (cDet) {
                document.getElementById('dScoreCustom').textContent = `${cDet.ai_probability}%`;
                const cBadge = document.getElementById('dBadgeCustom');
                cBadge.textContent = cDet.verdict.replace('Likely ', '');
                cBadge.style.background = cDet.verdict === 'Likely AI-generated' ? 'rgba(244,63,94,0.2)' : 'rgba(16,185,129,0.2)';
                cBadge.style.color = cDet.verdict === 'Likely AI-generated' ? '#f43f5e' : '#10b981';
            }

            // 2. HF
            const hfDet = indDetectors.hf_resnet50_t2v;
            if (hfDet) {
                document.getElementById('dScoreHf').textContent = `${hfDet.ai_probability}%`;
                const hfBadge = document.getElementById('dBadgeHf');
                hfBadge.textContent = hfDet.status === 'success' ? hfDet.verdict.replace('Likely ', '') : 'Unavailable';
                hfBadge.style.background = hfDet.verdict === 'Likely AI-generated' ? 'rgba(244,63,94,0.2)' : 'rgba(16,185,129,0.2)';
                hfBadge.style.color = hfDet.verdict === 'Likely AI-generated' ? '#f43f5e' : '#10b981';
            }

            // 3. Sightengine
            const seDet = indDetectors.sightengine_api;
            if (seDet) {
                document.getElementById('dScoreSe').textContent = seDet.status === 'success' ? `${seDet.ai_probability}%` : '--%';
                const seBadge = document.getElementById('dBadgeSe');
                seBadge.textContent = seDet.status === 'success' ? seDet.verdict.replace('Likely ', '') : seDet.status.toUpperCase();
                seBadge.style.background = seDet.status === 'success' ? (seDet.verdict === 'Likely AI-generated' ? 'rgba(244,63,94,0.2)' : 'rgba(16,185,129,0.2)') : 'rgba(255,255,255,0.06)';
                seBadge.style.color = seDet.status === 'success' ? (seDet.verdict === 'Likely AI-generated' ? '#f43f5e' : '#10b981') : '#94a3b8';
            }

            // Metrics
            document.getElementById('fFrames').textContent = data.frames_analyzed;
            document.getElementById('fActive').textContent = `${data.consensus?.active_detectors || 1} / ${data.consensus?.total_detectors || 1}`;
            document.getElementById('fLatency').textContent = `${data.total_latency_ms || '--'} ms`;
            document.getElementById('fStability').textContent = data.summary_features?.appearanceStability || '0.85';

            // Indicators
            const indList = document.getElementById('indicatorsList');
            indList.innerHTML = '';
            (data.visual_indicators || []).forEach(ind => {
                const item = document.createElement('div');
                item.className = 'indicator-item';
                item.textContent = `• ${ind}`;
                if (verdict === 'Likely AI-generated') {
                    item.style.borderLeftColor = '#f43f5e';
                } else if (verdict === 'Likely authentic') {
                    item.style.borderLeftColor = '#10b981';
                }
                indList.appendChild(item);
            });

            // Raw JSON
            document.getElementById('jsonViewer').textContent = JSON.stringify(data, null, 2);
        }

        function toggleJson() {
            const pre = document.getElementById('jsonViewer');
            pre.style.display = pre.style.display === 'block' ? 'none' : 'block';
        }

        async function checkModelStatuses() {
            try {
                const res = await fetch('/models');
                if (!res.ok) return;
                const data = await res.json();
                const se = data.models?.sightengine_api;
                if (se) {
                    const badge = document.getElementById('dBadgeSe');
                    if (se.status === 'active') {
                        badge.textContent = 'Active (Ready)';
                        badge.style.background = 'rgba(16, 185, 129, 0.2)';
                        badge.style.color = '#10b981';
                    } else {
                        badge.textContent = 'Unconfigured';
                        badge.style.background = 'rgba(255, 255, 255, 0.06)';
                        badge.style.color = '#94a3b8';
                    }
                }
            } catch (e) {
                console.error("Failed to check model status", e);
            }
        }

        function openSightengineModal(e) {
            if (e) e.stopPropagation();
            document.getElementById('configModal').style.display = 'flex';
        }

        function closeSightengineModal() {
            document.getElementById('configModal').style.display = 'none';
        }

        function closeModalOnBg(e) {
            if (e.target.id === 'configModal') closeSightengineModal();
        }

        async function saveSightengineConfig() {
            const user = document.getElementById('apiUserInput').value.trim();
            const secret = document.getElementById('apiSecretInput').value.trim();
            if (!user || !secret) {
                alert('Please enter both Sightengine API User and API Secret.');
                return;
            }

            const btn = document.getElementById('saveApiBtn');
            btn.textContent = 'Saving...';
            btn.disabled = true;

            try {
                const res = await fetch('/config/sightengine', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ api_user: user, api_secret: secret, enabled: true })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    closeSightengineModal();
                    await checkModelStatuses();
                    alert('✅ Sightengine API credentials saved and activated successfully!');
                } else {
                    alert('Error saving configuration.');
                }
            } catch (err) {
                alert(`Error: ${err.message}`);
            } finally {
                btn.textContent = 'Save & Activate';
                btn.disabled = false;
            }
        }

        window.addEventListener('DOMContentLoaded', checkModelStatuses);
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)


def run_cli_test():
    """CLI testing helper for Hybrid Video AI Detector."""
    print("=" * 60)
    print("HYBRID VIDEO AI DETECTOR - CLI INTEGRATION TEST")
    print("=" * 60)

    from dataset_builder import create_sample_video
    temp_dir = tempfile.mkdtemp()
    test_video = os.path.join(temp_dir, "test_sample.mp4")

    try:
        print("\nSynthesizing test video clip...")
        create_sample_video(test_video, is_ai=True, num_frames=30)

        detector = get_detector()
        result = detector.predict(test_video)

        print("\n========== HYBRID DETECTOR JSON RESULT ==========")
        import json
        print(json.dumps(result, indent=2))
        print("=================================================")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_cli_test()
    else:
        # Run on port 8001 so it doesn't conflict with text detector on 8000
        print("\nStarting Hybrid Video AI Content Detector server on http://127.0.0.1:8001")
        print("To run in test CLI mode instead: python app.py --test\n")
        uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=False)
