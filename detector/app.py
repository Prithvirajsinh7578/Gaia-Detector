# app.py - Gaia Detector Hybrid AI-Text Detection Server and Web Interface

import os
import sys
import json
import uvicorn
from pathlib import Path
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

try:
    from dotenv import load_dotenv
    _env_local = Path(__file__).resolve().parent / ".env"
    if _env_local.exists():
        load_dotenv(_env_local)
    else:
        load_dotenv()
except ImportError:
    pass

from hybrid_detector import HybridTextDetector
from utils.constants import FEATURE_NAMES

# Global detector instance (loaded once)
_detector = None


def get_detector() -> HybridTextDetector:
    global _detector
    if _detector is None:
        print("[Server] Initializing Hybrid Text Detector (Custom RF + HF RoBERTa + GPTZero)...")
        _detector = HybridTextDetector()
    return _detector


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up detector on server launch
    try:
        get_detector()
    except Exception as e:
        print(f"[Server] Notice during hybrid detector warmup: {e}")
    yield


app = FastAPI(
    title="Gaia Detector - Hybrid AI Text Content Detector API",
    description="Multi-evidence linguistic AI text detection fusing custom 18-feature Random Forest, pretrained RoBERTa transformer, and GPTZero API",
    version="2.0.0",
    lifespan=lifespan
)

# Enable CORS for cross-origin frontend requests
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
    device = getattr(detector.hf_detector, "device", "cpu") if (detector and detector.hf_detector) else "cpu"
    return {
        "status": "healthy",
        "service": "Gaia Detector - Hybrid AI Text Detection Engine",
        "hardware_acceleration": device.upper(),
        "hybrid_pipeline": True,
        "detector_loaded": detector is not None,
        "model_version": "2.0.0"
    }


@app.get("/models")
def list_models():
    """Returns active operational status of all three detection engines."""
    detector = get_detector()
    return {
        "hybrid_pipeline": True,
        "models": {
            "custom_rf": {
                "name": "Custom 18-Feature Random Forest Ensemble",
                "status": "active" if (detector and detector.custom_adapter) else "disabled",
                "features_count": len(FEATURE_NAMES),
                "version": "1.0.0"
            },
            "hf_roberta": {
                "name": "Pretrained RoBERTa AI Detector",
                "status": "active" if (detector and detector.hf_detector and detector.hf_detector.is_initialized) else "pending",
                "repo": getattr(detector.hf_detector, "model_id", "openai-community/roberta-base-openai-detector") if detector else "openai-community/roberta-base-openai-detector"
            },
            "gptzero_api": {
                "name": "GPTZero Commercial API v2",
                "status": "active" if (detector and detector.gptzero_detector and detector.gptzero_detector.is_configured) else "unconfigured",
                "endpoint": "v2/predict/text"
            }
        }
    }


class GPTZeroConfigRequest(BaseModel):
    api_key: str
    enabled: bool = True


@app.get("/config/gptzero")
def get_gptzero_config():
    detector = get_detector()
    gz = detector.gptzero_detector if detector else None
    configured = gz.is_configured if gz else False
    key = gz.api_key if gz else ""
    masked = (key[:4] + "****" + key[-4:]) if len(key) > 8 else ("****" if key else "")
    return {
        "is_configured": configured,
        "api_key_masked": masked,
        "enabled": detector.enable_gptzero if detector else False
    }


@app.post("/config/gptzero")
def set_gptzero_config(cfg: GPTZeroConfigRequest):
    key = cfg.api_key.strip()
    enabled = cfg.enabled

    detector = get_detector()
    detector.configure_gptzero(key, enabled=enabled)

    # Persist into .env file
    env_file = Path(__file__).parent / ".env"
    try:
        lines = []
        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
        key_written = False
        enabled_written = False
        new_lines = []
        for line in lines:
            if line.startswith("GPTZERO_API_KEY="):
                new_lines.append(f"GPTZERO_API_KEY={key}\n")
                key_written = True
            elif line.startswith("ENABLE_GPTZERO_API="):
                new_lines.append(f"ENABLE_GPTZERO_API={'true' if enabled else 'false'}\n")
                enabled_written = True
            else:
                new_lines.append(line)
        if not key_written:
            new_lines.append(f"GPTZERO_API_KEY={key}\n")
        if not enabled_written:
            new_lines.append(f"ENABLE_GPTZERO_API={'true' if enabled else 'false'}\n")

        with open(env_file, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        os.environ["GPTZERO_API_KEY"] = key
        os.environ["ENABLE_GPTZERO_API"] = "true" if enabled else "false"
    except Exception as e:
        print(f"[Config] Error writing .env: {e}")

    return {
        "status": "success",
        "is_configured": detector.gptzero_detector.is_configured if detector.gptzero_detector else False,
        "models": list_models()["models"]
    }


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


class DetectRequest(BaseModel):
    text: str


@app.post("/detect")
def detect_text(request: DetectRequest):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    detector = get_detector()
    result = detector.predict(request.text)
    return JSONResponse(content=result)


@app.get("/", response_class=HTMLResponse)
def index():
    html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gaia Detector | Hybrid AI Text Detection Architecture</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #090d16;
            --bg-card: rgba(18, 24, 38, 0.7);
            --bg-card-hover: rgba(26, 34, 54, 0.85);
            --border: rgba(255, 255, 255, 0.08);
            --border-highlight: rgba(99, 102, 241, 0.3);
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --primary: #6366f1;
            --primary-glow: rgba(99, 102, 241, 0.35);
            --primary-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            --ai-accent: #f43f5e;
            --ai-glow: rgba(244, 63, 94, 0.25);
            --human-accent: #10b981;
            --human-glow: rgba(16, 185, 129, 0.25);
            --warning-accent: #f59e0b;
            --radius-md: 12px;
            --radius-sm: 8px;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-base);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 15% 20%, rgba(99, 102, 241, 0.12) 0%, transparent 40%),
                radial-gradient(circle at 85% 80%, rgba(168, 85, 247, 0.1) 0%, transparent 40%);
        }

        header {
            border-bottom: 1px solid var(--border);
            backdrop-filter: blur(12px);
            background: rgba(9, 13, 22, 0.8);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1.1rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .logo-group {
            display: flex;
            align-items: center;
            gap: 0.85rem;
        }

        .logo-icon {
            font-size: 1.6rem;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .brand-title {
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }

        .brand-badge {
            font-size: 0.75rem;
            padding: 0.25rem 0.65rem;
            border-radius: 9999px;
            background: rgba(99, 102, 241, 0.15);
            color: #a5b4fc;
            border: 1px solid rgba(99, 102, 241, 0.3);
            font-weight: 600;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2.5rem 2rem;
            flex: 1;
            width: 100%;
        }

        .hero-banner {
            text-align: center;
            margin-bottom: 2rem;
        }

        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            margin-bottom: 0.6rem;
            background: linear-gradient(180deg, #ffffff 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero-sub {
            color: var(--text-muted);
            font-size: 0.98rem;
            max-width: 680px;
            margin: 0 auto;
            line-height: 1.6;
        }

        .main-layout {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
        }

        @media (max-width: 900px) {
            .main-layout {
                grid-template-columns: 1fr;
            }
        }

        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 1.75rem;
            backdrop-filter: blur(8px);
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }

        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .card-title {
            font-size: 1.1rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .sample-actions {
            display: flex;
            gap: 0.5rem;
        }

        .btn-pill {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border);
            color: var(--text-muted);
            padding: 0.35rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.2s ease;
            font-weight: 500;
        }

        .btn-pill:hover {
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-main);
            border-color: var(--text-muted);
        }

        .textarea-wrapper {
            position: relative;
            flex: 1;
        }

        textarea {
            width: 100%;
            height: 240px;
            background: rgba(9, 13, 22, 0.6);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 1rem;
            color: var(--text-main);
            font-family: inherit;
            font-size: 0.95rem;
            line-height: 1.6;
            resize: none;
            outline: none;
            transition: border-color 0.2s;
        }

        textarea:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 2px var(--primary-glow);
        }

        .textarea-meta {
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-top: 0.4rem;
        }

        .btn-primary {
            background: var(--primary-gradient);
            color: #fff;
            border: none;
            border-radius: var(--radius-sm);
            padding: 0.85rem 1.5rem;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            transition: all 0.2s;
            box-shadow: 0 4px 14px 0 var(--primary-glow);
        }

        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px 0 var(--primary-glow);
        }

        .btn-primary:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        /* 3-Model Detector Grid */
        .detectors-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 0.5rem;
        }

        .detector-box {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 10px;
            text-align: center;
            transition: border-color 0.2s;
        }

        .detector-box:hover {
            border-color: var(--border-highlight);
        }

        .d-box-title {
            font-size: 10.5px;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.4px;
            margin-bottom: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .d-box-score {
            font-family: 'JetBrains Mono', monospace;
            font-size: 16px;
            font-weight: 800;
            color: #fff;
            margin-bottom: 4px;
        }

        .d-box-badge {
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 999px;
            font-weight: 700;
            display: inline-block;
        }

        .cfg-pill-btn {
            background: rgba(99, 102, 241, 0.2);
            color: #c7d2fe;
            border: 1px solid rgba(99, 102, 241, 0.4);
            border-radius: 999px;
            font-size: 9.5px;
            font-weight: 700;
            padding: 1px 6px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .cfg-pill-btn:hover {
            background: var(--primary);
            color: #fff;
        }

        /* Consensus & Inconclusive Banners */
        .consensus-banner {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            padding: 8px 12px;
            border-radius: var(--radius-sm);
            font-size: 12px;
        }

        .consensus-pill {
            padding: 2px 8px;
            border-radius: 999px;
            font-weight: 700;
            font-size: 11px;
        }

        .consensus-full { background: rgba(16, 185, 129, 0.2); color: #10b981; }
        .consensus-majority { background: rgba(99, 102, 241, 0.2); color: #a5b4fc; }
        .consensus-conflict { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }

        .inconclusive-alert {
            display: none;
            background: rgba(245, 158, 11, 0.1);
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: var(--radius-sm);
            padding: 10px 12px;
            font-size: 12px;
            color: #fbbf24;
            line-height: 1.4;
        }

        /* Score Hero */
        .score-hero {
            display: flex;
            align-items: center;
            gap: 1.5rem;
            padding: 1.25rem;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
        }

        .gauge-circle {
            position: relative;
            width: 90px;
            height: 90px;
            flex-shrink: 0;
        }

        .gauge-svg {
            transform: rotate(-90deg);
            width: 100%;
            height: 100%;
        }

        .gauge-bg {
            fill: none;
            stroke: rgba(255, 255, 255, 0.05);
            stroke-width: 8;
        }

        .gauge-meter {
            fill: none;
            stroke: var(--primary);
            stroke-width: 8;
            stroke-linecap: round;
            stroke-dasharray: 283;
            stroke-dashoffset: 283;
            transition: stroke-dashoffset 1s ease, stroke 0.3s;
        }

        .gauge-text {
            position: absolute;
            inset: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .gauge-number {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.3rem;
            font-weight: 700;
        }

        .gauge-label {
            font-size: 0.65rem;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 600;
        }

        .verdict-info {
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
        }

        .verdict-title {
            font-size: 1.25rem;
            font-weight: 700;
        }

        .badge {
            display: inline-block;
            align-self: flex-start;
            font-size: 0.75rem;
            padding: 0.2rem 0.6rem;
            border-radius: 9999px;
            font-weight: 600;
        }

        .badge-high { background: rgba(244, 63, 94, 0.15); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.3); }
        .badge-medium { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }
        .badge-low { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }

        .indicators-list {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 0.45rem;
        }

        .indicator-item {
            font-size: 0.85rem;
            color: #cbd5e1;
            display: flex;
            align-items: flex-start;
            gap: 0.5rem;
            line-height: 1.4;
            padding: 6px 10px;
            background: rgba(255, 255, 255, 0.02);
            border-radius: var(--radius-sm);
            border-left: 3px solid var(--primary);
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.6rem;
        }

        .feature-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            padding: 0.65rem;
            border-radius: var(--radius-sm);
            text-align: center;
        }

        .feature-name {
            font-size: 0.72rem;
            color: var(--text-muted);
            margin-bottom: 0.2rem;
        }

        .feature-val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-main);
        }

        .json-toggle-btn {
            background: none;
            border: none;
            color: #818cf8;
            font-size: 0.8rem;
            cursor: pointer;
            padding: 0.4rem 0;
            font-weight: 500;
        }

        .json-viewer {
            display: none;
            background: #05070c;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem;
            color: #38bdf8;
            max-height: 250px;
            overflow: auto;
            white-space: pre-wrap;
            margin-top: 0.5rem;
        }

        /* Modal Styles */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(8px);
            display: none;
            align-items: center; justify-content: center;
            z-index: 1000;
        }

        .modal-card {
            background: #0f172a;
            border: 1px solid var(--border-highlight);
            border-radius: var(--radius-md);
            width: 90%; max-width: 480px;
            padding: 24px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
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
            box-sizing: border-box;
            margin: 8px 0 16px 0;
        }

        .cfg-input:focus { border-color: var(--primary); }

        .modal-btn {
            padding: 8px 16px; border-radius: var(--radius-sm);
            font-weight: 700; font-size: 13px; cursor: pointer; border: none;
        }
        .modal-btn-cancel { background: rgba(255, 255, 255, 0.08); color: var(--text-muted); }
        .modal-btn-save { background: var(--primary-gradient); color: #fff; }

        footer {
            border-top: 1px solid var(--border);
            padding: 1.5rem 2rem;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.85rem;
        }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <div class="logo-group">
                <div class="logo-icon">⚡</div>
                <div>
                    <div class="brand-title">Gaia Detector — Hybrid AI Text Architecture</div>
                </div>
            </div>
            <div style="display: flex; gap: 8px; align-items: center;">
                <span class="brand-badge" id="hardwareBadge">Hardware: Initializing...</span>
                <span class="brand-badge" style="background: rgba(16, 185, 129, 0.15); color: #10b981; border-color: rgba(16, 185, 129, 0.3);">Hybrid v2.0</span>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="hero-banner">
            <h1 class="hero-title">Hybrid AI Content Detector</h1>
            <p class="hero-sub">Multi-evidence verification fusing custom 18-feature linguistic metrics, pretrained RoBERTa sequence classification, and GPTZero commercial API.</p>
        </div>

        <div class="main-layout">
            <!-- Left: Input Area -->
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">📝 Input Content</h2>
                    <div class="sample-actions">
                        <button class="btn-pill" id="loadAiBtn">Load AI Sample</button>
                        <button class="btn-pill" id="loadHumanBtn">Load Human Sample</button>
                    </div>
                </div>

                <div class="textarea-wrapper">
                    <textarea id="textInput" placeholder="Paste your text here (minimum 25-50 words recommended for accurate linguistic analysis)..."></textarea>
                    <div class="textarea-meta">
                        <span id="wordCount">0 words</span>
                        <span id="charCount">0 characters</span>
                    </div>
                </div>

                <button class="btn-primary" id="analyzeBtn">
                    <span id="btnIcon">⚡</span>
                    <span id="btnText">Run Hybrid Text Analysis</span>
                </button>
            </div>

            <!-- Right: Results Panel -->
            <div class="card" id="resultCard">
                <div class="result-empty" id="resultEmpty" style="text-align: center; padding: 3rem 1rem;">
                    <div style="font-size: 2.5rem; margin-bottom: 0.8rem;">📊</div>
                    <h3>Awaiting Text Input</h3>
                    <p style="margin-top: 0.5rem; font-size: 0.9rem; color: var(--text-muted);">Enter text on the left to execute multi-model ensemble detection.</p>
                </div>

                <div id="resultContent" style="display: none; display: flex; flex-direction: column; gap: 14px;">
                    <!-- 3-Model Detector Cards Grid -->
                    <div class="detectors-grid">
                        <div class="detector-box">
                            <div class="d-box-title">Custom 18-RF</div>
                            <div class="d-box-score" id="dScoreCustom">--%</div>
                            <div class="d-box-badge" id="dBadgeCustom" style="background: rgba(255,255,255,0.06); color: var(--text-muted);">Pending</div>
                        </div>
                        <div class="detector-box">
                            <div class="d-box-title">HF RoBERTa</div>
                            <div class="d-box-score" id="dScoreHf">--%</div>
                            <div class="d-box-badge" id="dBadgeHf" style="background: rgba(255,255,255,0.06); color: var(--text-muted);">Pending</div>
                        </div>
                        <div class="detector-box">
                            <div class="d-box-title">
                                <span>GPTZero</span>
                                <button class="cfg-pill-btn" onclick="openGPTZeroModal(event)">⚙️ Config</button>
                            </div>
                            <div class="d-box-score" id="dScoreGz">--%</div>
                            <div class="d-box-badge" id="dBadgeGz" style="background: rgba(255,255,255,0.06); color: var(--text-muted);">Checking...</div>
                        </div>
                    </div>

                    <!-- Consensus Banner -->
                    <div class="consensus-banner" id="consensusBanner" style="display: none;">
                        <div><strong>Multi-Model Agreement:</strong> <span id="consensusText">--</span></div>
                        <span class="consensus-pill" id="consensusPill">--</span>
                    </div>

                    <!-- Inconclusive Alert -->
                    <div class="inconclusive-alert" id="inconclusiveAlert"></div>

                    <!-- Score Hero -->
                    <div class="score-hero">
                        <div class="gauge-circle">
                            <svg class="gauge-svg" viewBox="0 0 100 100">
                                <circle class="gauge-bg" cx="50" cy="50" r="45"></circle>
                                <circle class="gauge-meter" id="gaugeMeter" cx="50" cy="50" r="45"></circle>
                            </svg>
                            <div class="gauge-text">
                                <span class="gauge-number" id="probNumber">0%</span>
                                <span class="gauge-label">AI Score</span>
                            </div>
                        </div>
                        <div class="verdict-info">
                            <h3 class="verdict-title" id="verdictText">Likely AI-generated</h3>
                            <div class="verdict-badges">
                                <span class="badge" id="confidenceBadge">High Confidence</span>
                            </div>
                        </div>
                    </div>

                    <div style="font-size: 11.5px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Key Evidentiary Indicators</div>
                    <ul class="indicators-list" id="indicatorsList"></ul>

                    <div style="font-size: 11.5px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Preserved 18-Feature Dimensions</div>
                    <div class="features-grid" id="featuresGrid"></div>

                    <button class="json-toggle-btn" id="toggleJsonBtn">▶ View Full API Response JSON</button>
                    <pre class="json-viewer" id="jsonViewer"></pre>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal for GPTZero API Configuration -->
    <div class="modal-overlay" id="configModal" onclick="closeModalOnBg(event)">
        <div class="modal-card">
            <h3 style="margin-bottom: 8px;">⚙️ Configure GPTZero Commercial API</h3>
            <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 14px; line-height: 1.5;">
                Enter your GPTZero API Key from <a href="https://gptzero.me/api" target="_blank" style="color: var(--primary); text-decoration: underline;">gptzero.me/api</a> to enable independent commercial verification.
            </p>
            <label style="font-size: 12px; font-weight: 700; color: #cbd5e1;">API Key</label>
            <input type="password" id="gptzeroKeyInput" placeholder="e.g. gptzero_live_..." class="cfg-input">
            <div style="font-size: 11.5px; color: #64748b; margin-bottom: 16px;">
                💡 Stored locally in <code>detector/.env</code>. When left unconfigured, the system continues operating with the local 2-model ensemble.
            </div>
            <div style="display: flex; gap: 8px; justify-content: flex-end;">
                <button class="modal-btn modal-btn-cancel" onclick="closeGPTZeroModal()">Cancel</button>
                <button class="modal-btn modal-btn-save" id="saveKeyBtn" onclick="saveGPTZeroConfig()">Save & Activate</button>
            </div>
        </div>
    </div>

    <footer>
        Gaia Detector • Hybrid AI-Generated Text Detection System • Random Forest + RoBERTa + GPTZero
    </footer>

    <script>
        const AI_SAMPLE = `Artificial intelligence in education is rapidly transforming how students learn and teachers instruct, ushering in an era of personalized learning and greater accessibility. Traditionally, classrooms have relied on a one-size-fits-all model where a single educator attempts to cater to the diverse needs of numerous students. AI changes this dynamic by introducing adaptive learning platforms that can assess a student's individual strengths, weaknesses, and learning pace. By analyzing performance data, these systems provide customized resources, targeted exercises, and immediate feedback, ensuring that no student is left behind or bored by material that is too easy.`;

        const HUMAN_SAMPLE = `This weekend, KCRW teamed up with 826LA, a tutoring non-profit (and all-around great org), for an exciting weekend at the Los Angeles Times Festival of Books at USC. We encouraged people to contribute a line to our Longest Story in the World project by continuing the crowd-sourced story by writing the next line. These two stories twist and turn with each line, but can you find a common thread? It might be difficult for this story to stay on theme, but it sure was fun to see the community's input and ability to come together!`;

        const textInput = document.getElementById("textInput");
        const wordCount = document.getElementById("wordCount");
        const charCount = document.getElementById("charCount");
        const analyzeBtn = document.getElementById("analyzeBtn");
        const btnText = document.getElementById("btnText");
        const btnIcon = document.getElementById("btnIcon");
        const resultEmpty = document.getElementById("resultEmpty");
        const resultContent = document.getElementById("resultContent");

        function updateCounts() {
            const val = textInput.value.trim();
            const words = val.length ? val.split(/\s+/).length : 0;
            wordCount.textContent = `${words} words`;
            charCount.textContent = `${textInput.value.length} characters`;
        }

        textInput.addEventListener("input", updateCounts);

        document.getElementById("loadAiBtn").addEventListener("click", () => {
            textInput.value = AI_SAMPLE;
            updateCounts();
        });

        document.getElementById("loadHumanBtn").addEventListener("click", () => {
            textInput.value = HUMAN_SAMPLE;
            updateCounts();
        });

        const toggleJsonBtn = document.getElementById("toggleJsonBtn");
        const jsonViewer = document.getElementById("jsonViewer");
        toggleJsonBtn.addEventListener("click", () => {
            const isHidden = jsonViewer.style.display === "none" || !jsonViewer.style.display;
            jsonViewer.style.display = isHidden ? "block" : "none";
            toggleJsonBtn.textContent = isHidden ? "▼ Hide API Response JSON" : "▶ View Full API Response JSON";
        });

        analyzeBtn.addEventListener("click", async () => {
            const text = textInput.value.trim();
            if (!text) {
                alert("Please paste or type text to analyze.");
                return;
            }

            analyzeBtn.disabled = true;
            btnIcon.innerHTML = `<span class="loading-spinner"></span>`;
            btnText.textContent = "Running Hybrid Multi-Model Analysis...";

            try {
                const response = await fetch("/detect", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text })
                });

                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.detail || "Analysis failed");
                }

                const data = await response.json();
                renderResults(data);

            } catch (err) {
                alert(`Error: ${err.message}`);
            } finally {
                analyzeBtn.disabled = false;
                btnIcon.textContent = "⚡";
                btnText.textContent = "Run Hybrid Text Analysis";
            }
        });

        function renderResults(data) {
            resultEmpty.style.display = "none";
            resultContent.style.display = "flex";

            const prob = data.probability;
            const verdict = data.verdict;
            const confidence = data.confidence;

            // Gauge Fill
            document.getElementById("probNumber").textContent = `${prob}%`;
            const gaugeMeter = document.getElementById("gaugeMeter");
            const offset = 283 - (283 * (prob / 100));
            gaugeMeter.style.strokeDashoffset = offset;

            let strokeColor = "#10b981";
            if (verdict === "Likely AI-generated") strokeColor = "#f43f5e";
            else if (verdict === "Inconclusive / Uncertain") strokeColor = "#f59e0b";
            gaugeMeter.style.stroke = strokeColor;

            // Verdict Title & Badge
            const verdictTitle = document.getElementById("verdictText");
            verdictTitle.textContent = verdict;
            const badge = document.getElementById("confidenceBadge");
            badge.textContent = `${confidence} Confidence`;
            badge.className = "badge";
            if (confidence === "High") badge.classList.add(prob >= 50 ? "badge-high" : "badge-low");
            else if (confidence === "Medium") badge.classList.add("badge-medium");
            else badge.classList.add("badge-low");

            // 3-Model Cards Breakdown
            const ind = data.individual_detectors || {};
            const cDet = ind.custom_rf;
            if (cDet) {
                document.getElementById("dScoreCustom").textContent = `${cDet.ai_probability}%`;
                const b = document.getElementById("dBadgeCustom");
                b.textContent = cDet.verdict.replace("Likely ", "");
                b.style.background = cDet.ai_probability >= 50 ? "rgba(244,63,94,0.2)" : "rgba(16,185,129,0.2)";
                b.style.color = cDet.ai_probability >= 50 ? "#f43f5e" : "#10b981";
            }

            const hfDet = ind.hf_roberta;
            if (hfDet) {
                document.getElementById("dScoreHf").textContent = hfDet.status === "success" ? `${hfDet.ai_probability}%` : "--%";
                const b = document.getElementById("dBadgeHf");
                b.textContent = hfDet.status === "success" ? hfDet.verdict.replace("Likely ", "") : hfDet.status.toUpperCase();
                b.style.background = hfDet.status === "success" ? (hfDet.ai_probability >= 50 ? "rgba(244,63,94,0.2)" : "rgba(16,185,129,0.2)") : "rgba(255,255,255,0.06)";
                b.style.color = hfDet.status === "success" ? (hfDet.ai_probability >= 50 ? "#f43f5e" : "#10b981") : "#94a3b8";
            }

            const gzDet = ind.gptzero_api;
            if (gzDet) {
                document.getElementById("dScoreGz").textContent = gzDet.status === "success" ? `${gzDet.ai_probability}%` : "--%";
                const b = document.getElementById("dBadgeGz");
                b.textContent = gzDet.status === "success" ? gzDet.verdict.replace("Likely ", "") : gzDet.status.toUpperCase();
                b.style.background = gzDet.status === "success" ? (gzDet.ai_probability >= 50 ? "rgba(244,63,94,0.2)" : "rgba(16,185,129,0.2)") : "rgba(255,255,255,0.06)";
                b.style.color = gzDet.status === "success" ? (gzDet.ai_probability >= 50 ? "#f43f5e" : "#10b981") : "#94a3b8";
            }

            // Consensus Banner
            const banner = document.getElementById("consensusBanner");
            const pill = document.getElementById("consensusPill");
            const alertBox = document.getElementById("inconclusiveAlert");
            if (data.consensus) {
                banner.style.display = "flex";
                document.getElementById("consensusText").textContent = `${data.consensus.active_detectors}/${data.consensus.total_detectors} Models Active`;
                pill.textContent = data.consensus.agreement;
                pill.className = "consensus-pill";
                if (data.consensus.agreement === "Full Consensus") pill.classList.add("consensus-full");
                else if (data.consensus.agreement === "Majority Agreement") pill.classList.add("consensus-majority");
                else pill.classList.add("consensus-conflict");

                if (data.consensus.inconclusive_reason) {
                    alertBox.style.display = "block";
                    alertBox.innerHTML = `<strong>Inconclusive Notice:</strong> ${data.consensus.inconclusive_reason}`;
                } else {
                    alertBox.style.display = "none";
                }
            }

            // Indicators
            const indicatorsList = document.getElementById("indicatorsList");
            indicatorsList.innerHTML = "";
            (data.indicators || []).forEach(ind => {
                const li = document.createElement("li");
                li.className = "indicator-item";
                li.innerHTML = `<span>•</span><span>${ind}</span>`;
                indicatorsList.appendChild(li);
            });

            // Feature Grid
            const featuresGrid = document.getElementById("featuresGrid");
            featuresGrid.innerHTML = "";
            const features = data.features || {};
            const displayKeys = [
                { key: "perplexity", label: "GPT-2 Perplexity" },
                { key: "burstiness", label: "Burstiness Score" },
                { key: "vocabularyRichness", label: "Vocab Richness (TTR)" },
                { key: "semanticConsistency", label: "Semantic Coherence" },
                { key: "repetition", label: "Repetition Score" },
                { key: "grammarPatterns", label: "Grammar Precision" }
            ];

            displayKeys.forEach(item => {
                const val = features[item.key] !== undefined ? features[item.key] : "N/A";
                const div = document.createElement("div");
                div.className = "feature-card";
                div.innerHTML = `
                    <div class="feature-name">${item.label}</div>
                    <div class="feature-val">${val}</div>
                `;
                featuresGrid.appendChild(div);
            });

            // Raw JSON
            document.getElementById("jsonViewer").textContent = JSON.stringify(data, null, 2);
        }

        // Live Model Status Check
        async function checkModelStatuses() {
            try {
                const res = await fetch("/models");
                if (!res.ok) return;
                const data = await res.json();
                const gz = data.models?.gptzero_api;
                if (gz) {
                    const badge = document.getElementById("dBadgeGz");
                    if (gz.status === "active") {
                        badge.textContent = "Active (Ready)";
                        badge.style.background = "rgba(16, 185, 129, 0.2)";
                        badge.style.color = "#10b981";
                    } else {
                        badge.textContent = "Unconfigured";
                        badge.style.background = "rgba(255, 255, 255, 0.06)";
                        badge.style.color = "#94a3b8";
                    }
                }
            } catch (e) {
                console.error("Failed to check models:", e);
            }
        }

        // Modal Handlers
        function openGPTZeroModal(e) {
            if (e) e.stopPropagation();
            document.getElementById("configModal").style.display = "flex";
        }

        function closeGPTZeroModal() {
            document.getElementById("configModal").style.display = "none";
        }

        function closeModalOnBg(e) {
            if (e.target.id === "configModal") closeGPTZeroModal();
        }

        async function saveGPTZeroConfig() {
            const key = document.getElementById("gptzeroKeyInput").value.trim();
            if (!key) {
                alert("Please enter a valid GPTZero API key.");
                return;
            }

            const btn = document.getElementById("saveKeyBtn");
            btn.textContent = "Saving...";
            btn.disabled = true;

            try {
                const res = await fetch("/config/gptzero", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ api_key: key, enabled: true })
                });
                const data = await res.json();
                if (data.status === "success") {
                    closeGPTZeroModal();
                    await checkModelStatuses();
                    alert("✅ GPTZero API credentials saved and activated successfully!");
                } else {
                    alert("Failed to save credentials.");
                }
            } catch (err) {
                alert(`Error: ${err.message}`);
            } finally {
                btn.textContent = "Save & Activate";
                btn.disabled = false;
            }
        }

        // On Load: Health check & Model statuses
        window.addEventListener("DOMContentLoaded", () => {
            fetch("/health").then(r => r.json()).then(h => {
                document.getElementById("hardwareBadge").textContent = `Hardware: ${h.hardware_acceleration}`;
            }).catch(() => {});
            checkModelStatuses();
        });
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)


def run_cli_test():
    """Console test run displaying hybrid multi-model prediction output."""
    print("=" * 65)
    print("GAIA DETECTOR - HYBRID AI TEXT DETECTOR CLI VERIFICATION")
    print("=" * 65)

    ai_sample = (
        "Artificial intelligence in education is rapidly transforming how students "
        "learn and teachers instruct, ushering in an era of personalized learning "
        "and greater accessibility. Adaptive learning platforms assess individual "
        "strengths and weaknesses to deliver targeted feedback."
    )

    print("\n[Testing Sample Text]")
    print(f"Sample: {ai_sample[:80]}...\n")

    detector = get_detector()
    result = detector.predict(ai_sample)

    print("========== HYBRID DETECTOR JSON RESPONSE ==========")
    print(json.dumps(result, indent=2))
    print("====================================================")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_cli_test()
    else:
        print("\nStarting Gaia Hybrid AI Text Detector on http://127.0.0.1:8000")
        print("To run in test CLI mode instead: python app.py --test\n")
        uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)